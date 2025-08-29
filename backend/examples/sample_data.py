"""Sample data & mock analysis payloads (extracted from previous root sample_data.py).

Used for demo / testing outside core production path.
"""

SAMPLE_NUTRITION_LABEL_TEXT = """Nutrition Facts DEMO"""

def get_sample_data(product_type="healthy"):
    return {"analysisId": f"demo-{product_type}", "extractedText": SAMPLE_NUTRITION_LABEL_TEXT}
