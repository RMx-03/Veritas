import pytest

from app.core.parser_enhanced import parse_nutrition_data


def test_calories_not_misparsed_from_serving_size():
    text = (
        "Nutrition Facts\n"
        "Serving Size 1 cup (240 ml)\n"
        "Calories 120\n"
        "Total Fat 3g\n"
    )
    result = parse_nutrition_data(text)
    nf = result.get("nutrition_facts", {})
    assert nf.get("calories") == 120


def test_calories_from_fat_tracked_separately():
    text = (
        "Nutrition Facts\n"
        "Calories 120\n"
        "Calories from fat 30\n"
    )
    result = parse_nutrition_data(text)
    nf = result.get("nutrition_facts", {})
    assert nf.get("calories") == 120
    assert nf.get("calories_from_fat") == 30


def test_calcium_not_misparsed_as_calories_when_no_nutrition_keywords():
    # No keywords like calories/protein/fat present; ensure 'calcium' doesn't trigger calories fallback
    text = "Ingredients: Water\nCalcium 20 mg\nBest Before: 2026"
    result = parse_nutrition_data(text)
    nf = result.get("nutrition_facts", {})
    assert "calories" not in nf


def test_energy_kcal_is_parsed():
    text = "Per serving: Energy 350 kcal, Protein 5 g, Sodium 200 mg"
    result = parse_nutrition_data(text)
    nf = result.get("nutrition_facts", {})
    assert nf.get("calories") == 350


def test_number_plus_cal_at_line_end_is_parsed():
    text = "Per bar: 120 cal"
    result = parse_nutrition_data(text)
    nf = result.get("nutrition_facts", {})
    assert nf.get("calories") == 120
