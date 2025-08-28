# Veritas Setup Guide

## 🚀 Complete Setup Instructions

### Prerequisites Installation

**1. Install Node.js (v18+)**
```bash
# Download from: https://nodejs.org/
# Verify installation:
node --version
npm --version
```

**2. Install Python (3.8+)**
```bash
# Download from: https://python.org/
# Verify installation:
python --version
pip --version
```

**3. Create Hugging Face account & API key**
```bash
# Visit https://huggingface.co/settings/tokens
# Create a Read token and copy it to use as HUGGINGFACE_API_KEY
```

### Project Setup

**1. Install Dependencies**
```bash
# Frontend dependencies
cd frontend
npm install

# Backend dependencies  
cd ../backend
pip install -r requirements.txt
```

**2. Environment Configuration**

**Backend (.env):**
```bash
cd backend
cp .env.example .env
# Edit .env file with your API keys:
```

Required environment variables:
```env
# AI Services (Required)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# OpenRouter (LLM via Chat Completions)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
# Pick a model from https://openrouter.ai/models (examples below)
OPENROUTER_MODEL=deepseek/deepseek-r1
# Optional: used for HTTP Referer and X-Title headers (best practice)
OPENROUTER_SITE_URL=http://localhost:8000
OPENROUTER_APP_NAME=Veritas Local

# Database (Required)
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# OCR Configuration (HF Inference)
OCR_ENGINE=trocr                 # Options: trocr | donut
HF_TROCR_MODEL=microsoft/trocr-large-printed
HF_DONUT_MODEL=naver-clova-ix/donut-base-finetuned-docvqa
USE_LAYOUT_REFINER=false
HF_DOCVQA_MODEL=impira/layoutlm-document-qa

# Optional APIs
USDA_API_KEY=your_usda_api_key_here
```

**Frontend (.env):**
```bash
cd ../frontend
cp ../.env.example .env
# Edit .env file:
```

```env
VITE_API_URL=http://localhost:8000
```

### Database Setup

**1. Create Supabase Project**
- Go to [supabase.com](https://supabase.com)
- Create new project
- Copy URL and anon key to `.env`

**2. Run Database Schema**
- Open Supabase dashboard → SQL Editor
- Copy contents of `db/schema.sql`
- Execute the SQL commands

### API Keys Setup

**1. OpenRouter API (Required)**
- Visit [openrouter.ai](https://openrouter.ai)
- Sign up and generate an API key
- Add to backend `.env` file

**2. HuggingFace API (Optional)**
- Visit [huggingface.co](https://huggingface.co)
- Create account and generate token
- Add to backend `.env` file

**3. USDA API (Optional)**
- Visit [fdc.nal.usda.gov](https://fdc.nal.usda.gov/api-guide.html)
- Register for free API key
- Add to backend `.env` file

### Running the Application

**Development Mode:**

Terminal 1 - Backend:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

**Using Root Package.json:**
```bash
# From project root
npm run install:all      # Install all dependencies
npm start                # Start both frontend and backend
```

Access the application at: `http://localhost:3000`

### Testing the Application

**1. Test API Endpoints:**
```bash
cd backend
python test_api.py
```

**2. Manual Testing:**
- Visit `http://localhost:3000`
- Upload a clear food label image
- Verify OCR extraction works
- Check nutrition analysis results
- Confirm AI recommendations appear

### Common Issues & Solutions

**OCR Issues (HF Inference):**
```bash
# Ensure HUGGINGFACE_API_KEY is set in backend/.env
# First call to a model may return 503 while loading; retry after ~30s
# Try switching engine if results are poor:
OCR_ENGINE=donut   # or set back to trocr
```

**API Connection Issues:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Verify frontend can reach backend
curl http://localhost:8000/

# Check CORS settings in main.py if needed
```

**Database Connection Issues:**
```bash
# Verify Supabase credentials
# Check internet connection
# Confirm database schema is applied
```

### Performance Optimization

**1. Image Processing:**
- Limit upload size (10MB max)
- Preprocess images for better OCR
- Implement caching for repeated analyses

**2. API Rate Limits:**
- Monitor OpenRouter usage (model tokens/costs)
- Implement request queuing
- Cache API responses when possible

**3. Database Optimization:**
- Index frequently queried fields
- Archive old analysis results
- Implement pagination for history

### Security Best Practices

**1. API Keys:**
- Never commit `.env` files
- Use environment variables in production
- Rotate keys regularly

**2. File Upload Security:**
- Validate file types and sizes
- Scan for malicious content
- Implement upload rate limiting

**3. CORS Configuration:**
- Specify exact origins in production
- Remove wildcard (*) origins
- Enable credentials only when needed
