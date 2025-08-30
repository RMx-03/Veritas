import pytest

# ---- OpenFoodFacts lookup tests ----

def test_openfoodfacts_barcode_success(monkeypatch):
    from app.core import openfoodfacts_lookup as off

    class R:
        status_code = 200
        def json(self):
            return {
                "status": 1,
                "product": {
                    "code": "1234567890",
                    "product_name": "Test Bar",
                    "brands": "BrandX",
                    "nutriments": {
                        "energy-kcal_100g": 430,
                        "fat_100g": 15,
                        "saturated-fat_100g": 4,
                        "carbohydrates_100g": 60,
                        "sugars_100g": 40,
                        "proteins_100g": 6,
                        "salt_100g": 0.8,
                    },
                    "ingredients_text": "sugar, cocoa, milk",
                    "labels": "gluten-free",
                }
            }
    monkeypatch.setattr(off.requests, "get", lambda *a, **k: R())

    out = off.query_openfoodfacts(barcode="1234567890")
    assert out.get("ok") is True
    assert out.get("method") == "OpenFoodFacts"
    assert "Test Bar" in out.get("text", "")


# ---- DocTR API tests ----

def test_doctr_api_missing_key(monkeypatch):
    from app.core.doctr_api import doctr_api_ocr
    # Ensure API key is not set
    monkeypatch.delenv("HUGGINGFACE_API_KEY", raising=False)
    out = doctr_api_ocr(b"fake-bytes")
    assert out.get("ok") is False
    assert out.get("error") == "missing_huggingface_api_key"


def test_doctr_api_success_mock(monkeypatch):
    from app.core import doctr_api as dapi

    # Mock env
    monkeypatch.setenv("HUGGINGFACE_API_KEY", "test")

    class R:
        status_code = 200
        def json(self):
            return [{"generated_text": "Calories 150\nIngredients: water, sugar"}]
        @property
        def text(self):
            return ""

    monkeypatch.setattr(dapi.requests, "post", lambda *a, **k: R())

    out = dapi.doctr_api_ocr(b"img")
    assert out.get("ok") is True
    assert out.get("method") == "DocTR API"
    assert "Calories" in out.get("text", "")


# ---- Unified pipeline tests ----

def test_unified_prefers_openfoodfacts(monkeypatch):
    import app.core.ocr_unified as uni

    # OFF returns a hit
    monkeypatch.setattr(uni, "query_openfoodfacts", lambda **k: {
        "ok": True,
        "text": "Ingredients: water\nNutrition: calories 100",
        "structured": {"product_name": "OFF Product"},
    })
    # Ensure downstream tier would fail if called
    monkeypatch.setattr(uni, "doctr_api_ocr", lambda *a, **k: {"ok": False, "error": "should_not_call"})

    out = uni.extract_structured_from_image(b"img", barcode="123")
    assert out.get("method") == "OpenFoodFacts"
    assert out.get("text")


def test_unified_uses_doctr_when_off_fails(monkeypatch):
    import app.core.ocr_unified as uni

    monkeypatch.setattr(uni, "query_openfoodfacts", lambda **k: {"ok": False, "error": "not_found"})
    monkeypatch.setattr(uni, "doctr_api_ocr", lambda *a, **k: {"ok": True, "text": "Calories 90\nIngredients: water"})

    out = uni.extract_structured_from_image(b"img")
    assert out.get("method") == "DocTR API"
    assert "Calories" in out.get("text", "")
