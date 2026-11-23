# Human-in-the-Loop Financial Filing Auditor Agent

An Agentic AI application designed for financial filing validation (SEC 10-K & 10-Q). Combines autonomous document extraction with confidence scoring, accounting balance rules, YoY volatility checks, and human-in-the-loop review checkpoints.

---

## Architecture Overview

```text
financial-filing-auditor/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints (auth, audit, deps)
│   │   ├── core/            # Config, PBKDF2 password hashing & HS256 JWT tokens
│   │   ├── models/          # SQLite User, FilingAudit, and Metric entities
│   │   ├── schemas/         # Typed Pydantic v2 schemas
│   │   ├── services/        # Validation rules engine & financial filing fixtures
│   │   ├── database.py      # SQLite connection & repository layer
│   │   └── main.py          # App initialization & CORS
│   ├── seed_data.py         # Demo data seeder
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Common Navbar, Sidebar, ProtectedRoute, MetricCard, ReviewModal
│   │   ├── context/         # AuthContext with token persistence
│   │   ├── pages/           # Dashboard, Login, Register, AuditNew, AuditReview, History
│   │   ├── services/        # API client with automatic JWT bearer interceptor
│   │   └── App.jsx
│   └── package.json
└── README.md
```

---

## 🚀 Quickstart: Running the Web Application

### Step 1: Initialize Database & Seed Demo Data
```bash
python backend/seed_data.py
```
> Seeds the demo auditor account (`auditor@example.com` / `Password123!`) and corporate 10-K filings for Apple, Microsoft, and Tesla.

### Step 2: Start the FastAPI Backend
```bash
# From the project root:
uvicorn backend.app.main:app --reload --port 8000
```
- API Docs & Interactive Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

### Step 3: Start the React Frontend
```bash
# In a second terminal:
cd frontend
npm install
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 🔑 Demo Auditor Credentials
- **Email:** `auditor@example.com`
- **Password:** `Password123!`
*(Or click "Fill Demo Credentials" on the login screen, or register any new account)*

---

## 💡 Key Features
1. **Autonomous Financial Metric Extraction:** Captures 8 key metrics (Revenue, Net Income, Operating Cash Flow, Total Assets, Total Liabilities, Gross Profit, Operating Income, EPS).
2. **Multi-layer Validation Engine:**
   - Confidence scoring threshold ($< 85\%$ flagged).
   - Balance Sheet accounting identity ($\text{Assets} \approx \text{Liabilities} + \text{Equity}$).
   - Year-over-Year variance anomaly detection ($> 30\%$ fluctuation flagged).
3. **Human-in-the-Loop Review Console:** Reviewers inspect source snippets, modify values with audit justifications, or reject inconsistent filings.
4. **Audit History & Trail:** Comprehensive log of approvals, auditor IDs, and modified figures.
