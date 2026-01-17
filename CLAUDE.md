# CLAUDE.md - StockPulse Project Context

**Load this file at the start of each session.**

Last Updated: January 17, 2026

---

## 📚 Related Documentation

This file is your **session starter**. For deeper details, reference these files:

- **@PROJECT_SUMMARY.md** - High-level 18-week timeline and current status (lean version)
- **@docs/weeks/week-XX.md** - Current week's detailed tasks (load only what you need)
- **@AI_ROLE.md** - Guidelines for AI assistants on how to help with this project
- **@docs/AGENT_WORKFLOW.md** - Week-by-week guide for using the 8 specialized agents
- **@docs/DECISIONS.md** - Architectural decisions and rationale

**Quick workflow:** Load `@CLAUDE.md` → Check current week → Load `@docs/weeks/week-XX.md` for detailed tasks

**Note:** `PROJECT_PLAN.md` still exists as a complete reference, but use the weekly files to save tokens

---

## Quick Summary

StockPulse is an ML-powered stock analysis platform that analyzes S&P 500 stocks using rule-based scoring AND machine learning (XGBoost), with SHAP explainability. The goal is to demonstrate data engineering + ML + full-stack skills for job applications.

**Developer**: Junior dev (bootcamp grad), targeting backend/data/ML engineer roles
**Timeline**: ~21 weeks @ 2 hrs/day (18 core + 3 paper trading)
**Budget**: ~$20-30/month

---

## Current Status

**Phase**: 1 (Foundation & MVP)
**Week**: 3 - Database Schema Design COMPLETE
**Next**: Week 5 - ETL Pipeline (Data Ingestion)

### What's Working
- [x] PostgreSQL database (Docker, port 5433)
- [x] Database schema (13 tables, bronze/silver/gold architecture)
- [x] Python environment (venv, all packages installed)
- [x] Streamlit skeleton app (connects to DB, shows factor weights)
- [x] Alpha Vantage API key configured
- [x] yfinance data exploration (50-70 fields identified)
- [x] Scoring methodology defined (5 factors, validated by financial-expert)
- [x] Finance documentation created (finance_101.md, data_sources.md)
- [x] Database models (Pydantic) - `database/models.py`
- [x] Database helpers (CRUD operations) - `database/helpers.py`
- [x] Database utilities (connections) - `database/db_utils.py`
- [x] Database tests (27 passing) - `tests/test_database.py`

### What's Not Yet Built
- [ ] ETL pipeline (ingest, transform, score) - Week 5-7
- [ ] FastAPI backend - Week 8-9
- [ ] ML model (Phase 2) - Week 16-18
- [ ] SEC EDGAR scraper (Phase 2)
- [ ] AWS deployment - Week 13

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
├── .claude/              # Claude Code configuration
│   └── agents/           # Custom specialized agents (8 total)
│       ├── project-lead.md
│       ├── security-specialist.md
│       ├── code-reviewer.md
│       ├── data-engineer.md
│       ├── ml-specialist.md
│       ├── backend-specialist.md
│       ├── frontend-specialist.md
│       └── financial-expert.md
│
├── streamlit/
│   └── app.py            # Dashboard (skeleton)
│
├── backend/              # FastAPI (empty stubs)
├── etl/                  # ETL pipeline (empty stubs)
├── ml/                   # ML training (empty stubs)
│
├── database/
│   ├── __init__.py       # Package exports
│   ├── schema.sql        # Full schema (13 tables)
│   ├── seed.sql          # Factor weights
│   ├── models.py         # Pydantic models for validation
│   ├── db_utils.py       # Connection management
│   ├── helpers.py        # CRUD operations
│   └── migrations/       # Schema migrations
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

## Custom Agents

The project uses 8 specialized agents to handle different aspects of development. These agents are stored in `.claude/agents/` and provide focused expertise for different domains.

### Available Agents

| Agent | Domain | When to Use |
|-------|--------|-------------|
| **project-lead** | Architecture & integration | Phase boundaries, major changes, ensure components work together |
| **security-specialist** | Security & vulnerabilities | Before deployment, API changes, handling sensitive data |
| **code-reviewer** | Code quality & testing | After implementing features, before PRs, catching bugs |
| **data-engineer** | ETL, database, data exploration | Week 2 exploration, Week 5-7 ETL, query optimization |
| **ml-specialist** | ML models & features | Week 16-18 ML training, preventing look-ahead bias |
| **backend-specialist** | API, DevOps, performance | Week 8-9 FastAPI, Week 12-14 AWS deployment |
| **frontend-specialist** | UI/UX, visualizations | Week 10-11 Streamlit dashboard, Week 19 SHAP viz |
| **financial-expert** | Investment factors & methodology | Week 2 metric selection, Week 5-7 scoring design, Week 16-18 feature validation, Week 19 SHAP interpretation |

### How to Use Agents

**Ask Claude to use them explicitly:**
```
Use the data-engineer agent to review my ingest.py for data quality issues
```

**Claude may use them proactively:**
- `code-reviewer` runs after significant code changes
- `security-specialist` runs before deployment
- `project-lead` runs at phase boundaries

### Agent Benefits

- **Focused expertise**: Each agent specializes in one domain
- **Clean context**: Agent work stays isolated from main conversation
- **Parallel work**: Multiple agents can work simultaneously
- **Consistent standards**: Agents enforce best practices

### Current Phase Agents (Week 5 - ETL Pipeline)

For data ingestion, primarily use:
- **data-engineer**: ETL pipeline design, data quality, error handling
- **code-reviewer**: Review ingest.py after implementation
- **financial-expert**: Validate data fields being captured are correct

### Agent Interaction Patterns

**Technical + Financial Validation**
- `data-engineer` identifies available metrics → `financial-expert` validates which ones matter
- `ml-specialist` builds features → `financial-expert` ensures they're financially sound
- `backend-specialist` optimizes queries → `data-engineer` validates data quality

**Quality Gates**
- After coding: `code-reviewer` + `security-specialist`
- Before new phase: `project-lead`
- For methodology: `financial-expert`

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

## Git Branch Strategy

**Gitflow-style workflow:**

| Branch | Purpose |
|--------|---------|
| `main` | Production releases only (MVP, shipped versions) |
| `develop` | Integration branch for ongoing work |
| `feature/etl-pipeline` | Week 5-7: Data ingestion & scoring |
| `feature/fastapi-backend` | Week 8-9: API development |
| `feature/streamlit-dashboard` | Week 10-11: Frontend |
| `feature/ml-scoring` | Week 16-18: XGBoost + SHAP |

**Workflow:** `feature/*` → `develop` → `main` (at MVP/release milestones)

---

## Immediate Next Steps

### Week 5: ETL Pipeline - Data Ingestion (START HERE)
1. Create `feature/etl-pipeline` branch from develop
2. Build `etl/ingest.py` - Fetch stock data from yfinance
3. Handle rate limiting (50 stocks/batch, 2-second delays)
4. Save raw data to bronze layer (raw_stock_data table)
5. Track ETL runs in etl_runs table

### After That
- Week 6: Data transformation (bronze → silver)
- Week 7: Scoring engine (silver → gold)
- Week 8-9: FastAPI backend
- Week 10-11: Streamlit dashboard with real data
- Week 12-14: Integration, testing, deployment
- Week 15-18: ML model (XGBoost) + SHAP explanations
- Week 19-21: Paper trading via Alpaca (see FUTURE_FEATURES.md)

---

## Important Context

- **Rate Limits**: yfinance can get rate limited (429 errors). Use Alpha Vantage as backup.
- **SEC EDGAR**: 10 req/sec limit, no API key needed
- **Budget Conscious**: Prefer free tiers, avoid paid services unless necessary
- **Portfolio Project**: Everything should be explainable in interviews

---

## Links & Documentation

- **Repo**: (local for now)
- **Live Site**: Not deployed yet
- **Key Docs**:
  - `PROJECT_SUMMARY.md` - High-level overview (use this instead of full PROJECT_PLAN.md)
  - `docs/weeks/week-XX.md` - Weekly detailed tasks (load only current week)
  - `AI_ROLE.md` - AI assistant guidelines
  - `docs/AGENT_WORKFLOW.md` - Agent usage guide (week-by-week)
  - `docs/DECISIONS.md` - Architecture decisions
  - `FUTURE_FEATURES.md` - Phase 3 paper trading plan + future ideas
  - `.claude/agents/` - 8 specialized agent definitions
  - `PROJECT_PLAN.md` - Complete reference (2000+ lines - use sparingly to save tokens)
