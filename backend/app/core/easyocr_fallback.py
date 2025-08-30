import io
from typing import Dict, List, Union
import numpy as np
import cv2

try:
    import easyocr  # type: ignore
except Exception:
    easyocr = None

_reader_cache: dict = {}


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
        img = _load_image(image_path_or_bytes)
        pre = _preprocess(img)
        key = ",".join(langs)
        reader = _reader_cache.get(key)
        if reader is None:
            reader = easyocr.Reader(langs, gpu=False)
            _reader_cache[key] = reader
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
