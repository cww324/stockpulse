# StockPulse - Project Summary

**Last Updated:** January 17, 2026
**Status:** Week 2 Complete - Ready for Week 3
**Timeline:** 21 weeks @ 2 hours/day = ~290 total hours (18 core + 3 paper trading)

---

## 🎯 Project Vision

**Elevator Pitch:** "StockPulse is an ML-powered stock analysis platform that automatically analyzes 500 S&P 500 stocks weekly, combines rule-based and machine learning scoring systems, and surfaces the top 25 opportunities with explainable predictions—helping long-term investors make data-driven decisions."

**Why This Project?**
- **Career Goal:** Demonstrate data engineering + ML + full-stack skills to land first job
- **Learning Goal:** Master financial markets, ML, and data architecture
- **Personal Goal:** Build something genuinely useful and interesting

**Target Roles:**
- Backend engineer roles
- Data engineer roles
- ML engineer roles (junior)
- Full-stack roles at data-driven companies

---

## 📅 18-Week Timeline

### Phase 1: Foundation & MVP (Weeks 1-14)
**Goal:** Working app with rule-based scoring, deployed and live

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1-2 | Setup & Exploration | Dev environment + data understanding |
| 3-4 | Database Design | Warehouse schema + test data |
| 5-7 | ETL Pipeline | Rule-based scoring for 500 stocks |
| 8-9 | Backend API | FastAPI with all endpoints |
| 10-11 | Frontend Dashboard | Streamlit UI with visualizations |
| 12 | Integration & Testing | End-to-end working, bugs fixed |
| 13 | Deployment | Live on AWS App Runner |
| 14 | Documentation | README, demo video, portfolio |

**🎉 CHECKPOINT:** Deployed MVP ready to show employers!

### Phase 2: ML & Data Lake (Weeks 15-18)
**Goal:** Add ML predictions with SHAP explanations and data lake architecture

| Week | Focus | Deliverable |
|------|-------|-------------|
| 15 | Data Lake Setup | S3/R2 with 3 years historical data |
| 16 | Feature Engineering | ML training dataset prepared |
| 17 | Model Training | XGBoost trained, backtested, evaluated |
| 18 | ML Integration | ML endpoints in API, SHAP in UI |

**🚀 CHECKPOINT:** Production system with ML + explainability!

### Phase 3: Paper Trading (Weeks 19-21)
**Goal:** Validate strategy with automated paper trading via Alpaca

| Week | Focus | Deliverable |
|------|-------|-------------|
| 19 | Alpaca Integration | Buy signals, order execution |
| 20 | Risk Management | Sell signals, stop losses, position sizing |
| 21 | Portfolio Dashboard | Performance tracking, benchmark comparison |

**🎯 FINAL:** Automated trading system with real market validation!

---

## 🏗️ Tech Stack

| Layer | Technology | Status |
|-------|------------|--------|
| **Dashboard** | Streamlit | ✅ Skeleton working |
| **API** | FastAPI | Not started |
| **Database** | PostgreSQL 15 (Docker) | ✅ Running (port 5433) |
| **Data Lake** | AWS S3 or Cloudflare R2 | Not started |
| **ML** | XGBoost + SHAP | Phase 2 |
| **Hosting** | AWS App Runner | Phase 2 |
| **DNS** | Cloudflare | Not started |

---

## 🎨 System Architecture (High-Level)

```
┌─────────────────────────────────────────┐
│    User Interface (Streamlit)           │
│    - Rankings Dashboard                 │
│    - Stock Detail + SHAP                │
└──────────────┬──────────────────────────┘
               │ REST API
               ↓
┌─────────────────────────────────────────┐
│    Serving API (FastAPI)                │
│    - /api/rankings                      │
│    - /api/stocks/{ticker}               │
└──────────────┬──────────────────────────┘
               │ SQL Queries
               ↓
┌─────────────────────────────────────────┐
│    Data Warehouse (PostgreSQL)          │
│    - stock_scores (rule-based)          │
│    - ml_predictions (ML outputs)        │
│    - hybrid_scores (combined)           │
└──────────────┬──────────────────────────┘
               ↑ ETL Writes
               │
┌─────────────────────────────────────────┐
│    ETL Pipeline (Weekly)                │
│    ingest → transform → score → ML      │
└──────────────┬──────────────────────────┘
               ↑ Reads historical
               │
┌─────────────────────────────────────────┐
│    Data Lake (S3/R2)                    │
│    /bronze/ → /silver/ → /gold/         │
└──────────────┬──────────────────────────┘
               ↑
┌─────────────────────────────────────────┐
│    Data Sources (APIs)                  │
│    - Yahoo Finance (yfinance)           │
│    - Alpha Vantage (backup)             │
└─────────────────────────────────────────┘
```

---

## 📊 Database Tables (Overview)

**Bronze (Raw):** `raw_stock_data`, `etl_runs`
**Silver (Cleaned):** `processed_stocks`
**Gold (Scores):** `stock_scores`, `ml_predictions`, `hybrid_scores`, `shap_values`
**Insider Data:** `insider_trades`, `congressional_trades`
**Config:** `factor_weights`, `weekly_snapshots`, `sector_scores`, `model_performance`

---

## 🤖 Custom Agents

8 specialized agents for different domains (stored in `.claude/agents/`):

| Agent | Domain | Primary Use |
|-------|--------|-------------|
| **project-lead** | Architecture & integration | Phase boundaries, integration checks |
| **security-specialist** | Security & vulnerabilities | Before deployment, API security |
| **code-reviewer** | Code quality & testing | After coding, before PRs |
| **data-engineer** | ETL, database, data exploration | Week 2, 5-7, query optimization |
| **ml-specialist** | ML models & features | Week 16-18, preventing look-ahead bias |
| **backend-specialist** | API, DevOps, performance | Week 8-9, 12-14 |
| **frontend-specialist** | UI/UX, visualizations | Week 10-11, Week 19 |
| **financial-expert** | Investment methodology | Week 2, 5-7, 16-18 (methodology validation) |

**📖 See `docs/AGENT_WORKFLOW.md` for week-by-week agent usage guide**

---

## 📈 Current Status

**Phase:** 1 (Foundation & MVP)
**Week:** 2 Complete - Ready for Week 3
**Overall Completion:** ~15%

### ✅ What's Working
- [x] PostgreSQL database (Docker, port 5433)
- [x] Database schema (13 tables, bronze/silver/gold architecture)
- [x] Python environment (venv, all packages installed)
- [x] Streamlit skeleton app (connects to DB)
- [x] Alpha Vantage API key configured
- [x] yfinance data exploration complete (50-70 fields identified)
- [x] Scoring methodology v2.0 (validated by financial-expert agent)
- [x] Documentation: data_sources.md, finance_101.md, scoring_methodology.md

### 🚧 What's Not Yet Built
- [ ] Database schema updates (add ROA, dividend_yield, return_12m)
- [ ] ETL pipeline (ingest, transform, score) - Week 5-7
- [ ] FastAPI backend - Week 8-9
- [ ] ML model (Phase 2) - Week 16-18
- [ ] AWS deployment - Week 13

### 📍 Next Steps (Week 3)
1. Review/update database schema based on Week 2 findings
2. Add new fields: ROA, dividend_yield, return_12m
3. Create database helper functions (CRUD operations)
4. Add indexes for common queries
5. Test with sample data

**Agents to use:** `data-engineer`, `project-lead`

---

## 💰 Budget

**Monthly Costs:** ~$6-11/month
- Railway PostgreSQL: ~$5-10/mo
- Cloudflare R2: $0 (10GB free)
- Domain: $1/mo
- Everything else: Free tiers

---

## 🔗 Key Documentation

- **@docs/weeks/week-XX.md** - Detailed weekly tasks (load current week)
- **@AI_ROLE.md** - AI assistant guidelines
- **@docs/AGENT_WORKFLOW.md** - Agent usage guide (week-by-week)
- **@docs/DECISIONS.md** - Architectural decisions and rationale
- **@FUTURE_FEATURES.md** - Phase 3 paper trading plan and future ideas

---

## 🚀 Running the Project

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

## 🎓 Skills Demonstrated

### Phase 1 (MVP)
- Backend development (FastAPI, Python)
- Frontend development (Streamlit)
- Database design (PostgreSQL)
- ETL pipelines (data processing)
- API design (REST)
- DevOps (Docker, AWS deployment)

### Phase 2 (ML)
- Machine Learning (XGBoost, model training)
- MLOps (model versioning, deployment)
- Data engineering (data lake architecture)
- Feature engineering
- Model explainability (SHAP)
- Time-series validation

---

## 📝 Important Context

- **Rate Limits:** yfinance can get rate limited (429 errors). Use Alpha Vantage as backup.
- **SEC EDGAR:** 10 req/sec limit, no API key needed (Phase 2)
- **Budget Conscious:** Prefer free tiers, avoid paid services unless necessary
- **Portfolio Project:** Everything should be explainable in interviews

---

## 🎯 Success Criteria

**MVP Complete (Week 14):**
- ✅ Live, deployed full-stack application
- ✅ Data pipeline processing 500 stocks
- ✅ Rule-based scoring system
- ✅ Professional documentation

**ML Complete (Week 18):**
- ✅ Data lake with bronze/silver/gold architecture
- ✅ Trained XGBoost model predicting returns
- ✅ SHAP explanations for interpretability
- ✅ Hybrid scoring system (rules + ML)

**Paper Trading Complete (Week 21):**
- ✅ Alpaca paper trading integration
- ✅ Automated buy/sell execution based on scores
- ✅ Risk management (stop losses, position limits)
- ✅ Portfolio dashboard with performance vs S&P 500
- ✅ Strategy validated with real market data

---

**For detailed weekly tasks, see:** `docs/weeks/week-XX.md`
**For full project plan, see:** `PROJECT_PLAN.md` (reference only - load weekly files instead)
