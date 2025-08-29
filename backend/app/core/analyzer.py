import asyncio
import json
import logging
import os
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv
from .food_scientist_analyzer import analyze_with_food_science

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# API Configuration
USDA_API_KEY = os.getenv("USDA_API_KEY")  # Optional, USDA has public endpoints

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME")

# Initialize OpenRouter client
or_client: Optional[AsyncOpenAI] = None
if OPENROUTER_API_KEY:
    default_headers = {}
    if OPENROUTER_SITE_URL:
        default_headers["HTTP-Referer"] = OPENROUTER_SITE_URL
    if OPENROUTER_APP_NAME:
        default_headers["X-Title"] = OPENROUTER_APP_NAME
    or_client = AsyncOpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
        default_headers=default_headers or None
    )

# Knowledge base URLs
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
OPENFOODFACTS_URL = "https://world.openfoodfacts.org/api/v0/product"

async def analyze_nutrition_data(structured_data: Dict[str, Any], raw_text: str = "") -> Dict[str, Any]:
    """
    Comprehensive nutrition analysis pipeline with scientific insights
    """
    logger.info("Starting comprehensive food science analysis")
    
    # Extract basic info
    nutrition_facts = structured_data.get('nutrition_facts', {})
    ingredients = structured_data.get('ingredients', [])
    claims = structured_data.get('claims', [])
    
    try:
        # Get comprehensive scientific analysis
        logger.info("Starting scientific analysis with food science module")
        logger.info(f"Input nutrition_facts: {nutrition_facts}")
        logger.info(f"Input ingredients: {ingredients}")
        scientific_analysis = await analyze_with_food_science(nutrition_facts, ingredients, raw_text)
        logger.info(f"Scientific analysis completed: {type(scientific_analysis)}")
        logger.info(f"Scientific analysis keys: {scientific_analysis.keys() if scientific_analysis else 'None'}")
        if scientific_analysis:
            logger.info(f"Overall score: {scientific_analysis.get('overall_score')}")
            logger.info(f"Recommendation level: {scientific_analysis.get('recommendation_level')}")
        
        # Run additional analysis tasks concurrently
        additional_tasks = [
            verify_health_claims(claims, nutrition_facts),
            get_ai_health_recommendation(structured_data, raw_text),
        ]
        
        results = await asyncio.gather(*additional_tasks, return_exceptions=True)
        claim_verification = results[0] if not isinstance(results[0], Exception) else {"status": "error", "verified_claims": [], "warnings": []}
        ai_recommendation = results[1] if not isinstance(results[1], Exception) else None
        
        # Log AI recommendation result
        logger.info(f"AI recommendation result: {type(ai_recommendation)}")
        if ai_recommendation:
            logger.info(f"AI recommendation keys: {ai_recommendation.keys()}")
        else:
            logger.warning("AI recommendation failed or returned None")
        
        # Compile comprehensive analysis results with scientific insights - structured for frontend
        analysis_result = {
            "nutrition_facts": nutrition_facts,
            "scientific_analysis": {
                "nutrient_density_score": scientific_analysis.get('scientific_analysis', {}).get('nutrient_density_score', 0),
                "processing_level": scientific_analysis.get('scientific_analysis', {}).get('processing_level', 'ultra_processed'),
                "nova_classification": scientific_analysis.get('scientific_analysis', {}).get('nova_classification', 4),
                "macronutrient_balance": scientific_analysis.get('macronutrient_balance', {}),
                "additive_risk_score": scientific_analysis.get('scientific_analysis', {}).get('additive_risk_score', 0),
                "ingredient_complexity_index": scientific_analysis.get('ingredient_analysis', {}).get('complexity_index', 0),
                "evidence_based_insights": scientific_analysis.get('evidence_based_insights', {})
            },
            "ingredients_analysis": scientific_analysis.get('ingredient_analysis', {}),
            "health_score": {
                "score": scientific_analysis.get('overall_score', 50),
                "level": scientific_analysis.get('recommendation_level', 'moderate').lower(),
                "factors": scientific_analysis.get('evidence_based_insights', {}).get('key_findings', [])
            },
            "health_impact_assessment": scientific_analysis.get('health_impact_assessment', {}),
            "claim_verification": claim_verification,
            "key_insights": scientific_analysis.get('evidence_based_insights', {}).get('key_findings', []),
            "recommendations": scientific_analysis.get('evidence_based_insights', {}).get('consumption_recommendations', []),
            "ai_recommendation": ai_recommendation,
            "analysis_timestamp": asyncio.get_event_loop().time(),
            "processing_notes": {
                "ocr_confidence": "high" if len(raw_text) > 100 else "medium",
                "data_completeness": len(nutrition_facts) / 10.0 * 100,
                "analysis_version": "v3.0_scientific",
                "nova_classification": scientific_analysis.get('scientific_analysis', {}).get('nova_classification', 4),
                "nutrient_density": scientific_analysis.get('scientific_analysis', {}).get('nutrient_density_score', 0)
            }
        }
        
        logger.info(f"Scientific analysis completed with score: {scientific_analysis.get('overall_score', 'N/A')}")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error in scientific nutrition analysis: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        # Fallback to basic analysis if scientific analysis fails
        try:
            # Enhanced fallback analysis when scientific analysis fails
            ingredient_analysis = {
                "beneficial": [ing for ing in ingredients if any(good in ing.lower() for good in ['organic', 'whole grain', 'natural'])],
                "concerning": [ing for ing in ingredients if any(bad in ing.lower() for bad in ['artificial', 'preservative', 'dye', 'high fructose'])],
                "additives": [ing for ing in ingredients if any(add in ing.lower() for add in ['sodium', 'phosphate', 'extract', 'flavor'])]
            }
            
            calories = nutrition_facts.get('calories', 0)
            total_fat = nutrition_facts.get('total_fat', 0)
            
            key_insights = []
            if calories > 250:
                key_insights.append("High calorie content - consume in moderation")
            if total_fat > 15:
                key_insights.append("High fat content detected")
            if len(ingredients) > 10:
                key_insights.append("Highly processed product with many ingredients")
            
            # Add some basic ingredient analysis
            if any('sugar' in ing.lower() for ing in ingredients):
                key_insights.append("Contains added sugars")
            if any('butter' in ing.lower() for ing in ingredients):
                key_insights.append("Contains dairy ingredients")
            
            if not key_insights:
                key_insights = ["Basic nutritional analysis completed", "Consider portion control"]
            
            # Calculate basic score
            score = 60  # Start with moderate score
            if calories > 300: score -= 20
            if total_fat > 20: score -= 15
            if len(ingredients) > 15: score -= 10
            score = max(0, min(100, score))
            
            return {
                "nutrition_facts": nutrition_facts,
                "ingredients_analysis": ingredient_analysis,
                "health_score": {
                    "score": score,
                    "level": "moderate" if score >= 40 else "poor",
                    "factors": key_insights
                },
                "key_insights": key_insights,
                "recommendations": ["Consume in moderation", "Consider healthier alternatives"],
                "error": "Scientific analysis failed - using enhanced fallback",
                "analysis_timestamp": asyncio.get_event_loop().time(),
                "processing_notes": {
                    "analysis_type": "enhanced_fallback",
                    "data_completeness": len(nutrition_facts) / 10.0 * 100,
                    "ocr_confidence": "medium"
                }
            }
        except Exception as fallback_error:
            logger.error(f"Fallback analysis also failed: {str(fallback_error)}")
            return {
                "error": "Complete analysis failure",
                "message": str(e),
                "nutrition_facts": nutrition_facts,
                "basic_info": {
                    "ingredients_count": len(ingredients),
                    "claims_count": len(claims),
                    "status": "failed"
                }
            }

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
    
    # Use AI for complex claims if OpenRouter is available
    elif or_client:
        try:
            ai_verification = await get_ai_claim_verification(claim, nutrition_facts)
            verification.update(ai_verification)
        except Exception as e:
            print(f"AI verification error: {e}")
    
    return verification

async def get_ai_claim_verification(claim: str, nutrition_facts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use OpenRouter (Chat Completions) to verify complex health claims
    """
    if not or_client:
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
        response = await or_client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "You are a nutrition scientist who verifies product claims against nutrition facts and FDA guidelines."},
                {"role": "user", "content": prompt.strip()},
            ],
            max_tokens=200,
            temperature=0.3,
        )
        ai_response = response.choices[0].message.content.strip()

        # Parse AI response to determine status
        lower = ai_response.lower()
        if "verified" in lower or "accurate" in lower:
            status = "verified"
        elif "misleading" in lower or "deceptive" in lower:
            status = "misleading"
        elif "false" in lower or "contradicted" in lower:
            status = "false"
        else:
            status = "unknown"

        return {
            "status": status,
            "explanation": ai_response,
            "source": "AI analysis (OpenRouter)",
        }

    except Exception as e:
        print(f"[ANALYZER] OpenRouter error: {e}")
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
    if or_client and len(raw_text) > 50:
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
    Generate comprehensive AI-powered food science analysis via OpenRouter
    """
    if not or_client:
        return None

    nutrition_facts = structured_data.get('nutrition_facts', {})
    ingredients = structured_data.get('ingredients', [])
    
    # Enhanced context for scientific analysis
    serving_size = nutrition_facts.get('serving_size', 'Unknown')
    calories = nutrition_facts.get('calories', 0)
    total_fat = nutrition_facts.get('total_fat', 0)
    saturated_fat = nutrition_facts.get('saturated_fat', 0)
    sodium = nutrition_facts.get('sodium', 0)
    total_carbs = nutrition_facts.get('total_carbs', 0)
    fiber = nutrition_facts.get('dietary_fiber', 0)
    sugars = nutrition_facts.get('total_sugars', 0)
    protein = nutrition_facts.get('protein', 0)
    
    prompt = f"""
    As a PhD food scientist and registered dietitian specializing in nutritional biochemistry, conduct a comprehensive scientific analysis of this food product using evidence-based nutritional science principles.

    PRODUCT NUTRITIONAL PROFILE:
    Serving Size: {serving_size}
    Calories: {calories}
    Total Fat: {total_fat}g | Saturated Fat: {saturated_fat}g
    Sodium: {sodium}mg | Total Carbs: {total_carbs}g
    Dietary Fiber: {fiber}g | Total Sugars: {sugars}g | Protein: {protein}g
    
    COMPLETE NUTRITION DATA:
    {json.dumps(nutrition_facts, indent=2)}
    
    INGREDIENT LIST: {', '.join(ingredients[:20])}
    
    PERFORM DETAILED SCIENTIFIC ANALYSIS:
    
    1. NUTRIENT DENSITY EVALUATION:
    - Calculate nutrient density score (essential nutrients per 100 kcal)
    - Analyze macronutrient distribution vs. Acceptable Macronutrient Distribution Ranges (AMDR)
    - Assess micronutrient contributions to Daily Value requirements
    - Compare to USDA Dietary Guidelines and WHO recommendations
    
    2. BIOCHEMICAL IMPACT ASSESSMENT:
    - Glycemic response prediction based on carbohydrate profile and fiber content
    - Lipid metabolism implications from fat composition
    - Protein quality assessment (amino acid completeness if determinable)
    - Sodium impact on blood pressure and cardiovascular health
    
    3. NOVA FOOD CLASSIFICATION & PROCESSING ANALYSIS:
    - Classify product using NOVA system (unprocessed, processed culinary, processed, ultra-processed)
    - Identify ultra-processed ingredients and additives with health implications
    - Analyze preservation methods and their nutritional impact
    - Evaluate artificial additives, colors, flavors, and their safety profiles
    
    4. PATHOPHYSIOLOGICAL CONSIDERATIONS:
    - Cardiovascular disease risk factors (saturated fat, trans fat, sodium levels)
    - Diabetes/metabolic syndrome implications (sugar content, refined carbs, fiber)
    - Inflammation potential (omega-6/omega-3 ratios if applicable, processed ingredients)
    - Digestive health impact (fiber content, prebiotic potential, artificial ingredients)
    
    5. POPULATION-SPECIFIC RECOMMENDATIONS:
    - Suitability for children, adults, elderly populations
    - Considerations for diabetes, hypertension, cardiovascular disease
    - Athletic/active lifestyle compatibility
    - Weight management implications
    
    6. SCIENTIFIC EVIDENCE & REGULATORY COMPLIANCE:
    - Reference peer-reviewed nutritional research supporting analysis
    - FDA/USDA regulatory compliance assessment
    - Comparison to dietary pattern recommendations (Mediterranean, DASH, etc.)
    - Long-term epidemiological health outcomes from similar food patterns
    
    7. QUANTITATIVE HEALTH SCORE: Rate 1-100 (100=optimal nutrition)
    
    8. EVIDENCE-BASED RECOMMENDATIONS:
    - Optimal consumption frequency and portion size
    - Synergistic food pairings to enhance nutritional value
    - Healthier product alternatives with specific improvements needed
    - Meal planning context for optimal health benefits
    
    REQUIRED OUTPUT FORMAT:
    Structure your response with clear scientific headings and quantitative data where possible. Include specific nutritional biochemistry terminology. Reference established nutritional guidelines and research. Provide actionable, evidence-based recommendations suitable for both healthcare professionals and informed consumers.
    
    Focus on delivering the most comprehensive, scientifically rigorous nutritional analysis possible.
    """

    try:
        logger.info(f"Making OpenRouter API call with model: {OPENROUTER_MODEL}")
        response = await or_client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "You are a PhD-level food scientist and registered dietitian with 15+ years of experience in nutritional biochemistry, food technology, and public health nutrition. You specialize in evidence-based nutritional analysis, NOVA food classification, and pathophysiological impacts of food consumption. Provide comprehensive, quantitative, scientifically rigorous analysis with specific references to nutritional guidelines and research where applicable."},
                {"role": "user", "content": prompt.strip()},
            ],
            max_tokens=2000,  # Significantly increased for comprehensive analysis
            temperature=0.1,
        )
        logger.info("OpenRouter API call successful")

        ai_text = response.choices[0].message.content.strip()

        # Parse AI response into structured format
        level = "moderate"  # default
        if any(word in ai_text.upper() for word in ["EXCELLENT", "GOOD"]):
            level = "good"
        elif any(word in ai_text.upper() for word in ["POOR", "AVOID"]):
            level = "avoid"
        elif "MODERATE" in ai_text.upper():
            level = "moderate"

        # Extract key insights from AI response
        lines = ai_text.split('\n')
        insights = []
        tips = []
        concerns = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                if any(word in line.lower() for word in ['benefit', 'positive', 'good', 'healthy']):
                    insights.append(line)
                elif any(word in line.lower() for word in ['concern', 'risk', 'avoid', 'harmful']):
                    concerns.append(line)
                elif any(word in line.lower() for word in ['recommend', 'suggest', 'should', 'consider']):
                    tips.append(line)
        
        return {
            "level": level,
            "summary": ai_text[:300] if len(ai_text) > 300 else ai_text,
            "reasons": concerns[:3] if concerns else ["AI analysis completed"],
            "tips": tips[:2] if tips else ["Consume in moderation", "Consider healthier alternatives"],
            "insights": insights[:3] if insights else [],
            "aiAnalysis": ai_text,
        }

    except Exception as e:
        logger.error(f"AI health recommendation error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
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
