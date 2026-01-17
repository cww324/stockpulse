# Data Sources Analysis - StockPulse

**Date:** January 17, 2026
**Week:** 2 - Data Exploration
**Status:** Rate-Limited, Using Documentation + Cached Knowledge

---

## Executive Summary

**Primary Data Source:** yfinance (Yahoo Finance API wrapper)
**Backup Source:** Alpha Vantage API
**Rate Limiting Issue:** Yahoo Finance currently rate-limiting (429 errors)
**Recommendation:** Proceed with ETL design based on yfinance documentation + Alpha Vantage fallback

---

## 1. yfinance - Primary Data Source

### Overview
- **Package:** yfinance (Python wrapper for Yahoo Finance)
- **Cost:** Free (no API key required)
- **Rate Limits:** ~2000 requests/hour per IP (soft limit, varies)
- **Data Freshness:** Daily updates (after market close)
- **Coverage:** All US stocks, including S&P 500

### Available Data Structures

#### ticker.info - Primary Source (Recommended)
Pre-calculated financial metrics returned as a dictionary.

**Key Available Fields:**

| Category | Fields | Data Type | Null Risk |
|----------|--------|-----------|-----------|
| **Company Metadata** | symbol, longName, shortName, sector, industry, country | string | Low |
| **Valuation** | trailingPE, forwardPE, priceToBook, priceToSalesTrailing12Months, pegRatio, enterpriseToRevenue, enterpriseToEbitda | float | Medium |
| **Profitability** | returnOnEquity, returnOnAssets, profitMargins, grossMargins, operatingMargins, ebitdaMargins | float | Low-Medium |
| **Growth** | revenueGrowth, earningsGrowth, earningsQuarterlyGrowth | float | Medium |
| **Financial Health** | totalCash, totalDebt, debtToEquity, currentRatio, quickRatio, freeCashflow, totalCashPerShare | float/int | Low-Medium |
| **Dividends** | dividendRate, dividendYield, payoutRatio, fiveYearAvgDividendYield | float | High (many stocks don't pay dividends) |
| **Market Data** | currentPrice, marketCap, enterpriseValue, volume, averageVolume, beta | float/int | Low |
| **Momentum** | fiftyTwoWeekLow, fiftyTwoWeekHigh, fiftyDayAverage, twoHundredDayAverage | float | Low |
| **Analyst Data** | targetMeanPrice, targetHighPrice, targetLowPrice, recommendationKey, numberOfAnalystOpinions | float/string | Medium-High |

**Total Useful Fields:** ~50-70 fields per stock

**Data Completeness:**
- Metadata: 95-100%
- Core financials: 70-90%
- Dividends: 40-60% (many stocks don't pay dividends)
- Analyst data: 60-80%

#### ticker.history() - Price Data
Historical OHLCV (Open, High, Low, Close, Volume) data.

**Available Columns:**
- Open
- High
- Low
- Close
- Volume
- Dividends
- Stock Splits

**Periods Available:**
- 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max

**Use Cases:**
- Momentum calculation (3-month, 6-month returns)
- Moving averages (custom calculations)
- Volatility metrics
- Price trends

**Data Quality:** Excellent (rarely missing data)

#### ticker.financials - Income Statement
Quarterly and annual income statement data.

**Note:** Most useful metrics are already in `ticker.info` as ratios. We likely won't need this.

#### ticker.balance_sheet - Balance Sheet
Quarterly and annual balance sheet data.

**Note:** Most useful metrics are already in `ticker.info` as ratios. We likely won't need this.

#### ticker.cashflow - Cash Flow Statement
Quarterly and annual cash flow data.

**Note:** Free cash flow already available in `ticker.info`. We likely won't need this.

---

## 2. Alpha Vantage - Backup Source

### Overview
- **Cost:** Free tier (25 requests/day)
- **API Key:** Required (we have one configured)
- **Rate Limits:** 25 req/day (free), 75 req/min (premium ~$50/mo)
- **Use Case:** Fallback when yfinance fails or for validation

### Available Endpoints

#### Company Overview
Similar to yfinance info, provides:
- Market cap
- P/E ratio
- PEG ratio
- Dividend yield
- EPS
- ROE
- Profit margin
- Beta

**Endpoint:** `OVERVIEW`

#### Time Series Data
Daily, weekly, monthly price data.

**Endpoints:** `TIME_SERIES_DAILY`, `TIME_SERIES_WEEKLY`

### Integration Strategy

**Primary:** yfinance
**Fallback:** Alpha Vantage when yfinance returns null or fails

---

## 3. Data Quality Assessment

### Expected Issues

#### Null Values
**High-Risk Fields (expect 20-40% nulls):**
- forwardPE (growth stocks may not have estimates)
- dividendYield (many stocks don't pay dividends)
- pegRatio (requires earnings growth estimate)
- targetMeanPrice (not all stocks covered by analysts)

**Medium-Risk Fields (expect 5-20% nulls):**
- debtToEquity (young companies may not have debt)
- earningsGrowth (recent IPOs may lack history)
- fiveYearAvgDividendYield (stocks < 5 years old)

**Low-Risk Fields (expect < 5% nulls):**
- marketCap
- currentPrice
- trailingPE
- profitMargins
- returnOnEquity
- sector, industry

#### Data Freshness
- ticker.info updates: Daily after market close (~4 PM ET)
- Financial statements: Quarterly (within days of earnings release)
- Price data: Real-time to 15-minute delay (depending on source)

**Recommendation:** Run ETL Sunday nights for weekly updates.

#### Data Validation Concerns

**Watch for:**
1. **Outliers:** P/E > 1000 (unprofitable or tiny earnings)
2. **Negative values:** Some ratios can be negative (ROE when equity is negative)
3. **Missing sectors:** Small/new stocks may lack sector classification
4. **Stale data:** Check timestamp to ensure data is recent

---

## 4. Recommended Fields for Scoring System

Based on financial soundness + data availability:

### CRITICAL FIELDS (Must Have)

**Valuation (35% weight):**
- trailingPE ✅
- priceToBook ✅
- priceToSalesTrailing12Months ✅
- Current vs 52-week high/low ✅

**Profitability (25% weight):**
- returnOnEquity ✅
- profitMargins ✅
- operatingMargins ✅

**Growth (20% weight):**
- revenueGrowth ✅
- earningsGrowth ✅

**Financial Health (15% weight):**
- debtToEquity ✅
- currentRatio ✅

**Momentum (5% weight):**
- 3-month return (calculated from history) ✅
- 6-month return (calculated from history) ✅

### OPTIONAL FIELDS (Nice to Have)

**Quality Indicators:**
- grossMargins
- freeCashflow
- returnOnAssets

**Dividends (if applicable):**
- dividendYield
- payoutRatio

**Market Data:**
- beta (volatility)
- marketCap (company size)

---

## 5. Rate Limiting Strategy

### Current Issue
Yahoo Finance is rate-limiting our requests (429 errors).

### Solutions

#### Option 1: Wait and Retry
- Wait 30-60 minutes between failed attempts
- Use exponential backoff: 1min → 2min → 5min → 10min
- Cache successful requests

#### Option 2: Proxy Rotation (Future)
- Use rotating proxies (costs money)
- Not recommended for portfolio project

#### Option 3: Alpha Vantage Fallback
- Try yfinance first
- If fails, use Alpha Vantage
- Limited to 25 stocks/day on free tier

#### Option 4: Batch + Schedule
- Fetch 50 stocks per hour (well below limit)
- Run ETL over 10 hours (500 stocks ÷ 50/hr)
- Sunday morning start → finish by evening

**Recommended:** Option 4 (Batch + Schedule) for production ETL

### Implementation
```python
import time
import yfinance as yf

def fetch_with_retry(ticker, max_retries=3):
    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(ticker)
            data = stock.info
            return data
        except Exception as e:
            if "429" in str(e):
                wait_time = 2 ** attempt * 60  # 1min, 2min, 4min
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    return None  # Failed after retries
```

---

## 6. Data Lake Architecture

### Bronze Layer (Raw)
Store exact API responses as JSON.

**Purpose:** Point-in-time record, reproducibility, debugging

**Schema:**
```sql
CREATE TABLE raw_stock_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10),
    data_source VARCHAR(20),  -- 'yfinance' or 'alphavantage'
    raw_json JSONB,
    fetched_at TIMESTAMP DEFAULT NOW()
);
```

### Silver Layer (Cleaned)
Parse JSON, handle nulls, validate types.

**Purpose:** Clean data ready for scoring

**Schema:**
```sql
CREATE TABLE processed_stocks (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10),
    analysis_date DATE,
    -- Company info
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    -- Valuation
    trailing_pe NUMERIC,
    price_to_book NUMERIC,
    price_to_sales NUMERIC,
    -- Profitability
    return_on_equity NUMERIC,
    profit_margin NUMERIC,
    operating_margin NUMERIC,
    -- Growth
    revenue_growth NUMERIC,
    earnings_growth NUMERIC,
    -- Financial Health
    debt_to_equity NUMERIC,
    current_ratio NUMERIC,
    -- Market data
    market_cap BIGINT,
    current_price NUMERIC,
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, analysis_date)
);
```

### Gold Layer (Scored)
Calculated scores and rankings.

**Purpose:** Serving layer for API/dashboard

**Schema:**
```sql
CREATE TABLE stock_scores (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10),
    analysis_date DATE,
    -- Factor scores
    valuation_score NUMERIC,
    profitability_score NUMERIC,
    growth_score NUMERIC,
    health_score NUMERIC,
    momentum_score NUMERIC,
    -- Overall
    total_score NUMERIC,
    rank INTEGER,
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(ticker, analysis_date)
);
```

---

## 7. Field Mapping Reference

### yfinance → Our Database

| yfinance Field | Our Field | Transformation |
|----------------|-----------|----------------|
| trailingPE | trailing_pe | Direct |
| priceToBook | price_to_book | Direct |
| priceToSalesTrailing12Months | price_to_sales | Direct |
| returnOnEquity | return_on_equity | Direct |
| profitMargins | profit_margin | Direct |
| operatingMargins | operating_margin | Direct |
| revenueGrowth | revenue_growth | Direct |
| earningsGrowth | earnings_growth | Direct |
| debtToEquity | debt_to_equity | Direct |
| currentRatio | current_ratio | Direct |
| marketCap | market_cap | Direct |
| currentPrice | current_price | Direct |
| sector | sector | Direct |
| industry | industry | Direct |
| longName | company_name | Direct |

### Calculated Fields

| Field | Calculation | Source |
|-------|-------------|--------|
| return_3m | (price_now - price_3m_ago) / price_3m_ago | ticker.history() |
| return_6m | (price_now - price_6m_ago) / price_6m_ago | ticker.history() |
| price_vs_52w_high | current_price / fiftyTwoWeekHigh | ticker.info |

---

## 8. Next Steps

### Immediate (Week 2)
- ✅ Document yfinance structure (this file)
- ⏳ Wait for rate limit reset, test with 5-10 stocks
- ⏳ Validate field availability across sectors
- ⏳ Define null handling strategy
- ⏳ Create financial metrics cheat sheet

### Week 3-4 (Database Design)
- Finalize schema based on confirmed available fields
- Add indexes for common queries
- Plan for missing data handling

### Week 5-7 (ETL Pipeline)
- Implement batch fetching with delays
- Build retry logic with exponential backoff
- Add Alpha Vantage fallback
- Test with 100 stocks

---

## 9. Risk Mitigation

### Rate Limiting
**Risk:** Can't fetch 500 stocks quickly
**Mitigation:** Batch over 10+ hours, use caching, add delays

### Missing Data
**Risk:** Critical fields null for some stocks
**Mitigation:**
- Use sector medians for imputation
- Exclude stocks with >3 critical nulls
- Flag incomplete data in dashboard

### API Changes
**Risk:** yfinance breaks (has happened before)
**Mitigation:**
- Have Alpha Vantage fallback ready
- Monitor yfinance GitHub for issues
- Cache data aggressively

### Cost Overruns
**Risk:** Need paid API
**Mitigation:**
- Free tier works for 500 stocks with patience
- Alpha Vantage premium only if absolutely necessary

---

## 10. References

- yfinance documentation: https://github.com/ranaroussi/yfinance
- Alpha Vantage docs: https://www.alphavantage.co/documentation/
- Yahoo Finance rate limits: https://github.com/ranaroussi/yfinance/issues
- S&P 500 list: https://en.wikipedia.org/wiki/List_of_S%26P_500_companies

---

**Status:** Documentation complete. Awaiting rate limit reset to validate with real data.
