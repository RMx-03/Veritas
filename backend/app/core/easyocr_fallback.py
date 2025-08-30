import io
from typing import Dict, List, Union
import numpy as np
import cv2
import os
import logging

try:
    import easyocr  # type: ignore
except Exception:
    easyocr = None

_reader_cache: dict = {}

LOGGER = logging.getLogger("uvicorn.error")
EASYOCR_MODEL_DIR = os.path.expanduser(os.getenv("EASYOCR_MODEL_DIR", os.path.join("~", ".EasyOCR")))
EASYOCR_DOWNLOAD_ON_DEMAND = os.getenv("EASYOCR_DOWNLOAD_ON_DEMAND", "true").lower() == "true"


def _load_image(path_or_bytes: Union[str, bytes, bytearray]) -> np.ndarray:
    if isinstance(path_or_bytes, (bytes, bytearray)):
        arr = np.frombuffer(path_or_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(str(path_or_bytes))
    if img is None:
        raise ValueError("Unable to read image")
    return img


def _preprocess(img: np.ndarray) -> np.ndarray:
    # Lightweight preprocessing to improve OCR readability
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Slight upscale for small images
    h, w = gray.shape
    if max(h, w) < 1200:
        scale = max(1.0, 1200.0 / max(h, w))
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    # Adaptive histogram equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    # Denoise
    gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def easyocr_extract_text(image_path_or_bytes: Union[str, bytes, bytearray], langs: List[str] = ["en"]) -> Dict:
    if easyocr is None:
        return {"ok": False, "error": "easyocr_not_available"}
    try:
        key = ",".join(langs)
        reader = _reader_cache.get(key)
        if reader is None:
            # If downloads are disabled and no local models are present, short-circuit
            if not EASYOCR_DOWNLOAD_ON_DEMAND:
                if not (os.path.isdir(EASYOCR_MODEL_DIR) and os.listdir(EASYOCR_MODEL_DIR)):
                    try:
                        LOGGER.warning(f"[EASYOCR] Skipping EasyOCR: models not found at {EASYOCR_MODEL_DIR} and downloads disabled")
                    except Exception:
                        pass
                    return {"ok": False, "error": "easyocr_models_missing", "details": f"Models not present at {EASYOCR_MODEL_DIR} and EASYOCR_DOWNLOAD_ON_DEMAND=false"}

            # Initialize EasyOCR reader with configured storage dir and download policy
            try:
                try:
                    LOGGER.info(f"[EASYOCR] Initializing reader | model_dir={EASYOCR_MODEL_DIR} | download_on_demand={EASYOCR_DOWNLOAD_ON_DEMAND} | langs={key}")
                except Exception:
                    pass
                reader = easyocr.Reader(
                    langs,
                    gpu=False,
                    model_storage_directory=EASYOCR_MODEL_DIR,
                    download_enabled=EASYOCR_DOWNLOAD_ON_DEMAND,
                )
            except TypeError:
                # Older EasyOCR versions may not support these kwargs; fall back safely
                try:
                    LOGGER.info("[EASYOCR] Reader args not supported in this EasyOCR version; falling back to defaults")
                except Exception:
                    pass
                reader = easyocr.Reader(langs, gpu=False)
            _reader_cache[key] = reader

        # Load and preprocess only after reader is ready
        img = _load_image(image_path_or_bytes)
        pre = _preprocess(img)
        results = reader.readtext(pre)
        lines: List[str] = []
        for _, text, conf in results:
            if isinstance(text, str) and text.strip():
                lines.append(text.strip())
        text = "\n".join(lines)
        return {
            "ok": True,
            "method": "EasyOCR",
            "text": text,
            "raw": results,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
