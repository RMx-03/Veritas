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
from PIL import Image

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

def _local_trocr_extract(model_id: str, image_path: str) -> str:
    """Extract text from image using local TrOCR model.
    Returns plain text or raises on failure.
    """
    model_id = _sanitize_model_id(model_id)
    logger.info(f"[TrOCR] Processing image with model: {model_id}")
    
    try:
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # Get processor and model
        processor, model = _get_trocr_components(model_id)
        
        # Process image and generate text
        pixel_values = processor(image, return_tensors="pt").pixel_values
        logger.info(f"[TrOCR] Input image tensor shape: {pixel_values.shape}")
        
        generated_ids = model.generate(
            pixel_values,
            max_new_tokens=256,  # Allow much longer text generation
            do_sample=False,     # Use greedy decoding for consistency
            num_beams=4,         # Beam search for better quality
            early_stopping=True
        )
        logger.info(f"[TrOCR] Generated token IDs shape: {generated_ids.shape}")
        logger.info(f"[TrOCR] Generated token IDs: {generated_ids[0].tolist()[:20]}...")  # First 20 tokens
        
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        logger.info(f"[TrOCR] Extracted {len(generated_text)} characters")
        return generated_text.strip()
        
    except Exception as e:
        logger.error(f"[TrOCR] Extraction failed: {e}")
        raise RuntimeError(f"TrOCR extraction failed: {e}")


def _fallback_extract(image_path: str) -> str:
    """Simple fallback OCR extraction.
    Returns placeholder text for now.
    """
    logger.info(f"[FALLBACK] Using fallback extraction for: {image_path}")
    return "Nutrition Facts [Fallback OCR - please install transformers for better results]"


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
    
    # Default: Local TrOCR + parser
    text = _local_trocr_extract(HF_TROCR_MODEL, image_path)
    method = f"Local TrOCR ({HF_TROCR_MODEL})"
    structured = _structure_with_parser(text)
    return {"text": text, "structured": structured, "method": method}
