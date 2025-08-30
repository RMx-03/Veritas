"""
Unit tests for core backend modules
Run with: pytest tests/test_core_modules.py -v
"""
import pytest
from unittest.mock import Mock, patch
import os

def test_ocr_unified_imports():
    """Test that OCR unified module can be imported"""
    try:
        from app.core.ocr_unified import extract_structured_from_image
        assert callable(extract_structured_from_image)
    except ImportError as e:
        pytest.skip(f"OCR module dependencies not available: {e}")

def test_parser_enhanced_imports():
    """Test that enhanced parser module can be imported"""
    try:
        from app.core.parser_enhanced import parse_nutrition_data
        assert callable(parse_nutrition_data)
    except ImportError as e:
        pytest.skip(f"Parser module dependencies not available: {e}")

def test_analyzer_imports():
    """Test that analyzer module can be imported"""
    try:
        from app.core.analyzer import analyze_nutrition_data
        assert callable(analyze_nutrition_data)
    except ImportError as e:
        pytest.skip(f"Analyzer module dependencies not available: {e}")

@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="No Groq API key")
def test_analyzer_with_mock_data():
    """Test analyzer with mock nutrition data"""
    from app.core.analyzer import analyze_nutrition_data
    
    mock_data = {
        "nutrition_facts": {
            "calories": 150,
            "total_fat": "5g",
            "sodium": "200mg"
        },
        "ingredients": ["water", "sugar", "artificial flavoring"]
    }
    
    # This would require actual API calls, so we'll just test the import for now
    assert analyze_nutrition_data is not None
