# Veritas - Pocket Nutrition Scientist

## 1. Purpose
Veritas is an AI-powered companion designed to be your **pocket nutrition scientist**. The goal is to empower users to make informed food choices by analyzing product labels. Users can upload or capture food label images, and Veritas will:
- Extract nutrient facts, ingredients, and product claims from the label.
- Verify claims against trusted nutritional databases.
- Provide health impact analysis (nutrient balance, harmful ingredients, overconsumption risks).
- Deliver human-friendly explanations using AI reasoning.

This project focuses on building a **free-to-deploy web application** with modern open-source tools and free-tier APIs.

---

## 2. Project Flow

### User Flow
1. User uploads/captures food label image.
2. Backend runs OCR to extract text from the image.
3. Extracted text is structured into categories: nutrients, ingredients, claims.
4. Structured data is analyzed using OpenRouter (DeepSeek R1) and nutrition APIs.
5. Results are returned to the frontend:
   - Nutritional summary
   - Claim validation (true/false + explanation)
   - Harmful ingredient warnings
   - Daily value analysis
   - Simple recommendation (✅ Safe / ⚠️ Moderate / ❌ Avoid)

### System Flow
```
Frontend (React + Tailwind) → Backend (FastAPI on Deta) → OCR (HF TrOCR/Donut) → NLP Structuring (Regex + optional DocVQA) → AI Reasoning (OpenRouter DeepSeek R1) → Knowledge Base (USDA + OpenFoodFacts) → Supabase DB → Frontend Results
```

---

## 3. Tools & Stack

### Frontend
- **React + TailwindCSS** → UI development.
- **Vercel (Free)** → Deployment.

### Backend
- **Python (FastAPI)** → API framework.
- **Deta Space (Free)** → Backend hosting.

### OCR (Label Extraction)
- **Hugging Face TrOCR** (default) or **Donut** (end-to-end). Toggle via env `OCR_ENGINE`.

### NLP (Structuring Data)
- **Regex & heuristics** → For nutrients/values.
- **Hugging Face Inference API (Free)** → To classify text into nutrients/ingredients/claims.

### AI Reasoning
- **OpenRouter (DeepSeek R1)** → Used for natural explanations & claim verification via OpenRouter Chat Completions.

### Knowledge Base
- **USDA FoodData Central API** → Nutrient reference values.
- **OpenFoodFacts API** → Ingredients & product claim references.

### Database
- **Supabase (Free)** → PostgreSQL + authentication for storing user scans & analysis.

---

## 4. Deployment Summary
| Component   | Tool            | Free? | Notes |
|-------------|----------------|-------|-------|
| Frontend    | React + Tailwind, Vercel | ✅ | Smooth deploy via GitHub |
| Backend     | FastAPI, Deta Space | ✅ | Free hosting, lightweight only |
| OCR         | Tesseract OCR | ✅ | Local processing in backend |
| NLP Structuring | Regex + HuggingFace API | ✅ | Free tier: 30k tokens/month |
| AI Reasoning | OpenRouter (DeepSeek R1) | ✅ | Usage-based via OpenRouter |
| DB          | Supabase       | ✅ | 500MB free storage, 500k calls/month |
| Knowledge   | USDA / OpenFoodFacts | ✅ | Unlimited free |

---

## 5. Folder Structure
```
veritas/
│
├── frontend/                # React + Tailwind frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Upload, Results pages
│   │   └── utils/           # API calls
│   └── package.json
│
├── backend/                 # FastAPI backend
│   ├── main.py               # FastAPI entrypoint
│   ├── ocr_pipeline.py       # Unified OCR (TrOCR/Donut via HF)
│   ├── parser.py             # Regex + NLP structuring
│   ├── analyzer.py           # OpenRouter + API checks
│   ├── requirements.txt
│   └── tests/
│
├── db/                      # Supabase schema/migrations
│   └── schema.sql
│
└── products.md              # Project guide (this file)
```

---

## 6. Step-by-Step Development

### Step 1: Setup Frontend
- Initialize React app with Vite or CRA.
- Install TailwindCSS.
- Build UI: upload form, result dashboard.
- Deploy to Vercel.

### Step 2: Setup Backend
- Initialize FastAPI app.
- Create `/analyze` endpoint → accepts image.
- Add OCR (TrOCR or Donut via Hugging Face Inference) → extract text / JSON.

### Step 3: Data Structuring
- Parse nutrients/ingredients using regex.
- Use Hugging Face free API to classify claims vs facts.

### Step 4: AI Reasoning
- Send extracted claims + ingredients to OpenRouter (DeepSeek R1).
- Generate human-friendly explanations.

### Step 5: Knowledge Base Integration
- Query USDA API for nutrient standards.
- Query OpenFoodFacts for ingredient info.
- Cross-check against claims.

### Step 6: Database Integration
- Connect Supabase.
- Store user scans + analysis results.

### Step 7: Frontend Integration
- Fetch results from backend.
- Display:
  - Nutritional chart (basic calories/macros).
  - Claim verification with ✅ / ❌.
  - Ingredient risk labels.

### Step 8: Deploy
- Backend → Deta Space.
- Frontend → Vercel.
- DB → Supabase.
- Connect everything.

---

## 7. Future Enhancements
- Barcode scanner integration (mobile/webcam).
- Chrome extension for instant analysis on grocery sites.
- Personalized dietary recommendations (vegan, diabetic, fitness-focused).
- Community insights (ratings & reviews).
- Mobile app (React Native / Flutter).

---

## 8. Conclusion
This `products.md` provides the **end-to-end roadmap** to build Veritas:
- Purpose: AI nutrition scientist.
- Workflow: OCR → Structuring → AI Analysis → Knowledge Base → Results.
- Tools: Free-tier stack (React, FastAPI, OpenRouter/DeepSeek R1, Supabase, Deta Space, Hugging Face API).
- Deployment: Free-tier services only.

By following this guide, an AI coding assistant (like Windsurf) can generate the project from **0 to deployable MVP** without any hidden costs.
