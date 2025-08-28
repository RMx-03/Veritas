"""
Unified OCR/Extraction pipeline with local Transformers models.

Modes (select via env OCR_ENGINE):
- 'trocr' (default): TrOCR image-to-text using local transformers, then structure via parser (regex).
- 'donut': Donut end-to-end (future implementation).
- 'fallback': Simple text extraction fallback.

Env vars (backend/.env):
- OCR_ENGINE=trocr|donut|fallback
- HF_TROCR_MODEL=microsoft/trocr-large-printed (default)
- HF_DONUT_MODEL=naver-clova-ix/donut-base-finetuned-docvqa (default)
- USE_LAYOUT_REFINER=false (default)
"""
from __future__ import annotations

import os
import json
import logging
from typing import Dict, Any, Optional
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not installed. Install with: pip install transformers torch torchvision Pillow")

# Import local parser to build structured output from text
from parser import parse_nutrition_data

logger = logging.getLogger(__name__)

def _sanitize_model_id(mid: str) -> str:
    return (mid or "").strip().strip('"').strip("'")

OCR_ENGINE = (os.getenv("OCR_ENGINE", "trocr") or "trocr").strip().lower()
HF_TROCR_MODEL = _sanitize_model_id(os.getenv("HF_TROCR_MODEL", "microsoft/trocr-large-printed"))
HF_DONUT_MODEL = _sanitize_model_id(os.getenv("HF_DONUT_MODEL", "naver-clova-ix/donut-base-finetuned-docvqa"))
USE_LAYOUT_REFINER = (os.getenv("USE_LAYOUT_REFINER", "false") or "false").strip().lower() == "true"

# Global model cache to avoid reloading
_trocr_processor = None
_trocr_model = None


def _require_transformers():
    if not TRANSFORMERS_AVAILABLE:
        raise RuntimeError("transformers library not available. Install with: pip install transformers torch torchvision Pillow")


def _get_trocr_components(model_id: str):
    """Get or create TrOCR processor and model, cached globally."""
    global _trocr_processor, _trocr_model
    _require_transformers()
    
    # Force reload if model_id changed
    current_model = getattr(_get_trocr_components, '_current_model', None)
    if current_model != model_id:
        logger.info(f"[TrOCR] Model changed from {current_model} to {model_id}, clearing cache")
        _trocr_processor = None
        _trocr_model = None
        _get_trocr_components._current_model = model_id
    
    if _trocr_processor is None or _trocr_model is None:
        logger.info(f"[TrOCR] Loading model: {model_id}")
        try:
            _trocr_processor = TrOCRProcessor.from_pretrained(model_id)
            _trocr_model = VisionEncoderDecoderModel.from_pretrained(model_id)
            logger.info(f"[TrOCR] Model loaded successfully")
        except Exception as e:
            logger.error(f"[TrOCR] Failed to load model {model_id}: {e}")
            raise RuntimeError(f"Failed to load TrOCR model {model_id}: {e}")
    
    return _trocr_processor, _trocr_model

def _pil_preprocess(image: Image.Image) -> Image.Image:
    """Lightweight preprocessing to improve OCR robustness without extra deps.
    - Auto-orient using EXIF
    - Convert to RGB
    - Auto-contrast, gentle sharpen and contrast boost
    - Upscale small images to improve legibility before model resize
    """
    try:
        image = ImageOps.exif_transpose(image)
    except Exception:
        pass
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Improve contrast and sharpness slightly
    image = ImageOps.autocontrast(image)

    # Upscale if the image is relatively small
    max_side = max(image.size)
    if max_side < 1000:
        scale = 1280 / max_side
        new_size = (int(image.width * scale), int(image.height * scale))
        image = image.resize(new_size, Image.LANCZOS)

    image = ImageEnhance.Sharpness(image).enhance(1.2)
    image = ImageEnhance.Contrast(image).enhance(1.2)
    return image

def _local_trocr_extract(model_id: str, image_path: str) -> str:
    """Extract text from image using local TrOCR model.
    Returns plain text or raises on failure.
    """
    model_id = _sanitize_model_id(model_id)
    logger.info(f"[TrOCR] Processing image with model: {model_id}")
    
    try:
        # Load and preprocess image
        raw_image = Image.open(image_path)
        base_image = _pil_preprocess(raw_image)
        
        # Get processor and model
        processor, model = _get_trocr_components(model_id)
        model.eval()
        
        def _infer(img: Image.Image) -> str:
            pixel_values = processor(img, return_tensors="pt").pixel_values
            try:
                pixel_values = pixel_values.to(next(model.parameters()).device)
            except Exception:
                pass
            logger.info(f"[TrOCR] Input image tensor shape: {pixel_values.shape}")
            import torch
            with torch.no_grad():
                generated_ids = model.generate(
                    pixel_values,
                    max_new_tokens=256,
                    do_sample=False,
                    num_beams=4,
                    early_stopping=True,
                )
            logger.info(f"[TrOCR] Generated token IDs shape: {generated_ids.shape}")
            text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return text.strip()
        
        # Try multiple orientations to handle rotated labels
        candidates = []
        for angle in [0, 90, -90, 180]:
            img_try = base_image.rotate(angle, expand=True) if angle != 0 else base_image
            try:
                text = _infer(img_try)
                candidates.append((len(text), text, angle))
                logger.info(f"[TrOCR] Angle {angle}: extracted {len(text)} chars")
                # Quick win: if we already have decent length, stop early
                if len(text) >= 10:
                    break
            except Exception as ie:
                logger.warning(f"[TrOCR] Inference failed at angle {angle}: {ie}")
        
        # Choose the best candidate by length
        if candidates:
            best = max(candidates, key=lambda t: t[0])
            logger.info(f"[TrOCR] Best orientation {best[2]} with {best[0]} chars")
            return best[1]
        else:
            raise RuntimeError("TrOCR produced no candidates")
        
    except Exception as e:
        logger.error(f"[TrOCR] Extraction failed: {e}")
        raise RuntimeError(f"TrOCR extraction failed: {e}")


def _fallback_extract(image_path: str) -> str:
    """Best-effort fallback OCR extraction.
    Tries enhanced OCR providers, then Tesseract-based methods, then placeholder.
    """
    logger.info(f"[FALLBACK] Using enhanced fallback extraction for: {image_path}")

    # 1) Try enhanced OCR module if available (Gemini/Google Vision/EasyOCR/Tesseract)
    try:
        from ocr_enhanced import extract_text_from_image as enhanced_extract
        text = enhanced_extract(image_path)
        if text and len(text.strip()) >= 10:
            logger.info("[FALLBACK] Enhanced OCR succeeded")
            return text.strip()
    except Exception as e:
        logger.warning(f"[FALLBACK] Enhanced OCR failed: {e}")

    # 2) Try our OpenCV + Tesseract pipeline
    try:
        from ocr import extract_text_from_image as tesseract_extract
        text = tesseract_extract(image_path)
        if text and len(text.strip()) >= 10:
            logger.info("[FALLBACK] Tesseract OCR (opencv-preprocessed) succeeded")
            return text.strip()
    except Exception as e:
        logger.warning(f"[FALLBACK] Tesseract (opencv) failed: {e}")

    # 3) Try raw pytesseract if binary is present
    try:
        import pytesseract
        from PIL import Image
        # Allow explicit override via env var
        tcmd = os.getenv("TESSERACT_CMD")
        if tcmd:
            try:
                pytesseract.pytesseract.tesseract_cmd = tcmd
            except Exception:
                pass
        # Ensure binary is reachable
        _ = pytesseract.get_tesseract_version()

        img = Image.open(image_path)
        if img.mode != "L":
            img = img.convert("L")
        text = pytesseract.image_to_string(img, lang="eng", config="--psm 6")
        if text and len(text.strip()) >= 10:
            logger.info("[FALLBACK] Raw pytesseract succeeded")
            return text.strip()
    except Exception as e:
        logger.warning(f"[FALLBACK] Raw pytesseract failed: {e}")

    # 4) Last resort placeholder
    logger.warning("[FALLBACK] All fallback methods failed, returning placeholder text")
    return "Nutrition Facts (placeholder) — OCR failed. Try clearer photo; optionally install Tesseract and set TESSERACT_CMD."


def _structure_with_parser(text: str) -> Dict[str, Any]:
    structured = parse_nutrition_data(text or "")
    return structured


# LayoutLM refinement removed for now - can be added later if needed


def extract_structured_from_image(image_path: str) -> Dict[str, Any]:
    """Main entry point used by the API.
    Returns a dict with keys:
      - text: extracted text string
      - structured: dict { nutrition_facts, ingredients, claims, raw_text }
      - method: description string
    Raises RuntimeError on fatal OCR errors.
    """
    # Validate image file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    engine = OCR_ENGINE
    logger.info(f"[OCR] Engine selected: {engine}")

    if engine == "donut":
        # Donut not implemented yet - fallback to TrOCR
        logger.warning("[OCR] Donut mode not yet implemented, falling back to TrOCR")
        engine = "trocr"
    
    if engine == "fallback":
        # Simple fallback extraction
        text = _fallback_extract(image_path)
        method = "Fallback OCR"
        structured = _structure_with_parser(text)
        return {"text": text, "structured": structured, "method": method}
    
    # Default: Local TrOCR + parser with resilience
    tried = []
    text = ""
    method = ""
    # 1) Try configured model
    try:
        text = _local_trocr_extract(HF_TROCR_MODEL, image_path)
        tried.append(HF_TROCR_MODEL)
        method = f"Local TrOCR ({HF_TROCR_MODEL})"
    except Exception as e:
        logger.warning(f"[OCR] Primary TrOCR model failed: {e}")
        text = ""

    # 2) If too short, try base model as a fallback
    if not text or len(text.strip()) < 10:
        alt_model = "microsoft/trocr-base-printed"
        if alt_model not in tried:
            try:
                logger.info(f"[OCR] Trying fallback TrOCR model: {alt_model}")
                alt_text = _local_trocr_extract(alt_model, image_path)
                if len(alt_text.strip()) > len(text.strip()):
                    text = alt_text
                    method = f"Local TrOCR ({alt_model})"
            except Exception as e:
                logger.warning(f"[OCR] Fallback TrOCR model failed: {e}")

    # 3) Final fallback: placeholder to allow downstream parsing (better UX than hard fail)
    if not text or len(text.strip()) < 10:
        logger.warning("[OCR] Insufficient text after TrOCR attempts, using fallback extractor")
        text = _fallback_extract(image_path)
        method = "Fallback OCR"

    structured = _structure_with_parser(text)
    return {"text": text, "structured": structured, "method": method}
