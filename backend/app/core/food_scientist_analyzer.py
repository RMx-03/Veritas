"""
Advanced Food Science Analysis Module
Provides comprehensive nutritional analysis with scientific rigor for food professionals and consumers
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class NutrientDensityLevel(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"  
    MODERATE = "moderate"
    POOR = "poor"
    VERY_POOR = "very_poor"

class ProcessingLevel(Enum):
    UNPROCESSED = "unprocessed"
    MINIMALLY_PROCESSED = "minimally_processed"
    PROCESSED = "processed"
    ULTRA_PROCESSED = "ultra_processed"

@dataclass
class FoodScienceAnalysis:
    """Comprehensive food science analysis results"""
    
    # Core Analysis
    overall_score: int
    recommendation_level: str
    nutrient_density_score: float
    processing_level: ProcessingLevel
    
    # Nutritional Analysis
    macronutrient_balance: Dict[str, float]
    micronutrient_density: Dict[str, float]
    caloric_efficiency: float
    
    # Ingredient Assessment
    beneficial_ingredients: List[str]
    concerning_ingredients: List[str]
    additive_risk_score: int
    allergen_profile: List[str]
    
    # Health Impact
    cardiovascular_impact: str
    metabolic_impact: str  
    digestive_impact: str
    inflammatory_potential: str
    
    # Scientific Insights
    key_findings: List[str]
    evidence_based_benefits: List[str]
    health_concerns: List[str]
    consumption_recommendations: List[str]
    
    # Professional Data
    nova_classification: int
    nutrient_profiling_score: float
    ingredient_complexity_index: float

class FoodScientistAnalyzer:
    """Advanced food analysis with scientific methodology"""
    
    def __init__(self):
        self.harmful_additives = {
            # Preservatives of concern
            'sodium nitrite', 'sodium nitrate', 'bha', 'bht', 'tbhq',
            'potassium bromate', 'sodium benzoate', 'potassium sorbate',
            
            # Artificial colors
            'red dye 40', 'yellow 6', 'blue 1', 'red 3', 'yellow 5',
            'sunset yellow', 'allura red', 'tartrazine',
            
            # Artificial sweeteners
            'aspartame', 'acesulfame potassium', 'sucralose', 'saccharin',
            
            # Trans fats and concerning fats
            'partially hydrogenated', 'trans fat', 'shortening',
            
            # Other concerning additives
            'monosodium glutamate', 'high fructose corn syrup',
            'phosphoric acid', 'sodium phosphate', 'carrageenan'
        }
        
        self.beneficial_ingredients = {
            # Whole grains
            'whole wheat', 'brown rice', 'quinoa', 'oats', 'barley',
            'whole grain', 'steel cut oats',
            
            # Healthy fats
            'olive oil', 'avocado oil', 'coconut oil', 'nuts', 'seeds',
            'omega-3', 'flaxseed', 'chia seeds',
            
            # Proteins
            'organic', 'grass fed', 'free range', 'wild caught',
            'plant protein', 'legumes', 'lentils',
            
            # Functional ingredients
            'probiotics', 'prebiotics', 'fiber', 'antioxidants',
            'turmeric', 'ginger', 'green tea extract'
        }

    def analyze_nova_classification(self, ingredients: List[str]) -> int:
        """Classify food according to NOVA processing levels (1-4)"""
        if not ingredients:
            return 4  # Default to ultra-processed if no ingredients
            
        ingredient_text = ' '.join(ingredients).lower()
        
        # NOVA Group 4 indicators (Ultra-processed)
        ultra_processed_indicators = [
            'high fructose corn syrup', 'hydrogenated', 'modified starch',
            'maltodextrin', 'dextrose', 'fructose', 'glucose syrup',
            'artificial', 'natural flavor', 'preservative', 'emulsifier',
            'stabilizer', 'thickener', 'colorant', 'sweetener'
        ]
        
        # NOVA Group 3 indicators (Processed)
        processed_indicators = [
            'oil', 'sugar', 'salt', 'vinegar', 'flour', 'butter'
        ]
        
        ultra_processed_count = sum(1 for indicator in ultra_processed_indicators 
                                  if indicator in ingredient_text)
        processed_count = sum(1 for indicator in processed_indicators 
                            if indicator in ingredient_text)
        
        if ultra_processed_count >= 3:
            return 4  # Ultra-processed
        elif ultra_processed_count >= 1:
            return 3  # Processed
        elif processed_count >= 2:
            return 2  # Processed culinary ingredients
        else:
            return 1  # Unprocessed or minimally processed

    def calculate_nutrient_density(self, nutrition_facts: Dict[str, Any]) -> float:
        """Calculate nutrient density score based on nutrients per calorie"""
        calories = nutrition_facts.get('calories', 0)
        if calories == 0:
            return 0.0
            
        # Key nutrients for density calculation
        protein = nutrition_facts.get('protein', 0) or 0
        fiber = nutrition_facts.get('dietary_fiber', 0) or 0
        vitamin_c = nutrition_facts.get('vitamin_c', 0) or 0
        calcium = nutrition_facts.get('calcium', 0) or 0
        iron = nutrition_facts.get('iron', 0) or 0
        
        # Calculate density score (nutrients per 100 calories)
        nutrient_score = (
            (protein * 4) +      # Protein calories
            (fiber * 2) +        # Fiber importance
            (vitamin_c * 0.1) +  # Vitamin C (mg)
            (calcium * 0.01) +   # Calcium (mg) 
            (iron * 1)           # Iron (mg)
        )
        
        density = (nutrient_score / calories) * 100
        return min(100.0, density)  # Cap at 100

    def assess_macronutrient_balance(self, nutrition_facts: Dict[str, Any]) -> Dict[str, float]:
        """Analyze macronutrient distribution and balance"""
        calories = nutrition_facts.get('calories', 0)
        if calories == 0:
            return {'protein_percent': 0, 'carb_percent': 0, 'fat_percent': 0, 'balance_score': 0}
        
        protein = (nutrition_facts.get('protein', 0) or 0) * 4  # 4 cal/g
        total_fat = (nutrition_facts.get('total_fat', 0) or 0) * 9  # 9 cal/g
        total_carbs = (nutrition_facts.get('total_carbs', 0) or 0) * 4  # 4 cal/g
        
        # Calculate percentages
        protein_percent = (protein / calories) * 100 if calories > 0 else 0
        fat_percent = (total_fat / calories) * 100 if calories > 0 else 0
        carb_percent = (total_carbs / calories) * 100 if calories > 0 else 0
        
        # Assess balance (ideal ranges: P:10-35%, F:20-35%, C:45-65%)
        balance_score = 100
        if protein_percent < 10 or protein_percent > 35:
            balance_score -= 20
        if fat_percent < 20 or fat_percent > 35:
            balance_score -= 20
        if carb_percent < 45 or carb_percent > 65:
            balance_score -= 20
            
        return {
            'protein_percent': round(protein_percent, 1),
            'carb_percent': round(carb_percent, 1), 
            'fat_percent': round(fat_percent, 1),
            'balance_score': max(0, balance_score)
        }

    def analyze_ingredient_risks(self, ingredients: List[str]) -> Tuple[List[str], List[str], int]:
        """Analyze ingredients for beneficial compounds and health risks"""
        if not ingredients:
            return [], [], 0
            
        beneficial = []
        concerning = []
        risk_score = 0
        
        ingredient_text = ' '.join(str(ing) for ing in ingredients).lower()
        
        # Find beneficial ingredients
        for ingredient in self.beneficial_ingredients:
            if ingredient in ingredient_text:
                beneficial.append(ingredient.title())
        
        # Find concerning ingredients
        for additive in self.harmful_additives:
            if additive in ingredient_text:
                concerning.append(additive.title())
                if additive in ['sodium nitrite', 'bha', 'bht', 'red dye 40']:
                    risk_score += 15  # High concern additives
                else:
                    risk_score += 5   # Moderate concern additives
        
        # Additional risk factors
        if 'high fructose corn syrup' in ingredient_text:
            risk_score += 20
        if 'partially hydrogenated' in ingredient_text:
            risk_score += 25
        if isinstance(ingredients, list) and len(ingredients) > 20:  # Highly processed indicator
            risk_score += 10
            
        return beneficial[:10], concerning[:10], min(100, risk_score)

    def assess_health_impacts(self, nutrition_facts: Dict[str, Any], ingredients: List[str]) -> Dict[str, str]:
        """Assess potential health impacts across major body systems"""
        
        sodium = nutrition_facts.get('sodium', 0) or 0
        saturated_fat = nutrition_facts.get('saturated_fat', 0) or 0
        total_sugars = nutrition_facts.get('total_sugars', 0) or 0
        fiber = nutrition_facts.get('dietary_fiber', 0) or 0
        
        # Cardiovascular assessment
        cv_risk_factors = []
        if sodium > 500:  # High sodium
            cv_risk_factors.append("high sodium")
        if saturated_fat > 5:  # High saturated fat
            cv_risk_factors.append("high saturated fat")
        
        cv_impact = "LOW RISK" if not cv_risk_factors else f"MODERATE RISK ({', '.join(cv_risk_factors)})"
        if len(cv_risk_factors) >= 2:
            cv_impact = cv_impact.replace("MODERATE", "HIGH")
        
        # Metabolic assessment
        metabolic_concerns = []
        if total_sugars > 15:
            metabolic_concerns.append("high sugar content")
        if isinstance(ingredients, list) and 'high fructose corn syrup' in ' '.join(str(ing) for ing in ingredients).lower():
            metabolic_concerns.append("HFCS concerns")
            
        metabolic_impact = "FAVORABLE" if not metabolic_concerns else f"CONCERNING ({', '.join(metabolic_concerns)})"
        
        # Digestive assessment  
        digestive_impact = "SUPPORTIVE" if fiber >= 3 else "NEUTRAL"
        if isinstance(ingredients, list) and 'artificial sweetener' in ' '.join(str(ing) for ing in ingredients).lower():
            digestive_impact = "POTENTIALLY DISRUPTIVE"
            
        # Inflammatory potential
        inflammatory_ingredients = ['omega-3', 'turmeric', 'ginger']
        ingredient_text_safe = ' '.join(str(ing) for ing in ingredients).lower() if isinstance(ingredients, list) else ''
        
        anti_inflammatory_count = sum(1 for ing in inflammatory_ingredients 
                                    if ing in ingredient_text_safe)
        
        pro_inflammatory_factors = []
        if 'trans fat' in ingredient_text_safe:
            pro_inflammatory_factors.append("trans fats")
        if any(additive in ingredient_text_safe 
               for additive in ['red dye 40', 'yellow 6', 'blue 1']):
            pro_inflammatory_factors.append("artificial colors")
            
        if anti_inflammatory_count > len(pro_inflammatory_factors):
            inflammatory_potential = "ANTI-INFLAMMATORY"
        elif pro_inflammatory_factors:
            inflammatory_potential = f"PRO-INFLAMMATORY ({', '.join(pro_inflammatory_factors)})"
        else:
            inflammatory_potential = "NEUTRAL"
        
        return {
            'cardiovascular_impact': cv_impact,
            'metabolic_impact': metabolic_impact,
            'digestive_impact': digestive_impact,
            'inflammatory_potential': inflammatory_potential
        }

    def generate_scientific_insights(self, 
                                   nutrition_facts: Dict[str, Any], 
                                   ingredients: List[str],
                                   nova_class: int,
                                   nutrient_density: float) -> Tuple[List[str], List[str], List[str]]:
        """Generate comprehensive evidence-based insights, benefits, and concerns"""
        
        findings = []
        benefits = []
        concerns = []
        
        # Enhanced nutrient density analysis
        if nutrient_density > 20:
            findings.append(f"Exceptional nutrient density ({nutrient_density:.1f}) - among top 10% of foods for nutritional value per calorie")
            benefits.append("Outstanding nutritional efficiency - provides maximum nutrients with minimal calories")
        elif nutrient_density > 15:
            findings.append(f"High nutrient density score ({nutrient_density:.1f}) indicates excellent nutritional value per calorie")
            benefits.append("Nutrient-dense food providing excellent nutritional bang for your caloric buck")
        elif nutrient_density > 8:
            findings.append(f"Moderate nutrient density ({nutrient_density:.1f}) provides reasonable nutritional value")
            benefits.append("Decent nutritional value relative to calorie content")
        elif nutrient_density < 5:
            findings.append(f"Low nutrient density ({nutrient_density:.1f}) suggests limited nutritional benefits")
            concerns.append("Poor nutritional value relative to calorie content - mostly empty calories")
        
        # Enhanced processing level insights with health implications
        if nova_class == 4:
            findings.append("NOVA Group 4 classification indicates ultra-processed food with industrial formulation")
            concerns.append("Ultra-processed foods linked to increased obesity, diabetes, and cardiovascular disease risk")
            concerns.append("May contain additives and preservatives with limited long-term safety data")
        elif nova_class == 3:
            findings.append("NOVA Group 3 classification indicates processed food with added ingredients")
            concerns.append("Moderate processing may reduce some nutritional benefits of original ingredients")
        elif nova_class == 2:
            findings.append("NOVA Group 2 classification indicates processed culinary ingredients")
            benefits.append("Minimally processed with basic culinary modifications")
        elif nova_class == 1:
            findings.append("NOVA Group 1 classification indicates unprocessed or minimally processed whole food")
            benefits.append("Whole food with minimal processing retains natural nutritional profile")
        
        # Enhanced macronutrient analysis
        protein = nutrition_facts.get('protein', 0) or 0
        fiber = nutrition_facts.get('dietary_fiber', 0) or 0
        calories = nutrition_facts.get('calories', 0) or 0
        
        if protein > 15:
            benefits.append(f"Excellent protein content ({protein}g) supports muscle synthesis and metabolic health")
        elif protein > 10:
            benefits.append(f"Good protein content ({protein}g) supports muscle maintenance and satiety")
        elif protein > 5:
            findings.append(f"Moderate protein content ({protein}g) contributes to daily protein needs")
        else:
            concerns.append("Low protein content - consider pairing with protein-rich foods")
        
        # Fiber analysis with specific health benefits
        if fiber > 10:
            benefits.append(f"Exceptional fiber content ({fiber}g) promotes gut health, blood sugar control, and cardiovascular health")
        elif fiber > 5:
            benefits.append(f"High fiber content ({fiber}g) promotes digestive health and blood sugar control")
        elif fiber > 3:
            findings.append(f"Moderate fiber content ({fiber}g) contributes to daily fiber intake")
        elif fiber < 2:
            concerns.append("Very low fiber content provides minimal digestive and metabolic benefits")
        
        # Enhanced sodium assessment with cardiovascular risk
        sodium = nutrition_facts.get('sodium', 0) or 0
        sodium_per_calorie = (sodium / calories * 100) if calories > 0 else 0
        
        if sodium > 800:
            concerns.append(f"Very high sodium content ({sodium}mg) significantly increases hypertension and stroke risk")
            findings.append("Sodium level exceeds WHO recommended daily maximum in single serving")
        elif sodium > 600:
            concerns.append(f"High sodium content ({sodium}mg) may contribute to hypertension and cardiovascular risk")
            findings.append("Exceeds heart-healthy sodium recommendations")
        elif sodium > 300:
            findings.append(f"Moderate sodium content ({sodium}mg) - monitor total daily intake")
        elif sodium < 140:
            benefits.append(f"Low sodium content ({sodium}mg) supports cardiovascular health")
        
        # Enhanced sugar analysis with metabolic implications
        total_sugars = nutrition_facts.get('total_sugars', 0) or 0
        added_sugars = nutrition_facts.get('added_sugars', 0) or 0
        
        if added_sugars > 15:
            concerns.append(f"Very high added sugar content ({added_sugars}g) significantly increases diabetes and obesity risk")
            findings.append("Added sugars exceed WHO recommended daily maximum")
        elif added_sugars > 10:
            concerns.append(f"High added sugar content ({added_sugars}g) linked to metabolic health issues")
            findings.append("Added sugars exceed recommended daily intake guidelines")
        elif added_sugars > 5:
            findings.append(f"Moderate added sugar content ({added_sugars}g) - limit frequency of consumption")
        elif added_sugars <= 1 and total_sugars <= 5:
            benefits.append("Low sugar content supports stable blood glucose levels")
        
        # Saturated fat analysis
        sat_fat = nutrition_facts.get('saturated_fat', 0) or 0
        if sat_fat > 10:
            concerns.append(f"High saturated fat content ({sat_fat}g) may increase LDL cholesterol and heart disease risk")
        elif sat_fat > 5:
            findings.append(f"Moderate saturated fat content ({sat_fat}g) - balance with unsaturated fats")
        
        # Trans fat analysis
        trans_fat = nutrition_facts.get('trans_fat', 0) or 0
        if trans_fat > 0:
            concerns.append(f"Contains trans fats ({trans_fat}g) - strongly linked to cardiovascular disease")
        
        return findings[:6], benefits[:6], concerns[:6]

    def generate_consumption_recommendations(self, 
                                           overall_score: int,
                                           health_impacts: Dict[str, str],
                                           concerning_ingredients: List[str]) -> List[str]:
        """Generate evidence-based consumption recommendations"""
        
        recommendations = []
        
        if overall_score >= 80:
            recommendations.append("Excellent choice - can be consumed regularly as part of balanced diet")
            recommendations.append("Consider as staple food option with high nutritional value")
        elif overall_score >= 60:
            recommendations.append("Good option - suitable for regular moderate consumption")
            recommendations.append("Pair with nutrient-dense foods to maximize nutritional benefits")
        elif overall_score >= 40:
            recommendations.append("Consume occasionally - limit to 2-3 times per week maximum")
            recommendations.append("Consider healthier alternatives when possible")
        else:
            recommendations.append("Limit consumption - reserve for special occasions only")
            recommendations.append("Seek whole food alternatives for better health outcomes")
        
        # Specific recommendations based on health impacts
        if "HIGH RISK" in health_impacts.get('cardiovascular_impact', ''):
            recommendations.append("Monitor blood pressure if consuming regularly due to cardiovascular concerns")
        
        if "CONCERNING" in health_impacts.get('metabolic_impact', ''):
            recommendations.append("Consider timing consumption around physical activity to mitigate metabolic impact")
            
        if concerning_ingredients:
            recommendations.append(f"Be aware of concerning ingredients: {', '.join(concerning_ingredients[:3])}")
        
        return recommendations[:4]

    async def analyze_food_product(self, 
                                 nutrition_facts: Dict[str, Any], 
                                 ingredients: List[str],
                                 raw_text: str = "") -> FoodScienceAnalysis:
        """Comprehensive food science analysis"""
        
        # Core calculations
        nutrient_density = self.calculate_nutrient_density(nutrition_facts)
        nova_class = self.analyze_nova_classification(ingredients)
        macro_balance = self.assess_macronutrient_balance(nutrition_facts)
        beneficial_ing, concerning_ing, additive_risk = self.analyze_ingredient_risks(ingredients)
        health_impacts = self.assess_health_impacts(nutrition_facts, ingredients)
        
        # Overall scoring
        base_score = 50
        base_score += min(30, nutrient_density * 2)  # Nutrient density contribution
        base_score -= (nova_class - 1) * 10          # Processing penalty
        base_score += macro_balance['balance_score'] * 0.2  # Macronutrient balance
        base_score -= additive_risk * 0.3            # Additive penalty
        
        overall_score = max(0, min(100, int(base_score)))
        
        # Recommendation level
        if overall_score >= 80:
            rec_level = "EXCELLENT"
        elif overall_score >= 65:
            rec_level = "GOOD"
        elif overall_score >= 45:
            rec_level = "MODERATE"
        elif overall_score >= 25:
            rec_level = "POOR"
        else:
            rec_level = "AVOID"
        
        # Generate insights
        findings, benefits, concerns = self.generate_scientific_insights(
            nutrition_facts, ingredients, nova_class, nutrient_density
        )
        
        recommendations = self.generate_consumption_recommendations(
            overall_score, health_impacts, concerning_ing
        )
        
        # Calculate additional metrics
        ingredient_complexity = len(ingredients) / 5.0  # Complexity index
        nutrient_profiling = (nutrient_density + macro_balance['balance_score']) / 2
        
        return FoodScienceAnalysis(
            overall_score=overall_score,
            recommendation_level=rec_level,
            nutrient_density_score=round(nutrient_density, 1),
            processing_level=ProcessingLevel.ULTRA_PROCESSED if nova_class == 4 else ProcessingLevel.PROCESSED,
            
            macronutrient_balance=macro_balance,
            micronutrient_density={
                'vitamin_c': nutrition_facts.get('vitamin_c', 0) or 0,
                'calcium': nutrition_facts.get('calcium', 0) or 0,
                'iron': nutrition_facts.get('iron', 0) or 0,
            },
            caloric_efficiency=(
                round(
                    nutrient_density / (((nutrition_facts.get('calories') or 0) / 100)),
                    2
                ) if (nutrition_facts.get('calories') or 0) > 0 else 0.0
            ),
            
            beneficial_ingredients=beneficial_ing,
            concerning_ingredients=concerning_ing,
            additive_risk_score=additive_risk,
            allergen_profile=[], # Would need allergen detection logic
            
            cardiovascular_impact=health_impacts['cardiovascular_impact'],
            metabolic_impact=health_impacts['metabolic_impact'],
            digestive_impact=health_impacts['digestive_impact'],
            inflammatory_potential=health_impacts['inflammatory_potential'],
            
            key_findings=findings,
            evidence_based_benefits=benefits,
            health_concerns=concerns,
            consumption_recommendations=recommendations,
            
            nova_classification=nova_class,
            nutrient_profiling_score=round(nutrient_profiling, 1),
            ingredient_complexity_index=round(ingredient_complexity, 1)
        )

# Global analyzer instance
food_scientist = FoodScientistAnalyzer()

async def analyze_with_food_science(nutrition_facts: Dict[str, Any], 
                                  ingredients: List[str],
                                  raw_text: str = "") -> Dict[str, Any]:
    """Main entry point for scientific food analysis"""
    
    analysis = await food_scientist.analyze_food_product(nutrition_facts, ingredients, raw_text)
    
    # Convert to API response format
    return {
        "overall_score": analysis.overall_score,
        "recommendation_level": analysis.recommendation_level,
        "scientific_analysis": {
            "nutrient_density_score": analysis.nutrient_density_score,
            "processing_level": analysis.processing_level.value,
            "nova_classification": analysis.nova_classification,
            "macronutrient_balance": analysis.macronutrient_balance,
            "additive_risk_score": analysis.additive_risk_score
        },
        "health_impact_assessment": {
            "cardiovascular": analysis.cardiovascular_impact,
            "metabolic": analysis.metabolic_impact,
            "digestive": analysis.digestive_impact,
            "inflammatory": analysis.inflammatory_potential
        },
        "ingredient_analysis": {
            "beneficial": analysis.beneficial_ingredients,
            "concerning": analysis.concerning_ingredients,
            "complexity_index": analysis.ingredient_complexity_index
        },
        "evidence_based_insights": {
            "key_findings": analysis.key_findings,
            "health_benefits": analysis.evidence_based_benefits,
            "health_concerns": analysis.health_concerns,
            "consumption_recommendations": analysis.consumption_recommendations
        },
        "professional_metrics": {
            "nutrient_profiling_score": analysis.nutrient_profiling_score,
            "caloric_efficiency": analysis.caloric_efficiency
        }
    }
