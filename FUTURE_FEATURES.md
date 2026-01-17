# Future Features - StockPulse

**Purpose:** Track planned enhancements beyond the core 18-week project
**Last Updated:** January 17, 2026

---

## Phase 3: Paper Trading Integration (Weeks 19-21)

**Status:** Planned
**Priority:** High
**Estimated Time:** 3 weeks (~40 hours)

### Overview

Integrate StockPulse scoring system with Alpaca's paper trading API to automatically execute trades based on ML predictions. This validates the strategy with simulated money before any real capital is risked.

### Why This Matters

**For Learning:**
- Real-world trading system experience
- Order execution, position management, risk controls
- MLOps in production (model → action)

**For Portfolio:**
- Demonstrates end-to-end ML pipeline
- Shows you can build production trading systems
- Differentiates from typical "predict stock prices" projects

**For Personal Use:**
- Actually test if the strategy works
- Track performance vs S&P 500
- Potentially transition to real money if profitable

### Platform: Alpaca

**Why Alpaca?**
- Free paper trading (unlimited)
- Excellent Python SDK (`alpaca-trade-api`)
- Designed for algo trading
- Commission-free
- Real market data
- Easy transition to live trading

**Alpaca Resources:**
- Docs: https://alpaca.markets/docs/
- Python SDK: https://github.com/alpacahq/alpaca-trade-api-python
- Paper trading: https://app.alpaca.markets/paper/dashboard/overview

---

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    StockPulse System                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Weekly     │    │   Scoring    │    │   Trading    │  │
│  │   ETL        │───▶│   Engine     │───▶│   Signals    │  │
│  │   Pipeline   │    │   (ML)       │    │   Generator  │  │
│  └──────────────┘    └──────────────┘    └──────┬───────┘  │
│                                                  │          │
│                                                  ▼          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                 Trading Engine                        │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────┐  │  │
│  │  │  Position  │  │    Risk    │  │     Order      │  │  │
│  │  │  Manager   │  │  Manager   │  │   Executor     │  │  │
│  │  └────────────┘  └────────────┘  └───────┬────────┘  │  │
│  └──────────────────────────────────────────┼───────────┘  │
│                                              │              │
└──────────────────────────────────────────────┼──────────────┘
                                               │
                                               ▼
                              ┌────────────────────────────┐
                              │      Alpaca API            │
                              │   (Paper Trading)          │
                              │                            │
                              │  • Market Orders           │
                              │  • Portfolio Tracking      │
                              │  • Position Data           │
                              │  • Account Balance         │
                              └────────────────────────────┘
```

---

### Trading Strategy

**Entry Rules (Buy):**
```python
# Buy when:
# 1. Stock enters top 25 rankings
# 2. Score > 70
# 3. Not already holding position
# 4. Available cash > minimum position size

def should_buy(stock, portfolio):
    return (
        stock.rank <= 25 and
        stock.total_score >= 70 and
        stock.ticker not in portfolio.positions and
        portfolio.cash >= MIN_POSITION_SIZE
    )
```

**Exit Rules (Sell):**
```python
# Sell when:
# 1. Stock drops out of top 50
# 2. Score drops below 50
# 3. Stop loss triggered (-15%)
# 4. Take profit triggered (+30%)

def should_sell(stock, position):
    return (
        stock.rank > 50 or
        stock.total_score < 50 or
        position.unrealized_pnl_pct <= -0.15 or
        position.unrealized_pnl_pct >= 0.30
    )
```

**Position Sizing:**
```python
# Equal weight: divide capital across max 25 positions
# Max 4% per position (25 positions = 100%)
# Minimum position: $1,000

def calculate_position_size(portfolio, num_positions=25):
    max_per_position = portfolio.equity * 0.04
    return max(MIN_POSITION_SIZE, max_per_position)
```

---

### Week-by-Week Plan

#### Week 19: Alpaca Integration & Buy Signals

**Tasks:**
- [ ] Create Alpaca paper trading account
- [ ] Install `alpaca-trade-api` package
- [ ] Create `trading/alpaca_client.py` - API wrapper
- [ ] Create `trading/signals.py` - generate buy/sell signals
- [ ] Create `trading/executor.py` - execute market orders
- [ ] Test: manually trigger buy for one stock
- [ ] Add trading config to `.env` (API keys)

**Deliverables:**
- Working Alpaca connection
- Can execute buy orders from scoring output
- Basic logging of trades

**Code Structure:**
```
trading/
├── __init__.py
├── alpaca_client.py    # Alpaca API wrapper
├── signals.py          # Buy/sell signal generation
├── executor.py         # Order execution
├── position_manager.py # Track positions
├── risk_manager.py     # Risk rules
└── config.py           # Trading parameters
```

#### Week 20: Sell Signals & Risk Management

**Tasks:**
- [ ] Implement sell signal logic
- [ ] Add stop loss monitoring
- [ ] Add take profit monitoring
- [ ] Create `trading/position_manager.py`
- [ ] Create `trading/risk_manager.py`
- [ ] Add position size calculation
- [ ] Test: full buy → hold → sell cycle
- [ ] Add trade history logging to database

**Deliverables:**
- Complete trading logic (buy + sell)
- Risk management rules enforced
- Trade history tracked

**New Database Tables:**
```sql
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10),
    side VARCHAR(4),  -- 'buy' or 'sell'
    quantity INTEGER,
    price NUMERIC,
    total_value NUMERIC,
    signal_score NUMERIC,
    signal_rank INTEGER,
    executed_at TIMESTAMP,
    alpaca_order_id VARCHAR(50)
);

CREATE TABLE portfolio_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_date DATE,
    total_equity NUMERIC,
    cash NUMERIC,
    positions_value NUMERIC,
    daily_pnl NUMERIC,
    total_pnl NUMERIC,
    sp500_benchmark NUMERIC,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Week 21: Dashboard & Performance Tracking

**Tasks:**
- [ ] Add portfolio page to Streamlit dashboard
- [ ] Show current positions with P&L
- [ ] Show trade history
- [ ] Add performance chart (equity curve)
- [ ] Add benchmark comparison (vs S&P 500)
- [ ] Calculate Sharpe ratio, max drawdown
- [ ] Create daily snapshot job
- [ ] Add email/Slack alerts for trades (optional)

**Deliverables:**
- Portfolio dashboard in Streamlit
- Performance metrics calculated
- Historical tracking working

**Dashboard Components:**
```
Portfolio Dashboard
├── Account Summary
│   ├── Total Equity
│   ├── Cash Available
│   ├── Positions Value
│   └── Today's P&L
│
├── Current Positions
│   ├── Ticker | Shares | Avg Cost | Current | P&L | Score
│   └── (table of all positions)
│
├── Performance Chart
│   ├── Equity curve over time
│   └── S&P 500 benchmark overlay
│
├── Metrics
│   ├── Total Return
│   ├── Sharpe Ratio
│   ├── Max Drawdown
│   └── Win Rate
│
└── Recent Trades
    └── (table of last 20 trades)
```

---

### Risk Controls

**Hard Limits (Non-negotiable):**
```python
RISK_LIMITS = {
    'max_position_pct': 0.05,      # Max 5% in any single stock
    'max_positions': 25,            # Max 25 positions
    'stop_loss_pct': -0.15,         # Sell if down 15%
    'max_daily_trades': 10,         # Max 10 trades per day
    'min_cash_reserve': 0.10,       # Keep 10% in cash
}
```

**Why These Limits:**
- Prevents over-concentration in one stock
- Limits losses on any single position
- Prevents overtrading (and potential pattern day trader issues)
- Maintains liquidity for opportunities

---

### API Keys & Security

**Environment Variables:**
```bash
# .env (add to .gitignore!)
ALPACA_API_KEY=your_api_key
ALPACA_SECRET_KEY=your_secret_key
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Paper trading
```

**Security Notes:**
- NEVER commit API keys to git
- Use paper trading URL until strategy is validated
- Paper and live accounts have different API keys

---

### Success Metrics

**Strategy Validation:**
- [ ] Sharpe ratio > 1.0 (risk-adjusted returns)
- [ ] Beat S&P 500 over 3+ months
- [ ] Max drawdown < 20%
- [ ] Win rate > 50%

**System Validation:**
- [ ] Orders execute correctly
- [ ] Risk limits enforced
- [ ] No bugs in position tracking
- [ ] Dashboard shows accurate data

---

### Interview Talking Points

**System Design:**
> "After validating the ML model with backtesting, I integrated it with Alpaca's paper trading API to test the strategy in real market conditions. The system automatically generates buy signals when stocks enter the top 25 rankings and exit signals based on score degradation or risk limits."

**Risk Management:**
> "I implemented position sizing using equal-weight allocation across up to 25 positions, with a 5% max per stock. Risk management includes 15% stop losses and daily trade limits to prevent overtrading."

**Validation:**
> "The paper trading portfolio is tracked in a Streamlit dashboard showing equity curves, performance vs S&P 500 benchmark, and trade history. After 3 months of paper trading, I can validate whether the strategy has real alpha."

---

### Future Enhancements (Phase 4+)

If paper trading is successful:

1. **Live Trading** (with small capital)
   - Switch to live Alpaca endpoint
   - Start with $1,000-5,000
   - Strict risk limits

2. **Advanced Order Types**
   - Limit orders instead of market
   - Bracket orders (entry + stop + target)
   - Time-weighted execution for large orders

3. **Options Integration**
   - Sell covered calls on positions
   - Buy protective puts
   - Requires options approval

4. **Multi-Strategy**
   - Long-only (current)
   - Long-short (short low-ranked stocks)
   - Sector rotation

---

## Other Future Ideas

### Idea: Real-Time Alerts
**Priority:** Medium
- Push notifications when top 25 changes
- Email digest of weekly rankings
- Slack integration

### Idea: User Accounts
**Priority:** Low
- Multiple users with own watchlists
- Custom factor weights per user
- Saved searches

### Idea: Backtesting Engine
**Priority:** Medium
- Test strategy on historical data
- Walk-forward optimization
- Monte Carlo simulation

### Idea: Alternative Data
**Priority:** Low (Phase 4+)
- News sentiment (NLP)
- Social media mentions
- Earnings call transcripts

---

## Priority Order

| Priority | Feature | Timeline |
|----------|---------|----------|
| 1 | **Phase 3: Paper Trading** | Weeks 19-21 |
| 2 | Backtesting Engine | Phase 4 |
| 3 | Real-Time Alerts | Phase 4 |
| 4 | User Accounts | Phase 4+ |
| 5 | Alternative Data | Phase 4+ |

---

**Remember:** Complete Phase 1-2 first! These features are for AFTER you have a working, deployed project.

---

**Last Updated:** January 17, 2026
**Status:** Phase 3 planned, awaiting Phase 1-2 completion
