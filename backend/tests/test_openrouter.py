#!/usr/bin/env python3
"""
Test OpenRouter DeepSeek R1 integration
"""

import os
import asyncio
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME")

async def test_openrouter_connection():
    """Test basic OpenRouter API connection"""
    
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY not found in environment")
        return False
    
    print(f"✅ OpenRouter API Key: {'*' * (len(OPENROUTER_API_KEY) - 8) + OPENROUTER_API_KEY[-8:]}")
    print(f"✅ Base URL: {OPENROUTER_BASE_URL}")
    print(f"✅ Model: {OPENROUTER_MODEL}")
    
    # Setup headers
    default_headers = {}
    if OPENROUTER_SITE_URL:
        default_headers["HTTP-Referer"] = OPENROUTER_SITE_URL
    if OPENROUTER_APP_NAME:
        default_headers["X-Title"] = OPENROUTER_APP_NAME
    
    try:
        client = AsyncOpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
            default_headers=default_headers or None
        )
        
        print("\n📡 Testing OpenRouter connection...")
        
        response = await client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful food science assistant."},
                {"role": "user", "content": "Analyze this chocolate cookie nutrition: calories 66, fat 26g. Is this healthy?"},
            ],
            max_tokens=200,
            temperature=0.1,
        )
        
        ai_response = response.choices[0].message.content.strip()
        print(f"✅ OpenRouter API Response:")
        print(f"   Model: {response.model}")
        print(f"   Response length: {len(ai_response)} characters")
        print(f"   Content preview: {ai_response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter API Error: {e}")
        return False

async def test_nutrition_analysis():
    """Test nutrition analysis with sample data"""
    
    # Sample chocolate cookie data
    nutrition_facts = {"calories": 66.0, "total_fat": 26.0}
    ingredients = ["Butter", "Sugar", "Flour", "Chocolate Chips", "Vanilla"]
    
    print(f"\n🧪 Testing nutrition analysis...")
    print(f"   Nutrition: {nutrition_facts}")
    print(f"   Ingredients: {ingredients}")
    
    try:
        from analyzer import analyze_nutrition_data
        
        structured_data = {
            "nutrition_facts": nutrition_facts,
            "ingredients": ingredients,
            "claims": []
        }
        
        result = await analyze_nutrition_data(structured_data, "Sample chocolate cookie text")
        
        print(f"✅ Analysis completed:")
        print(f"   Health Score: {result.get('health_score', {}).get('score', 'N/A')}")
        print(f"   Analysis keys: {list(result.keys())}")
        
        # Check if AI recommendation worked
        if result.get('ai_recommendation'):
            print(f"   AI Recommendation: ✅ Working")
            print(f"   Summary: {result['ai_recommendation'].get('summary', '')[:50]}...")
        else:
            print(f"   AI Recommendation: ❌ Failed")
        
        return result
        
    except Exception as e:
        print(f"❌ Nutrition Analysis Error: {e}")
        import traceback
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    async def main():
        print("🧪 Testing Veritas OpenRouter Integration\n")
        
        # Test 1: OpenRouter Connection
        or_working = await test_openrouter_connection()
        
        # Test 2: Full nutrition analysis
        if or_working:
            analysis_result = await test_nutrition_analysis()
        
        print(f"\n📊 Test Summary:")
        print(f"   OpenRouter API: {'✅ Working' if or_working else '❌ Failed'}")
        if or_working:
            print(f"   Nutrition Analysis: {'✅ Working' if analysis_result else '❌ Failed'}")
    
    asyncio.run(main())
