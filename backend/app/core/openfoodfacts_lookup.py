import os
import requests
from typing import Any, Dict, Optional, Union, List

DEFAULT_OFF_PRODUCT_URL = "https://world.openfoodfacts.org/api/v0/product/"
DEFAULT_OFF_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"


def _extract_structured_from_off_product(product: Dict[str, Any]) -> Dict[str, Any]:
    nutriments = product.get("nutriments", {}) or {}

    def _get_num(key: str) -> Optional[float]:
        try:
            val = nutriments.get(key)
            if val is None:
                return None
            return float(val)
        except Exception:
            return None

    nutrition_facts = {
        "serving_size": product.get("serving_size"),
        "energy_kcal_100g": _get_num("energy-kcal_100g") or _get_num("energy-kcal_value") or _get_num("energy_100g"),
        "fat_100g": _get_num("fat_100g"),
        "saturated_fat_100g": _get_num("saturated-fat_100g"),
        "carbohydrates_100g": _get_num("carbohydrates_100g"),
        "sugars_100g": _get_num("sugars_100g"),
        "protein_100g": _get_num("proteins_100g") or _get_num("protein_100g"),
        "salt_100g": _get_num("salt_100g"),
        "sodium_100g": _get_num("sodium_100g"),
        "fiber_100g": _get_num("fiber_100g"),
    }

    # Ingredients
    ingredients_text = product.get("ingredients_text") or product.get("ingredients_text_en") or ""
    ingredients_list: List[str] = []
    if isinstance(ingredients_text, str) and ingredients_text.strip():
        ingredients_list = [s.strip() for s in ingredients_text.replace(";", ",").split(",") if s.strip()]

    # Claims / labels
    labels = product.get("labels") or ""
    labels_tags = product.get("labels_tags") or []
    additives = product.get("additives_original_tags") or product.get("additives_tags") or []
    allergens = product.get("allergens") or product.get("allergens_tags") or []
    nutri_grade = product.get("nutriscore_grade")
    nova_group = product.get("nova_group")

    claims: List[str] = []
    if isinstance(labels, str) and labels:
        claims.append(f"labels: {labels}")
    if labels_tags:
        claims.append("labels_tags: " + ", ".join(labels_tags))
    if additives:
        claims.append("additives: " + ", ".join(additives if isinstance(additives, list) else [str(additives)]))
    if allergens:
        claims.append("allergens: " + (", ".join(allergens) if isinstance(allergens, list) else str(allergens)))
    if nutri_grade:
        claims.append(f"nutriscore: {nutri_grade}")
    if nova_group:
        claims.append(f"nova_group: {nova_group}")

    structured = {
        "product_name": product.get("product_name") or product.get("product_name_en"),
        "brand": (product.get("brands") or "").split(",")[0].strip() if product.get("brands") else None,
        "ingredients": ingredients_list,
        "nutrition_facts": {k: v for k, v in nutrition_facts.items() if v is not None or k == "serving_size"},
        "claim_verification": claims,
        "source": {
            "name": "OpenFoodFacts",
            "code": product.get("code"),
            "url": product.get("url") or product.get("image_url") or None,
        },
    }

    # Build a synthetic text block to keep the API contract consistent
    text_lines: List[str] = []
    if structured.get("product_name"):
        text_lines.append(str(structured["product_name"]))
    if ingredients_list:
        text_lines.append("Ingredients: " + ", ".join(ingredients_list))
    nf = structured.get("nutrition_facts") or {}
    if nf:
        nutrition_line = []
        for key in [
            "energy_kcal_100g",
            "fat_100g",
            "saturated_fat_100g",
            "carbohydrates_100g",
            "sugars_100g",
            "protein_100g",
            "fiber_100g",
            "salt_100g",
            "sodium_100g",
        ]:
            if key in nf and nf[key] is not None:
                nutrition_line.append(f"{key.replace('_', ' ').replace('100g','/100g')}: {nf[key]}")
        if nutrition_line:
            text_lines.append("Nutrition: " + ", ".join(nutrition_line))
    if claims:
        text_lines.append("Claims: " + ", ".join(claims))

    synthetic_text = "\n".join(text_lines)

    return {
        "ok": True,
        "method": "OpenFoodFacts",
        "text": synthetic_text,
        "structured": structured,
        "raw": product,
    }


def query_openfoodfacts(
    barcode: Optional[str] = None,
    product_name: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: int = 12,
) -> Dict[str, Any]:
    """
    Attempt to resolve a product by barcode (preferred) or product_name (fallback) via OpenFoodFacts.
    Returns a dict with keys: {ok, method, text, structured, raw} or {ok: False, error}
    """
    base_product_url = (base_url or os.getenv("OPENFOODFACTS_BASE_URL") or DEFAULT_OFF_PRODUCT_URL).rstrip("/") + "/"

    try:
        # Priority 1: Barcode lookup
        if barcode:
            url = f"{base_product_url}{barcode}.json"
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == 1 and data.get("product"):
                    return _extract_structured_from_off_product(data["product"])  # type: ignore
            # If barcode not found, do not treat as fatal; try name next.

        # Priority 2: Name search
        if product_name:
            params = {
                "search_terms": product_name,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 1,
            }
            resp = requests.get(DEFAULT_OFF_SEARCH_URL, params=params, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                prods = data.get("products") or []
                if prods:
                    return _extract_structured_from_off_product(prods[0])

        return {"ok": False, "error": "not_found"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
