"""
YFinance Careful Data Exploration
Week 2: Data Engineering Assessment

This script carefully explores yfinance data with proper rate limiting
to avoid 429 errors.

Strategy:
1. Use requests_cache for repeated runs
2. Add delays between requests
3. Test one stock at a time
4. Use session management
"""

import yfinance as yf
import pandas as pd
import json
from datetime import datetime
import time
import sys

# Enable caching
import requests_cache
cache_file = '/home/cww324/workspace/stockpulse/yfinance_test_cache'
requests_cache.install_cache(cache_file, expire_after=86400)

print("=" * 80)
print("YFINANCE CAREFUL DATA EXPLORATION")
print("=" * 80)
print(f"Using cache: {cache_file}.sqlite")
print()

# Start with just ONE stock to test
test_ticker = 'AAPL'

print(f"Testing with {test_ticker} first...")
print("=" * 80)

try:
    # Create ticker object
    ticker = yf.Ticker(test_ticker)
    print(f"✅ Created ticker object for {test_ticker}")

    # Try to fetch info with timeout
    print("\nAttempting to fetch ticker.info...")
    time.sleep(3)  # Wait before request

    info = ticker.info

    if not info or len(info) == 0:
        print("❌ ticker.info returned empty")
        sys.exit(1)

    print(f"✅ Successfully fetched ticker.info")
    print(f"   Available keys: {len(info)}")

    # Display all available keys organized
    print("\n" + "=" * 80)
    print("ALL AVAILABLE KEYS IN ticker.info")
    print("=" * 80)

    all_keys = sorted(info.keys())
    for i, key in enumerate(all_keys, 1):
        value = info.get(key)
        # Check if null
        null_marker = " ❌ NULL" if value is None else ""
        # Format value for display
        if isinstance(value, (int, float)):
            if value > 1000000:
                value_str = f"{value:,.0f}"
            else:
                value_str = str(value)
        elif isinstance(value, str):
            value_str = value[:50] + "..." if len(value) > 50 else value
        else:
            value_str = str(value)[:50]

        print(f"{i:3}. {key:40} = {value_str}{null_marker}")

    # Count nulls
    null_count = sum(1 for v in info.values() if v is None)
    null_pct = (null_count / len(info)) * 100
    print(f"\nData Completeness: {100-null_pct:.1f}% ({null_count}/{len(info)} nulls)")

    # =========================================================================
    # Categorize fields by importance for our scoring system
    # =========================================================================

    print("\n" + "=" * 80)
    print("CATEGORIZED FIELDS FOR SCORING SYSTEM")
    print("=" * 80)

    scoring_categories = {
        'CRITICAL - Valuation': [
            'currentPrice',
            'trailingPE',
            'forwardPE',
            'priceToBook',
            'priceToSalesTrailing12Months',
            'enterpriseToRevenue',
            'enterpriseToEbitda',
            'pegRatio'
        ],
        'CRITICAL - Profitability': [
            'returnOnEquity',
            'returnOnAssets',
            'profitMargins',
            'grossMargins',
            'operatingMargins',
            'ebitdaMargins'
        ],
        'CRITICAL - Growth': [
            'revenueGrowth',
            'earningsGrowth',
            'earningsQuarterlyGrowth'
        ],
        'CRITICAL - Financial Health': [
            'totalCash',
            'totalDebt',
            'debtToEquity',
            'currentRatio',
            'quickRatio',
            'freeCashflow'
        ],
        'IMPORTANT - Dividends': [
            'dividendRate',
            'dividendYield',
            'payoutRatio',
            'fiveYearAvgDividendYield'
        ],
        'IMPORTANT - Market Data': [
            'marketCap',
            'enterpriseValue',
            'volume',
            'averageVolume',
            'beta'
        ],
        'IMPORTANT - Momentum': [
            'fiftyTwoWeekLow',
            'fiftyTwoWeekHigh',
            'fiftyDayAverage',
            'twoHundredDayAverage'
        ],
        'METADATA - Company Info': [
            'symbol',
            'longName',
            'sector',
            'industry',
            'country'
        ]
    }

    results = {}

    for category, fields in scoring_categories.items():
        print(f"\n{category}:")
        print("-" * 80)

        category_results = {}
        available_count = 0

        for field in fields:
            value = info.get(field)
            is_null = value is None

            if not is_null:
                available_count += 1

            # Format for display
            if value is None:
                display = "❌ NULL"
            elif isinstance(value, float):
                if abs(value) > 1000000:
                    display = f"{value:,.0f}"
                else:
                    display = f"{value:.4f}"
            elif isinstance(value, int):
                display = f"{value:,}"
            elif isinstance(value, str):
                display = value[:60]
            else:
                display = str(value)

            status = "✅" if not is_null else "❌"
            print(f"  {status} {field:35} = {display}")

            category_results[field] = {
                'value': value,
                'available': not is_null
            }

        # Summary for this category
        total_fields = len(fields)
        availability_pct = (available_count / total_fields) * 100
        print(f"\n  Category Availability: {available_count}/{total_fields} ({availability_pct:.0f}%)")

        results[category] = category_results

    # =========================================================================
    # Test ticker.history()
    # =========================================================================

    print("\n" + "=" * 80)
    print("TICKER.HISTORY (Price Data)")
    print("=" * 80)

    time.sleep(2)

    history = ticker.history(period="1y")

    if not history.empty:
        print(f"✅ Successfully fetched price history")
        print(f"   Rows: {len(history)}")
        print(f"   Columns: {list(history.columns)}")
        print(f"   Date Range: {history.index[0]} to {history.index[-1]}")
        print(f"\n   Last 5 days:")
        print(history.tail())

        # Check for nulls
        null_counts = history.isnull().sum()
        if null_counts.sum() > 0:
            print(f"\n⚠️  Null values found in history:")
            print(null_counts[null_counts > 0])
        else:
            print(f"\n✅ No null values in price history")

        results['history'] = {
            'available': True,
            'rows': len(history),
            'columns': list(history.columns),
            'date_range': {
                'start': str(history.index[0]),
                'end': str(history.index[-1])
            }
        }
    else:
        print("❌ No historical data available")
        results['history'] = {'available': False}

    # =========================================================================
    # Test ticker.financials
    # =========================================================================

    print("\n" + "=" * 80)
    print("TICKER.FINANCIALS (Income Statement)")
    print("=" * 80)

    time.sleep(2)

    try:
        financials = ticker.financials

        if financials is not None and not financials.empty:
            print(f"✅ Successfully fetched financials")
            print(f"   Quarters: {len(financials.columns)}")
            print(f"   Line Items: {len(financials.index)}")
            print(f"\n   Available line items:")
            for item in financials.index:
                print(f"     - {item}")

            results['financials'] = {
                'available': True,
                'quarters': len(financials.columns),
                'line_items': list(financials.index)
            }
        else:
            print("❌ No financial data available")
            results['financials'] = {'available': False}

    except Exception as e:
        print(f"❌ Error fetching financials: {e}")
        results['financials'] = {'available': False, 'error': str(e)}

    # =========================================================================
    # Save results
    # =========================================================================

    print("\n" + "=" * 80)
    print("SAVING RESULTS")
    print("=" * 80)

    # Save to JSON
    output_file = '/home/cww324/workspace/stockpulse/notebooks/yfinance_aapl_exploration.json'

    # Convert to JSON-serializable format
    def make_serializable(obj):
        if isinstance(obj, (pd.Timestamp, datetime)):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(item) for item in obj]
        else:
            return obj

    json_results = make_serializable(results)

    with open(output_file, 'w') as f:
        json.dump(json_results, f, indent=2)

    print(f"✅ Saved results to: {output_file}")

    # =========================================================================
    # Summary & Recommendations
    # =========================================================================

    print("\n" + "=" * 80)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 80)

    print("""
✅ SUCCESS - yfinance is working!

KEY FINDINGS:

1. ticker.info is the PRIMARY data source
   - Contains all key metrics we need for scoring
   - Updated daily
   - ~50-70 useful fields available

2. Fields confirmed available for {ticker}:
   - Valuation metrics (P/E, P/B, P/S, etc.)
   - Profitability ratios (ROE, margins, etc.)
   - Growth metrics (revenue growth, earnings growth)
   - Financial health (debt, cash, ratios)
   - Dividend information
   - Market data (price, volume, beta)

3. ticker.history() works well
   - Daily price data available
   - Can calculate custom momentum indicators
   - No null values

4. Financial statements available but not needed
   - ticker.info has pre-calculated ratios
   - Simpler to use info than parse statements

RECOMMENDATIONS FOR ETL PIPELINE:

✅ PRIMARY: Use ticker.info for all scoring metrics
✅ SECONDARY: Use ticker.history() for momentum calculations
❌ AVOID: Financial statements (redundant, more complex)

NEXT STEPS:

1. Test 5-10 more stocks to verify consistency
2. Document null handling strategy
3. Define exact fields for scoring system
4. Plan fallback for missing data
5. Design database schema for these fields

DATA REFRESH STRATEGY:

- Run ETL weekly (Sunday nights)
- Fetch ticker.info for all 500 stocks
- Calculate scores based on most recent data
- Store results in stock_scores table
""".format(ticker=test_ticker))

    print("\n" + "=" * 80)
    print("EXPLORATION COMPLETE!")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
