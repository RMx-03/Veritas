# Veritas Backend

Clean, organized backend for the Veritas nutrition analysis application.

## 🏗️ Project Structure

```
backend/
├── app/                    # Main application code
│   ├── api/               # FastAPI routes and endpoints
│   │   └── main.py        # Main FastAPI application
│   ├── core/              # Core business logic
│   │   ├── analyzer.py    # AI nutrition analysis (OpenRouter)
│   │   ├── ocr_unified.py # OCR processing pipeline
│   │   ├── parser_enhanced.py # Nutrition data parsing
│   │   ├── food_scientist_analyzer.py # Scientific analysis
│   │   └── knowledge_base.py # External API integrations
│   ├── database/          # Database operations
│   │   └── database.py    # Supabase integration
│   └── utils/             # Utility functions
├── tests/                 # Test files
│   ├── test_api.py        # API endpoint tests
│   ├── test_core_modules.py # Core module tests
│   └── integration_test.py # Full integration tests
├── scripts/               # Deployment and utility scripts
├── examples/              # Sample data and documentation
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── pytest.ini           # Test configuration
└── .env.example         # Environment configuration template
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy configuration template
cp .env.example .env

# Edit .env with your API keys:
# - OPENROUTER_API_KEY (required)
# - SUPABASE_URL and SUPABASE_ANON_KEY (required)
# - HUGGINGFACE_API_KEY (optional)
```

### 3. Run the Application
```bash
# Start the server
python main.py

# Or with uvicorn directly
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_api.py -v
pytest tests/test_core_modules.py -v

# Run with coverage
pytest --cov=app tests/
```

## 📋 API Endpoints

- `GET /` - Root endpoint with API info
- `GET /health` - Health check
- `POST /analyze` - Analyze food label image
- `GET /history` - Get analysis history
- `POST /save` - Save analysis result

## 🔧 Configuration

Key environment variables:

### Required
- `OPENROUTER_API_KEY` - For AI analysis
- `SUPABASE_URL` - Database URL
- `SUPABASE_ANON_KEY` - Database access key

### Optional
- `HUGGINGFACE_API_KEY` - Used by the DocTR OCR API tier
- `USDA_API_KEY` - USDA nutrition database access
- `OCR_ENGINE` - OCR engine selection (default: advanced)
- `OPENFOODFACTS_BASE_URL` - Base URL for OpenFoodFacts product endpoint (default: https://world.openfoodfacts.org/api/v0/product/)
- `DOCTR_API_MODEL` - HF model for OCR via API (default: microsoft/trocr-small-printed)
- `ALLOWED_ORIGINS` - Comma-separated list of allowed origins for CORS. Use `*` only in development.
- `MAX_UPLOAD_MB` - Max upload size in MB for `/analyze` (default: 10).
- `RATE_LIMIT_PER_MINUTE` - Simple per-IP requests/min limit (default: 120).
- `WARMUP_ON_STARTUP` - Pre-download OCR models on startup to avoid cold starts (`true`/`false`, default: true).
- `WARMUP_ENGINES` - Comma-separated OCR engines to warm (`easyocr,paddle`).

## 🛡️ Security & Performance Middleware

The FastAPI app includes production hardening in `app/api/main.py`:

- **CORS**: Configurable via `ALLOWED_ORIGINS` (comma-separated). Defaults to `*` in dev.
- **GZip compression**: Added for responses >= 1KB.
- **Security headers**: `X-Content-Type-Options=nosniff`, `X-Frame-Options=DENY`, `Referrer-Policy=no-referrer`, `Permissions-Policy` restrictions.
- **Request ID**: Every response includes `X-Request-ID` for traceability.
- **Rate limiting**: In-memory per-IP limiter with 60s window, limit from `RATE_LIMIT_PER_MINUTE`.
- **Upload size limit**: Enforced in `/analyze` using `MAX_UPLOAD_MB`.
- **Warmup**: `/warmup` endpoint and optional startup warmup (`WARMUP_ON_STARTUP`, `WARMUP_ENGINES`) for OCR weights.

## 🧠 Multi-tier OCR Pipeline

The OCR/data retrieval now follows a low-memory, API-first chain:

1. OpenFoodFacts lookup (if `barcode` or `product_name` provided) – returns structured data and skips OCR when found.
2. Hugging Face Inference API (DocTR) – uses `HUGGINGFACE_API_KEY` and `DOCTR_API_MODEL`.
3. Local EasyOCR fallback – runs on CPU, low footprint.

Each tier logs which method was used and gracefully falls back on errors or rate limits. See `app/core/ocr_unified.py`.

### /analyze usage with optional lookup hints

`POST /analyze` accepts two optional query params:

- `barcode`: e.g. `barcode=737628064502`
- `product_name`: e.g. `product_name=Kind Dark Chocolate Nuts & Sea Salt`

Example (curl):

```bash
curl -X POST "http://localhost:8000/analyze?barcode=737628064502" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@path/to/label.jpg"
```

## 📁 Module Overview

### Core Modules
- **analyzer.py** - Main AI analysis using OpenRouter
- **ocr_unified.py** - Multi-engine OCR pipeline (PaddleOCR, EasyOCR, Tesseract)
- **parser_enhanced.py** - Nutrition facts parsing and extraction
- **food_scientist_analyzer.py** - Scientific nutrition analysis
- **knowledge_base.py** - External API integrations (USDA, OpenFoodFacts)

### API Layer
- **main.py** - FastAPI application with all endpoints

### Database Layer
- **database.py** - Supabase operations for storing analysis results

This structure follows Python best practices with clear separation of concerns, making the codebase maintainable and scalable.
