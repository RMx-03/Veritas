"""
Demo endpoint for testing without OCR dependencies
Add this to main.py for testing purposes
"""

from fastapi import APIRouter
from sample_data import get_sample_data, get_sample_nutrition_text
import uuid
from datetime import datetime

router = APIRouter()

@router.get("/demo/healthy")
async def demo_healthy_analysis():
    """Demo endpoint returning sample healthy product analysis"""
    return get_sample_data("healthy")

@router.get("/demo/unhealthy") 
async def demo_unhealthy_analysis():
    """Demo endpoint returning sample unhealthy product analysis"""
    return get_sample_data("unhealthy")

@router.post("/demo/analyze")
async def demo_analyze():
    """Demo analyze endpoint that returns mock data without OCR processing"""
    
    # Simulate processing delay
    import asyncio
    await asyncio.sleep(2)
    
    # Return sample analysis
    sample_data = get_sample_data("healthy")
    sample_data["analysisId"] = str(uuid.uuid4())
    sample_data["timestamp"] = datetime.utcnow().isoformat()
    
    return sample_data

# Add these routes to main.py:
# app.include_router(demo_router, prefix="/demo", tags=["demo"])
