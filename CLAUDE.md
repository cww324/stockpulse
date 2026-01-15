# CLAUDE.md - StockPulse Project Context

**Load this file at the start of each session.**

Last Updated: January 15, 2026

---

## Quick Summary

StockPulse is an ML-powered stock analysis platform that analyzes S&P 500 stocks using rule-based scoring AND machine learning (XGBoost), with SHAP explainability. The goal is to demonstrate data engineering + ML + full-stack skills for job applications.

**Developer**: Junior dev (bootcamp grad), targeting backend/data/ML engineer roles
**Timeline**: ~21 weeks @ 2 hrs/day
**Budget**: ~$20-30/month

---

## Current Status

**Phase**: 1 (Foundation & MVP)
**Week**: 1 - Setup Complete
**Next**: Week 2 - Data Exploration

### What's Working
- [x] PostgreSQL database (Docker, port 5433)
- [x] Database schema (13 tables, bronze/silver/gold architecture)
- [x] Python environment (venv, all packages installed)
- [x] Streamlit skeleton app (connects to DB, shows factor weights)
- [x] Alpha Vantage API key configured

### What's Not Yet Built
- [ ] ETL pipeline (ingest, transform, score)
- [ ] yfinance data fetching (got rate limited, retry later)
- [ ] FastAPI backend
- [ ] ML model (Phase 2)
- [ ] SEC EDGAR scraper (Phase 2)
- [ ] AWS deployment

---

## Tech Stack (Actual)

| Layer | Technology | Status |
|-------|------------|--------|
| **Dashboard** | Streamlit | ✅ Skeleton working |
| **API** | FastAPI | Not started |
| **Database** | PostgreSQL 15 (Docker) | ✅ Running |
| **Data Lake** | AWS S3 | Not started |
| **ML** | XGBoost + SHAP | Phase 2 |
| **Hosting** | AWS App Runner | Phase 2 |
| **DNS** | Cloudflare | Not started |

---

## Key Decisions Made

1. **Frontend**: Streamlit (not React) - faster to build, Python-native
2. **Hosting**: AWS App Runner - scales to zero, ~$0 when idle
3. **DNS/Email**: Cloudflare - free SSL, email forwarding
4. **Insider Trading Data**: Build our own SEC EDGAR scraper (Form 4)
5. **Congressional Trades**: Build our own scraper from House/Senate disclosures

See `docs/DECISIONS.md` for full details.

---

## Project Structure

```
stockpulse/
├── .env                  # API keys (gitignored)
├── docker-compose.yml    # PostgreSQL
├── requirements.txt      # Python dependencies
├── venv/                 # Virtual environment
│
├── streamlit/
│   └── app.py            # Dashboard (skeleton)
│
├── backend/              # FastAPI (empty stubs)
├── etl/                  # ETL pipeline (empty stubs)
├── ml/                   # ML training (empty stubs)
│
├── database/
│   ├── schema.sql        # Full schema (13 tables)
│   └── seed.sql          # Factor weights
│
├── docs/
│   ├── DECISIONS.md      # Architecture decisions
│   └── ...
│
├── AI_ROLE.md            # Static AI guidance
├── PROJECT_PLAN.md       # Full 21-week plan
└── CLAUDE.md             # This file (living doc)
```

---

## Database Tables

**Bronze (Raw)**: `raw_stock_data`, `etl_runs`
**Silver (Cleaned)**: `processed_stocks`
**Gold (Scores)**: `stock_scores`, `ml_predictions`, `hybrid_scores`, `shap_values`
**Insider Data**: `insider_trades`, `congressional_trades`
**Config**: `factor_weights`, `weekly_snapshots`, `sector_scores`, `model_performance`

---

## Running the Project

```bash
# Start database
docker-compose up -d

# Activate Python environment
source venv/bin/activate

# Run Streamlit dashboard
streamlit run streamlit/app.py
# Opens at http://localhost:8501

# Database connection
# Host: localhost, Port: 5433, User: stockpulse, Pass: stockpulse_dev
```

---

## Environment Variables (.env)

```
DATABASE_URL=postgresql://stockpulse:stockpulse_dev@localhost:5433/stockpulse
ALPHA_VANTAGE_API_KEY=<configured>
```

---

## Immediate Next Steps

### Week 2: Data Exploration
1. Create Jupyter notebook for data exploration
2. Test yfinance with sample stocks (AAPL, MSFT, NVDA)
3. Understand data structure and available fields
4. Document findings in `docs/data_sources.md`
5. Define scoring methodology

### After That
- Week 3-4: Database testing, helper functions
- Week 5-7: ETL pipeline (ingest → transform → score)
- Week 8-9: FastAPI backend
- Week 10-11: Streamlit dashboard with real data

---

## Important Context

- **Rate Limits**: yfinance can get rate limited (429 errors). Use Alpha Vantage as backup.
- **SEC EDGAR**: 10 req/sec limit, no API key needed
- **Budget Conscious**: Prefer free tiers, avoid paid services unless necessary
- **Portfolio Project**: Everything should be explainable in interviews

---

## Links

- **Repo**: (local for now)
- **Live Site**: Not deployed yet
- **Decisions**: `docs/DECISIONS.md`
- **Full Plan**: `PROJECT_PLAN.md`
- **AI Guidelines**: `AI_ROLE.md`
