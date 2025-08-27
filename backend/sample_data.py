"""
Sample data for testing Veritas API
Contains mock nutrition data and test cases
"""

# Sample extracted text from OCR (simulating food label reading)
SAMPLE_NUTRITION_LABEL_TEXT = """
Nutrition Facts
Serving Size 1 cup (240ml)
Servings Per Container 2

Calories 150

Total Fat 3g                     4%
  Saturated Fat 1g              5%
  Trans Fat 0g
Cholesterol 5mg                  2%
Sodium 200mg                     9%
Total Carbohydrate 25g           9%
  Dietary Fiber 3g              12%
  Total Sugars 12g
    Added Sugars 10g            20%
Protein 8g

Vitamin C 15mg                  17%
Calcium 300mg                   23%
Iron 2mg                        11%

INGREDIENTS: Milk, Sugar, Cocoa, Natural Vanilla Flavor, 
Carrageenan, Vitamin A Palmitate, Vitamin D3

CONTAINS: Milk

No Artificial Colors
Low Fat
Good Source of Calcium
"""

SAMPLE_CEREAL_LABEL_TEXT = """
Nutrition Facts
Serving Size 3/4 cup (30g)
Servings Per Container about 12

Calories 110

Total Fat 1g                     1%
  Saturated Fat 0g               0%
Cholesterol 0mg                  0%
Sodium 160mg                     7%
Total Carbohydrate 23g           8%
  Dietary Fiber 5g              18%
  Total Sugars 3g
    Added Sugars 0g              0%
Protein 3g

Iron 8mg                        45%
Vitamin B6 0.5mg                25%
Folic Acid 100mcg               25%

INGREDIENTS: Whole Grain Wheat, Wheat Bran, Sugar, Salt, 
Natural Flavor, Vitamins and Minerals

High Fiber
Whole Grain
No Artificial Preservatives
"""

SAMPLE_PROCESSED_FOOD_TEXT = """
Nutrition Facts  
Serving Size 1 package (85g)
Servings Per Container 1

Calories 380

Total Fat 18g                   23%
  Saturated Fat 8g              40%
  Trans Fat 0.5g
Cholesterol 35mg                12%
Sodium 950mg                    41%
Total Carbohydrate 42g          15%
  Dietary Fiber 1g               4%
  Total Sugars 6g
    Added Sugars 4g              8%
Protein 12g

INGREDIENTS: Enriched Flour, Water, Cheese (Milk, Salt, Enzymes), 
Palm Oil, High Fructose Corn Syrup, Salt, Monosodium Glutamate, 
Sodium Nitrite, Artificial Colors (Red 40, Yellow 6), 
Partially Hydrogenated Soybean Oil, Sodium Benzoate

CONTAINS: Wheat, Milk, Soy
"""

# Mock analysis results for testing UI components
MOCK_ANALYSIS_RESULTS = {
    "healthy_product": {
        "analysisId": "test-001",
        "timestamp": "2025-08-26T03:30:00Z",
        "extractedText": SAMPLE_NUTRITION_LABEL_TEXT,
        "nutritionFacts": {
            "servingSize": "1 cup (240ml)",
            "servingsPerContainer": 2,
            "calories": 150,
            "fat": 3,
            "fatDV": 4,
            "saturatedFat": 1,
            "saturatedFatDV": 5,
            "cholesterol": 5,
            "cholesterolDV": 2,
            "sodium": 200,
            "sodiumDV": 9,
            "carbohydrates": 25,
            "carbohydratesDV": 9,
            "fiber": 3,
            "fiberDV": 12,
            "sugar": 12,
            "addedSugar": 10,
            "addedSugarDV": 20,
            "protein": 8
        },
        "claimVerification": [
            {
                "claim": "Low Fat",
                "status": "verified",
                "explanation": "Confirmed: Contains 3g fat, meeting FDA criteria for 'low fat' (≤3g per serving)",
                "source": "FDA regulations"
            },
            {
                "claim": "Good Source of Calcium",
                "status": "verified",
                "explanation": "Confirmed: Contains 300mg calcium (23% DV), meeting 'good source' criteria (≥10% DV)",
                "source": "FDA regulations"
            }
        ],
        "ingredientAnalysis": {
            "ingredients": ["Milk", "Sugar", "Cocoa", "Natural Vanilla Flavor", "Carrageenan", "Vitamin A Palmitate", "Vitamin D3"],
            "flaggedIngredients": [],
            "allergens": ["Milk"],
            "additives": {
                "preservatives": 0,
                "artificialColors": 0,
                "artificialFlavors": 0
            }
        },
        "healthRecommendation": {
            "level": "safe",
            "summary": "This product is a healthy choice with good nutritional balance and verified health claims.",
            "reasons": [
                "Low fat content supports heart health",
                "Good source of calcium for bone health", 
                "Reasonable calorie content",
                "No artificial colors or preservatives"
            ],
            "tips": [
                "Enjoy as part of a balanced diet",
                "Good option for calcium intake"
            ]
        },
        "overallScore": 78,
        "keyInsights": [
            {"type": "positive", "text": "Good calcium content (300mg, 23% DV) promotes bone health"},
            {"type": "neutral", "text": "Moderate sugar content (12g) - consider portion control"},
            {"type": "positive", "text": "Low sodium content supports heart health"}
        ],
        "recommendations": [
            "This product can be part of a balanced diet",
            "Good source of essential nutrients like calcium",
            "Consider pairing with high-fiber foods"
        ]
    },
    
    "unhealthy_product": {
        "analysisId": "test-002", 
        "timestamp": "2025-08-26T03:30:00Z",
        "extractedText": SAMPLE_PROCESSED_FOOD_TEXT,
        "nutritionFacts": {
            "servingSize": "1 package (85g)",
            "servingsPerContainer": 1,
            "calories": 380,
            "fat": 18,
            "fatDV": 23,
            "saturatedFat": 8,
            "saturatedFatDV": 40,
            "transFat": 0.5,
            "cholesterol": 35,
            "cholesterolDV": 12,
            "sodium": 950,
            "sodiumDV": 41,
            "carbohydrates": 42,
            "carbohydratesDV": 15,
            "fiber": 1,
            "fiberDV": 4,
            "sugar": 6,
            "addedSugar": 4,
            "addedSugarDV": 8,
            "protein": 12
        },
        "claimVerification": [],
        "ingredientAnalysis": {
            "ingredients": ["Enriched Flour", "Water", "Cheese", "Palm Oil", "High Fructose Corn Syrup", "Salt", "Monosodium Glutamate", "Sodium Nitrite", "Artificial Colors", "Partially Hydrogenated Soybean Oil", "Sodium Benzoate"],
            "flaggedIngredients": [
                {
                    "name": "High Fructose Corn Syrup",
                    "riskLevel": "high",
                    "reason": "Linked to obesity, diabetes, and metabolic issues",
                    "alternatives": ["cane sugar", "maple syrup", "honey"]
                },
                {
                    "name": "Partially Hydrogenated Soybean Oil",
                    "riskLevel": "high",
                    "reason": "Contains trans fats, linked to heart disease",
                    "alternatives": ["olive oil", "coconut oil", "avocado oil"]
                },
                {
                    "name": "Monosodium Glutamate",
                    "riskLevel": "medium",
                    "reason": "May cause headaches and reactions in sensitive individuals",
                    "alternatives": ["natural spices", "herbs", "garlic powder"]
                },
                {
                    "name": "Artificial Colors",
                    "riskLevel": "medium", 
                    "reason": "May cause hyperactivity in children",
                    "alternatives": ["natural colors", "fruit/vegetable extracts"]
                }
            ],
            "allergens": ["Wheat", "Milk", "Soy"],
            "additives": {
                "preservatives": 2,
                "artificialColors": 2,
                "artificialFlavors": 0
            }
        },
        "healthRecommendation": {
            "level": "avoid",
            "summary": "This product has several nutritional red flags and should be consumed sparingly.",
            "reasons": [
                "Very high sodium content (950mg, 41% DV)",
                "High saturated fat content (8g, 40% DV)",
                "Contains trans fats (0.5g)",
                "Multiple harmful additives and preservatives",
                "High calorie density with low nutritional value"
            ],
            "tips": [
                "Look for alternatives with lower sodium",
                "Choose products without trans fats",
                "Avoid foods with artificial colors and preservatives"
            ]
        },
        "overallScore": 25,
        "keyInsights": [
            {"type": "warning", "text": "Very high sodium (950mg, 41% DV) may contribute to hypertension"},
            {"type": "warning", "text": "Contains trans fats (0.5g) which increase heart disease risk"},
            {"type": "warning", "text": "Multiple artificial additives may cause adverse reactions"},
            {"type": "warning", "text": "High calorie content (380 cal) with minimal nutrients"}
        ],
        "recommendations": [
            "Consider healthier alternatives with less processing",
            "Look for products without trans fats",
            "Choose items with lower sodium content",
            "Read ingredient lists and avoid artificial additives",
            "Limit consumption of highly processed foods"
        ]
    }
}

def get_sample_data(product_type="healthy"):
    """Get sample analysis data for testing"""
    return MOCK_ANALYSIS_RESULTS.get(f"{product_type}_product", MOCK_ANALYSIS_RESULTS["healthy_product"])

def get_sample_nutrition_text(product_type="milk"):
    """Get sample nutrition label text for testing OCR"""
    if product_type == "cereal":
        return SAMPLE_CEREAL_LABEL_TEXT
    elif product_type == "processed":
        return SAMPLE_PROCESSED_FOOD_TEXT
    else:
        return SAMPLE_NUTRITION_LABEL_TEXT
