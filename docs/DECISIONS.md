# Architecture & Infrastructure Decisions

This document tracks key decisions made during planning and development.

---

## Decision 1: Frontend Framework

**Date:** January 2026
**Status:** Under consideration

### Options Discussed

| Option | Pros | Cons |
|--------|------|------|
| **Next.js/React/Tailwind** | Most in-demand frontend skill, large ecosystem | More complex, longer to build |
| **Streamlit** (Python) | Build in days not weeks, stays in Python, great for data/ML demos | Less impressive for frontend roles |
| **Dash (Plotly)** | Python-based, better charts | Steeper learning curve than Streamlit |

### Recommendation
- If targeting **backend/data/ML roles**: Streamlit (saves 4-6 weeks)
- If targeting **full-stack roles**: Next.js/React

### Decision
TBD

---

## Decision 2: Hosting Platform

**Date:** January 2026
**Status:** Under consideration

### Original Plan
- Vercel (frontend)
- Railway (backend + PostgreSQL)
- Cloudflare R2 or S3 (data lake)

### Alternative: Full AWS Stack
More impressive for job applications - AWS skills are highly valued.

| Service | Purpose | Free Tier | After Free Tier |
|---------|---------|-----------|-----------------|
| EC2 t3.micro | App server (Streamlit/FastAPI + Nginx) | 12 months | ~$8/mo |
| RDS db.t3.micro | PostgreSQL database | 12 months | ~$15/mo |
| S3 | Data lake storage | 5GB free | ~$0.25/mo |
| Route 53 | DNS (optional, can use Cloudflare) | N/A | ~$0.50/mo |

### Recommendation
AWS App Runner - scales to zero, ~$0 when idle, simpler than EC2.

### Decision
**AWS App Runner** for deployment (scale to zero, auto-sleep, ~10 sec cold start). Will set up during deployment phase.

---

## Decision 3: DNS & Email

**Date:** January 2026
**Status:** Under consideration

### Current Setup
- Domain registered at GoDaddy
- Email hosting paid through GoDaddy (includes Microsoft 365)
- Separate personal Office 365 subscription (possibly redundant)

### Recommended Setup

**Move DNS to Cloudflare (free):**
1. Sign up at cloudflare.com
2. Add domain, Cloudflare imports existing DNS records
3. Get Cloudflare nameservers (e.g., `anna.ns.cloudflare.com`)
4. In GoDaddy: Domain Settings → Nameservers → Custom → Enter Cloudflare NS
5. Wait 15min-48hrs for propagation

**Benefits of Cloudflare:**
- Faster DNS resolution
- Free SSL certificates
- Free email forwarding (Cloudflare Email Routing)
- Free CDN/caching
- DDoS protection
- Cleaner interface than GoDaddy

**Email forwarding setup (after DNS migration):**
1. In Cloudflare dashboard → Email → Email Routing
2. Add destination address (your personal email)
3. Create routing rule: `you@yourdomain.com` → `yourpersonal@gmail.com`
4. Verify destination email
5. Done - free professional email address

**Cost savings:** Can cancel GoDaddy email hosting (~$70/yr saved)

### Decision
TBD - Review when starting Week 1

---

## Decision 4: Revised Architecture (If AWS + Streamlit)

```
┌─────────────────────────────────────────┐
│      Cloudflare (DNS + SSL + CDN)       │
│      stockpulse.yourdomain.com          │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    EC2 Instance (t3.micro/small)        │
│    ├── Nginx (reverse proxy + SSL)      │
│    ├── Streamlit (dashboard on :8501)   │
│    └── FastAPI (API on :8000)           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         RDS PostgreSQL                  │
│         (db.t3.micro - free tier)       │
└─────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│              S3 Bucket                  │
│    ├── /bronze/ (raw JSON)              │
│    ├── /silver/ (cleaned Parquet)       │
│    ├── /gold/ (ML features)             │
│    └── /models/ (XGBoost models)        │
└─────────────────────────────────────────┘
```

---

---

## Decision 5: Add Insider/Congressional Trading Data

**Date:** January 2026
**Status:** Approved - Add to Phase 2

### The Feature

Add "smart money" signals to the stock analysis:
1. **Corporate Insiders** (SEC Form 4) - When CEOs/CFOs buy their own stock
2. **Congressional Trading** (STOCK Act) - When members of Congress trade

### Why This Makes Sense
- Structured data (no NLP needed, unlike Reddit sentiment)
- Legally required disclosures (verifiable, not people lying)
- Proven signal (studies show insider buying correlates with outperformance)
- Great interview talking point
- Doesn't blow up the scope

### Data Sources

| Source | Data | Cost | Approach |
|--------|------|------|----------|
| **SEC EDGAR** | Corporate insider trades (Form 4) | Free | **Build our own scraper** |
| House/Senate disclosures | Congressional trades | Free | **Build our own scraper** |
| Quiver Quantitative | Backup/validation | Free tier | Only if needed |

### Why Build Our Own SEC Scraper (Not Use Paid APIs)

**Interview gold:** "Instead of paying for a third-party API, I built my own data pipeline that ingests SEC EDGAR Form 4 filings, parses the XML, and extracts insider trading signals."

SEC EDGAR is public government data:
- No API key needed
- Rate limit: 10 requests/second (generous)
- Form 4 = insider buy/sell transactions (filed within 2 business days)

```python
# SEC EDGAR endpoints:
# Recent Form 4 filings (RSS):
# https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&output=atom

# By company:
# https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=AAPL&type=4&output=atom
```

### Implementation Plan (Phase 2, Weeks 15-21)

**Option B chosen: ML Feature integration + Build our own scrapers**

#### Checklist

**SEC EDGAR Scraper (Insider Trades)**
- [ ] Research SEC EDGAR RSS feed and XML format
- [ ] Build Form 4 fetcher (get recent filings)
- [ ] Build XML parser (extract: insider, ticker, buy/sell, shares, price)
- [ ] Store raw filings in bronze layer (S3)
- [ ] Process to silver layer (cleaned data)
- [ ] Load into `insider_trades` table
- [ ] Test with sample companies (AAPL, NVDA, etc.)

**Congressional Trades Scraper**
- [ ] Research House/Senate disclosure formats
- [ ] Build scraper for congressional filings
- [ ] Parse and extract trade data
- [ ] Store in `congressional_trades` table
- [ ] Test and validate data

**ML Feature Integration**
- [ ] Create `insider_buy_last_30d` feature (boolean or count)
- [ ] Create `insider_buy_amount` feature (dollar value)
- [ ] Create `congress_buy_last_30d` feature (boolean or count)
- [ ] Add features to XGBoost training pipeline
- [ ] Evaluate feature importance

**Dashboard Enhancements**
- [ ] Badge on stock cards: "👔 CEO bought" / "🏛️ Congress bought"
- [ ] "Smart Money" tab showing recent insider activity
- [ ] Filter/sort by insider activity

### Architecture Update

```
Data Sources:
├── yfinance (fundamentals, prices)
├── Alpha Vantage (backup fundamentals)
├── SEC EDGAR (insider Form 4 filings)      ← NEW
└── Quiver/Capitol Trades (congress trades) ← NEW

XGBoost Features:
├── Fundamental (P/E, ROE, margins, etc.)
├── Technical (momentum, moving averages)
├── insider_buy_signal                       ← NEW
└── congress_buy_signal                      ← NEW
```

### Estimated Additional Time
- 2-3 weeks added to Phase 2
- Total project timeline: ~20-21 weeks instead of 18

### Interview Talking Points
- "I incorporated SEC Form 4 insider trading data as an ML feature"
- "The model learns whether insider buying is predictive of future returns"
- "I built a data pipeline that combines fundamental data with alternative data sources"

---

## Notes

- AWS free tier lasts 12 months - great for this project timeline
- Cloudflare is free forever for these features
- Can always migrate later if needed
