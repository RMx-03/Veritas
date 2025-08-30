#!/usr/bin/env python3
"""
Test script to verify Hugging Face API token and model access
"""
import os
import requests
import pytest
from dotenv import load_dotenv

load_dotenv()

# Opt-in integration test to avoid network calls by default
RUN_HF_TESTS = os.getenv("RUN_HF_TESTS", "false").lower() in ("1", "true", "yes", "y")
pytestmark = pytest.mark.integration
if not RUN_HF_TESTS:
    pytest.skip(
        "Skipping Hugging Face token/model access test by default. Set RUN_HF_TESTS=true to enable.",
        allow_module_level=True,
    )

def test_hf_token():
    token = os.getenv('HUGGINGFACE_API_KEY')
    if not token:
        print("❌ HUGGINGFACE_API_KEY not found in .env")
        return False
    
    if not token.startswith('hf_'):
        print("❌ Invalid token format - should start with 'hf_'")
        return False
    
    print(f"✅ Token found: hf_{'*' * (len(token) - 6)}...")
    
    # Test different TrOCR models
    models_to_test = [
        "microsoft/trocr-base-printed",
        "microsoft/trocr-large-printed", 
        "microsoft/trocr-base-handwritten",
        "microsoft/trocr-small-printed"
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    working_models = []
    
    for model in models_to_test:
        try:
            url = f"https://api-inference.huggingface.co/models/{model}"
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                print(f"✅ {model}: Accessible")
                working_models.append(model)
            elif resp.status_code == 404:
                print(f"❌ {model}: Not found (404)")
            elif resp.status_code == 403:
                print(f"❌ {model}: Forbidden (403) - token may not have access")
            else:
                print(f"⚠️  {model}: {resp.status_code} - {resp.text[:100]}")
                
        except Exception as e:
            print(f"❌ {model}: Request failed - {e}")
    
    if working_models:
        print(f"\n✅ Working models found: {working_models}")
        print(f"💡 Recommend using: {working_models[0]}")
        return working_models[0]
    else:
        print("\n❌ No accessible TrOCR models found")
        return None

if __name__ == "__main__":
    print("🧪 Testing Hugging Face API access...")
    print("=" * 50)
    result = test_hf_token()
    if result:
        print(f"\n🎯 Update your .env file:")
        print(f"DOCTR_API_MODEL={result}")
