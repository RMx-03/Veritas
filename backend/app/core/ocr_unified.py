# ocr_system.py
import os
import re
import json
from typing import List, Dict, Tuple, Optional, Union
import numpy as np
import cv2
from PIL import Image, ImageFilter, ImageOps
import traceback

# Try imports of optional heavy libs. Fallback gracefully.
try:
    import easyocr
except Exception:
    easyocr = None

try:
    from paddleocr import PaddleOCR
except Exception:
    PaddleOCR = None

try:
    # TrOCR via transformers
    from transformers import VisionEncoderDecoderModel, TrOCRProcessor
    import torch
except Exception:
    VisionEncoderDecoderModel = None
    TrOCRProcessor = None
    torch = None

# Optional nutrition parsers for structured output (backward compatibility with previous unified OCR API)
try:
    from .parser_enhanced import parse_nutrition_data as _enhanced_parse
    ENHANCED_PARSER = True
except Exception:
    ENHANCED_PARSER = False
    try:
        from .parser import parse_nutrition_data as _basic_parse
    except Exception:
        _basic_parse = None
        _enhanced_parse = None

# Cache heavy OCR engine instances so we don't re-create per crop
_paddle_instance: Optional['PaddleOCR'] = None
_easy_reader_cache: Dict[str, 'easyocr.Reader'] = {}

# ---- Utilities ----
def load_image(path_or_bytes):
    if isinstance(path_or_bytes, (bytes, bytearray)):
        arr = np.frombuffer(path_or_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(path_or_bytes)
    if img is None:
        raise ValueError("Unable to read image")
    return img

def to_pil(img):
    if isinstance(img, np.ndarray):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img)
    return img

# ---- Preprocessing ----
def preprocess_image_for_ocr(img: np.ndarray, upscale: bool = True) -> np.ndarray:
    """
    Preprocessing steps:
    - Convert to gray
    - Resize if small (upscale)
    - Apply CLAHE (adaptive histogram equalization)
    - Denoise and sharpen
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    # upscale small images
    if upscale and max(h, w) < 1200:
        scale = max(1.0, 1200.0 / max(h, w))
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    # CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    # denoise
    gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    # sharpen (unsharp mask)
    blur = cv2.GaussianBlur(gray, (0,0), 3)
    sharp = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)
    # convert back to BGR for engines expecting color
    return cv2.cvtColor(sharp, cv2.COLOR_GRAY2BGR)

# ---- Simple panel detection (nutrition block) ----
def detect_text_contours(img: np.ndarray, min_area_ratio=0.0005) -> List[Tuple[int,int,int,int]]:
    """Return list of bounding boxes likely to contain text (x,y,w,h)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # binarize
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # morphology to join letters into blocks
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15,3))
    morphed = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    h, w = gray.shape
    min_area = h * w * min_area_ratio
    for cnt in contours:
        x, y, ww, hh = cv2.boundingRect(cnt)
        area = ww * hh
        if area > min_area and hh > 20 and ww > 40:
            boxes.append((x,y,ww,hh))
    # sort left->right, top->down
    boxes = sorted(boxes, key=lambda b: (b[1], b[0]))
    return boxes

def crop_boxes(img: np.ndarray, boxes: List[Tuple[int,int,int,int]]) -> List[np.ndarray]:
    crops = []
    for (x,y,w,h) in boxes:
        pad = 5
        x0,y0,x1,y1 = max(0,x-pad), max(0,y-pad), min(img.shape[1], x+w+pad), min(img.shape[0], y+h+pad)
        crops.append(img[y0:y1, x0:x1])
    return crops

# ---- OCR wrappers ----
def ocr_easyocr(img: np.ndarray, langs: List[str]=["en"]) -> List[Dict]:
    if easyocr is None:
        return []
    try:
        key = ",".join(langs)
        reader = _easy_reader_cache.get(key)
        if reader is None:
            reader = easyocr.Reader(langs, gpu=False)
            _easy_reader_cache[key] = reader
        results = reader.readtext(img)
        out = []
        for bbox, text, conf in results:
            out.append({"text": text, "conf": float(conf), "bbox": bbox})
        return out
    except Exception as e:
        print("EasyOCR error:", e)
        return []

def ocr_paddle(img: np.ndarray) -> List[Dict]:
    if PaddleOCR is None:
        return []
    global _paddle_instance
    try:
        if _paddle_instance is None:
            _paddle_instance = PaddleOCR(use_angle_cls=True, lang='en')
        result = _paddle_instance.ocr(img, cls=True)
        out = []
        for line in result:
            if isinstance(line, list) and len(line) >= 2:
                bbox = line[0]
                txt, conf = line[1]
                out.append({"text": txt, "conf": float(conf), "bbox": bbox})
        return out
    except Exception as e:
        print("PaddleOCR error:", e)
        return []

# TrOCR wrapper (requires transformers + torch)
_trocr_model = None
_trocr_processor = None
def init_trocr(model_name="microsoft/trocr-small-printed"):
    global _trocr_model, _trocr_processor
    if VisionEncoderDecoderModel is None or TrOCRProcessor is None or torch is None:
        return False
    try:
        _trocr_model = VisionEncoderDecoderModel.from_pretrained(model_name)
        _trocr_processor = TrOCRProcessor.from_pretrained(model_name)
        _trocr_model.to("cpu")
        return True
    except Exception as e:
        print("TrOCR init error:", e)
        return False

def ocr_trocr(img: np.ndarray) -> List[Dict]:
    """
    Run TrOCR on the whole image. Returns single-block output (image->text).
    For region-level OCR, crop first and call this per-crop.
    """
    if _trocr_model is None or _trocr_processor is None:
        return []
    try:
        pil = to_pil(img).convert("RGB")
        pixel_values = _trocr_processor(images=pil, return_tensors="pt").pixel_values
        with torch.no_grad():
            output_ids = _trocr_model.generate(pixel_values)
        pred = _trocr_processor.batch_decode(output_ids, skip_special_tokens=True)[0]
        # return single item with full image bbox
        h, w = img.shape[:2]
        return [{"text": pred, "conf": 0.9, "bbox": [(0,0),(w,0),(w,h),(0,h)]}]
    except Exception as e:
        print("TrOCR error:", e)
        return []

# ---- Ensemble / merge utilities ----
def merge_ocr_results(boxed_results: List[Tuple[Tuple[int,int,int,int], List[Dict]]]) -> List[Dict]:
    """
    boxed_results: list of (box, [ocr_results for that box]) where each ocr_result has 'text','conf'
    We'll pick best text per box by confidence and apply simple voting if multiple texts similar.
    """
    merged = []
    for (box, results) in boxed_results:
        if not results:
            continue
        # pick highest confidence string
        best = max(results, key=lambda r: r.get("conf", 0.0))
        merged.append({"box": box, "text": best["text"], "conf": best.get("conf", 0.0)})
    return merged

# ---- Post-processing to sections ----
def split_to_sections(merged_texts: List[Dict]) -> Dict[str, str]:
    """
    Simple heuristics:
    - If a line contains 'ingredient' -> ingredients section
    - If a line contains 'nutrition' or 'calories' or '% Daily' -> nutrition block
    - 'claim' patterns: free-from, sugar-free, low fat, etc -> claims
    We'll join texts in reading order.
    """
    text_lines = [m["text"] for m in merged_texts]
    joined = "\n".join(text_lines)
    lower = joined.lower()
    sections = {"ingredients": "", "nutrition": "", "claims": "", "other": joined}
    # ingredients
    m = re.search(r"(ingredients?[:\s]*)(.*)", joined, flags=re.I|re.S)
    if m:
        sections["ingredients"] = m.group(2).split("\n")[0].strip()
    else:
        # fallback: look for a line starting with ingredients
        for line in text_lines:
            if line.lower().strip().startswith("ingredients"):
                sections["ingredients"] = line.split(":",1)[-1].strip()
                break
    # nutrition
    if "nutrition" in lower or "calories" in lower or "per 100" in lower:
        # attempt to extract contiguous block containing calories/nutrients
        lines = []
        for line in text_lines:
            if any(k in line.lower() for k in ("calories","fat","protein","carbohydrate","sugars","serving")):
                lines.append(line)
        sections["nutrition"] = "\n".join(lines)
    # claims
    claims_list = []
    for line in text_lines:
        if any(k in line.lower() for k in ("free","no added","low","dietary","sugar-free","gluten-free","boost")):
            claims_list.append(line)
    sections["claims"] = "\n".join(claims_list)
    return sections

# ---- Main pipeline function ----
def extract_structured_from_image(image_path_or_bytes: Union[str, bytes]) -> Dict:
    """
    Returns:
    {
      "raw_ocr": [ {box, text, conf}, ... ],
      "sections": {ingredients, nutrition, claims, other},
      "debug": {infos}
    }
    """
    debug = {"engines": [], "notes": []}
    try:
        img = load_image(image_path_or_bytes)
        pre = preprocess_image_for_ocr(img)
        # detect boxes
        boxes = detect_text_contours(pre)
        crops = crop_boxes(pre, boxes)
        all_box_results = []
        # for each crop, run recognizers (Paddle, TrOCR, EasyOCR) in order
        for i, crop in enumerate(crops):
            engine_res = []
            box_tuple = boxes[i]
            # Paddle
            if PaddleOCR is not None:
                try:
                    cres = ocr_paddle(crop)
                    if cres:
                        engine_res.extend([{"text": r["text"], "conf": r.get("conf",0.0)} for r in cres])
                        debug["engines"].append("paddle")
                except Exception as e:
                    debug["notes"].append(f"paddle error: {e}")
            # TrOCR per crop if available
            if VisionEncoderDecoderModel is not None and TrOCRProcessor is not None and torch is not None:
                try:
                    if _trocr_model is None:
                        init_trocr()
                    tres = ocr_trocr(crop)
                    if tres:
                        engine_res.extend([{"text": r["text"], "conf": r.get("conf",0.0)} for r in tres])
                        debug["engines"].append("trocr")
                except Exception as e:
                    debug["notes"].append(f"trocr error: {e}")
            # EasyOCR
            if easyocr is not None:
                try:
                    eres = ocr_easyocr(crop)
                    if eres:
                        engine_res.extend([{"text": r["text"], "conf": r.get("conf",0.0)} for r in eres])
                        debug["engines"].append("easyocr")
                except Exception as e:
                    debug["notes"].append(f"easyocr error: {e}")
            # fallback empty
            all_box_results.append((box_tuple, engine_res))
        # Also, run a whole-image OCR fallback (for labels where detection misses)
        whole_img_results = []
        if VisionEncoderDecoderModel is not None and TrOCRProcessor is not None and torch is not None:
            try:
                if _trocr_model is None:
                    init_trocr()
                wres = ocr_trocr(pre)
                whole_img_results.extend(wres)
                debug["engines"].append("trocr_whole")
            except Exception as e:
                debug["notes"].append(f"trocr whole error: {e}")
        if easyocr is not None and not whole_img_results:
            try:
                wres = ocr_easyocr(pre)
                whole_img_results.extend(wres)
                debug["engines"].append("easyocr_whole")
            except Exception as e:
                debug["notes"].append(f"easyocr whole error: {e}")

        merged = merge_ocr_results(all_box_results)
        # if merged is empty, use whole image text as fallback
        if not merged and whole_img_results:
            merged = [{"box": (0,0,pre.shape[1], pre.shape[0]), "text": r["text"], "conf": r.get("conf",0.0)} for r in whole_img_results]

        sections = split_to_sections(merged)

        # Build backward-compatible structured nutrition object if parser available
        structured = {}
        full_text = "\n".join([m["text"] for m in merged]) if merged else ""
        if ENHANCED_PARSER and _enhanced_parse:
            try:
                structured = _enhanced_parse(full_text)
            except Exception:
                pass
        elif not ENHANCED_PARSER and '_basic_parse' in globals() and _basic_parse:
            try:
                structured = _basic_parse(full_text)
            except Exception:
                pass

        # Determine primary method heuristically based on engines used
        method_priority = [
            ("paddle", "PaddleOCR"),
            ("trocr", "TrOCR"),
            ("easyocr", "EasyOCR"),
        ]
        chosen_method = "unknown"
        for key, label in method_priority:
            if any(key in e for e in debug["engines"]):
                chosen_method = label
                break

        # Confidence heuristic: number of boxes + presence of high-confidence engines
        if chosen_method in ("PaddleOCR", "TrOCR") and len(merged) >= 3:
            confidence = "high"
        elif len(merged) >= 1:
            confidence = "medium"
        else:
            confidence = "low"

        # Original style return (for existing API code)
        compatibility_payload = {
            "text": full_text,
            "structured": structured if structured else sections,
            "method": chosen_method,
            "confidence": confidence,
            # Extended debug info retained
            "raw_ocr": merged,
            "sections": sections,
            "debug": debug,
        }
        return compatibility_payload
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

