from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import os
import tempfile
import uuid
from datetime import datetime
from dotenv import load_dotenv
# New imports for warmup/background tasks
import asyncio
import logging
from fastapi import BackgroundTasks
from typing import Optional
from collections import deque, defaultdict

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

# CORS, Compression, and Security configuration
# Read allowed origins from environment (comma-separated). Use '*' to allow all.
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = ["*"] if ALLOWED_ORIGINS_ENV.strip() in ("*", "") else [o.strip() for o in ALLOWED_ORIGINS_ENV.split(",") if o.strip()]
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip response compression (1KB+)
app.add_middleware(GZipMiddleware, minimum_size=1024)

# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "accelerometer=(), camera=(), geolocation=()"
    return response

# Simple in-memory rate limiting per IP (per-process)
rate_store = defaultdict(deque)
rate_exempt_paths = {"/health", "/warmup"}

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    try:
        if request.method == "OPTIONS" or request.url.path in rate_exempt_paths:
            return await call_next(request)
        # Identify client IP (respect proxies)
        forwarded = request.headers.get("x-forwarded-for")
        client_ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")
        window = 60.0
        now = asyncio.get_event_loop().time()
        dq = rate_store[client_ip]
        while dq and now - dq[0] > window:
            dq.popleft()
        if len(dq) >= RATE_LIMIT_PER_MINUTE:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Please slow down."})
        dq.append(now)
    except Exception:
        # Fail-open on rate limiter errors
        pass
    return await call_next(request)

# ---- Warmup configuration & task (cloud-only, no local engines) ----
WARMUP_ON_STARTUP = os.getenv("WARMUP_ON_STARTUP", "true").lower() == "true"
logger = logging.getLogger("uvicorn.error")

# Log resolved config early for deploy verification
try:
    logger.info(f"[CONFIG] WARMUP_ON_STARTUP={WARMUP_ON_STARTUP}")
    provider = (os.getenv("CLOUD_OCR_PROVIDER", "hf") or "hf").lower()
    logger.info(f"[CONFIG] Cloud-only OCR mode enabled (OpenFoodFacts + provider={provider})")
    # Additional diagnostics for cloud OCR configuration
    if provider == "mistral":
        mk = os.getenv("MISTRAL_API_KEY") or ""
        mm = os.getenv("MISTRAL_OCR_MODEL", "pixtral-12b")
        masked_mk = (mk[:3] + "*" * max(0, len(mk) - 7) + mk[-4:]) if mk else None
        logger.info(f"[CONFIG] MISTRAL_API_KEY present: {bool(mk)}" + (f" ({masked_mk})" if masked_mk else ""))
        logger.info(f"[CONFIG] MISTRAL_OCR_MODEL={mm}")
    else:
        hf_key = os.getenv("HUGGINGFACE_API_KEY") or ""
        doctr_model = os.getenv("DOCTR_API_MODEL", "microsoft/trocr-small-printed")
        masked = ("hf_" + "*" * max(0, len(hf_key) - 6) + hf_key[-4:]) if hf_key.startswith("hf_") else None
        logger.info(f"[CONFIG] HUGGINGFACE_API_KEY present: {bool(hf_key)}" + (f" ({masked})" if masked else ""))
        logger.info(f"[CONFIG] DOCTR_API_MODEL={doctr_model}")
except Exception:
    pass

async def warmup_ocr_models():
    # No-op: We no longer warm local OCR models since pipeline is cloud-only
    try:
        logger.info("[WARMUP] Cloud-only mode: no local OCR engines to warm")
    except Exception:
        pass

@app.on_event("startup")
async def _trigger_warmup_on_startup():
    if WARMUP_ON_STARTUP:
        # Launch warmup in background to avoid blocking server startup/health checks
        asyncio.create_task(warmup_ocr_models())

@app.get("/")
async def root():
    return {"message": "Veritas API - Pocket Nutrition Scientist", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/warmup")
async def manual_warmup(background_tasks: BackgroundTasks):
    """
    Trigger OCR model warmup asynchronously.
    Returns immediately; check logs to track progress.
    """
    background_tasks.add_task(warmup_ocr_models)
    return {"started": True, "cloud_only": True}

@app.post("/analyze")
async def analyze_food_label(
    image: UploadFile = File(...),
    barcode: Optional[str] = Query(None, description="Optional barcode to prioritize OpenFoodFacts lookup"),
    product_name: Optional[str] = Query(None, description="Optional product name to try OpenFoodFacts search")
):
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
            # Validate file size (configurable limit) after reading content
            if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
                raise HTTPException(status_code=400, detail=f"File size too large (max {MAX_UPLOAD_MB}MB)")
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Step 1: Extract OCR + structure via unified pipeline
            print(f"[ANALYZE] Step 1: Starting OCR pipeline for analysis {analysis_id}")
            if barcode or product_name:
                print(f"[ANALYZE] OpenFoodFacts priority lookup | barcode={barcode} | product_name={product_name}")
            else:
                print("[ANALYZE] OpenFoodFacts skipped: no barcode or product_name provided")
            ocr_out = extract_structured_from_image(temp_file_path, barcode=barcode, product_name=product_name)
            extracted_text = ocr_out.get("text", "")
            structured_data = ocr_out.get("structured", {}) or {}
            ocr_method = ocr_out.get("method", "unknown")
            print(f"[ANALYZE] OCR method: {ocr_method}")
            print(f"[ANALYZE] OCR extracted {len(extracted_text) if extracted_text else 0} characters")
            print(f"[ANALYZE] OCR text preview: {extracted_text[:200] if extracted_text else 'None'}...")

            if not extracted_text or len(extracted_text.strip()) < 10:
                # Surface internal OCR pipeline debug info to logs for diagnostics
                try:
                    dbg = ocr_out.get("debug", {}) if isinstance(ocr_out, dict) else {}
                    print(f"[OCR_DEBUG] pipeline: {dbg.get('pipeline')}")
                    print(f"[OCR_DEBUG] engines: {dbg.get('engines')}")
                    notes = dbg.get("notes")
                    if notes:
                        print(f"[OCR_DEBUG] notes: {notes}")
                except Exception:
                    pass
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

# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

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
