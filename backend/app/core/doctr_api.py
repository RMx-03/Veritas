import os
import time
import requests
from typing import Any, Dict, Optional, Union

HF_INFERENCE_BASE = "https://api-inference.huggingface.co/models"


def _read_image_bytes(image_path_or_bytes: Union[str, bytes, bytearray]) -> bytes:
    if isinstance(image_path_or_bytes, (bytes, bytearray)):
        return bytes(image_path_or_bytes)
    with open(str(image_path_or_bytes), "rb") as f:
        return f.read()


def doctr_api_ocr(
    image_path_or_bytes: Union[str, bytes, bytearray],
    model: Optional[str] = None,
    timeout: int = 30,
    max_retries: int = 1,
) -> Dict[str, Any]:
    """
    Call Hugging Face Inference API for OCR/image-to-text.
    Default model can be set via DOCTR_API_MODEL, falls back to microsoft/trocr-small-printed.

    Returns {ok, method, text, raw}
    """
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return {"ok": False, "error": "missing_huggingface_api_key"}

    model_name = model or os.getenv("DOCTR_API_MODEL", "microsoft/trocr-small-printed")
    url = f"{HF_INFERENCE_BASE}/{model_name}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        # Sending raw bytes
        "Content-Type": "application/octet-stream",
    }

    data = _read_image_bytes(image_path_or_bytes)

    attempt = 0
    while True:
        attempt += 1
        try:
            resp = requests.post(url, headers=headers, data=data, timeout=timeout, params={"wait_for_model": "true"})
            if resp.status_code == 200:
                try:
                    out = resp.json()
                except Exception:
                    out = None
                # Parse common HF outputs
                text = None
                if isinstance(out, list) and out:
                    first = out[0]
                    if isinstance(first, dict):
                        text = (
                            first.get("generated_text")
                            or first.get("text")
                            or first.get("answer")
                        )
                elif isinstance(out, dict):
                    text = out.get("generated_text") or out.get("text")
                if text is None:
                    # As a fallback, take response text if it's plain string
                    try:
                        text = resp.text if isinstance(resp.text, str) else None
                    except Exception:
                        text = None
                return {"ok": True, "method": "DocTR API", "text": text or "", "raw": out}

            # Handle transient errors/rate limits/model loading
            if resp.status_code in (429, 503):
                if attempt <= max_retries:
                    retry_after = resp.headers.get("retry-after")
                    sleep_s = float(retry_after) if retry_after else 2.0
                    time.sleep(sleep_s)
                    continue
            # Other error
            return {"ok": False, "error": f"http_{resp.status_code}", "details": resp.text}
        except requests.RequestException as e:
            if attempt <= max_retries:
                time.sleep(1.5)
                continue
            return {"ok": False, "error": str(e)}
