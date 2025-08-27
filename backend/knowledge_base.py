import requests
import asyncio
import aiohttp
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import json

load_dotenv()

# API Configuration
USDA_API_KEY = os.getenv("USDA_API_KEY")  # Optional - USDA has public endpoints
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
OPENFOODFACTS_BASE_URL = "https://world.openfoodfacts.org/api/v0"

class USDAClient:
    """Client for USDA FoodData Central API"""
    
    def __init__(self):
        self.base_url = USDA_BASE_URL
        self.api_key = USDA_API_KEY
        
    async def search_foods(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for foods in USDA database"""
        url = f"{self.base_url}/foods/search"
        params = {
            "query": query,
            "pageSize": limit,
            "dataType": ["Foundation", "SR Legacy"]
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("foods", [])
                    else:
                        print(f"USDA API error: {response.status}")
                        return []
        except Exception as e:
            print(f"USDA search error: {e}")
            return []
    
    async def get_food_details(self, fdc_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed nutrition info for a specific food"""
        url = f"{self.base_url}/food/{fdc_id}"
        params = {}
        
        if self.api_key:
            params["api_key"] = self.api_key
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"USDA details error: {response.status}")
                        return None
        except Exception as e:
            print(f"USDA details error: {e}")
            return None
    
    async def get_nutrient_standards(self, nutrient_name: str) -> Optional[Dict[str, Any]]:
        """Get recommended daily values for nutrients"""
        # FDA Daily Values (2016 standards)
        daily_values = {
            "calories": {"adult": 2000, "unit": "kcal"},
            "fat": {"adult": 78, "unit": "g"},
            "saturated_fat": {"adult": 20, "unit": "g"},
            "cholesterol": {"adult": 300, "unit": "mg"},
            "sodium": {"adult": 2300, "unit": "mg"},
            "carbohydrates": {"adult": 275, "unit": "g"},
            "fiber": {"adult": 28, "unit": "g"},
            "sugar": {"adult": 50, "unit": "g"},  # Added sugars limit
            "protein": {"adult": 50, "unit": "g"},
            "vitamin_c": {"adult": 90, "unit": "mg"},
            "calcium": {"adult": 1300, "unit": "mg"},
            "iron": {"adult": 18, "unit": "mg"},
            "potassium": {"adult": 4700, "unit": "mg"}
        }
        
        return daily_values.get(nutrient_name.lower().replace(" ", "_"))

class OpenFoodFactsClient:
    """Client for OpenFoodFacts API"""
    
    def __init__(self):
        self.base_url = OPENFOODFACTS_BASE_URL
        
    async def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for products in OpenFoodFacts database"""
        url = f"{self.base_url}/search"
        params = {
            "search_terms": query,
            "page_size": limit,
            "json": 1,
            "fields": "product_name,brands,ingredients_text,nutriments,nova_group,nutriscore_grade"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("products", [])
                    else:
                        print(f"OpenFoodFacts API error: {response.status}")
                        return []
        except Exception as e:
            print(f"OpenFoodFacts search error: {e}")
            return []
    
    async def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get product details by barcode"""
        url = f"{self.base_url}/product/{barcode}.json"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == 1:
                            return data.get("product")
                    return None
        except Exception as e:
            print(f"OpenFoodFacts barcode error: {e}")
            return None
    
    async def get_ingredient_info(self, ingredient: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific ingredient"""
        # Search for products containing this ingredient
        products = await self.search_products(ingredient, limit=3)
        
        if not products:
            return None
        
        # Analyze common characteristics of products with this ingredient
        analysis = {
            "ingredient": ingredient,
            "common_in": [],
            "average_nutriscore": None,
            "processing_level": None
        }
        
        nutriscores = []
        nova_groups = []
        
        for product in products:
            if product.get("nutriscore_grade"):
                nutriscores.append(product["nutriscore_grade"])
            if product.get("nova_group"):
                nova_groups.append(product["nova_group"])
            if product.get("brands"):
                analysis["common_in"].extend(product["brands"].split(",")[:2])
        
        if nutriscores:
            # Calculate average nutriscore (A=1, B=2, C=3, D=4, E=5)
            score_map = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
            avg_score = sum(score_map.get(score.lower(), 3) for score in nutriscores) / len(nutriscores)
            analysis["average_nutriscore"] = avg_score
        
        if nova_groups:
            avg_nova = sum(nova_groups) / len(nova_groups)
            analysis["processing_level"] = "highly_processed" if avg_nova >= 3.5 else "processed" if avg_nova >= 2.5 else "minimally_processed"
        
        return analysis

class KnowledgeBaseManager:
    """Manager for all knowledge base integrations"""
    
    def __init__(self):
        self.usda = USDAClient()
        self.openfoodfacts = OpenFoodFactsClient()
        
    async def verify_nutrition_claims(self, claims: List[str], nutrition_facts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Cross-reference nutrition claims with knowledge bases"""
        verified_claims = []
        
        for claim in claims:
            verification = await self._verify_single_claim(claim, nutrition_facts)
            verified_claims.append(verification)
        
        return verified_claims
    
    async def _verify_single_claim(self, claim: str, nutrition_facts: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a single claim against standards"""
        claim_lower = claim.lower()
        
        # Get relevant nutrient standards
        relevant_nutrients = []
        if "fat" in claim_lower:
            relevant_nutrients.append("fat")
        if "sodium" in claim_lower:
            relevant_nutrients.append("sodium")
        if "sugar" in claim_lower:
            relevant_nutrients.append("sugar")
        if "fiber" in claim_lower:
            relevant_nutrients.append("fiber")
        if "protein" in claim_lower:
            relevant_nutrients.append("protein")
        
        # Get standards from USDA
        standards = {}
        for nutrient in relevant_nutrients:
            standard = await self.usda.get_nutrient_standards(nutrient)
            if standard:
                standards[nutrient] = standard
        
        # Verify claim against standards and actual nutrition facts
        verification = {
            "claim": claim,
            "status": "unknown",
            "explanation": "Unable to verify claim",
            "source": "Knowledge base analysis",
            "standards_used": standards
        }
        
        # Apply verification logic based on claim type
        if "low fat" in claim_lower and "fat" in nutrition_facts and "fat" in standards:
            fat_content = nutrition_facts["fat"]
            # FDA standard: ≤3g per serving for "low fat"
            if fat_content <= 3:
                verification.update({
                    "status": "verified",
                    "explanation": f"Confirmed: {fat_content}g fat meets FDA 'low fat' standard (≤3g per serving)"
                })
            else:
                verification.update({
                    "status": "false",
                    "explanation": f"Misleading: {fat_content}g fat exceeds FDA 'low fat' standard (≤3g per serving)"
                })
        
        return verification
    
    async def analyze_ingredients_against_database(self, ingredients: List[str]) -> Dict[str, Any]:
        """Analyze ingredients using OpenFoodFacts database"""
        analysis = {
            "total_ingredients": len(ingredients),
            "ingredient_details": [],
            "processing_indicators": [],
            "common_allergens": [],
            "additives_count": 0
        }
        
        # Analyze each ingredient
        for ingredient in ingredients[:10]:  # Limit to first 10 for API efficiency
            ingredient_info = await self.openfoodfacts.get_ingredient_info(ingredient)
            if ingredient_info:
                analysis["ingredient_details"].append(ingredient_info)
                
                # Check processing level
                if ingredient_info.get("processing_level") == "highly_processed":
                    analysis["processing_indicators"].append(ingredient)
        
        # Identify additives and preservatives
        additive_keywords = [
            "sodium benzoate", "potassium sorbate", "calcium propionate",
            "bht", "bha", "tbhq", "sodium nitrite", "sodium nitrate",
            "monosodium glutamate", "msg", "artificial flavor", "artificial color"
        ]
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            for additive in additive_keywords:
                if additive in ingredient_lower:
                    analysis["additives_count"] += 1
                    break
        
        return analysis
    
    async def get_similar_products(self, product_name: str, nutrition_facts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar products for comparison"""
        try:
            # Search both databases
            usda_results = await self.usda.search_foods(product_name, limit=3)
            off_results = await self.openfoodfacts.search_products(product_name, limit=3)
            
            similar_products = []
            
            # Process USDA results
            for food in usda_results:
                if food.get("foodNutrients"):
                    similar_products.append({
                        "name": food.get("description", "Unknown"),
                        "source": "USDA",
                        "calories": self._extract_nutrient_value(food["foodNutrients"], "Energy"),
                        "protein": self._extract_nutrient_value(food["foodNutrients"], "Protein"),
                        "fat": self._extract_nutrient_value(food["foodNutrients"], "Total lipid (fat)"),
                        "carbs": self._extract_nutrient_value(food["foodNutrients"], "Carbohydrate, by difference")
                    })
            
            # Process OpenFoodFacts results
            for product in off_results:
                if product.get("nutriments"):
                    similar_products.append({
                        "name": product.get("product_name", "Unknown"),
                        "source": "OpenFoodFacts",
                        "calories": product["nutriments"].get("energy-kcal_100g", 0),
                        "protein": product["nutriments"].get("proteins_100g", 0),
                        "fat": product["nutriments"].get("fat_100g", 0),
                        "carbs": product["nutriments"].get("carbohydrates_100g", 0),
                        "nutriscore": product.get("nutriscore_grade", "unknown")
                    })
            
            return similar_products[:5]  # Return top 5 matches
            
        except Exception as e:
            print(f"Similar products error: {e}")
            return []
    
    def _extract_nutrient_value(self, nutrients: List[Dict], nutrient_name: str) -> float:
        """Extract nutrient value from USDA nutrient list"""
        for nutrient in nutrients:
            if nutrient.get("nutrientName") == nutrient_name:
                return nutrient.get("value", 0.0)
        return 0.0
    
    async def get_health_insights(self, nutrition_facts: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate health insights based on knowledge base standards"""
        insights = []
        
        # Get daily value standards
        standards = {}
        for nutrient in ["calories", "fat", "sodium", "fiber", "protein"]:
            std = await self.usda.get_nutrient_standards(nutrient)
            if std:
                standards[nutrient] = std
        
        # Generate insights based on standards
        for nutrient, value in nutrition_facts.items():
            if nutrient in standards and isinstance(value, (int, float)):
                standard = standards[nutrient]["adult"]
                percentage = (value / standard) * 100
                
                if percentage > 25:  # High content
                    insights.append({
                        "type": "warning" if nutrient in ["fat", "sodium"] else "positive",
                        "text": f"High {nutrient} content: {value}{standards[nutrient]['unit']} ({percentage:.1f}% of daily value)"
                    })
                elif percentage < 5:  # Low content
                    insights.append({
                        "type": "neutral",
                        "text": f"Low {nutrient} content: {value}{standards[nutrient]['unit']} ({percentage:.1f}% of daily value)"
                    })
        
        return insights[:5]  # Limit to 5 insights

# Initialize global knowledge base manager
knowledge_base = KnowledgeBaseManager()
