# Veritas - Pocket Nutrition Scientist

 **AI-powered nutrition analysis for smarter food choices**

Veritas analyzes food labels through image upload, providing instant AI-powered nutrition insights, claim verification, and health recommendations.

## Features

- ** Multi-tier OCR & Lookup** - OpenFoodFacts lookup → HF Inference OCR (DocTR/TroCR) → EasyOCR fallback
- ** AI Analysis** - Verify health claims using OpenRouter (DeepSeek R1)
- ** Nutrition Insights** - Comprehensive nutritional breakdown with charts
- ** Ingredient Warnings** - Identify harmful ingredients and allergens
- ** Health Recommendations** - Get personalized safety ratings
- ** Knowledge Base Integration** - Cross-reference with USDA & OpenFoodFacts

## Tech Stack

**Frontend:**
- React 18 + Vite
- TailwindCSS for styling
- Recharts for data visualization
- Axios for API calls

**Backend:**
- FastAPI (Python)
- OpenFoodFacts API first, then Hugging Face Inference OCR (DocTR/TroCR), with EasyOCR fallback
- OpenRouter (DeepSeek R1) for AI reasoning
- Optional DocVQA (LayoutLM family) for layout-aware refinement

**Database & APIs:**
- Supabase (PostgreSQL)
- USDA FoodData Central API
- OpenFoodFacts API
- HuggingFace Inference API

## Prerequisites

1. **Node.js** (v18+)
2. **Python** (3.8+)
3. (Optional) **Hugging Face** account and API key (for OCR via HF Inference)
4. API keys for:
   - OpenRouter (uses your chosen model via OpenRouter)
   - HuggingFace (free tier: 30k tokens/month)
   - Supabase project

## Quick Start

### 1. Clone & Setup
```bash
git clone <your-repo>
cd veritas
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install

# Copy and configure environment
cp ../.env.example .env
# Edit .env with your backend URL
```

### 4. Database Setup
1. Create a Supabase project
2. Run the SQL schema from `db/schema.sql` in Supabase SQL Editor
3. Update `.env` files with Supabase credentials

### 5. Configure Multi-tier OCR Pipeline

```env
# backend/.env
# 1) OpenFoodFacts lookup (no API key required)
OPENFOODFACTS_BASE_URL=https://world.openfoodfacts.org/api/v0/product/

# 2) Hugging Face Inference OCR (optional)
HUGGINGFACE_API_KEY=your_hf_token
DOCTR_API_MODEL=microsoft/trocr-small-printed

# 3) Local fallback
WARMUP_ON_STARTUP=true
WARMUP_ENGINES=easyocr
```

### 6. Run Development Servers

**Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

Visit: `http://localhost:3000`

## API Keys Setup

### Required:
1. **OpenRouter API** - [Get API key](https://openrouter.ai/)
   - Used for AI claim verification and recommendations (DeepSeek R1)

2. **Supabase** - [Create free project](https://supabase.com/)
   - 500MB database, 500k API calls/month
   - Used for storing analysis results

### Optional:
3. **HuggingFace** - [Get free API key](https://huggingface.co/)
   - 30k tokens free for Inference API (varies)
   - Used for enhanced NLP processing

4. **USDA API** - [Get free API key](https://fdc.nal.usda.gov/api-guide.html)
   - Unlimited free requests
   - Public endpoints available without key

## Project Structure

```
veritas/
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── utils/         # API utilities
│   │   └── App.jsx        # Main app
│   └── package.json
├── backend/               # FastAPI backend
│   ├── main.py           # API entry point
│   ├── ocr_pipeline.py   # Unified OCR pipeline (TrOCR/Donut)
│   ├── parser.py         # Data extraction
│   ├── analyzer.py       # AI analysis
│   ├── knowledge_base.py # External APIs
│   ├── database.py       # Database operations
│   └── requirements.txt
├── db/
│   └── schema.sql        # Database schema
└── README.md
```

## API Endpoints

- `POST /analyze` - Analyze food label image
- `GET /history` - Get analysis history
- `GET /health` - Health check
- `POST /save` - Save analysis result

## Testing

Upload test images of food labels to verify:
- OCR text extraction works
- Nutrition facts parsing
- AI claim verification
- Ingredient analysis
- Health recommendations

## Deployment

### Frontend (Vercel)
```bash
cd frontend
npm run build
# Deploy via Vercel CLI or GitHub integration
```

### Backend (Deta Space)
```bash
cd backend
# Install Deta CLI and deploy
deta new --python
```

### Database (Supabase)
- Already hosted, just configure environment variables

## Security Notes

- API keys stored in environment variables
- CORS configured for specific origins
- Input validation on file uploads
- Rate limiting recommended for production

## Cost Breakdown (All Free Tier)

| Service | Notes |
|---------|-------|
| OpenRouter | Usage-based pricing; choose models like DeepSeek R1 via OpenRouter |
| HuggingFace | 30k tokens free for Inference API (varies) |
| Supabase | 500MB DB, 500k calls free tier |
| Vercel | 100GB bandwidth free tier |
| Deta Space | Free tier available |
| USDA API | Unlimited |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🐛 Common Issues

**OCR not working:**
- Ensure `HUGGINGFACE_API_KEY` is set in `backend/.env`
- Initial HF model call may return 503 (model loading); retry after ~30s
- Check image quality and lighting; upload clear nutrition panel

**API errors:**
- Verify all API keys are correct
- Check API rate limits

**Database connection:**
- Confirm Supabase credentials
- Check internet connection

## 💡 Future Enhancements

- [ ] Barcode scanner integration
- [ ] Mobile app (React Native)
- [ ] Chrome extension for grocery sites
- [ ] Personalized dietary recommendations
- [ ] Community ratings and reviews
- [ ] Batch analysis for meal planning

## 📞 Support

For issues and questions:
- Create GitHub issue
- Check troubleshooting guide
- Review API documentation

---

**Built with ❤️ for healthier food choices**
