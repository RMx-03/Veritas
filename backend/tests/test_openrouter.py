#!/usr/bin/env python3
"""
Test Groq integration (OpenAI-compatible API)
"""

import os
import asyncio
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
import pytest

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "deepseek-r1-distill-llama-70b")

# Mark as integration and skip by default unless explicitly enabled
pytestmark = pytest.mark.integration
RUN_GROQ_TESTS = os.getenv("RUN_GROQ_TESTS", "false").lower() in ("1", "true", "yes", "y")
if not RUN_GROQ_TESTS:
    pytest.skip(
        "Skipping Groq integration tests by default. Set RUN_GROQ_TESTS=true to enable.",
        allow_module_level=True,
    )

@pytest.mark.asyncio
async def test_groq_connection():
    """Test basic Groq API connection"""
    
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found in environment")
        return False
    
    print(f"✅ Groq API Key: {'*' * (len(GROQ_API_KEY) - 8) + GROQ_API_KEY[-8:]} ")
    print(f"✅ Base URL: {GROQ_BASE_URL}")
    print(f"✅ Model: {GROQ_MODEL}")
    
    # Setup headers (none required for Groq)
    default_headers = None
    
    try:
        client = AsyncOpenAI(
            base_url=GROQ_BASE_URL,
            api_key=GROQ_API_KEY,
            default_headers=default_headers or None
        )
        
        print("\n📡 Testing Groq connection...")
        
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful food science assistant."},
                {"role": "user", "content": "Analyze this chocolate cookie nutrition: calories 66, fat 26g. Is this healthy?"},
            ],
            max_tokens=200,
            temperature=0.1,
        )
        
        ai_response = response.choices[0].message.content.strip()
        print(f"✅ Groq API Response:")
        print(f"   Model: {response.model}")
        print(f"   Response length: {len(ai_response)} characters")
        print(f"   Content preview: {ai_response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        return False

@pytest.mark.asyncio
async def test_nutrition_analysis():
    """Test nutrition analysis with sample data"""
    
    # Sample chocolate cookie data
    nutrition_facts = {"calories": 66.0, "total_fat": 26.0}
    ingredients = ["Butter", "Sugar", "Flour", "Chocolate Chips", "Vanilla"]
    
    print(f"\n🧪 Testing nutrition analysis...")
    print(f"   Nutrition: {nutrition_facts}")
    print(f"   Ingredients: {ingredients}")
    
    try:
        from app.core.analyzer import analyze_nutrition_data
        
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
        print("🧪 Testing Veritas Groq Integration\n")
        
        # Test 1: Groq Connection
        or_working = await test_groq_connection()
        
        # Test 2: Full nutrition analysis
        if or_working:
            analysis_result = await test_nutrition_analysis()
        
        print(f"\n📊 Test Summary:")
        print(f"   Groq API: {'✅ Working' if or_working else '❌ Failed'}")
        if or_working:
            print(f"   Nutrition Analysis: {'✅ Working' if analysis_result else '❌ Failed'}")
    
    asyncio.run(main())
