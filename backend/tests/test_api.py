"""
Pytest-style API tests for Veritas backend
Run with: pytest tests/test_api.py -v
"""
import pytest
import requests
from fastapi.testclient import TestClient

# Import the FastAPI app from the reorganized structure
try:
    from app.api.main import app
    client = TestClient(app)
    USE_TEST_CLIENT = True
except ImportError:
    # Fallback to live server testing
    USE_TEST_CLIENT = False
    API_BASE = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint"""
    if USE_TEST_CLIENT:
        response = client.get("/health")
    else:
        response = requests.get(f"{API_BASE}/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_root_endpoint():
    """Test the root endpoint"""
    if USE_TEST_CLIENT:
        response = client.get("/")
    else:
        response = requests.get(f"{API_BASE}/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Veritas API" in data["message"]

@pytest.mark.skipif(USE_TEST_CLIENT, reason="Requires running server for live test")
def test_history_endpoint():
    """Test the history endpoint (requires database)"""
    response = requests.get(f"{API_BASE}/history")
    # Should either succeed (200) or fail gracefully
    assert response.status_code in [200, 500]  # 500 if DB not configured
