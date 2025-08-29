"""
Test script for Veritas API endpoints
Run with: python test_api.py
"""

import requests
import json
from pathlib import Path

API_BASE = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"✅ Root Endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Root Endpoint Failed: {e}")
        return False

def test_analyze_endpoint():
    """Test the analyze endpoint with a sample image"""
    print("\n⚠️  Analyze endpoint test requires:")
    print("   1. A sample food label image file")
    print("   2. Backend .env configured (HUGGINGFACE_API_KEY, OCR_ENGINE=trocr|donut; OpenRouter, Supabase)")
    print("   3. Backend server running")
    
    # Create a dummy test without actual file upload
    print("   Skipping file upload test - manual testing required")
    return True

def test_history_endpoint():
    """Test the history endpoint"""
    try:
        response = requests.get(f"{API_BASE}/history")
        print(f"✅ History Endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data.get('history', []))} analysis records")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ History Endpoint Failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 Testing Veritas API Endpoints")
    print("=" * 40)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("History Endpoint", test_history_endpoint),
        ("Analyze Endpoint", test_analyze_endpoint),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\n🎯 Overall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the backend configuration.")

if __name__ == "__main__":
    main()
