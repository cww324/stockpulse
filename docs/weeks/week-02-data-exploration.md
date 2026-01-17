# Week 2: Data Exploration

**Goal:** Understand what data is available and how to use it

**Duration:** 14 hours (2 hrs/day × 7 days)

**Status:** COMPLETE

---

## 🎯 Week Objective

By the end of this week, you should:
- Understand the structure of data from yfinance
- Know which financial metrics are available
- Have working calculations for 5 sample stocks
- Have defined the initial scoring methodology
- Be ready to design the database schema (Week 3)

---

## 📋 Detailed Checklist

### 1. Jupyter Notebook Setup (2 hours)

- [x] Install Jupyter in virtual environment
  ```bash
  pip install jupyter ipykernel
  python -m ipykernel install --user --name=stockpulse
  ```
- [x] Create `notebooks/01_data_exploration.ipynb`
- [x] Test: can run Jupyter and import libraries
  ```bash
  jupyter notebook
  ```
- [x] Import test: pandas, yfinance, numpy should all work

**Deliverable:** Working Jupyter notebook that can import all necessary libraries

---

### 2. Experiment with yfinance (4 hours)

- [x] **Fetch data for 5 test stocks**
  - Test stocks: AAPL, MSFT, GOOGL, AMZN, NVDA
  - Sample code:
    ```python
    import yfinance as yf

    ticker = yf.Ticker("AAPL")
    info = ticker.info
    history = ticker.history(period="1y")
    financials = ticker.financials
    ```

- [x] **Understand structure: OHLCV (Open, High, Low, Close, Volume)**
  - What fields are in `ticker.info`? → 50-70 fields identified
  - What's in `ticker.history()`? → OHLCV price data
  - What's in `ticker.financials`? → Income statement (not needed, metrics in info)
  - What's in `ticker.balance_sheet`? → Balance sheet (not needed, metrics in info)
  - What's in `ticker.cashflow`? → Cash flow (not needed, metrics in info)

- [x] **Check data quality**
  - Missing values: 70-90% completeness for critical fields
  - Outliers: P/E > 100, negative margins flagged
  - Consistency: Similar structure across stocks

- [x] **Document findings in `docs/data_sources.md`**
  - Available fields list - comprehensive
  - Data quality notes - documented
  - Rate limiting strategy - batch 50/hour with delays
  - Backup plan (Alpha Vantage) documented

**Deliverable:** `docs/data_sources.md` with comprehensive field list and quality notes

---

### 3. Learn Financial Metrics (3 hours)

**Read and understand these key metrics:**

- [x] **Valuation Ratios**
  - P/E (Price-to-Earnings): What it means, why it matters
  - P/B (Price-to-Book): What it means, typical values
  - P/S (Price-to-Sales): When it's useful
  - Forward P/E vs Trailing P/E

- [x] **Profitability Metrics**
  - ROE (Return on Equity): Formula, what's "good"
  - ROA (Return on Assets): Added to prevent leverage inflation
  - Profit Margin: Gross vs Operating vs Net
  - Earnings growth YoY

- [x] **Financial Health Metrics**
  - Debt-to-Equity ratio: What's healthy varies by sector
  - Current Ratio: Liquidity measure
  - Free Cash Flow: Why it matters

- [x] **Create cheat sheet: `docs/finance_101.md`**
  - One-paragraph explanation of each metric
  - Formula (if simple)
  - What value ranges are "good" vs "bad"
  - Example with real numbers

**Resources:**
- Investopedia (free, great explanations)
- "The Little Book of Valuation" concepts
- Compare real stocks on Yahoo Finance

**Deliverable:** `docs/finance_101.md` - Your personal reference guide

---

### 4. Define Scoring Methodology (3 hours)

- [x] **Pick 5 factors for rule-based scoring**
  - Final factors (validated by financial-expert):
    1. **Valuation Score (30%)** - P/E, P/B, P/S, dividend yield
    2. **Profitability Score (25%)** - ROE (leverage-adjusted), ROA, margins
    3. **Growth Score (20%)** - Revenue growth, Earnings growth
    4. **Momentum Score (15%)** - 6m and 12m returns (increased from 5%)
    5. **Health Score (10%)** - Debt-to-Equity, Current ratio

- [x] **Decide initial weights**
  - Valuation: 30%, Profitability: 25%, Growth: 20%, Momentum: 15%, Health: 10%
  - Validated by financial-expert agent based on academic research

- [x] **Document reasoning in `docs/scoring_methodology.md`**
  - Why these 5 factors? Academic research (Fama-French, Jegadeesh-Titman)
  - How will each be scored (0-100 scale)? Sector-relative for valuation/profitability
  - How to normalize? Sector median comparison
  - How to handle outliers? Thresholds and caps
  - How to combine into final score? Weighted average with value trap detection

**Important:** This doesn't have to be perfect! Start simple, iterate later.

**Deliverable:** `docs/scoring_methodology.md` with initial methodology design

---

### 5. Test Calculations (2 hours)

- [x] **Manually calculate scores for 5 test stocks**
  - Sample calculations documented in scoring_methodology.md
  - AAPL example walkthrough included
  - Composite score calculation explained

- [x] **Sanity check: Does the ranking make sense?**
  - Methodology validated by financial-expert agent
  - Value trap detection added
  - Leverage adjustment for ROE added

- [x] **Adjust factors/weights if needed**
  - Momentum increased from 5% to 15% (academic research)
  - Health reduced from 15% to 10% (already captured in profitability)
  - Dividend yield added to valuation
  - ROA added to profitability

**Deliverable:** Updated notebook with working calculations and sensible rankings

---

## 🤖 Agents to Use This Week

### Primary Agents

1. **data-engineer** (Use throughout the week)
   - Test yfinance and understand data structure
   - Identify data quality issues
   - Recommend data refresh frequency
   - Validate that data is sufficient for scoring

2. **financial-expert** (Use in Steps 3-5)
   - Which financial metrics actually matter for alpha generation?
   - Validate that P/E, ROE, dividend yield, etc. are sound choices
   - Recommend factor weighting strategy
   - Flag any metrics that are financially questionable
   - Review scoring methodology for defensibility

### Why Both?
- `data-engineer` tells you WHAT data is available
- `financial-expert` tells you what MATTERS financially
- Together they ensure your methodology is both technically sound AND financially defensible

### How to Use Them

```
# After exploring yfinance structure:
"Use the data-engineer agent to review the data quality issues I found"

# When selecting metrics:
"Use the financial-expert agent to validate my factor selection"

# Before finalizing methodology:
"Use both data-engineer and financial-expert agents to review
my scoring methodology in docs/scoring_methodology.md"
```

---

## 📊 Expected Outputs

By end of Week 2, you should have:

1. ✅ **`notebooks/01_data_exploration.ipynb`**
   - Working code that fetches and explores data
   - Calculations for all 5 factors
   - Rankings for 5 test stocks

2. ✅ **`docs/data_sources.md`**
   - List of available fields from yfinance
   - Data quality notes
   - Any limitations discovered

3. ✅ **`docs/finance_101.md`**
   - Personal cheat sheet for financial metrics
   - Definitions and examples

4. ✅ **`docs/scoring_methodology.md`**
   - Initial scoring methodology
   - 5 factors defined
   - Weighting strategy
   - Normalization approach

5. ✅ **Validated by agents**
   - Data quality checked by data-engineer
   - Methodology validated by financial-expert

---

## 💡 Tips & Tricks

### Avoid These Pitfalls

❌ **Don't spend 10 hours reading about finance** - You can learn as you go
❌ **Don't try to create the perfect methodology** - Start simple, iterate later
❌ **Don't get stuck on missing data** - Note it and move on
❌ **Don't try to fetch all 500 stocks yet** - Just use 5 test stocks this week

### Do These Instead

✅ **Focus on understanding, not perfection** - Goal is to be ready for Week 3
✅ **Document everything you learn** - Future you will thank you
✅ **Use real examples** - Calculate metrics for AAPL to understand them
✅ **Validate with experts** - Use the agents to check your work

---

## 🚧 Blockers & Solutions

### Common Issues

**Issue:** yfinance rate limiting (429 errors)
- **Solution:** Add delays between requests (time.sleep(1))
- **Solution:** Use Alpha Vantage as backup
- **Solution:** Only fetch 5 stocks this week (not 500)

**Issue:** Confused about financial metrics
- **Solution:** Use Investopedia for clear explanations
- **Solution:** Ask the financial-expert agent
- **Solution:** Focus on just 5-7 key metrics initially

**Issue:** Not sure if methodology is good
- **Solution:** It doesn't have to be perfect! Start simple
- **Solution:** Use financial-expert agent for validation
- **Solution:** Compare results to analyst ratings (sanity check)

---

## 📚 Recommended Reading (Optional)

**If you have extra time:**
- Investopedia: "Financial Ratios" section
- "The Little Book That Still Beats the Market" by Joel Greenblatt
- yfinance documentation: https://pypi.org/project/yfinance/

**But remember:** 2 hours/day focus is better than 10 hours of reading!

---

## ✅ Definition of Done

**This week is DONE when:**

- [x] Jupyter notebook runs without errors
- [x] Can fetch data for 5 stocks using yfinance
- [x] Understand what P/E, ROE, and other key metrics mean
- [x] Have documented scoring methodology
- [x] Have working calculations that rank 5 stocks
- [x] Rankings make intuitive sense (validated)
- [x] All 4 documentation files created
- [x] Data quality reviewed by data-engineer agent
- [x] Methodology validated by financial-expert agent

**Ready to move to Week 3:** Database schema design

---

## 🎉 Week 2 Celebration

Once you complete this week, you will:
- ✅ Understand financial data structure
- ✅ Know which metrics matter for stock analysis
- ✅ Have a working scoring methodology
- ✅ Be ready to design your database schema
- ✅ Have taken a big step toward your goal!

**Take a moment to celebrate progress!** 🎊

---

**Next Week:** Week 3 - Database Schema Design
**See:** `docs/weeks/week-03-database-schema.md` (when you get there)
