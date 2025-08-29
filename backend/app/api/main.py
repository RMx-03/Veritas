from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Ensure environment variables are loaded before importing modules that read them
load_dotenv()

from ..core.ocr_unified import extract_structured_from_image
from ..core.parser_enhanced import parse_nutrition_data
from ..core.analyzer import analyze_nutrition_data
from ..database.database import save_analysis_result

app = FastAPI(
    title="Veritas API",
    description="AI-powered nutrition analysis API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Veritas API - Pocket Nutrition Scientist", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/analyze")
async def analyze_food_label(image: UploadFile = File(...)):
    """
    Analyze a food label image and return comprehensive nutrition analysis
    """
    try:
        # Validate file type
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            content = await image.read()
            # Validate file size (10MB limit) after reading content
            if len(content) > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="File size too large (max 10MB)")
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Step 1: Extract OCR + structure via unified pipeline
            print(f"[ANALYZE] Step 1: Starting OCR pipeline for analysis {analysis_id}")
            ocr_out = extract_structured_from_image(temp_file_path)
            extracted_text = ocr_out.get("text", "")
            structured_data = ocr_out.get("structured", {}) or {}
            ocr_method = ocr_out.get("method", "unknown")
            print(f"[ANALYZE] OCR method: {ocr_method}")
            print(f"[ANALYZE] OCR extracted {len(extracted_text) if extracted_text else 0} characters")
            print(f"[ANALYZE] OCR text preview: {extracted_text[:200] if extracted_text else 'None'}...")

            if not extracted_text or len(extracted_text.strip()) < 10:
                print(f"[ANALYZE] ERROR: Insufficient text extracted ({len(extracted_text.strip()) if extracted_text else 0} chars)")
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract readable text from image. Please ensure the label is clear and well-lit."
                )

            # Step 2: Ensure structured data present (fallback to parser if needed)
            if not structured_data or not isinstance(structured_data, dict):
                print(f"[ANALYZE] Structured data missing from OCR pipeline, falling back to regex parser")
                structured_data = parse_nutrition_data(extracted_text)
            print(f"[ANALYZE] Parsed nutrition facts: {structured_data.get('nutrition_facts', {})}")
            print(f"[ANALYZE] Parsed ingredients: {len(structured_data.get('ingredients', []))} items")
            
            # Step 3: Analyze using AI and knowledge bases
            print(f"[ANALYZE] Step 3: Starting AI analysis")
            analysis_results = await analyze_nutrition_data(structured_data, extracted_text)
            print(f"[ANALYZE] AI analysis complete - overall score: {analysis_results.get('overall_score', 'N/A')}")
            
            # Step 4: Prepare response
            print(f"[ANALYZE] Step 4: Preparing response data")
            print(f"[ANALYZE] Analysis results keys: {list(analysis_results.keys()) if analysis_results else 'None'}")
            response_data = {
                "analysisId": analysis_id,
                "timestamp": datetime.utcnow().isoformat(),
                "extractedText": extracted_text,
                "nutrition_facts": analysis_results.get("nutrition_facts", {}),
                "scientific_analysis": analysis_results.get("scientific_analysis", {}),
                "health_score": analysis_results.get("health_score", {"score": analysis_results.get("overall_score", 0), "level": "moderate"}),
                "health_impact_assessment": analysis_results.get("health_impact_assessment", {}),
                "ingredients_analysis": analysis_results.get("ingredient_analysis", {}),
                "claim_verification": analysis_results.get("claim_verification", []),
                "key_insights": analysis_results.get("key_insights", []),
                "recommendations": analysis_results.get("recommendations", []),
                "ai_recommendation": analysis_results.get("ai_recommendation", {}),
                "overall_score": analysis_results.get("overall_score", 0),
                "processedImage": None,  # Add image processing if needed
                # Legacy fields for backward compatibility
                "nutritionFacts": analysis_results.get("nutrition_facts", {}),
                "claimVerification": analysis_results.get("claim_verification", []),
                "ingredientAnalysis": analysis_results.get("ingredient_analysis", {}),
                "healthRecommendation": analysis_results.get("health_recommendation", {}),
                "overallScore": analysis_results.get("overall_score", 0),
                "keyInsights": analysis_results.get("key_insights", [])
            }
            print(f"[ANALYZE] Response data prepared with score: {response_data['overallScore']}")
            print(f"[ANALYZE] Nutrition facts in response: {response_data['nutritionFacts']}")
            print(f"[ANALYZE] Claims in response: {len(response_data['claimVerification'])} items")
            
            # Step 5: Save to database (async)
            try:
                await save_analysis_result(analysis_id, response_data, image.filename)
            except Exception as db_error:
                # Log error but don't fail the request
                print(f"Database save error: {db_error}")
            
            return JSONResponse(content=response_data)
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred during analysis. Please try again."
        )

@app.get("/usage")
async def usage_root(request: Request):
    """
    Temporary handler for legacy/monitoring calls to /usage to prevent 404 spam.
    Logs caller metadata to help identify the source.
    """
    referer = request.headers.get("referer")
    ua = request.headers.get("user-agent")
    client = request.client.host if request.client else "unknown"
    print(f"[USAGE] /usage hit | method={request.method} | referer={referer} | ua={ua} | client={client}")
    return {"handled": True, "message": "Usage endpoint is not implemented. Request logged."}

@app.api_route("/usage/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def usage_catch_all(path: str, request: Request):
    """
    Catch-all route for /usage/* to avoid 404s and surface the source of these requests.
    """
    referer = request.headers.get("referer")
    ua = request.headers.get("user-agent")
    client = request.client.host if request.client else "unknown"
    print(f"[USAGE] /usage/{path} hit | method={request.method} | referer={referer} | ua={ua} | client={client}")
    return {"handled": True, "path": path}

@app.get("/history")
async def get_analysis_history(limit: int = 10):
    """
    Get recent analysis history
    """
    try:
        from ..database.database import get_analysis_history
        history = await get_analysis_history(limit)
        return {"history": history}
    except Exception as e:
        print(f"History fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")

@app.post("/save")
async def save_analysis(analysis_data: dict):
    """
    Save analysis results
    """
    try:
        analysis_id = str(uuid.uuid4())
        await save_analysis_result(analysis_id, analysis_data)
        return {"analysisId": analysis_id, "saved": True}
    except Exception as e:
        print(f"Save error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save analysis")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
