# ocr_system.py
import os
import re
import json
from typing import List, Dict, Tuple, Optional, Union
import numpy as np
import cv2
from PIL import Image, ImageFilter, ImageOps
import traceback

# Local OCR engines removed (EasyOCR, PaddleOCR, TrOCR). Cloud-only pipeline remains.

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
from .openfoodfacts_lookup import query_openfoodfacts
from .doctr_api import doctr_api_ocr

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
# Removed (EasyOCR/Paddle/TrOCR). Cloud-only OCR via DocTR API.

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
def extract_structured_from_image(
    image_path_or_bytes: Union[str, bytes],
    barcode: Optional[str] = None,
    product_name: Optional[str] = None,
) -> Dict:
    """
    Returns:
    {
      "raw_ocr": [ {box, text, conf}, ... ],
      "sections": {ingredients, nutrition, claims, other},
      "debug": {infos}
    }
    """
    debug = {"engines": [], "notes": [], "pipeline": []}
    try:
        # Step 1: OpenFoodFacts (skip OCR if product is found)
        if barcode or product_name:
            off = query_openfoodfacts(barcode=barcode, product_name=product_name)
            if off.get("ok"):
                text = off.get("text", "") or ""
                merged = [{"box": (0,0,0,0), "text": line, "conf": 0.99} for line in text.splitlines() if line.strip()]
                sections = split_to_sections(merged)
                structured = off.get("structured") or {}
                debug["engines"].append("openfoodfacts")
                debug["pipeline"].append("OpenFoodFacts")
                return {
                    "text": text,
                    "structured": structured if structured else sections,
                    "method": "OpenFoodFacts",
                    "confidence": "high",
                    "raw_ocr": merged,
                    "sections": sections,
                    "debug": debug,
                }
            else:
                debug["notes"].append(f"OpenFoodFacts lookup failed: {off.get('error')}")
                debug["pipeline"].append("OpenFoodFacts:fail")

        # Step 2: Hugging Face DocTR Inference API
        doc = doctr_api_ocr(image_path_or_bytes)
        if doc.get("ok") and (doc.get("text") or "").strip():
            full_text = doc.get("text", "")
            merged = [{"box": (0,0,0,0), "text": line, "conf": 0.85} for line in full_text.splitlines() if line.strip()]
            sections = split_to_sections(merged)
            structured = {}
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
            debug["engines"].append("doctr_api")
            debug["pipeline"].append("DocTR API")
            confidence = "medium" if len(full_text.strip()) > 10 else "low"
            return {
                "text": full_text,
                "structured": structured if structured else sections,
                "method": "DocTR API",
                "confidence": confidence,
                "raw_ocr": merged,
                "sections": sections,
                "debug": debug,
            }
        else:
            if not doc.get("ok"):
                debug["notes"].append(f"DocTR API error: {doc.get('error') or doc.get('details')}")
            debug["pipeline"].append("DocTR API:fail")

        # All tiers failed; return graceful, minimal payload
        return {
            "text": "",
            "structured": {},
            "method": "none",
            "confidence": "low",
            "raw_ocr": [],
            "sections": {"ingredients": "", "nutrition": "", "claims": "", "other": ""},
            "debug": debug,
        }
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

