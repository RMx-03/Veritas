import os
import time
import base64
import requests
from typing import Any, Dict, Optional, Union


def _read_image_bytes(image_path_or_bytes: Union[str, bytes, bytearray]) -> bytes:
    if isinstance(image_path_or_bytes, (bytes, bytearray)):
        return bytes(image_path_or_bytes)
    with open(str(image_path_or_bytes), "rb") as f:
        return f.read()


def _guess_mime(data: bytes) -> str:
    # Very simple sniffing for PNG vs JPEG; default to jpeg
    if len(data) >= 8 and data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if len(data) >= 3 and data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    return "image/jpeg"


def mistral_api_ocr(
    image_path_or_bytes: Union[str, bytes, bytearray],
    model: Optional[str] = None,
    timeout: int = 45,
    max_retries: int = 1,
) -> Dict[str, Any]:
    """
    Call Mistral AI La Plateforme (chat/completions with vision) to perform OCR-like text extraction.

    Returns {ok, method, text, raw}
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("[MISTRAL] Missing MISTRAL_API_KEY; skipping Mistral OCR call")
        return {"ok": False, "error": "missing_mistral_api_key"}

    model_name = model or os.getenv("MISTRAL_OCR_MODEL", "pixtral-12b")
    base_url = os.getenv("MISTRAL_API_BASE", "https://api.mistral.ai/v1").rstrip("/")
    url = f"{base_url}/chat/completions"

    data_bytes = _read_image_bytes(image_path_or_bytes)
    mime = _guess_mime(data_bytes)
    b64 = base64.b64encode(data_bytes).decode("utf-8")
    data_url = f"data:{mime};base64,{b64}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Prompt the model to return only the extracted text
    system_msg = "You are an OCR engine. Extract and return only the exact text content found in the image. Preserve line breaks. No commentary."
    user_text = "Extract the raw text from this image and output only the text."

    # Prepare multiple payload variants to handle possible schema differences
    payload_variants = []
    # Variant A: OpenAI-like, image_url as object with url
    payload_variants.append({
        "variant": "image_url_object",
        "body": {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_msg},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            "temperature": 0.0,
            "max_tokens": 2048,
        }
    })
    # Variant B: image_url as a direct string
    payload_variants.append({
        "variant": "image_url_string",
        "body": {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_msg},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": data_url},
                    ],
                },
            ],
            "temperature": 0.0,
            "max_tokens": 2048,
        }
    })
    # Variant C: Mistral-style input_text/input_image
    payload_variants.append({
        "variant": "input_text_image",
        "body": {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_msg},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": user_text},
                        {"type": "input_image", "image_url": data_url},
                    ],
                },
            ],
            "temperature": 0.0,
            "max_tokens": 2048,
        }
    })

    for variant in payload_variants:
        attempt = 0
        while True:
            attempt += 1
            try:
                print(f"[MISTRAL] POST variant={variant['variant']} attempt={attempt} model={model_name} url={url}")
                resp = requests.post(url, headers=headers, json=variant["body"], timeout=timeout)
                print(f"[MISTRAL] Response status={resp.status_code} len={len(resp.content)}")
                if resp.status_code == 200:
                    try:
                        out = resp.json()
                    except Exception:
                        out = None
                    text = None
                    if isinstance(out, dict):
                        choices = out.get("choices") or []
                        if choices:
                            msg = choices[0].get("message") or {}
                            text = msg.get("content")
                    if (text or "").strip():
                        print(f"[MISTRAL] Parsed text length={len(text)} via {variant['variant']}")
                    else:
                        print(f"[MISTRAL] No text parsed from successful response via {variant['variant']}; returning empty string")
                    return {"ok": True, "method": "Mistral OCR", "text": text or "", "raw": out}

                if resp.status_code in (429, 503):
                    if attempt <= max_retries:
                        retry_after = resp.headers.get("retry-after")
                        sleep_s = float(retry_after) if retry_after else 2.0
                        print(f"[MISTRAL] Transient status={resp.status_code}; retrying in {sleep_s}s (attempt {attempt}/{max_retries})")
                        time.sleep(sleep_s)
                        continue
                # For 400/415/422, try next payload variant
                if resp.status_code in (400, 415, 422):
                    snippet = resp.text[:200]
                    print(f"[MISTRAL] Likely schema mismatch for {variant['variant']}: {resp.status_code} {snippet}; trying next variant")
                    break
                snippet = resp.text[:300] if isinstance(resp.text, str) else str(resp.content[:300])
                print(f"[MISTRAL] Error status={resp.status_code} body~{len(resp.text)}: {snippet}")
                return {"ok": False, "error": f"http_{resp.status_code}", "details": resp.text}
            except requests.RequestException as e:
                print(f"[MISTRAL] Request exception: {e.__class__.__name__}: {e}")
                if attempt <= max_retries:
                    time.sleep(1.5)
                    continue
                return {"ok": False, "error": str(e)}

    # If all variants failed due to schema mismatch
    return {"ok": False, "error": "no_payload_variant_succeeded", "details": "Tried multiple payload variants; all failed"}
