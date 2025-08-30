import os
import time
import requests
from typing import Any, Dict, Optional, Union

HF_INFERENCE_BASE = "https://api-inference.huggingface.co/models"
HF_INFERENCE_PIPELINE_BASE = "https://api-inference.huggingface.co/pipeline"


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
        # Explicit diagnostic
        print("[DOCTR] Missing HUGGINGFACE_API_KEY; skipping DocTR API call")
        return {"ok": False, "error": "missing_huggingface_api_key"}

    model_name = model or os.getenv("DOCTR_API_MODEL", "microsoft/trocr-small-printed")
    task = os.getenv("DOCTR_API_TASK", "image-to-text")
    url_models = f"{HF_INFERENCE_BASE}/{model_name}"
    url_pipeline = f"{HF_INFERENCE_PIPELINE_BASE}/{task}/{model_name}"
    try:
        masked = ("hf_" + "*" * max(0, len(api_key) - 6) + api_key[-4:]) if api_key.startswith("hf_") else "present"
        print(f"[DOCTR] Using model={model_name} | task={task} | url={url_models} | key={masked}")
    except Exception:
        pass
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        # Sending raw bytes
        "Content-Type": "application/octet-stream",
        "X-Wait-For-Model": "true",
    }

    data = _read_image_bytes(image_path_or_bytes)

    # Try the unified models route first, then fall back to the pipeline route if we see a 404
    for which, url in (("models", url_models), ("pipeline", url_pipeline)):
        attempt = 0
        while True:
            attempt += 1
            try:
                print(f"[DOCTR] POST ({which}) attempt={attempt} timeout={timeout}s wait_for_model=true -> {url}")
                params = {"wait_for_model": "true"} if which == "models" else None
                resp = requests.post(url, headers=headers, data=data, timeout=timeout, params=params)
                print(f"[DOCTR] ({which}) response status={resp.status_code} len={len(resp.content)}")
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
                    if (text or "").strip():
                        print(f"[DOCTR] Parsed text length={len(text)}")
                    else:
                        print("[DOCTR] No text parsed from successful response; returning empty string")
                    return {"ok": True, "method": "DocTR API", "text": text or "", "raw": out}

                # Handle transient errors/rate limits/model loading
                if resp.status_code in (429, 503):
                    if attempt <= max_retries:
                        retry_after = resp.headers.get("retry-after")
                        sleep_s = float(retry_after) if retry_after else 2.0
                        print(f"[DOCTR] Transient status={resp.status_code}; retrying in {sleep_s}s (attempt {attempt}/{max_retries})")
                        time.sleep(sleep_s)
                        continue
                if resp.status_code == 404 and which == "models":
                    # Fallback to pipeline route
                    print("[DOCTR] 404 from models route; trying pipeline route next")
                    break
                # Other error
                snippet = resp.text[:300] if isinstance(resp.text, str) else str(resp.content[:300])
                print(f"[DOCTR] Error status={resp.status_code} body~{len(resp.text)}: {snippet}")
                return {"ok": False, "error": f"http_{resp.status_code}", "details": resp.text}
            except requests.RequestException as e:
                print(f"[DOCTR] Request exception: {e.__class__.__name__}: {e}")
                if attempt <= max_retries:
                    time.sleep(1.5)
                    continue
                return {"ok": False, "error": str(e)}
    # If we exit the loop without returning, fall back with a friendly error
    return {"ok": False, "error": "no_route_succeeded", "details": "Both models and pipeline routes failed"}
