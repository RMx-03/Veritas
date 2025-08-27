# Veritas Deployment Guide

## 🚀 Production Deployment

### Frontend Deployment (Vercel)

**1. Prepare for Deployment**
```bash
cd frontend
npm run build
# Verify build works locally
npm run preview
```

**2. Deploy via Vercel CLI**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from frontend directory
cd frontend
vercel

# Follow prompts:
# - Link to existing project or create new
# - Set root directory to frontend/
# - Build command: npm run build
# - Output directory: dist
```

**3. Configure Environment Variables**
In Vercel dashboard:
- Go to Project Settings → Environment Variables
- Add: `VITE_API_URL` = `https://your-backend-url.deta.dev`

**4. Deploy via GitHub (Alternative)**
```bash
# Push to GitHub
git add .
git commit -m "Initial deployment"
git push origin main

# Connect GitHub repo in Vercel dashboard
# Auto-deploy on git push
```

### Backend Deployment (Deta Space)

**1. Install Deta CLI**
```bash
# Install Deta CLI
curl -fsSL https://get.deta.dev/cli.sh | sh

# Or download from: https://docs.deta.sh/docs/cli/install
```

**2. Initialize Deta Project**
```bash
cd backend
deta login
deta new --python veritas-api
```

**3. Configure Environment Variables**
```bash
# Set environment variables in Deta
deta update -e COHERE_API_KEY="your_key_here"
deta update -e HUGGINGFACE_API_KEY="your_hf_key_here" 
deta update -e OCR_ENGINE="trocr"   # or donut
deta update -e HF_TROCR_MODEL="microsoft/trocr-large-printed"
deta update -e HF_DONUT_MODEL="naver-clova-ix/donut-base-finetuned-docvqa"
deta update -e USE_LAYOUT_REFINER="false"
deta update -e HF_DOCVQA_MODEL="impira/layoutlm-document-qa"
deta update -e SUPABASE_URL="your_supabase_url"
deta update -e SUPABASE_ANON_KEY="your_supabase_key"
```

**4. Deploy Backend**
```bash
deta deploy
# Get deployment URL: https://your-app.deta.dev
```

**5. Update CORS Origins**
Edit `main.py` to include your frontend URL:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app"  # Add your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Database Setup (Supabase)

**Already configured - no deployment needed**
- Database runs on Supabase cloud
- Ensure schema is applied from `db/schema.sql`
- Configure Row Level Security if needed

### Domain Configuration

**1. Custom Domain (Optional)**
```bash
# Vercel custom domain
vercel domains add yourdomain.com

# Deta custom domain (requires paid plan)
# Use Deta-provided subdomain for free tier
```

**2. SSL Certificate**
- Automatically provided by Vercel and Deta
- No additional configuration needed

### Environment Variables Summary

**Frontend (.env.production):**
```env
VITE_API_URL=https://your-backend.deta.dev
```

**Backend (Deta Environment):**
```env
COHERE_API_KEY=your_cohere_key
HUGGINGFACE_API_KEY=your_hf_key
OCR_ENGINE=trocr
HF_TROCR_MODEL=microsoft/trocr-large-printed
HF_DONUT_MODEL=naver-clova-ix/donut-base-finetuned-docvqa
USE_LAYOUT_REFINER=false
HF_DOCVQA_MODEL=impira/layoutlm-document-qa
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
ALLOWED_ORIGINS=https://your-app.vercel.app
```

### Post-Deployment Checklist

**1. Test All Endpoints**
```bash
# Health check
curl https://your-backend.deta.dev/health

# Root endpoint
curl https://your-backend.deta.dev/

# Upload test (with actual image file)
curl -X POST https://your-backend.deta.dev/analyze \
  -F "image=@test_image.jpg"
```

**2. Frontend Testing**
- Visit your Vercel URL
- Test image upload functionality
- Verify results display correctly
- Check responsive design on mobile

**3. Database Verification**
- Check Supabase dashboard for analysis records
- Verify data is being saved correctly
- Monitor database usage and performance

### Monitoring & Maintenance

**1. Error Monitoring**
```bash
# Deta logs
deta logs

# Vercel logs (in dashboard)
# Check Function Logs section
```

**2. Performance Monitoring**
- Monitor API response times
- Track Cohere API token usage
- Monitor Supabase database usage

**3. Regular Updates**
```bash
# Update dependencies
npm update  # Frontend
pip install --upgrade -r requirements.txt  # Backend

# Redeploy after updates
vercel --prod  # Frontend
deta deploy    # Backend
```

### Scaling Considerations

**Free Tier Limits:**
- Vercel: 100GB bandwidth/month
- Deta: No strict limits on free tier
- Supabase: 500MB storage, 500k API calls/month
- Cohere: 100k tokens/month

**Upgrade Paths:**
- Vercel Pro: $20/month for better performance
- Deta Pro: Custom pricing for dedicated resources
- Supabase Pro: $25/month for 8GB storage
- Cohere Production: Usage-based pricing

### Backup & Recovery

**1. Database Backup**
```sql
-- Export data from Supabase
SELECT * FROM analysis_results;
-- Save as CSV or JSON
```

**2. Code Backup**
```bash
# Version control with Git
git push origin main
git tag -a v1.0 -m "Production release"
git push origin v1.0
```

**3. Environment Backup**
- Save all environment variables securely
- Document API keys and credentials
- Keep deployment configuration files

### Troubleshooting

**Common Deployment Issues:**

**1. OCR Not Working on Deta**
```bash
# Ensure HF key is set and models load on first call (cold start may take ~30s)
deta update -e HUGGINGFACE_API_KEY="your_hf_key"
deta update -e OCR_ENGINE="trocr"  # or donut
```

**2. CORS Errors**
```python
# Update CORS origins in main.py
allow_origins=["https://your-actual-frontend-url.vercel.app"]
```

**3. API Key Issues**
```bash
# Verify all environment variables are set
deta details  # Check environment variables
```

**4. Database Connection Issues**
```bash
# Check Supabase credentials
# Verify network connectivity
# Check Supabase service status
```

### Security Hardening

**1. API Security**
- Implement rate limiting
- Add request validation
- Enable HTTPS only

**2. Environment Security**
- Rotate API keys regularly
- Use least-privilege access
- Monitor for security vulnerabilities

**3. Data Protection**
- Implement data retention policies
- Add user consent mechanisms
- Ensure GDPR compliance if applicable
