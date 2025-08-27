import cohere
import requests
import json
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import asyncio

load_dotenv()

# API Configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
USDA_API_KEY = os.getenv("USDA_API_KEY")  # Optional, USDA has public endpoints

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY) if COHERE_API_KEY else None

# Knowledge base URLs
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
OPENFOODFACTS_URL = "https://world.openfoodfacts.org/api/v0/product"

async def analyze_nutrition_data(structured_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
    """
    Comprehensive analysis using AI reasoning and knowledge bases
    """
    results = {
        "nutrition_facts": structured_data.get("nutrition_facts", {}),
        "claim_verification": [],
        "ingredient_analysis": {},
        "health_recommendation": {},
        "overall_score": 0,
        "key_insights": [],
        "recommendations": []
    }
    
    try:
        # Run analysis tasks concurrently
        tasks = [
            verify_health_claims(structured_data.get("claims", []), structured_data.get("nutrition_facts", {})),
            analyze_ingredients(structured_data.get("ingredients", [])),
            generate_health_recommendation(structured_data, raw_text),
            get_nutrition_insights(structured_data.get("nutrition_facts", {}))
        ]
        
        claim_verification, ingredient_analysis, health_recommendation, nutrition_insights = await asyncio.gather(*tasks)
        
        results["claim_verification"] = claim_verification
        results["ingredient_analysis"] = ingredient_analysis
        results["health_recommendation"] = health_recommendation
        results["key_insights"] = nutrition_insights
        
        # Calculate overall health score
        results["overall_score"] = calculate_overall_score(results)
        
        # Generate recommendations
        results["recommendations"] = generate_recommendations(results)
        
    except Exception as e:
        print(f"Analysis error: {e}")
        # Return basic results even if AI analysis fails
        results["health_recommendation"] = {
            "level": "moderate",
            "summary": "Analysis completed with limited data. Please verify nutrition information manually.",
            "reasons": ["Limited data available for comprehensive analysis"]
        }
    
    return results

async def verify_health_claims(claims: List[str], nutrition_facts: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Verify health claims against nutrition data and databases
    """
    verified_claims = []
    
    for claim in claims:
        verification = await verify_single_claim(claim, nutrition_facts)
        verified_claims.append(verification)
    
    return verified_claims

async def verify_single_claim(claim: str, nutrition_facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify a single health claim
    """
    claim_lower = claim.lower()
    
    # Rule-based verification for common claims
    verification = {
        "claim": claim,
        "status": "unknown",
        "explanation": "Unable to verify this claim.",
        "source": "Internal analysis"
    }
    
    # Fat-related claims
    if "fat free" in claim_lower or "0g fat" in claim_lower:
        fat = nutrition_facts.get("fat", 0)
        if fat <= 0.5:
            verification.update({
                "status": "verified",
                "explanation": f"Confirmed: Contains {fat}g fat, meeting FDA criteria for 'fat free' (≤0.5g per serving)."
            })
        else:
            verification.update({
                "status": "false",
                "explanation": f"Misleading: Contains {fat}g fat, which exceeds FDA criteria for 'fat free' (≤0.5g per serving)."
            })
    
    elif "low fat" in claim_lower:
        fat = nutrition_facts.get("fat", 0)
        if fat <= 3:
            verification.update({
                "status": "verified",
                "explanation": f"Confirmed: Contains {fat}g fat, meeting FDA criteria for 'low fat' (≤3g per serving)."
            })
        else:
            verification.update({
                "status": "misleading",
                "explanation": f"Questionable: Contains {fat}g fat, which may exceed FDA criteria for 'low fat' (≤3g per serving)."
            })
    
    # Sugar-related claims
    elif "sugar free" in claim_lower or "no sugar" in claim_lower:
        sugar = nutrition_facts.get("sugar", 0)
        if sugar <= 0.5:
            verification.update({
                "status": "verified",
                "explanation": f"Confirmed: Contains {sugar}g sugar, meeting FDA criteria for 'sugar free' (≤0.5g per serving)."
            })
        else:
            verification.update({
                "status": "false",
                "explanation": f"Misleading: Contains {sugar}g sugar, which exceeds FDA criteria for 'sugar free' (≤0.5g per serving)."
            })
    
    # Sodium claims
    elif "low sodium" in claim_lower:
        sodium = nutrition_facts.get("sodium", 0)
        if sodium <= 140:
            verification.update({
                "status": "verified",
                "explanation": f"Confirmed: Contains {sodium}mg sodium, meeting FDA criteria for 'low sodium' (≤140mg per serving)."
            })
        else:
            verification.update({
                "status": "misleading",
                "explanation": f"Questionable: Contains {sodium}mg sodium, which exceeds FDA criteria for 'low sodium' (≤140mg per serving)."
            })
    
    # High fiber claims
    elif "high fiber" in claim_lower:
        fiber = nutrition_facts.get("fiber", 0)
        if fiber >= 5:
            verification.update({
                "status": "verified",
                "explanation": f"Confirmed: Contains {fiber}g fiber, meeting FDA criteria for 'high fiber' (≥5g per serving)."
            })
        else:
            verification.update({
                "status": "false",
                "explanation": f"Misleading: Contains {fiber}g fiber, which is below FDA criteria for 'high fiber' (≥5g per serving)."
            })
    
    # Use AI for complex claims if Cohere is available
    elif co:
        try:
            ai_verification = await get_ai_claim_verification(claim, nutrition_facts)
            verification.update(ai_verification)
        except Exception as e:
            print(f"AI verification error: {e}")
    
    return verification

async def get_ai_claim_verification(claim: str, nutrition_facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use Cohere AI to verify complex health claims
    """
    if not co:
        return {"status": "unknown", "explanation": "AI verification not available"}
    
    prompt = f"""
    Analyze this health claim against the nutrition facts:
    
    Claim: "{claim}"
    Nutrition Facts: {json.dumps(nutrition_facts, indent=2)}
    
    Based on FDA regulations and nutritional science, is this claim:
    1. Verified (accurate and supported by data)
    2. Misleading (technically true but potentially deceptive)  
    3. False (contradicted by the data)
    
    Provide a brief explanation with scientific reasoning.
    """
    
    try:
        import socket
        # Test DNS resolution first
        socket.gethostbyname('api.cohere.ai')
        
        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=200,
            temperature=0.3
        )
        ai_response = response.generations[0].text.strip()
        
        # Parse AI response to determine status
        if "verified" in ai_response.lower() or "accurate" in ai_response.lower():
            status = "verified"
        elif "misleading" in ai_response.lower() or "deceptive" in ai_response.lower():
            status = "misleading"
        elif "false" in ai_response.lower() or "contradicted" in ai_response.lower():
            status = "false"
        else:
            status = "unknown"
            
        return {
            "status": status,
            "explanation": ai_response,
            "source": "AI analysis (Cohere)"
        }
        
    except socket.gaierror as dns_error:
        print(f"[ANALYZER] DNS resolution failed for api.cohere.ai: {dns_error}")
        print("[ANALYZER] Check internet connection or DNS settings")
        return {"status": "unknown", "explanation": "Network connectivity issue"}
    except Exception as e:
        print(f"[ANALYZER] Cohere API error: {e}")
        return {"status": "unknown", "explanation": "AI analysis failed"}

async def analyze_ingredients(ingredients: List[str]) -> Dict[str, Any]:
    """
    Analyze ingredients for health concerns and allergens
    """
    analysis = {
        "ingredients": ingredients,
        "flaggedIngredients": [],
        "allergens": [],
        "additives": {
            "preservatives": 0,
            "artificialColors": 0,
            "artificialFlavors": 0
        }
    }
    
    # Known problematic ingredients
    harmful_ingredients = {
        "high_fructose_corn_syrup": {
            "riskLevel": "high",
            "reason": "Linked to obesity, diabetes, and metabolic issues",
            "alternatives": ["cane sugar", "maple syrup", "honey"]
        },
        "partially_hydrogenated_oil": {
            "riskLevel": "high", 
            "reason": "Contains trans fats, linked to heart disease",
            "alternatives": ["olive oil", "coconut oil", "avocado oil"]
        },
        "monosodium_glutamate": {
            "riskLevel": "medium",
            "reason": "May cause headaches and reactions in sensitive individuals",
            "alternatives": ["natural spices", "herbs", "garlic powder"]
        },
        "sodium_nitrite": {
            "riskLevel": "medium",
            "reason": "Potential carcinogen when heated",
            "alternatives": ["celery powder", "natural preservatives"]
        },
        "artificial_colors": {
            "riskLevel": "medium",
            "reason": "May cause hyperactivity in children",
            "alternatives": ["natural colors", "fruit/vegetable extracts"]
        }
    }
    
    # Common allergens
    allergen_keywords = [
        "milk", "eggs", "fish", "shellfish", "tree nuts", "peanuts", 
        "wheat", "soy", "sesame", "dairy", "gluten"
    ]
    
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower()
        
        # Check for harmful ingredients
        for harmful_key, harmful_info in harmful_ingredients.items():
            if harmful_key.replace("_", " ") in ingredient_lower:
                analysis["flaggedIngredients"].append({
                    "name": ingredient,
                    **harmful_info
                })
        
        # Check for allergens
        for allergen in allergen_keywords:
            if allergen in ingredient_lower:
                if allergen not in analysis["allergens"]:
                    analysis["allergens"].append(allergen.title())
        
        # Count additives
        if any(word in ingredient_lower for word in ["preserve", "sodium benzoate", "potassium sorbate"]):
            analysis["additives"]["preservatives"] += 1
        
        if any(word in ingredient_lower for word in ["red dye", "blue dye", "yellow dye", "artificial color"]):
            analysis["additives"]["artificialColors"] += 1
        
        if "artificial flavor" in ingredient_lower:
            analysis["additives"]["artificialFlavors"] += 1
    
    return analysis

async def generate_health_recommendation(structured_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
    """
    Generate overall health recommendation using AI
    """
    nutrition_facts = structured_data.get("nutrition_facts", {})
    ingredients = structured_data.get("ingredients", [])
    
    # Calculate basic health score
    score = 50  # Start with neutral score
    reasons = []
    tips = []
    
    # Analyze calories
    calories = nutrition_facts.get("calories", 0)
    if calories > 400:
        score -= 10
        reasons.append("High calorie content per serving")
        tips.append("Consider smaller portions or look for lower-calorie alternatives")
    elif calories < 100:
        score += 5
        reasons.append("Reasonable calorie content")
    
    # Analyze fat content
    fat = nutrition_facts.get("fat", 0)
    saturated_fat = nutrition_facts.get("saturatedFat", 0)
    if saturated_fat > 5:
        score -= 15
        reasons.append("High saturated fat content")
        tips.append("Limit saturated fat to reduce heart disease risk")
    elif fat < 3:
        score += 5
        reasons.append("Low fat content")
    
    # Analyze sodium
    sodium = nutrition_facts.get("sodium", 0)
    if sodium > 600:
        score -= 20
        reasons.append("Very high sodium content")
        tips.append("High sodium can increase blood pressure risk")
    elif sodium > 300:
        score -= 10
        reasons.append("Moderate to high sodium content")
    elif sodium < 140:
        score += 10
        reasons.append("Low sodium content")
    
    # Analyze sugar
    sugar = nutrition_facts.get("sugar", 0)
    if sugar > 15:
        score -= 15
        reasons.append("High sugar content")
        tips.append("Excessive sugar can lead to weight gain and diabetes")
    elif sugar < 5:
        score += 5
        reasons.append("Low sugar content")
    
    # Analyze fiber
    fiber = nutrition_facts.get("fiber", 0)
    if fiber >= 5:
        score += 15
        reasons.append("Good source of fiber")
        tips.append("Fiber helps with digestion and heart health")
    elif fiber >= 3:
        score += 5
        reasons.append("Contains some fiber")
    
    # Analyze protein
    protein = nutrition_facts.get("protein", 0)
    if protein >= 10:
        score += 10
        reasons.append("Good protein content")
    
    # Analyze ingredients
    if len(ingredients) > 15:
        score -= 5
        reasons.append("Long ingredient list may indicate heavy processing")
        tips.append("Choose products with fewer, recognizable ingredients")
    
    # Determine recommendation level
    if score >= 75:
        level = "safe"
        summary = "This product appears to be a healthy choice with good nutritional balance."
    elif score >= 50:
        level = "moderate"
        summary = "This product is okay in moderation but has some nutritional concerns."
    else:
        level = "avoid"
        summary = "This product has several nutritional red flags and should be consumed sparingly."
    
    # Use AI for more sophisticated analysis if available
    if co and len(raw_text) > 50:
        try:
            ai_recommendation = await get_ai_health_recommendation(structured_data, raw_text)
            if ai_recommendation:
                return ai_recommendation
        except Exception as e:
            print(f"AI recommendation error: {e}")
    
    return {
        "level": level,
        "summary": summary,
        "reasons": reasons[:5],  # Limit to top 5 reasons
        "tips": tips[:3],  # Limit to top 3 tips
        "score": max(0, min(100, score))  # Ensure score is 0-100
    }

async def get_ai_health_recommendation(structured_data: Dict[str, Any], raw_text: str) -> Optional[Dict[str, Any]]:
    """
    Generate AI-powered health recommendation
    """
    if not co:
        return None
    
    prompt = f"""
    As a nutrition scientist, analyze this food product and provide a health recommendation:
    
    Nutrition Facts: {json.dumps(structured_data.get('nutrition_facts', {}), indent=2)}
    Ingredients: {', '.join(structured_data.get('ingredients', []))}
    
    Provide:
    1. Overall recommendation: SAFE (good choice), MODERATE (okay in moderation), or AVOID (nutritional concerns)
    2. 2-3 sentence summary explaining your reasoning
    3. Top 3 specific health concerns or benefits
    4. 2 practical tips for consumers
    
    Base your analysis on current nutritional science and FDA guidelines.
    """
    
    try:
        response = co.generate(
            model='command',
            prompt=prompt,
            max_tokens=300,
            temperature=0.2
        )
        
        ai_text = response.generations[0].text.strip()
        
        # Parse AI response (simplified parsing)
        level = "moderate"  # default
        if "SAFE" in ai_text:
            level = "safe"
        elif "AVOID" in ai_text:
            level = "avoid"
        
        return {
            "level": level,
            "summary": ai_text[:200],  # First part as summary
            "reasons": ["AI-generated comprehensive analysis"],
            "tips": ["Follow AI recommendations above"],
            "aiAnalysis": ai_text
        }
    
    except Exception as e:
        print(f"AI health recommendation error: {e}")
        return None

async def get_nutrition_insights(nutrition_facts: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate key nutrition insights
    """
    insights = []
    
    # Calorie insights
    calories = nutrition_facts.get("calories", 0)
    if calories > 0:
        if calories > 300:
            insights.append({
                "type": "warning",
                "text": f"High calorie content ({calories} cal/serving) - consider portion control"
            })
        elif calories < 150:
            insights.append({
                "type": "positive", 
                "text": f"Moderate calorie content ({calories} cal/serving) fits well in most diets"
            })
    
    # Macro balance insights
    carbs = nutrition_facts.get("carbohydrates", 0)
    protein = nutrition_facts.get("protein", 0)
    fat = nutrition_facts.get("fat", 0)
    
    if carbs + protein + fat > 0:
        carb_pct = (carbs * 4) / (carbs * 4 + protein * 4 + fat * 9) * 100
        protein_pct = (protein * 4) / (carbs * 4 + protein * 4 + fat * 9) * 100
        
        if protein_pct > 25:
            insights.append({
                "type": "positive",
                "text": f"High protein content ({protein}g) supports muscle health and satiety"
            })
        elif protein_pct < 10:
            insights.append({
                "type": "neutral",
                "text": f"Low protein content ({protein}g) - consider pairing with protein sources"
            })
    
    # Sodium insights
    sodium = nutrition_facts.get("sodium", 0)
    sodium_dv = nutrition_facts.get("sodiumDV", 0)
    if sodium_dv > 20:
        insights.append({
            "type": "warning",
            "text": f"High sodium ({sodium}mg, {sodium_dv}% DV) may contribute to hypertension"
        })
    
    # Fiber insights
    fiber = nutrition_facts.get("fiber", 0)
    if fiber >= 5:
        insights.append({
            "type": "positive",
            "text": f"Excellent fiber source ({fiber}g) promotes digestive health"
        })
    
    return insights[:5]  # Limit to 5 insights

def calculate_overall_score(results: Dict[str, Any]) -> int:
    """
    Calculate overall nutritional score (0-100)
    """
    score = 50  # Base score
    
    # Nutrition facts scoring
    nutrition_facts = results.get("nutrition_facts", {})
    
    # Positive factors
    fiber = nutrition_facts.get("fiber", 0)
    protein = nutrition_facts.get("protein", 0)
    
    score += min(20, fiber * 2)  # Up to 20 points for fiber
    score += min(15, protein)    # Up to 15 points for protein
    
    # Negative factors
    sodium = nutrition_facts.get("sodium", 0)
    sugar = nutrition_facts.get("sugar", 0)
    saturated_fat = nutrition_facts.get("saturatedFat", 0)
    
    score -= min(25, sodium / 50)      # Reduce for high sodium
    score -= min(20, sugar / 2)        # Reduce for high sugar
    score -= min(15, saturated_fat * 2) # Reduce for saturated fat
    
    # Ingredient analysis impact
    ingredient_analysis = results.get("ingredient_analysis", {})
    flagged_ingredients = ingredient_analysis.get("flaggedIngredients", [])
    
    for flagged in flagged_ingredients:
        if flagged.get("riskLevel") == "high":
            score -= 15
        elif flagged.get("riskLevel") == "medium":
            score -= 8
    
    # Claim verification impact
    claims = results.get("claim_verification", [])
    for claim in claims:
        if claim.get("status") == "verified":
            score += 3
        elif claim.get("status") == "false":
            score -= 10
        elif claim.get("status") == "misleading":
            score -= 5
    
    return max(0, min(100, int(score)))

def generate_recommendations(results: Dict[str, Any]) -> List[str]:
    """
    Generate actionable recommendations based on analysis
    """
    recommendations = []
    
    nutrition_facts = results.get("nutrition_facts", {})
    ingredient_analysis = results.get("ingredient_analysis", {})
    
    # Sodium recommendations
    sodium = nutrition_facts.get("sodium", 0)
    if sodium > 600:
        recommendations.append("Consider lower-sodium alternatives to support heart health")
    
    # Sugar recommendations  
    sugar = nutrition_facts.get("sugar", 0)
    if sugar > 15:
        recommendations.append("Look for products with less added sugar to reduce diabetes risk")
    
    # Fiber recommendations
    fiber = nutrition_facts.get("fiber", 0)
    if fiber < 3:
        recommendations.append("Add high-fiber foods to your meal to improve digestion")
    
    # Ingredient recommendations
    flagged_ingredients = ingredient_analysis.get("flaggedIngredients", [])
    if len(flagged_ingredients) > 2:
        recommendations.append("Choose products with fewer processed ingredients when possible")
    
    # Allergen recommendations
    allergens = ingredient_analysis.get("allergens", [])
    if allergens:
        recommendations.append(f"Check for allergen warnings: contains {', '.join(allergens[:3])}")
    
    # General recommendations
    if len(recommendations) == 0:
        recommendations.append("This product can be part of a balanced diet when consumed in moderation")
    
    return recommendations[:5]  # Limit to 5 recommendations
