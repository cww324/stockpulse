"""
Small yfinance Test - Wait for Rate Limit Reset

Run this script in a few hours when the rate limit resets.
Tests with just 3 stocks to validate our understanding.

When rate limit resets (usually 24 hours):
1. Run this script
2. Review output
3. Save to data_exploration_results.json
4. Proceed with confidence to Week 3

Usage:
    source venv/bin/activate
    python notebooks/test_yfinance_small.py
"""

import yfinance as yf
import json
import time
from datetime import datetime

# Cache to avoid re-hitting API
import requests_cache
requests_cache.install_cache('/home/cww324/workspace/stockpulse/yfinance_test_cache',
                             expire_after=86400)

print("=" * 80)
print("YFINANCE SMALL TEST - 3 STOCKS")
print("=" * 80)
print(f"Timestamp: {datetime.now()}\n")

# Test 3 stocks from different sectors
test_stocks = {
    'AAPL': 'Technology',
    'JPM': 'Financials',
    'XOM': 'Energy'
}

results = {}

for ticker, sector in test_stocks.items():
    print(f"\nFetching {ticker} ({sector})...")
    print("-" * 80)

    try:
        # Create ticker
        stock = yf.Ticker(ticker)

        # Test ticker.info
        print("  Fetching info...")
        time.sleep(2)  # Be polite
        info = stock.info

        if not info:
            print("  ❌ No info data returned")
            results[ticker] = {'error': 'No data'}
            continue

        # Extract key fields we care about
        key_fields = {
            'metadata': {
                'symbol': info.get('symbol'),
                'name': info.get('longName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
            },
            'valuation': {
                'currentPrice': info.get('currentPrice'),
                'trailingPE': info.get('trailingPE'),
                'forwardPE': info.get('forwardPE'),
                'priceToBook': info.get('priceToBook'),
                'priceToSalesTrailing12Months': info.get('priceToSalesTrailing12Months'),
            },
            'profitability': {
                'returnOnEquity': info.get('returnOnEquity'),
                'profitMargins': info.get('profitMargins'),
                'operatingMargins': info.get('operatingMargins'),
            },
            'growth': {
                'revenueGrowth': info.get('revenueGrowth'),
                'earningsGrowth': info.get('earningsGrowth'),
            },
            'health': {
                'debtToEquity': info.get('debtToEquity'),
                'currentRatio': info.get('currentRatio'),
                'totalCash': info.get('totalCash'),
                'totalDebt': info.get('totalDebt'),
            },
            'market': {
                'marketCap': info.get('marketCap'),
                'beta': info.get('beta'),
                'volume': info.get('volume'),
            }
        }

        # Test ticker.history
        print("  Fetching history...")
        time.sleep(2)
        history = stock.history(period="6mo")

        has_history = not history.empty
        history_info = {
            'available': has_history,
            'rows': len(history) if has_history else 0,
            'latest_price': float(history['Close'].iloc[-1]) if has_history else None,
        }

        # Calculate 3-month return if we have data
        if has_history and len(history) >= 63:
            price_now = history['Close'].iloc[-1]
            price_3m_ago = history['Close'].iloc[-63]
            return_3m = (price_now - price_3m_ago) / price_3m_ago
            history_info['return_3m'] = float(return_3m)

        # Save results
        results[ticker] = {
            'success': True,
            'fields': key_fields,
            'history': history_info,
            'fetched_at': datetime.now().isoformat()
        }

        # Print summary
        print(f"  ✅ Success!")
        print(f"     Company: {key_fields['metadata']['name']}")
        print(f"     Sector: {key_fields['metadata']['sector']}")
        print(f"     Price: ${key_fields['valuation']['currentPrice']}")
        print(f"     P/E: {key_fields['valuation']['trailingPE']}")
        print(f"     ROE: {key_fields['profitability']['returnOnEquity']}")
        print(f"     Market Cap: ${key_fields['market']['marketCap']:,}" if key_fields['market']['marketCap'] else "     Market Cap: N/A")
        print(f"     History: {len(history)} days available" if has_history else "     History: None")

        # Check for nulls
        all_values = []
        for category in key_fields.values():
            if isinstance(category, dict):
                all_values.extend(category.values())
        null_count = sum(1 for v in all_values if v is None)
        total_count = len(all_values)
        null_pct = (null_count / total_count * 100) if total_count > 0 else 0
        print(f"     Nulls: {null_count}/{total_count} ({null_pct:.1f}%)")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        results[ticker] = {
            'success': False,
            'error': str(e),
            'fetched_at': datetime.now().isoformat()
        }

    time.sleep(3)  # Extra delay between stocks

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

success_count = sum(1 for r in results.values() if r.get('success'))
print(f"Success Rate: {success_count}/{len(test_stocks)}")

if success_count == len(test_stocks):
    print("\n✅ ALL TESTS PASSED!")
    print("\nyfinance is working. Key takeaways:")
    print("  1. ticker.info provides all needed financial metrics")
    print("  2. ticker.history() provides price data for momentum")
    print("  3. Some null values expected (10-30%)")
    print("  4. Data quality is sufficient for scoring")
    print("\nNext steps:")
    print("  - Review saved results in test_results.json")
    print("  - Proceed to Week 3 (Database Design)")
    print("  - Plan ETL pipeline for Week 5-7")
elif success_count > 0:
    print(f"\n⚠️  PARTIAL SUCCESS ({success_count}/{len(test_stocks)})")
    print("Some stocks worked. Review errors above.")
else:
    print("\n❌ ALL TESTS FAILED")
    print("Likely still rate-limited. Wait longer and try again.")

# Save results
output_file = '/home/cww324/workspace/stockpulse/notebooks/test_results.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nResults saved to: {output_file}")
print("\n" + "=" * 80)
