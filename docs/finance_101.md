# Finance 101 - StockPulse Reference Guide

**Purpose:** Quick reference for financial metrics used in StockPulse scoring
**Audience:** Developer learning finance while building
**Last Updated:** January 17, 2026

---

## Table of Contents
1. [Valuation Ratios](#valuation-ratios)
2. [Profitability Metrics](#profitability-metrics)
3. [Growth Metrics](#growth-metrics)
4. [Financial Health Metrics](#financial-health-metrics)
5. [Momentum Metrics](#momentum-metrics)
6. [Sector Differences](#sector-differences)
7. [Common Pitfalls](#common-pitfalls)

---

## Valuation Ratios

### P/E Ratio (Price-to-Earnings)

**What it measures:** How much investors pay for $1 of earnings

**Formula:** `Stock Price / Earnings Per Share`

**Example:**
- Stock price: $100
- Earnings per share: $5/year
- P/E = 100 / 5 = **20**

**Interpretation:**
| P/E Range | Meaning |
|-----------|---------|
| < 10 | Very cheap (or troubled company) |
| 10-20 | Reasonably valued |
| 20-30 | Growth expectations priced in |
| > 30 | Expensive (or high-growth company) |

**Why investors care:**
- Lower P/E = cheaper stock (potentially undervalued)
- BUT low P/E can mean the company is declining (value trap)
- Must compare to sector (tech has higher P/E than utilities)

**How we use it:** Sector-relative comparison. Score higher if below sector median.

---

### P/B Ratio (Price-to-Book)

**What it measures:** How much investors pay for $1 of book value (assets - liabilities)

**Formula:** `Stock Price / Book Value Per Share`

**Example:**
- Stock price: $50
- Book value per share: $25
- P/B = 50 / 25 = **2.0**

**Interpretation:**
| P/B Range | Meaning |
|-----------|---------|
| < 1.0 | Trading below asset value (potentially undervalued) |
| 1.0-3.0 | Normal range |
| > 3.0 | Premium valuation (brand/intangibles valued) |

**Why investors care:**
- P/B < 1.0 means you can theoretically buy assets for less than they're worth
- BUT book value doesn't capture intangible assets (brand, patents, software)
- Less meaningful for tech companies (their value is in IP, not physical assets)

**How we use it:** Sector-relative. Tech naturally has higher P/B.

---

### P/S Ratio (Price-to-Sales)

**What it measures:** How much investors pay for $1 of revenue

**Formula:** `Market Cap / Annual Revenue`

**Example:**
- Market cap: $10B
- Annual revenue: $2B
- P/S = 10 / 2 = **5.0**

**Interpretation:**
| P/S Range | Meaning |
|-----------|---------|
| < 1.0 | Very cheap |
| 1.0-3.0 | Reasonable |
| > 5.0 | Expensive (high growth expected) |

**Why investors care:**
- Useful for unprofitable companies (can't use P/E)
- Revenue is harder to manipulate than earnings
- BUT ignores profitability (high revenue means nothing if unprofitable)

**How we use it:** Sector-relative comparison.

---

### Dividend Yield

**What it measures:** Annual dividend as percentage of stock price

**Formula:** `Annual Dividend / Stock Price`

**Example:**
- Annual dividend: $2 per share
- Stock price: $50
- Yield = 2 / 50 = **4%**

**Interpretation:**
| Yield Range | Meaning |
|-------------|---------|
| 0% | No dividend (growth stocks often reinvest) |
| 1-2% | Low yield (common for growth companies) |
| 2-4% | Moderate yield (balanced companies) |
| 4-6% | High yield (income-focused stocks) |
| > 6% | Very high yield (could be a warning sign) |

**Why investors care:**
- Dividend = tangible return while you hold the stock
- High yield can indicate undervaluation OR distress
- Companies that grow dividends tend to outperform

**Warning - Value Trap:**
If yield > 8% AND company is unprofitable, it's likely a trap (dividend will be cut).

**How we use it:** Part of valuation score. Higher is better, with trap detection.

---

## Profitability Metrics

### ROE (Return on Equity)

**What it measures:** How much profit a company generates with shareholder money

**Formula:** `Net Income / Shareholder Equity`

**Example:**
- Net income: $10M
- Shareholder equity: $50M
- ROE = 10 / 50 = **20%**

**Interpretation:**
| ROE Range | Meaning |
|-----------|---------|
| < 10% | Below average |
| 10-15% | Acceptable |
| 15-20% | Good |
| > 20% | Excellent |

**Why investors care:**
- Higher ROE = more efficient use of capital
- Warren Buffett famously looks for ROE > 15%
- Consistent high ROE = competitive advantage

**Important Caveat - Leverage:**
High debt inflates ROE! A company can boost ROE by taking on debt.

**Example:**
```
Company A: $100M income, $1000M equity → ROE = 10%
Company B: $100M income, $200M equity (borrowed $800M) → ROE = 50%
```
Company B looks better but is just more leveraged (riskier).

**How we use it:** Sector-relative, with leverage adjustment.

---

### ROA (Return on Assets)

**What it measures:** How much profit a company generates with ALL its assets

**Formula:** `Net Income / Total Assets`

**Example:**
- Net income: $10M
- Total assets: $100M
- ROA = 10 / 100 = **10%**

**Interpretation:**
| ROA Range | Meaning |
|-----------|---------|
| < 5% | Below average |
| 5-10% | Acceptable |
| > 10% | Good |
| > 15% | Excellent |

**Why investors care:**
- ROA is NOT inflated by leverage (unlike ROE)
- Better for comparing companies with different capital structures
- Tells you how efficiently ALL capital is being used

**How we use it:** Added to profitability score to balance ROE.

---

### Profit Margin (Net Margin)

**What it measures:** Percentage of revenue that becomes profit

**Formula:** `Net Income / Revenue`

**Example:**
- Revenue: $100M
- Net income: $15M
- Margin = 15 / 100 = **15%**

**Interpretation:**
| Margin Range | Meaning |
|--------------|---------|
| < 0% | Unprofitable (losing money) |
| 0-5% | Low margin (retail, grocery) |
| 5-15% | Moderate margin (most industries) |
| 15-25% | High margin (good business) |
| > 25% | Very high (software, luxury goods) |

**Why investors care:**
- Higher margin = more pricing power
- Harder to manipulate than earnings
- Varies significantly by industry (must compare to sector)

**How we use it:** Sector-relative comparison.

---

### Operating Margin

**What it measures:** Profit from core operations (before interest/taxes)

**Formula:** `Operating Income / Revenue`

**Example:**
- Revenue: $100M
- Operating income: $20M
- Operating margin = 20 / 100 = **20%**

**Why it differs from net margin:**
- Operating margin excludes interest expense and taxes
- Better measure of operational efficiency
- Less affected by financing decisions

**How we use it:** Part of profitability score, sector-relative.

---

## Growth Metrics

### Revenue Growth (YoY)

**What it measures:** Year-over-year increase in sales

**Formula:** `(Revenue This Year - Revenue Last Year) / Revenue Last Year`

**Example:**
- Last year revenue: $100M
- This year revenue: $115M
- Growth = (115 - 100) / 100 = **15%**

**Interpretation:**
| Growth Rate | Meaning |
|-------------|---------|
| < 0% | Declining (red flag) |
| 0-5% | Slow growth (mature company) |
| 5-15% | Moderate growth |
| 15-25% | Strong growth |
| > 25% | Hypergrowth (often unprofitable) |

**Why investors care:**
- Revenue growth is harder to manipulate than earnings
- Shows demand for company's products/services
- Declining revenue is a major warning sign

**How we use it:** Higher growth = higher score, with diminishing returns at very high levels.

---

### Earnings Growth (YoY)

**What it measures:** Year-over-year increase in profit

**Formula:** `(EPS This Year - EPS Last Year) / EPS Last Year`

**Why investors care:**
- Earnings growth drives stock price appreciation
- Can be more volatile than revenue growth
- Easier to manipulate (buybacks, one-time items)

**How we use it:** Combined with revenue growth (50/50 weight).

---

## Financial Health Metrics

### Debt-to-Equity Ratio

**What it measures:** How much debt vs shareholder equity

**Formula:** `Total Debt / Shareholder Equity`

**Example:**
- Total debt: $40M
- Equity: $100M
- D/E = 40 / 100 = **0.4**

**Interpretation:**
| D/E Ratio | Meaning |
|-----------|---------|
| < 0.5 | Conservative (low debt) |
| 0.5-1.0 | Moderate |
| 1.0-2.0 | Elevated |
| > 2.0 | High leverage (risky) |

**Sector differences:**
- Utilities: High debt is normal (2.0+ is fine)
- Tech: Should be low (< 0.5 expected)
- Banks: Different calculation (leverage IS their business)

**Why investors care:**
- High debt = more risk in downturns
- Interest payments reduce profits
- Can't raise more debt in crisis

**How we use it:** Lower is better, with sector-aware thresholds.

---

### Current Ratio

**What it measures:** Ability to pay short-term obligations

**Formula:** `Current Assets / Current Liabilities`

**Example:**
- Current assets: $50M
- Current liabilities: $25M
- Current ratio = 50 / 25 = **2.0**

**Interpretation:**
| Ratio | Meaning |
|-------|---------|
| < 1.0 | Danger zone (can't pay bills) |
| 1.0-1.5 | Tight but okay |
| 1.5-2.5 | Healthy |
| > 3.0 | Maybe too conservative |

**Why investors care:**
- Below 1.0 means potential liquidity crisis
- Too high means inefficient use of capital
- ~2.0 is the sweet spot for most companies

**How we use it:** Target around 2.0, penalize extremes.

---

## Momentum Metrics

### 6-Month Return

**What it measures:** Stock price change over 6 months

**Formula:** `(Price Now - Price 6 Months Ago) / Price 6 Months Ago`

**Example:**
- Price 6 months ago: $100
- Price now: $115
- Return = (115 - 100) / 100 = **15%**

**Why investors care:**
- Academic research shows momentum persists (winners keep winning)
- 6-12 month timeframe is the sweet spot
- Negative correlation with value = diversification

**How we use it:** Part of momentum score (50% weight).

---

### 12-Month Return

**What it measures:** Stock price change over 12 months

Same logic as 6-month, but longer timeframe.

**Why 12 months?**
- Captures full market cycle effects
- Avoids short-term noise
- Well-documented in academic research

**How we use it:** Part of momentum score (50% weight).

---

## Sector Differences

Different sectors have different "normal" values:

| Sector | Typical P/E | Typical Margin | Typical D/E |
|--------|-------------|----------------|-------------|
| Technology | 25-40 | 15-30% | < 0.5 |
| Healthcare | 20-35 | 10-25% | 0.5-1.0 |
| Financials | 10-15 | N/A (different metrics) | High (it's their business) |
| Consumer Staples | 15-25 | 8-15% | 0.5-1.5 |
| Utilities | 12-18 | 10-15% | 1.5-3.0 |
| Energy | 10-20 | 5-15% | 0.5-1.5 |
| Real Estate | 15-25 | 20-40% | 1.0-2.5 |

**Key Insight:** Always compare a stock to its sector, not to the market as a whole.

---

## Common Pitfalls

### 1. Value Traps

**What it is:** A stock that looks cheap but deserves to be cheap

**Signs:**
- Very low P/E (< 50% of sector median)
- Declining revenue
- Falling stock price

**Example:** Newspaper companies in 2010 (low P/E, but business dying)

**How we avoid it:** Value trap detection in scoring methodology.

---

### 2. Growth Traps

**What it is:** High-growth company that never becomes profitable

**Signs:**
- High revenue growth
- Negative profit margins
- High cash burn

**Example:** WeWork (high growth, massive losses)

**How we avoid it:** Profitability factor balances growth factor.

---

### 3. Leverage Inflation

**What it is:** ROE looks great because company has tons of debt

**Signs:**
- ROE > 30%
- Debt-to-Equity > 2.0

**How we avoid it:** ROA added to balance ROE, leverage adjustment applied.

---

### 4. Survivorship Bias

**What it is:** Only looking at companies that exist today (ignoring failures)

**Why it matters for ML:** If training data only includes survivors, model is biased.

**How we avoid it:** Important for Phase 2 ML training - include delisted stocks.

---

### 5. Look-Ahead Bias

**What it is:** Using future information to make past predictions

**Example:** Using 2024 earnings to "predict" 2023 stock returns

**Why it matters:** Makes backtests look better than real performance

**How we avoid it:** Only use point-in-time data, never future data.

---

## Quick Reference Card

### The "Good Stock" Profile
- P/E: Below sector median
- ROE: > 15% (or sector median)
- Profit margin: > 10% (or sector median)
- Revenue growth: > 5%
- Debt/Equity: < 1.0
- Current ratio: 1.5-2.5
- 6-month return: Positive

### Red Flags
- P/E < 0 (unprofitable)
- ROE < 0 (losing money)
- Revenue growth < -10% (declining)
- Debt/Equity > 3.0 (highly leveraged)
- Current ratio < 1.0 (liquidity risk)
- Dividend yield > 8% + negative margins (yield trap)

---

## Resources for Learning More

**Free:**
- Investopedia.com - Great explanations of any term
- Yahoo Finance - Real data to practice with
- Khan Academy - Basic accounting/finance courses

**Books (Optional):**
- "The Intelligent Investor" by Benjamin Graham
- "The Little Book That Beats the Market" by Joel Greenblatt
- "One Up on Wall Street" by Peter Lynch

**For ML/Finance:**
- "Advances in Financial Machine Learning" by Marcos López de Prado

---

**Remember:** You don't need to memorize everything. This is a reference guide. Look things up when needed, and understanding will come with practice.

---

**Last Updated:** January 17, 2026
**Status:** Complete reference guide for StockPulse development
