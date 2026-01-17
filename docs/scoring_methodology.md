# StockPulse Scoring Methodology

**Version:** 2.0 (Financial-Expert Validated)
**Date:** January 17, 2026
**Status:** APPROVED - Ready for Implementation

---

## Validation Summary

**Reviewed by:** financial-expert agent
**Financial Soundness:** 9.5/10
**Verdict:** Approved for implementation

**Key Changes from v1.0:**
- Increased momentum weight from 5% to 15% (academic research)
- Added dividend yield to valuation factor
- Added ROA to profitability factor (prevents leverage-inflated ROE)
- Changed momentum timeframes from 3m+6m to 6m+12m
- Added value trap detection
- Added sector-aware debt thresholds

---

## Overview

StockPulse uses a **multi-factor scoring system** to rank S&P 500 stocks based on value, profitability, growth, financial health, and momentum. Each stock receives a score from 0-100, with higher scores indicating better investment opportunities.

**Philosophy:** "Buy quality companies at reasonable prices with strong fundamentals and positive momentum"

**Academic Foundation:**
- Value factor: Fama-French research
- Quality factor: Buffett-style investing
- Momentum factor: Jegadeesh-Titman research
- Multi-factor combination provides diversification (low correlation between factors)

---

## Factor Weights (Validated)

| Factor | Weight | Rationale |
|--------|--------|-----------|
| **Valuation** | 30% | Core value investing principle |
| **Profitability** | 25% | Quality companies outperform |
| **Growth** | 20% | Future value creation |
| **Momentum** | 15% | Strongest short-term predictor |
| **Health** | 10% | Downside protection |

**Why these weights?**
> "I weighted valuation at 30% because I'm targeting long-term value investors, quality at 25% for downside protection, and momentum at 15% based on academic research showing it's the strongest short-term predictor. The negative correlation between value and momentum provides portfolio diversification."

---

## Factor 1: Valuation (30% weight)

**Concept:** Lower valuation multiples indicate better value

### Metrics and Sub-Weights

| Metric | Weight | Direction | Notes |
|--------|--------|-----------|-------|
| Trailing P/E | 30% | Lower is better | Sector-relative |
| Price-to-Book | 25% | Lower is better | Sector-relative |
| Price-to-Sales | 15% | Lower is better | Sector-relative |
| **Dividend Yield** | 20% | Higher is better | NEW - with value trap check |
| Price vs 52-Week High | 10% | Lower is better | Contrarian indicator |

### Scoring Logic

```python
def calculate_valuation_score(stock, sector_stocks):
    sector_pe_median = median([s.trailing_pe for s in sector_stocks])
    sector_pb_median = median([s.price_to_book for s in sector_stocks])
    sector_ps_median = median([s.price_to_sales for s in sector_stocks])

    # P/E score (lower is better, sector-relative)
    if stock.trailing_pe <= 0 or stock.trailing_pe > 100:
        pe_score = 0  # Unprofitable or suspicious
    elif stock.trailing_pe < sector_pe_median * 0.7:
        pe_score = 100
    elif stock.trailing_pe < sector_pe_median:
        pe_score = 75
    elif stock.trailing_pe < sector_pe_median * 1.3:
        pe_score = 50
    else:
        pe_score = 25

    # P/B score (similar logic)
    # P/S score (similar logic)

    # Dividend yield score (NEW)
    # Higher yield is better, but watch for value traps
    if stock.dividend_yield is None or stock.dividend_yield == 0:
        div_score = 25  # No dividend is okay (growth stocks)
    elif stock.dividend_yield > 0.08 and stock.profit_margin < 0:
        div_score = 0  # VALUE TRAP: High yield + unprofitable
    elif stock.dividend_yield > 0.04:
        div_score = 100  # 4%+ yield is excellent
    elif stock.dividend_yield > 0.02:
        div_score = 75   # 2-4% yield is good
    else:
        div_score = 50   # 0-2% yield is moderate

    # Price position (contrarian)
    price_range = stock.fifty_two_week_high - stock.fifty_two_week_low
    if price_range > 0:
        position = (stock.current_price - stock.fifty_two_week_low) / price_range
        price_score = 100 - (position * 100)  # Lower = better
    else:
        price_score = 50

    valuation_score = (
        pe_score * 0.30 +
        pb_score * 0.25 +
        ps_score * 0.15 +
        div_score * 0.20 +
        price_score * 0.10
    )

    return valuation_score
```

---

## Factor 2: Profitability (25% weight)

**Concept:** More profitable = higher quality company

### Metrics and Sub-Weights

| Metric | Weight | Direction | Notes |
|--------|--------|-----------|-------|
| ROE (leverage-adjusted) | 40% | Higher is better | Sector-relative, adjusted for debt |
| **ROA** | 20% | Higher is better | NEW - not inflated by leverage |
| Profit Margin | 25% | Higher is better | Sector-relative |
| Operating Margin | 15% | Higher is better | Operational efficiency |

### Why ROA was added

**The Problem with ROE alone:**
- ROE = Net Income / Shareholder Equity
- High debt reduces equity, artificially inflating ROE
- A leveraged mediocre company can show higher ROE than an excellent unleveraged company

**Example:**
```
Company A: $100M income, $1000M equity → ROE = 10%
Company B: $100M income, $200M equity (borrowed $800M) → ROE = 50%

Company B looks better, but it's just more leveraged!
```

**Solution:** Add ROA (Return on Assets) which isn't inflated by leverage.

### Scoring Logic

```python
def calculate_profitability_score(stock, sector_stocks):
    sector_roe_median = median([s.return_on_equity for s in sector_stocks])
    sector_roa_median = median([s.return_on_assets for s in sector_stocks])

    # ROE score with leverage adjustment
    roe = stock.return_on_equity

    # Penalize ROE if inflated by excessive leverage
    if roe > 0.30 and stock.debt_to_equity > 2.0:
        roe = roe * (1 / (1 + stock.debt_to_equity / 3))

    if roe > sector_roe_median * 1.5:
        roe_score = 100
    elif roe > sector_roe_median:
        roe_score = 75
    elif roe > sector_roe_median * 0.5:
        roe_score = 50
    else:
        roe_score = 25

    # ROA score (NEW - not affected by leverage)
    roa = stock.return_on_assets or 0
    if roa > 0.15:
        roa_score = 100
    elif roa > 0.10:
        roa_score = 75
    elif roa > 0.05:
        roa_score = 50
    else:
        roa_score = 25

    # Profit margin score (sector-relative)
    # Operating margin score (sector-relative)

    profitability_score = (
        roe_score * 0.40 +
        roa_score * 0.20 +
        margin_score * 0.25 +
        operating_margin_score * 0.15
    )

    return profitability_score
```

---

## Factor 3: Growth (20% weight)

**Concept:** Faster growth = higher future value

### Metrics and Sub-Weights

| Metric | Weight | Direction | Notes |
|--------|--------|-----------|-------|
| Revenue Growth (YoY) | 50% | Higher is better | More stable than earnings |
| Earnings Growth (YoY) | 50% | Higher is better | Bottom-line improvement |

### Scoring Logic

```python
def calculate_growth_score(stock):
    # Revenue growth score
    if stock.revenue_growth > 0.20:
        rev_score = 100  # 20%+ is excellent
    elif stock.revenue_growth > 0.10:
        rev_score = 75   # 10-20% is good
    elif stock.revenue_growth > 0:
        rev_score = 50   # Positive growth
    elif stock.revenue_growth > -0.10:
        rev_score = 25   # Slight decline
    else:
        rev_score = 0    # Significant decline

    # Earnings growth score (similar thresholds)
    # ...

    growth_score = (rev_score * 0.50 + earnings_score * 0.50)

    return growth_score
```

---

## Factor 4: Momentum (15% weight) - UPDATED

**Concept:** Recent price strength tends to continue

**Why 15%?** Academic research (Jegadeesh-Titman 1993) shows momentum is the strongest short-term predictor. The combination of value (contrarian) and momentum (trend-following) provides diversification.

### Metrics and Sub-Weights (CHANGED)

| Metric | Weight | Notes |
|--------|--------|-------|
| 6-Month Return | 50% | Sweet spot for momentum |
| **12-Month Return** | 50% | NEW - replaced 3-month |

**Why remove 3-month?**
- 1-month shows reversal effects (not momentum)
- 3-month is borderline
- 6-12 month is the proven momentum window

### Scoring Logic

```python
def calculate_momentum_score(stock):
    # 6-month return score
    if stock.return_6m > 0.15:
        r6m_score = 100  # 15%+ in 6 months
    elif stock.return_6m > 0.10:
        r6m_score = 75   # 10-15%
    elif stock.return_6m > 0.05:
        r6m_score = 50   # 5-10%
    elif stock.return_6m > 0:
        r6m_score = 25   # Slightly positive
    else:
        r6m_score = 0    # Negative

    # 12-month return score (similar thresholds, scaled)
    if stock.return_12m > 0.25:
        r12m_score = 100  # 25%+ in 12 months
    elif stock.return_12m > 0.15:
        r12m_score = 75   # 15-25%
    elif stock.return_12m > 0.05:
        r12m_score = 50   # 5-15%
    elif stock.return_12m > 0:
        r12m_score = 25   # Slightly positive
    else:
        r12m_score = 0    # Negative

    momentum_score = (r6m_score * 0.50 + r12m_score * 0.50)

    return momentum_score
```

---

## Factor 5: Financial Health (10% weight)

**Concept:** Strong balance sheet = lower risk

### Metrics and Sub-Weights

| Metric | Weight | Direction | Notes |
|--------|--------|-----------|-------|
| Debt-to-Equity | 60% | Lower is better | Sector-aware thresholds |
| Current Ratio | 40% | ~2.0 is ideal | Short-term liquidity |

### Sector-Aware Debt Thresholds (NEW)

```python
def get_debt_thresholds(sector):
    """Utilities and REITs can handle higher debt"""
    if sector in ['Utilities', 'Real Estate']:
        return {'excellent': 1.0, 'good': 2.0, 'concerning': 4.0}
    else:
        return {'excellent': 0.5, 'good': 1.0, 'concerning': 2.0}
```

### Scoring Logic

```python
def calculate_health_score(stock):
    thresholds = get_debt_thresholds(stock.sector)

    # Debt/Equity score (lower is better, sector-aware)
    if stock.debt_to_equity < thresholds['excellent']:
        de_score = 100
    elif stock.debt_to_equity < thresholds['good']:
        de_score = 75
    elif stock.debt_to_equity < thresholds['concerning']:
        de_score = 50
    else:
        de_score = 25

    # Current ratio score (target ~2.0)
    if 1.5 <= stock.current_ratio <= 2.5:
        cr_score = 100
    elif 1.0 <= stock.current_ratio < 1.5:
        cr_score = 75
    elif stock.current_ratio > 2.5:
        cr_score = 75  # Too high is okay (just inefficient)
    elif 0.5 <= stock.current_ratio < 1.0:
        cr_score = 50
    else:
        cr_score = 25

    health_score = (de_score * 0.60 + cr_score * 0.40)

    return health_score
```

---

## Value Trap Detection (NEW)

**What's a value trap?**
A stock that looks cheap (low P/E) but deserves to be cheap because the business is declining.

**Detection Logic:**
```python
def detect_value_trap(stock, sector_stocks):
    """
    Value trap: Very cheap + declining revenue + falling price
    """
    sector_pe_median = median([s.trailing_pe for s in sector_stocks])

    is_very_cheap = stock.trailing_pe < sector_pe_median * 0.5
    is_declining = stock.revenue_growth < -0.10
    is_falling = stock.return_6m < -0.20

    if is_very_cheap and is_declining and is_falling:
        return True, 0.5  # Reduce score by 50%

    return False, 1.0
```

---

## Overall Score Calculation

```python
def calculate_total_score(stock, sector_stocks):
    valuation_score = calculate_valuation_score(stock, sector_stocks)
    profitability_score = calculate_profitability_score(stock, sector_stocks)
    growth_score = calculate_growth_score(stock)
    health_score = calculate_health_score(stock)
    momentum_score = calculate_momentum_score(stock)

    # Weighted average (v2.0 weights)
    total_score = (
        valuation_score * 0.30 +      # Was 0.35
        profitability_score * 0.25 +  # Same
        growth_score * 0.20 +         # Same
        momentum_score * 0.15 +       # Was 0.05
        health_score * 0.10           # Was 0.15
    )

    # Apply value trap penalty
    is_trap, multiplier = detect_value_trap(stock, sector_stocks)
    if is_trap:
        total_score *= multiplier

    return {
        'total_score': round(total_score, 2),
        'valuation_score': round(valuation_score, 2),
        'profitability_score': round(profitability_score, 2),
        'growth_score': round(growth_score, 2),
        'momentum_score': round(momentum_score, 2),
        'health_score': round(health_score, 2),
        'is_value_trap': is_trap,
    }
```

---

## Ranking

After scoring all 500 stocks:

1. Sort by `total_score` (descending)
2. Assign rank 1-500
3. Surface top 25 to dashboard

**Ties:** Break by valuation score (lower valuation wins)

---

## Null Handling

### Required Fields (exclude stock if missing)
- ticker, company_name, sector
- currentPrice, marketCap
- trailingPE, returnOnEquity

### Imputation Strategy
| Field | Strategy |
|-------|----------|
| Dividend yield | 0 (no dividend) |
| Growth metrics | Sector median or 0 |
| ROA | Calculate from net income / total assets if available |
| Forward P/E | Fall back to trailing P/E |
| Debt/Equity (young companies) | 0 |

---

## Data Requirements

### From yfinance `ticker.info`
| Our Field | yfinance Field |
|-----------|----------------|
| trailing_pe | trailingPE |
| price_to_book | priceToBook |
| price_to_sales | priceToSalesTrailing12Months |
| dividend_yield | dividendYield |
| return_on_equity | returnOnEquity |
| return_on_assets | returnOnAssets |
| profit_margin | profitMargins |
| operating_margin | operatingMargins |
| revenue_growth | revenueGrowth |
| earnings_growth | earningsGrowth |
| debt_to_equity | debtToEquity |
| current_ratio | currentRatio |
| current_price | currentPrice |
| fifty_two_week_high | fiftyTwoWeekHigh |
| fifty_two_week_low | fiftyTwoWeekLow |

### Calculated from `ticker.history()`
| Our Field | Calculation |
|-----------|-------------|
| return_6m | (price_now - price_6m_ago) / price_6m_ago |
| return_12m | (price_now - price_12m_ago) / price_12m_ago |

---

## Interview Talking Points

### Factor Selection
> "I combined value, quality, growth, and momentum factors based on academic research from Fama-French and Jegadeesh-Titman. Each factor captures different aspects of expected returns with low correlation, providing diversification."

### Sector-Relative Scoring
> "I use sector-relative scoring for valuation and profitability metrics because a P/E of 30 is expensive for utilities but normal for tech. This prevents sector bias and allows me to find opportunities across all sectors."

### Momentum Weight
> "I increased momentum to 15% based on research showing it's the strongest short-term predictor. The negative correlation between value and momentum provides portfolio diversification."

### Quality Focus
> "The profitability and health factors provide downside protection during market downturns. High-quality companies with strong balance sheets tend to decline less than low-quality companies."

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 17, 2026 | Initial methodology |
| 2.0 | Jan 17, 2026 | Financial-expert validated, added dividend yield, ROA, value trap detection, updated weights |

---

## References

- Fama, E., & French, K. (1993). Common risk factors in stock and bond returns
- Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers
- Greenblatt, J. (2006). The Little Book That Beats the Market
- Graham, B. (1949). The Intelligent Investor

---

**Status:** APPROVED - Ready for Implementation
**Validated by:** financial-expert agent
**Next Step:** Implement in ETL pipeline (Week 5-7)
