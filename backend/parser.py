import re
import json
from typing import Dict, List, Optional, Any
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# HuggingFace API configuration
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

def parse_nutrition_data(extracted_text: str) -> Dict[str, Any]:
    """
    Parse extracted OCR text into structured nutrition data
    """
    result = {
        "nutrition_facts": {},
        "ingredients": [],
        "claims": [],
        "raw_text": extracted_text
    }
    
    # Parse nutrition facts
    result["nutrition_facts"] = parse_nutrition_facts(extracted_text)
    
    # Parse ingredients
    result["ingredients"] = parse_ingredients(extracted_text)
    
    # Parse health claims
    result["claims"] = parse_health_claims(extracted_text)
    
    return result

def parse_nutrition_facts(text: str) -> Dict[str, Any]:
    """
    Extract nutrition facts using regex patterns
    """
    nutrition_facts = {}
    
    # Serving size patterns
    serving_patterns = [
        r'serving size[:\s]+([^\n]+)',
        r'serving[:\s]+([^\n]+)',
        r'per serving[:\s]+([^\n]+)'
    ]
    
    for pattern in serving_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            nutrition_facts["servingSize"] = match.group(1).strip()
            break
    
    # Servings per container
    servings_pattern = r'servings per container[:\s]+(\d+)'
    match = re.search(servings_pattern, text, re.IGNORECASE)
    if match:
        nutrition_facts["servingsPerContainer"] = int(match.group(1))
    
    # Calories
    calorie_patterns = [
        r'calories[:\s]+(\d+)',
        r'energy[:\s]+(\d+)\s*cal',
        r'(\d+)\s*calories'
    ]
    
    for pattern in calorie_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            nutrition_facts["calories"] = int(match.group(1))
            break
    
    # Macronutrients with daily values
    nutrient_patterns = {
        "fat": [r'total fat[:\s]+(\d+(?:\.\d+)?)g?(?:\s*(\d+)%)?', r'fat[:\s]+(\d+(?:\.\d+)?)g?(?:\s*(\d+)%)?'],
        "saturatedFat": [r'saturated fat[:\s]+(\d+(?:\.\d+)?)g?(?:\s*(\d+)%)?'],
        "transFat": [r'trans fat[:\s]+(\d+(?:\.\d+)?)g?'],
        "cholesterol": [r'cholesterol[:\s]+(\d+(?:\.\d+)?)\s*mg?(?:\s*(\d+)%)?'],
        "sodium": [r'sodium[:\s]+(\d+(?:\.\d+)?)\s*mg?(?:\s*(\d+)%)?'],
        "carbohydrates": [r'total carbohydrate[s]?[:\s]+(\d+(?:\.\d+)?)g?(?:\s*(\d+)%)?', r'carbs[:\s]+(\d+(?:\.\d+)?)g?(?:\s*(\d+)%)?'],
        "fiber": [r'dietary fiber[:\s]+(\d+(?:\.\d+)?)g?(?:\s*(\d+)%)?', r'fiber[:\s]+(\d+(?:\.\d+)?)g?(?:\s*(\d+)%)?'],
        "sugar": [r'total sugars[:\s]+(\d+(?:\.\d+)?)g?', r'sugars[:\s]+(\d+(?:\.\d+)?)g?', r'sugar[:\s]+(\d+(?:\.\d+)?)g?'],
        "addedSugar": [r'added sugars[:\s]+(\d+(?:\.\d+)?)g?(?:\s*(\d+)%)?'],
        "protein": [r'protein[:\s]+(\d+(?:\.\d+)?)g?(?:\s*(\d+)%)?']
    }
    
    for nutrient, patterns in nutrient_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                nutrition_facts[nutrient] = float(match.group(1))
                if len(match.groups()) > 1 and match.group(2):
                    nutrition_facts[f"{nutrient}DV"] = int(match.group(2))
                break
    
    # Calculate daily value percentages if missing
    nutrition_facts = calculate_daily_values(nutrition_facts)
    
    return nutrition_facts

def calculate_daily_values(nutrition_facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate daily value percentages based on FDA guidelines
    """
    daily_values = {
        "calories": 2000,
        "fat": 78,  # grams
        "saturatedFat": 20,  # grams
        "cholesterol": 300,  # mg
        "sodium": 2300,  # mg
        "carbohydrates": 275,  # grams
        "fiber": 28,  # grams
        "protein": 50,  # grams
    }
    
    for nutrient, dv in daily_values.items():
        if nutrient in nutrition_facts and f"{nutrient}DV" not in nutrition_facts:
            value = nutrition_facts[nutrient]
            if nutrient in ["cholesterol", "sodium"]:
                # These are in mg
                percentage = (value / dv) * 100
            else:
                # These are in grams or calories
                percentage = (value / dv) * 100
            nutrition_facts[f"{nutrient}DV"] = round(percentage, 1)
    
    return nutrition_facts

def parse_ingredients(text: str) -> List[str]:
    """
    Extract ingredients list from text
    """
    ingredients = []
    
    # Look for ingredients section
    ingredient_patterns = [
        r'ingredients[:\s]+([^.]+?)(?:\.|allergen|contains|may contain|\n\n)',
        r'ingredients[:\s]+(.+?)(?=\n[A-Z]|\nNutrition|\nDirect|\nMade)',
        r'ingredients[:\s]+(.+?)$'
    ]
    
    for pattern in ingredient_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            ingredient_text = match.group(1).strip()
            
            # Split by commas and clean up
            ingredients = [
                ingredient.strip().rstrip(',').strip()
                for ingredient in ingredient_text.split(',')
                if ingredient.strip()
            ]
            
            # Remove empty strings and clean up
            ingredients = [ing for ing in ingredients if ing and len(ing) > 1]
            break
    
    return ingredients

def parse_health_claims(text: str) -> List[str]:
    """
    Extract health claims and marketing statements
    """
    claims = []
    
    # Common health claim patterns
    claim_patterns = [
        r'(no trans fat)',
        r'(zero trans fat)',
        r'(low fat)',
        r'(reduced fat)',
        r'(fat free)',
        r'(sugar free)',
        r'(no sugar added)',
        r'(reduced sugar)',
        r'(low sodium)',
        r'(no sodium)',
        r'(reduced sodium)',
        r'(high fiber)',
        r'(good source of fiber)',
        r'(excellent source of)',
        r'(good source of)',
        r'(contains \d+% daily value)',
        r'(fortified with)',
        r'(enriched with)',
        r'(natural)',
        r'(organic)',
        r'(non-gmo)',
        r'(gluten free)',
        r'(whole grain)',
        r'(heart healthy)',
        r'(low cholesterol)',
        r'(cholesterol free)',
        r'(vitamin enriched)',
        r'(calcium enriched)',
        r'(iron enriched)'
    ]
    
    for pattern in claim_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        claims.extend(matches)
    
    # Remove duplicates and normalize
    claims = list(set([claim.lower().strip() for claim in claims]))
    
    return claims

def classify_text_with_huggingface(text: str, task: str = "classification") -> Dict[str, Any]:
    """
    Use HuggingFace API to classify text (fallback if API key not available)
    """
    if not HF_API_KEY:
        return {"classification": "unknown", "confidence": 0.0}
    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    try:
        # For text classification, we'll use a simple approach
        # In production, you'd use specific models for ingredient classification
        response = requests.post(
            "https://api-inference.huggingface.co/models/distilbert-base-uncased",
            headers=headers,
            json={"inputs": text[:512]},  # Limit input length
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"classification": "unknown", "confidence": 0.0}
            
    except Exception as e:
        print(f"HuggingFace API error: {e}")
        return {"classification": "unknown", "confidence": 0.0}

def enhance_parsing_with_ai(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance parsing results using AI classification
    """
    # Classify ingredients if available
    if structured_data.get("ingredients"):
        enhanced_ingredients = []
        for ingredient in structured_data["ingredients"]:
            classification = classify_text_with_huggingface(ingredient, "ingredient_type")
            enhanced_ingredients.append({
                "name": ingredient,
                "classification": classification.get("classification", "unknown"),
                "confidence": classification.get("confidence", 0.0)
            })
        structured_data["enhanced_ingredients"] = enhanced_ingredients
    
    return structured_data

def validate_nutrition_data(nutrition_facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean nutrition data for consistency
    """
    # Check for reasonable ranges
    validations = {
        "calories": (0, 9999),
        "fat": (0, 999),
        "saturatedFat": (0, 999),
        "cholesterol": (0, 9999),
        "sodium": (0, 99999),
        "carbohydrates": (0, 999),
        "fiber": (0, 999),
        "sugar": (0, 999),
        "protein": (0, 999)
    }
    
    for nutrient, (min_val, max_val) in validations.items():
        if nutrient in nutrition_facts:
            value = nutrition_facts[nutrient]
            if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                print(f"Warning: {nutrient} value {value} seems unreasonable")
                # You might want to flag this for manual review
    
    return nutrition_facts
