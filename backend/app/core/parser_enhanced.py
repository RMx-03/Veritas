"""
Enhanced nutrition data parser with improved extraction and categorization.
Supports comprehensive nutrition facts parsing with better regex patterns,
fuzzy matching, and structured data validation.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import asdict
import json

try:
    from fuzzywuzzy import fuzz, process
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False

logger = logging.getLogger(__name__)

class NutritionParser:
    """Enhanced nutrition facts parser with comprehensive patterns and validation"""
    
    def __init__(self):
        self.nutrition_patterns = self._build_nutrition_patterns()
        self.serving_patterns = self._build_serving_patterns()
        self.ingredient_patterns = self._build_ingredient_patterns()
        self.allergen_patterns = self._build_allergen_patterns()
        self.claim_patterns = self._build_claim_patterns()
        
        # Standard nutrition keywords for fuzzy matching
        self.standard_nutrients = {
            'calories': ['calories', 'cal', 'kcal', 'energy'],
            'total_fat': ['total fat', 'fat', 'total fats'],
            'saturated_fat': ['saturated fat', 'saturated', 'sat fat', 'sat. fat'],
            'trans_fat': ['trans fat', 'trans', 'trans fatty acids', 'trans fats'],
            'cholesterol': ['cholesterol', 'chol', 'cholest'],
            'sodium': ['sodium', 'salt'],
            'total_carbs': ['total carbohydrate', 'carbohydrate', 'carbs', 'total carbs', 'carbohydrates'],
            'dietary_fiber': ['dietary fiber', 'fiber', 'fibre', 'total fiber'],
            'total_sugars': ['total sugars', 'sugars', 'sugar', 'total sugar'],
            'added_sugars': ['added sugars', 'added sugar', 'includes added sugars'],
            'protein': ['protein', 'proteins'],
            'vitamin_a': ['vitamin a', 'vit a', 'vit. a', 'retinol'],
            'vitamin_c': ['vitamin c', 'vit c', 'vit. c', 'ascorbic acid'],
            'vitamin_d': ['vitamin d', 'vit d', 'vit. d'],
            'calcium': ['calcium', 'ca'],
            'iron': ['iron', 'fe'],
            'potassium': ['potassium', 'k'],
            'magnesium': ['magnesium', 'mg'],
            'phosphorus': ['phosphorus', 'p'],
            'zinc': ['zinc', 'zn'],
            'folate': ['folate', 'folic acid', 'folacin', 'vitamin b9'],
            'niacin': ['niacin', 'vitamin b3', 'nicotinic acid'],
            'vitamin_b6': ['vitamin b6', 'pyridoxine', 'vit b6'],
            'vitamin_b12': ['vitamin b12', 'cobalamin', 'vit b12'],
            'thiamine': ['thiamine', 'vitamin b1', 'vit b1'],
            'riboflavin': ['riboflavin', 'vitamin b2', 'vit b2']
        }
    
    def _build_nutrition_patterns(self) -> Dict[str, List[str]]:
        """Build comprehensive regex patterns for nutrition facts"""
        return {
            'calories': [
                r'calories?\s*(?:per serving|from fat)?\s*[:.]?\s*(\d+(?:\.\d+)?)',
                r'energy\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:kcal|cal)\b',
                r'(\d+(?:\.\d+)?)\s*(?:kcal|cal|calories?)\b'
            ],
            'serving_info': [
                r'serving size\s*[:.]?\s*([^\n\r]+?)(?:\n|\r|$)',
                r'servings? per (?:container|package|pkg)\s*[:.]?\s*(\d+(?:\.\d+)?)',
                r'portions? per (?:container|package|pkg)\s*[:.]?\s*(\d+(?:\.\d+)?)'
            ],
            'fat': [
                r'total fat\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g',
                r'fat\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g',
                r'saturated fat\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g',
                r'trans fat\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g',
                r'polyunsaturated fat\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g',
                r'monounsaturated fat\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g'
            ],
            'cholesterol': [
                r'cholesterol\s*[:.]?\s*(\d+(?:\.\d+)?)\s*mg'
            ],
            'sodium': [
                r'sodium\s*[:.]?\s*(\d+(?:\.\d+)?)\s*mg',
                r'salt\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:g|mg)'
            ],
            'carbohydrates': [
                r'total carbohydrate\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g',
                r'carbohydrates?\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g',
                r'dietary fiber\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g',
                r'fiber\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g',
                r'total sugars?\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g',
                r'sugars?\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g',
                r'added sugars?\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g'
            ],
            'protein': [
                r'protein\s*[:.]?\s*(\d+(?:\.\d+)?)\s*g'
            ],
            'vitamins': [
                r'vitamin ([abcdefk])\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|mcg|µg|iu)',
                r'(?:vit\.?|vitamin)\s*([abcdefk])\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|mcg|µg|iu)',
                r'ascorbic acid\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|mcg)',
                r'folate\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|mcg|µg)',
                r'folic acid\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|mcg|µg)',
                r'niacin\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|mcg)',
                r'thiamine\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|mcg)',
                r'riboflavin\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|mcg)'
            ],
            'minerals': [
                r'calcium\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|g)',
                r'iron\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|g)',
                r'potassium\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|g)',
                r'magnesium\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|g)',
                r'phosphorus\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|g)',
                r'zinc\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|g)',
                r'selenium\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|mcg|µg)',
                r'copper\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|mcg)',
                r'manganese\s*[:.]?\s*(\d+(?:\.\d+)?)\s*(?:mg|mcg)'
            ],
            'daily_values': [
                r'(\d+)\s*%\s*(?:daily value|dv|d\.?v\.?)',
                r'(\d+)\s*%',
                r'(\d+(?:\.\d+)?)\s*percent'
            ]
        }
    
    def _build_serving_patterns(self) -> List[str]:
        """Build patterns for serving size extraction"""
        return [
            r'serving size\s*[:.]?\s*(.+?)(?:\(|$|\n)',
            r'per serving\s*[:.]?\s*(.+?)(?:\(|$|\n)',
            r'portion size\s*[:.]?\s*(.+?)(?:\(|$|\n)',
            r'(\d+(?:\.\d+)?)\s*(?:cup|cups|tablespoon|tbsp|teaspoon|tsp|oz|g|ml|piece|pieces|slice|slices)',
            r'(\d+(?:\.\d+)?\/\d+)\s*(?:cup|package|container)'
        ]
    
    def _build_ingredient_patterns(self) -> List[str]:
        """Build patterns for ingredient extraction"""
        return [
            r'ingredients?\s*[:.]?\s*(.+?)(?:contains?[:.]|allergen|nutrition|$)',
            r'ingredient list\s*[:.]?\s*(.+?)(?:contains?[:.]|allergen|nutrition|$)'
        ]
    
    def _build_allergen_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for allergen detection"""
        return {
            'contains': [
                r'contains?\s*[:.]?\s*(.+?)(?:may contain|manufactured|produced|$)',
                r'allergens?\s*[:.]?\s*(.+?)(?:may contain|manufactured|produced|$)'
            ],
            'may_contain': [
                r'may contain\s*[:.]?\s*(.+?)(?:manufactured|produced|$)',
                r'may be present\s*[:.]?\s*(.+?)(?:manufactured|produced|$)'
            ],
            'common_allergens': [
                'milk', 'eggs', 'fish', 'shellfish', 'tree nuts', 'peanuts', 
                'wheat', 'soy', 'sesame', 'dairy', 'gluten', 'nuts'
            ]
        }
    
    def _build_claim_patterns(self) -> List[str]:
        """Build patterns for health claim extraction"""
        return [
            r'(fat free|low fat|reduced fat|light)',
            r'(sugar free|no sugar|low sugar|reduced sugar)',
            r'(sodium free|low sodium|reduced sodium|no salt)',
            r'(high fiber|good source of fiber|excellent source of fiber)',
            r'(organic|natural|all natural)',
            r'(non-?gmo|gmo free)',
            r'(gluten free|dairy free|lactose free)',
            r'(fortified with|enriched with|added)',
            r'(whole grain|multigrain)',
            r'(no artificial|no preservatives|no additives)',
            r'(kosher|halal)',
            r'(vegan|vegetarian)',
            r'(\d+% daily value of [^,.\n]+)',
            r'(excellent source of [^,.\n]+)',
            r'(good source of [^,.\n]+)',
            r'(high in [^,.\n]+)',
            r'(low in [^,.\n]+)'
        ]
    
    def fuzzy_match_nutrient(self, text: str, threshold: int = 80) -> Optional[str]:
        """Use fuzzy matching to identify nutrition terms"""
        if not FUZZY_AVAILABLE:
            return None
        
        text_lower = text.lower().strip()
        best_match = None
        best_score = 0
        
        for nutrient, keywords in self.standard_nutrients.items():
            for keyword in keywords:
                score = fuzz.ratio(text_lower, keyword)
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = nutrient
        
        return best_match
    
    def extract_numerical_values(self, text: str, context: str = "") -> List[Tuple[float, str, Optional[float]]]:
        """Extract numerical values with units and optional daily values"""
        results = []
        
        # Pattern for value with unit and optional DV%
        pattern = r'(\d+(?:\.\d+)?)\s*(g|mg|mcg|µg|iu|cal|kcal)?\s*(?:.*?(\d+)%)?'
        
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            value = float(match.group(1))
            unit = match.group(2) or ""
            dv_percent = float(match.group(3)) if match.group(3) else None
            results.append((value, unit.lower(), dv_percent))
        
        return results
    
    def parse_serving_info(self, text: str) -> Dict[str, Any]:
        """Extract serving size and servings per container"""
        serving_info = {}
        
        for pattern in self.serving_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                serving_text = match.group(1).strip() if len(match.groups()) > 0 else match.group(0)
                
                if 'serving size' in pattern or 'per serving' in pattern:
                    serving_info['serving_size'] = serving_text
                elif 'servings per' in pattern or 'portions per' in pattern:
                    try:
                        serving_info['servings_per_container'] = float(match.group(1))
                    except (ValueError, IndexError):
                        pass
        
        return serving_info
    
    def parse_nutrition_facts(self, text: str) -> Dict[str, Any]:
        """Extract comprehensive nutrition facts"""
        nutrition_facts = {}
        
        # Handle case where text might not have nutrition facts table
        if not any(keyword in text.lower() for keyword in ['calories', 'nutrition facts', 'total fat', 'protein', 'carbs', 'sodium']):
            logger.info("No nutrition facts table detected in text, returning basic info")
            # Only infer calories from lines that explicitly mention calories/kcal to avoid serving-size misparse
            for line in text.splitlines():
                lower = line.lower()
                # Gate by explicit tokens using word boundaries to avoid 'calcium'
                if re.search(r'\b(calories?|kcal|cal)\b', lower):
                    # Avoid false positives like 'calcium'
                    if 'calcium' in lower:
                        continue
                    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:kcal|cal|calories?)\b', line, re.IGNORECASE)
                    if m:
                        try:
                            val = float(m.group(1))
                            if 0 <= val <= 2000:
                                nutrition_facts['calories'] = val
                                break
                        except ValueError:
                            pass
            return nutrition_facts
        
        # Parse each category
        for category, patterns in self.nutrition_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if category == 'serving_info':
                        serving_info = self.parse_serving_info(text)
                        nutrition_facts.update(serving_info)
                    elif category == 'daily_values':
                        continue  # Handled inline with other nutrients
                    else:
                        try:
                            value = float(match.group(1))
                            
                            if category == 'calories':
                                # Avoid mis-parsing 'calcium' as calories
                                full_match_lower = match.group(0).lower()
                                if 'calcium' in full_match_lower:
                                    continue
                                # Handle 'calories from fat'
                                if 'from fat' in full_match_lower:
                                    nutrition_facts['calories_from_fat'] = value
                                    continue
                                nutrition_facts['calories'] = value
                            elif category == 'fat':
                                if 'total fat' in match.group(0).lower():
                                    nutrition_facts['total_fat'] = value
                                elif 'saturated' in match.group(0).lower():
                                    nutrition_facts['saturated_fat'] = value
                                elif 'trans' in match.group(0).lower():
                                    nutrition_facts['trans_fat'] = value
                                elif 'polyunsaturated' in match.group(0).lower():
                                    nutrition_facts['polyunsaturated_fat'] = value
                                elif 'monounsaturated' in match.group(0).lower():
                                    nutrition_facts['monounsaturated_fat'] = value
                                elif 'fat' in match.group(0).lower():
                                    nutrition_facts['total_fat'] = value
                            elif category == 'cholesterol':
                                nutrition_facts['cholesterol'] = value
                            elif category == 'sodium':
                                nutrition_facts['sodium'] = value
                            elif category == 'carbohydrates':
                                if 'total carbohydrate' in match.group(0).lower():
                                    nutrition_facts['total_carbs'] = value
                                elif 'fiber' in match.group(0).lower():
                                    nutrition_facts['dietary_fiber'] = value
                                elif 'added sugar' in match.group(0).lower():
                                    nutrition_facts['added_sugars'] = value
                                elif 'sugar' in match.group(0).lower():
                                    nutrition_facts['total_sugars'] = value
                                elif 'carbohydrate' in match.group(0).lower():
                                    nutrition_facts['total_carbs'] = value
                            elif category == 'protein':
                                nutrition_facts['protein'] = value
                            elif category == 'vitamins':
                                vitamin_name = match.group(1).lower() if len(match.groups()) > 1 else 'unknown'
                                vitamin_value = float(match.group(2)) if len(match.groups()) > 1 else value
                                nutrition_facts[f'vitamin_{vitamin_name}'] = vitamin_value
                            elif category == 'minerals':
                                mineral_match = re.search(r'(calcium|iron|potassium|magnesium|phosphorus|zinc|selenium|copper|manganese)', 
                                                        match.group(0), re.IGNORECASE)
                                if mineral_match:
                                    mineral_name = mineral_match.group(1).lower()
                                    nutrition_facts[mineral_name] = value
                        except (ValueError, IndexError):
                            continue
        
        # Extract daily values
        self._extract_daily_values(text, nutrition_facts)
        
        return nutrition_facts
    
    def _extract_daily_values(self, text: str, nutrition_facts: Dict[str, Any]) -> None:
        """Extract daily value percentages and associate with nutrients"""
        lines = text.split('\n')
        
        for line in lines:
            # Look for patterns like "Total Fat 5g 7%"
            dv_match = re.search(r'(\d+)%', line)
            if dv_match:
                dv_value = float(dv_match.group(1))
                
                # Try to match with known nutrients
                line_lower = line.lower()
                for nutrient in ['total_fat', 'saturated_fat', 'cholesterol', 'sodium', 
                               'total_carbs', 'dietary_fiber', 'vitamin_a', 'vitamin_c', 
                               'calcium', 'iron']:
                    nutrient_keywords = self.standard_nutrients.get(nutrient, [nutrient.replace('_', ' ')])
                    if any(keyword in line_lower for keyword in nutrient_keywords):
                        nutrition_facts[f'{nutrient}_dv'] = dv_value
                        break
    
    def parse_ingredients(self, text: str) -> List[str]:
        """Extract and clean ingredient list"""
        ingredients = []
        
        # Look for ingredients section using patterns
        for pattern in self.ingredient_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                ingredient_text = match.group(1)
                
                # Clean and split ingredients
                ingredient_text = re.sub(r'\([^)]*\)', '', ingredient_text)  # Remove parentheses
                ingredient_list = re.split(r'[,;]', ingredient_text)
                
                for ingredient in ingredient_list:
                    cleaned = ingredient.strip().title()
                    if cleaned and len(cleaned) > 1:
                        ingredients.append(cleaned)
        
        # Fallback: if no formal ingredients list found, try to extract common ingredient words
        if not ingredients:
            common_ingredients = ['butter', 'sugar', 'flour', 'eggs', 'milk', 'chocolate', 'vanilla', 
                                'salt', 'baking powder', 'cocoa', 'oil', 'water', 'cream', 'nuts']
            text_lower = text.lower()
            for ingredient in common_ingredients:
                if ingredient in text_lower:
                    ingredients.append(ingredient.title())
        
        return ingredients[:25]  # Limit to first 25 ingredients
    
    def parse_allergens(self, text: str) -> List[str]:
        """Extract allergen information"""
        allergens = []
        
        # Check for explicit allergen statements
        for category, patterns in self.allergen_patterns.items():
            if category == 'common_allergens':
                continue
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    allergen_text = match.group(1).lower()
                    
                    # Check against common allergens
                    for allergen in self.allergen_patterns['common_allergens']:
                        if allergen in allergen_text:
                            allergens.append(allergen.title())
        
        return list(set(allergens))  # Remove duplicates
    
    def parse_health_claims(self, text: str) -> List[str]:
        """Extract health and nutrition claims"""
        claims = []
        
        for pattern in self.claim_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                claim = match.group(1) if len(match.groups()) > 0 else match.group(0)
                claims.append(claim.strip().title())
        
        return list(set(claims))[:15]  # Limit to 15 unique claims
    
    def validate_nutrition_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean nutrition data"""
        validated = {}
        
        # Validate numeric ranges
        numeric_ranges = {
            'calories': (0, 2000),
            'total_fat': (0, 100),
            'saturated_fat': (0, 50),
            'trans_fat': (0, 10),
            'cholesterol': (0, 1000),
            'sodium': (0, 5000),
            'total_carbs': (0, 200),
            'dietary_fiber': (0, 50),
            'total_sugars': (0, 100),
            'added_sugars': (0, 100),
            'protein': (0, 100)
        }
        
        for key, value in data.items():
            if key in numeric_ranges and isinstance(value, (int, float)):
                min_val, max_val = numeric_ranges[key]
                if min_val <= value <= max_val:
                    validated[key] = value
                else:
                    logger.warning(f"Value {value} for {key} outside expected range [{min_val}, {max_val}]")
            else:
                validated[key] = value
        
        return validated


# Global parser instance
enhanced_parser = NutritionParser()

def parse_nutrition_data_enhanced(text: str) -> Dict[str, Any]:
    """
    Enhanced nutrition data parsing function.
    
    Returns comprehensive structured data including:
    - nutrition_facts: Complete nutritional information
    - ingredients: List of ingredients
    - allergens: List of allergens
    - claims: List of health/nutrition claims
    - raw_text: Original text
    """
    
    if not text or not text.strip():
        return {
            'nutrition_facts': {},
            'ingredients': [],
            'allergens': [],
            'claims': [],
            'raw_text': ''
        }
    
    try:
        # Parse different sections
        nutrition_facts = enhanced_parser.parse_nutrition_facts(text)
        ingredients = enhanced_parser.parse_ingredients(text)
        allergens = enhanced_parser.parse_allergens(text)
        claims = enhanced_parser.parse_health_claims(text)
        
        # Validate nutrition data
        nutrition_facts = enhanced_parser.validate_nutrition_data(nutrition_facts)
        
        return {
            'nutrition_facts': nutrition_facts,
            'ingredients': ingredients,
            'allergens': allergens,
            'claims': claims,
            'raw_text': text
        }
        
    except Exception as e:
        logger.error(f"Enhanced parsing failed: {e}")
        # Safe minimal fallback to avoid import errors and ensure backend stability
        return {
            'nutrition_facts': {},
            'ingredients': [],
            'allergens': [],
            'claims': [],
            'raw_text': text or ''
        }

# Backward compatibility
def parse_nutrition_data(text: str) -> Dict[str, Any]:
    """Backward compatible parsing function"""
    return parse_nutrition_data_enhanced(text)
