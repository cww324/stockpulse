"""
YFinance Deep Data Exploration
Week 2: Data Engineering Assessment

This script comprehensively explores ALL available data from yfinance
to understand what we can use for stock scoring.

Test Stocks: AAPL, MSFT, NVDA, JPM, XOM (diverse sectors)
"""

import yfinance as yf
import pandas as pd
import json
from datetime import datetime
from collections import defaultdict
import time

# Enable caching to avoid rate limits
import requests_cache
requests_cache.install_cache('yfinance_test_cache', expire_after=86400)

print("=" * 80)
print("YFINANCE COMPREHENSIVE DATA EXPLORATION")
print("=" * 80)

# Test stocks across different sectors
test_tickers = {
    'AAPL': 'Technology',
    'MSFT': 'Technology',
    'NVDA': 'Technology',
    'JPM': 'Financials',
    'XOM': 'Energy'
}

def explore_ticker(symbol):
    """Comprehensive exploration of a single ticker"""
    print(f"\n{'=' * 80}")
    print(f"EXPLORING: {symbol} ({test_tickers[symbol]})")
    print(f"{'=' * 80}")

    ticker = yf.Ticker(symbol)
    results = {}

    # =========================================================================
    # 1. TICKER.INFO - Key financial metrics
    # =========================================================================
    print("\n1. TICKER.INFO (Financial Metrics)")
    print("-" * 80)

    try:
        info = ticker.info

        # Categorize info fields
        categories = {
            'Company': ['longName', 'shortName', 'symbol', 'sector', 'industry',
                       'country', 'website', 'longBusinessSummary'],
            'Market Data': ['currentPrice', 'previousClose', 'open', 'dayHigh', 'dayLow',
                          'volume', 'averageVolume', 'marketCap', 'enterpriseValue'],
            'Valuation': ['trailingPE', 'forwardPE', 'priceToBook', 'priceToSalesTrailing12Months',
                         'enterpriseToRevenue', 'enterpriseToEbitda', 'pegRatio'],
            'Profitability': ['profitMargins', 'grossMargins', 'operatingMargins', 'ebitdaMargins',
                            'returnOnAssets', 'returnOnEquity'],
            'Financial Health': ['totalCash', 'totalDebt', 'debtToEquity', 'currentRatio',
                               'quickRatio', 'totalCashPerShare', 'revenuePerShare'],
            'Growth': ['revenueGrowth', 'earningsGrowth', 'earningsQuarterlyGrowth'],
            'Dividends': ['dividendRate', 'dividendYield', 'payoutRatio', 'fiveYearAvgDividendYield'],
            'Trading': ['beta', 'fiftyTwoWeekLow', 'fiftyTwoWeekHigh', 'fiftyDayAverage',
                       'twoHundredDayAverage'],
            'Analyst': ['targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 'recommendationKey',
                       'numberOfAnalystOpinions']
        }

        results['info_available'] = True
        results['info_fields'] = {}

        for category, fields in categories.items():
            print(f"\n{category}:")
            category_data = {}
            for field in fields:
                value = info.get(field)
                null_status = " ❌ NULL" if value is None else ""
                category_data[field] = value
                print(f"  {field}: {value}{null_status}")
            results['info_fields'][category] = category_data

        # Count nulls
        total_fields = sum(len(fields) for fields in categories.values())
        null_count = sum(1 for cat_data in results['info_fields'].values()
                        for v in cat_data.values() if v is None)
        results['info_null_pct'] = (null_count / total_fields) * 100

        print(f"\nData Completeness: {100 - results['info_null_pct']:.1f}% ({null_count}/{total_fields} nulls)")

    except Exception as e:
        print(f"❌ Error fetching info: {e}")
        results['info_available'] = False

    # =========================================================================
    # 2. TICKER.HISTORY - Price data
    # =========================================================================
    print("\n2. TICKER.HISTORY (Price Data)")
    print("-" * 80)

    try:
        history = ticker.history(period="1y")

        if not history.empty:
            results['history_available'] = True
            results['history_rows'] = len(history)
            results['history_columns'] = list(history.columns)
            results['history_date_range'] = {
                'start': str(history.index[0]),
                'end': str(history.index[-1])
            }

            print(f"Rows: {len(history)}")
            print(f"Columns: {list(history.columns)}")
            print(f"Date Range: {history.index[0]} to {history.index[-1]}")
            print(f"\nSample (last 5 days):")
            print(history.tail())

            # Check for nulls
            null_counts = history.isnull().sum()
            if null_counts.sum() > 0:
                print(f"\n⚠️  Null values found:")
                print(null_counts[null_counts > 0])
            else:
                print("\n✅ No null values in price history")

        else:
            print("❌ No historical data available")
            results['history_available'] = False

    except Exception as e:
        print(f"❌ Error fetching history: {e}")
        results['history_available'] = False

    # =========================================================================
    # 3. TICKER.FINANCIALS - Income Statement
    # =========================================================================
    print("\n3. TICKER.FINANCIALS (Income Statement)")
    print("-" * 80)

    try:
        financials = ticker.financials

        if financials is not None and not financials.empty:
            results['financials_available'] = True
            results['financials_columns'] = list(financials.columns)
            results['financials_rows'] = list(financials.index)

            print(f"Columns (dates): {len(financials.columns)}")
            print(f"Rows (line items): {len(financials.index)}")
            print(f"\nAvailable line items:")
            for item in financials.index:
                print(f"  - {item}")

            print(f"\nLatest data (most recent quarter):")
            print(financials.iloc[:, 0])

        else:
            print("❌ No financial data available")
            results['financials_available'] = False

    except Exception as e:
        print(f"❌ Error fetching financials: {e}")
        results['financials_available'] = False

    # =========================================================================
    # 4. TICKER.BALANCE_SHEET
    # =========================================================================
    print("\n4. TICKER.BALANCE_SHEET")
    print("-" * 80)

    try:
        balance_sheet = ticker.balance_sheet

        if balance_sheet is not None and not balance_sheet.empty:
            results['balance_sheet_available'] = True
            results['balance_sheet_columns'] = list(balance_sheet.columns)
            results['balance_sheet_rows'] = list(balance_sheet.index)

            print(f"Columns (dates): {len(balance_sheet.columns)}")
            print(f"Rows (line items): {len(balance_sheet.index)}")
            print(f"\nAvailable line items:")
            for item in balance_sheet.index:
                print(f"  - {item}")

        else:
            print("❌ No balance sheet data available")
            results['balance_sheet_available'] = False

    except Exception as e:
        print(f"❌ Error fetching balance sheet: {e}")
        results['balance_sheet_available'] = False

    # =========================================================================
    # 5. TICKER.CASHFLOW
    # =========================================================================
    print("\n5. TICKER.CASHFLOW")
    print("-" * 80)

    try:
        cashflow = ticker.cashflow

        if cashflow is not None and not cashflow.empty:
            results['cashflow_available'] = True
            results['cashflow_columns'] = list(cashflow.columns)
            results['cashflow_rows'] = list(cashflow.index)

            print(f"Columns (dates): {len(cashflow.columns)}")
            print(f"Rows (line items): {len(cashflow.index)}")
            print(f"\nAvailable line items:")
            for item in cashflow.index:
                print(f"  - {item}")

        else:
            print("❌ No cashflow data available")
            results['cashflow_available'] = False

    except Exception as e:
        print(f"❌ Error fetching cashflow: {e}")
        results['cashflow_available'] = False

    # =========================================================================
    # 6. OTHER USEFUL ATTRIBUTES
    # =========================================================================
    print("\n6. OTHER YFINANCE ATTRIBUTES")
    print("-" * 80)

    # Check for quarterly financials
    try:
        quarterly_financials = ticker.quarterly_financials
        if quarterly_financials is not None and not quarterly_financials.empty:
            print(f"✅ quarterly_financials: {len(quarterly_financials.columns)} quarters available")
            results['quarterly_financials_available'] = True
        else:
            print("❌ quarterly_financials: Not available")
            results['quarterly_financials_available'] = False
    except:
        print("❌ quarterly_financials: Error")
        results['quarterly_financials_available'] = False

    # Check for quarterly balance sheet
    try:
        quarterly_balance_sheet = ticker.quarterly_balance_sheet
        if quarterly_balance_sheet is not None and not quarterly_balance_sheet.empty:
            print(f"✅ quarterly_balance_sheet: {len(quarterly_balance_sheet.columns)} quarters available")
            results['quarterly_balance_sheet_available'] = True
        else:
            print("❌ quarterly_balance_sheet: Not available")
            results['quarterly_balance_sheet_available'] = False
    except:
        print("❌ quarterly_balance_sheet: Error")
        results['quarterly_balance_sheet_available'] = False

    # Check for quarterly cashflow
    try:
        quarterly_cashflow = ticker.quarterly_cashflow
        if quarterly_cashflow is not None and not quarterly_cashflow.empty:
            print(f"✅ quarterly_cashflow: {len(quarterly_cashflow.columns)} quarters available")
            results['quarterly_cashflow_available'] = True
        else:
            print("❌ quarterly_cashflow: Not available")
            results['quarterly_cashflow_available'] = False
    except:
        print("❌ quarterly_cashflow: Error")
        results['quarterly_cashflow_available'] = False

    # Check for actions (dividends, splits)
    try:
        actions = ticker.actions
        if actions is not None and not actions.empty:
            print(f"✅ actions: {len(actions)} events (dividends, splits)")
            results['actions_available'] = True
        else:
            print("❌ actions: Not available")
            results['actions_available'] = False
    except:
        print("❌ actions: Error")
        results['actions_available'] = False

    # Check for recommendations
    try:
        recommendations = ticker.recommendations
        if recommendations is not None and not recommendations.empty:
            print(f"✅ recommendations: {len(recommendations)} analyst recommendations")
            results['recommendations_available'] = True
        else:
            print("❌ recommendations: Not available")
            results['recommendations_available'] = False
    except:
        print("❌ recommendations: Error")
        results['recommendations_available'] = False

    return results


# ============================================================================
# MAIN EXPLORATION
# ============================================================================

all_results = {}

for symbol in test_tickers.keys():
    try:
        all_results[symbol] = explore_ticker(symbol)
        time.sleep(2)  # Be nice to API
    except Exception as e:
        print(f"\n❌ ERROR exploring {symbol}: {e}")
        all_results[symbol] = {'error': str(e)}

# ============================================================================
# CROSS-STOCK COMPARISON
# ============================================================================

print("\n" + "=" * 80)
print("CROSS-STOCK DATA AVAILABILITY COMPARISON")
print("=" * 80)

# Check consistency across stocks
availability_summary = defaultdict(lambda: {'available': 0, 'unavailable': 0})

for symbol, results in all_results.items():
    if 'error' in results:
        continue

    for key, value in results.items():
        if key.endswith('_available'):
            if value:
                availability_summary[key]['available'] += 1
            else:
                availability_summary[key]['unavailable'] += 1

print("\nData Source Availability Across All Stocks:")
print("-" * 80)
for data_source, counts in sorted(availability_summary.items()):
    total = counts['available'] + counts['unavailable']
    pct = (counts['available'] / total) * 100 if total > 0 else 0
    status = "✅" if pct == 100 else "⚠️" if pct >= 60 else "❌"
    print(f"{status} {data_source.replace('_available', '')}: {counts['available']}/{total} ({pct:.0f}%)")

# ============================================================================
# DATA QUALITY ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("DATA QUALITY ANALYSIS")
print("=" * 80)

# Compare null percentages across stocks
print("\ninfo field null percentage by stock:")
print("-" * 80)
for symbol, results in all_results.items():
    if 'error' not in results and 'info_null_pct' in results:
        null_pct = results['info_null_pct']
        status = "✅" if null_pct < 20 else "⚠️" if null_pct < 40 else "❌"
        print(f"{status} {symbol}: {null_pct:.1f}% null fields")

# ============================================================================
# RECOMMENDATIONS FOR SCORING SYSTEM
# ============================================================================

print("\n" + "=" * 80)
print("RECOMMENDATIONS FOR SCORING SYSTEM")
print("=" * 80)

print("""
Based on this exploration, here are the recommended fields for scoring:

PRIMARY SOURCES (ticker.info):
  ✅ Valuation: trailingPE, forwardPE, priceToBook, priceToSalesTrailing12Months
  ✅ Profitability: returnOnEquity, profitMargins, operatingMargins
  ✅ Growth: revenueGrowth, earningsGrowth
  ✅ Financial Health: debtToEquity, currentRatio
  ✅ Dividends: dividendYield
  ✅ Momentum: beta, 52-week high/low

SECONDARY SOURCES (if needed):
  - ticker.history() for custom momentum calculations
  - ticker.financials for detailed analysis (if info fields are null)
  - ticker.balance_sheet for detailed balance sheet items
  - ticker.cashflow for cash flow metrics

AVOID:
  ❌ Quarterly data (less consistent, more complex)
  ❌ Analyst recommendations (noisy, not always available)
  ❌ Deep financial statement items (most available in info)

DATA REFRESH FREQUENCY:
  - ticker.info updates daily
  - Financial statements update quarterly
  - Price history updates daily

RECOMMENDATION: Rely primarily on ticker.info fields for simplicity and consistency.
Only dive into financial statements if critical fields are missing.
""")

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

# Save detailed results as JSON
with open('yfinance_exploration_results.json', 'w') as f:
    # Convert results to JSON-serializable format
    json_results = {}
    for symbol, data in all_results.items():
        json_results[symbol] = {}
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                json_results[symbol][key] = value
            else:
                json_results[symbol][key] = str(value)

    json.dump(json_results, f, indent=2)
    print("✅ Saved detailed results to: yfinance_exploration_results.json")

print("\n" + "=" * 80)
print("EXPLORATION COMPLETE!")
print("=" * 80)
print(f"\nTimestamp: {datetime.now()}")
print(f"Stocks explored: {', '.join(test_tickers.keys())}")
print("\nNext Steps:")
print("1. Review yfinance_exploration_results.json for detailed findings")
print("2. Define scoring methodology based on available fields")
print("3. Test with a larger sample of stocks (10-20)")
print("4. Document findings in docs/data_sources.md")
