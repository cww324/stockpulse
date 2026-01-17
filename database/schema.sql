-- StockPulse Database Schema
-- Bronze/Silver/Gold medallion architecture

-- ============================================
-- BRONZE LAYER: Raw data from APIs
-- ============================================

CREATE TABLE IF NOT EXISTS raw_stock_data (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    data_source VARCHAR(50) NOT NULL,  -- 'yfinance', 'alpha_vantage', 'sec_edgar', etc.
    raw_json JSONB NOT NULL,
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    run_id UUID NOT NULL
);

CREATE TABLE IF NOT EXISTS etl_runs (
    id UUID PRIMARY KEY,
    run_type VARCHAR(50) NOT NULL,  -- 'ingest', 'transform', 'score', 'ml_inference'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'running',  -- 'running', 'success', 'failed'
    stocks_processed INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB
);

-- ============================================
-- SILVER LAYER: Cleaned, normalized data
-- ============================================

CREATE TABLE IF NOT EXISTS processed_stocks (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,

    -- Price data
    current_price DECIMAL(12, 4),
    price_change_1d DECIMAL(8, 4),
    price_change_1w DECIMAL(8, 4),
    price_change_1m DECIMAL(8, 4),
    price_change_3m DECIMAL(8, 4),
    price_change_6m DECIMAL(8, 4),
    price_change_1y DECIMAL(8, 4),

    -- Valuation ratios
    pe_ratio DECIMAL(12, 4),
    pb_ratio DECIMAL(12, 4),
    ps_ratio DECIMAL(12, 4),
    peg_ratio DECIMAL(12, 4),

    -- Profitability
    profit_margin DECIMAL(8, 4),
    operating_margin DECIMAL(8, 4),
    roe DECIMAL(8, 4),
    roa DECIMAL(8, 4),
    roic DECIMAL(8, 4),

    -- Growth
    revenue_growth_yoy DECIMAL(8, 4),
    earnings_growth_yoy DECIMAL(8, 4),

    -- Financial health
    debt_to_equity DECIMAL(12, 4),
    current_ratio DECIMAL(8, 4),
    quick_ratio DECIMAL(8, 4),
    free_cash_flow BIGINT,

    -- Dividend
    dividend_yield DECIMAL(8, 4),
    payout_ratio DECIMAL(8, 4),

    -- 52-week range (for valuation scoring)
    fifty_two_week_high DECIMAL(12, 4),
    fifty_two_week_low DECIMAL(12, 4),

    -- Risk metrics
    beta DECIMAL(6, 4),

    -- Metadata
    snapshot_date DATE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(ticker, snapshot_date)
);

-- ============================================
-- GOLD LAYER: Scores and ML predictions
-- ============================================

CREATE TABLE IF NOT EXISTS stock_scores (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    snapshot_date DATE NOT NULL,

    -- Individual factor scores (0-100)
    -- Mapping to scoring_methodology.md v2.0:
    --   value_score = valuation (30% weight)
    --   profitability_score = profitability (25% weight)
    --   growth_score = growth (20% weight)
    --   momentum_score = momentum (15% weight)
    --   quality_score = health (10% weight)
    value_score DECIMAL(5, 2),
    growth_score DECIMAL(5, 2),
    profitability_score DECIMAL(5, 2),
    momentum_score DECIMAL(5, 2),
    quality_score DECIMAL(5, 2),

    -- Composite score
    composite_score DECIMAL(5, 2),
    rank INTEGER,
    percentile DECIMAL(5, 2),

    -- Value trap detection (from financial-expert validation)
    is_value_trap BOOLEAN DEFAULT FALSE,

    -- Explanations (human-readable)
    value_explanation TEXT,
    growth_explanation TEXT,
    profitability_explanation TEXT,
    momentum_explanation TEXT,
    quality_explanation TEXT,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(ticker, snapshot_date)
);

CREATE TABLE IF NOT EXISTS ml_predictions (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    snapshot_date DATE NOT NULL,
    model_version VARCHAR(50) NOT NULL,

    -- Prediction
    predicted_return_3m DECIMAL(8, 4),  -- e.g., 0.15 = 15% predicted return
    prediction_confidence DECIMAL(5, 4),
    ml_score DECIMAL(5, 2),  -- Normalized to 0-100 for comparison
    ml_rank INTEGER,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(ticker, snapshot_date, model_version)
);

CREATE TABLE IF NOT EXISTS hybrid_scores (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    snapshot_date DATE NOT NULL,

    rule_score DECIMAL(5, 2),
    ml_score DECIMAL(5, 2),
    hybrid_score DECIMAL(5, 2),  -- Weighted average
    hybrid_rank INTEGER,

    rule_weight DECIMAL(3, 2) DEFAULT 0.50,
    ml_weight DECIMAL(3, 2) DEFAULT 0.50,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(ticker, snapshot_date)
);

CREATE TABLE IF NOT EXISTS shap_values (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    snapshot_date DATE NOT NULL,
    model_version VARCHAR(50) NOT NULL,

    -- Top contributing features stored as JSON
    -- e.g., {"pe_ratio": -0.05, "revenue_growth": 0.12, ...}
    feature_contributions JSONB NOT NULL,
    base_value DECIMAL(8, 4),

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(ticker, snapshot_date, model_version)
);

-- ============================================
-- INSIDER/CONGRESSIONAL TRADING (Phase 2)
-- ============================================

CREATE TABLE IF NOT EXISTS insider_trades (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    filed_date DATE NOT NULL,
    trade_date DATE,

    insider_name VARCHAR(255),
    insider_title VARCHAR(100),  -- CEO, CFO, Director, etc.
    trade_type VARCHAR(20),  -- 'buy', 'sell'
    shares INTEGER,
    price_per_share DECIMAL(12, 4),
    total_value DECIMAL(16, 2),

    source VARCHAR(50),  -- 'sec_form4'
    filing_url TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS congressional_trades (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    disclosure_date DATE NOT NULL,
    trade_date DATE,

    representative VARCHAR(255) NOT NULL,
    chamber VARCHAR(20),  -- 'house', 'senate'
    party VARCHAR(20),
    state VARCHAR(2),

    trade_type VARCHAR(20),  -- 'buy', 'sell'
    amount_range VARCHAR(50),  -- '$1,001 - $15,000', etc.

    source VARCHAR(50),  -- 'capitol_trades', 'quiver'

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- SNAPSHOTS & CONFIGURATION
-- ============================================

CREATE TABLE IF NOT EXISTS weekly_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL UNIQUE,
    scoring_model VARCHAR(20) NOT NULL,  -- 'rules', 'ml', 'hybrid'

    top_25_tickers TEXT[],  -- Array of top 25 ticker symbols
    config_hash VARCHAR(64),  -- Hash of scoring config for reproducibility

    total_stocks_processed INTEGER,
    etl_run_id UUID REFERENCES etl_runs(id),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sector_scores (
    id SERIAL PRIMARY KEY,
    sector VARCHAR(100) NOT NULL,
    snapshot_date DATE NOT NULL,

    avg_score DECIMAL(5, 2),
    stock_count INTEGER,
    top_3_tickers TEXT[],

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(sector, snapshot_date)
);

CREATE TABLE IF NOT EXISTS factor_weights (
    id SERIAL PRIMARY KEY,
    factor_name VARCHAR(50) NOT NULL UNIQUE,
    weight DECIMAL(4, 3) NOT NULL,  -- e.g., 0.200 = 20%
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS model_performance (
    id SERIAL PRIMARY KEY,
    model_version VARCHAR(50) NOT NULL,
    trained_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Training metrics
    train_rmse DECIMAL(8, 4),
    val_rmse DECIMAL(8, 4),
    test_rmse DECIMAL(8, 4),
    r2_score DECIMAL(6, 4),

    -- Backtest metrics
    sharpe_ratio DECIMAL(6, 4),
    total_return DECIMAL(8, 4),
    max_drawdown DECIMAL(6, 4),
    win_rate DECIMAL(5, 4),

    -- Feature importance (top 10)
    feature_importance JSONB,

    -- Config
    hyperparameters JSONB,
    training_data_range TEXT,  -- e.g., '2021-01-01 to 2024-01-01'

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX IF NOT EXISTS idx_raw_stock_data_ticker ON raw_stock_data(ticker);
CREATE INDEX IF NOT EXISTS idx_raw_stock_data_fetched_at ON raw_stock_data(fetched_at);
CREATE INDEX IF NOT EXISTS idx_raw_stock_data_run_id ON raw_stock_data(run_id);

CREATE INDEX IF NOT EXISTS idx_processed_stocks_ticker ON processed_stocks(ticker);
CREATE INDEX IF NOT EXISTS idx_processed_stocks_date ON processed_stocks(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_processed_stocks_sector ON processed_stocks(sector);

CREATE INDEX IF NOT EXISTS idx_stock_scores_ticker ON stock_scores(ticker);
CREATE INDEX IF NOT EXISTS idx_stock_scores_date ON stock_scores(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_stock_scores_rank ON stock_scores(rank);
CREATE INDEX IF NOT EXISTS idx_stock_scores_composite ON stock_scores(composite_score DESC);
CREATE INDEX IF NOT EXISTS idx_stock_scores_date_rank ON stock_scores(snapshot_date, rank);

CREATE INDEX IF NOT EXISTS idx_ml_predictions_ticker ON ml_predictions(ticker);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_date ON ml_predictions(snapshot_date);

CREATE INDEX IF NOT EXISTS idx_insider_trades_ticker ON insider_trades(ticker);
CREATE INDEX IF NOT EXISTS idx_insider_trades_date ON insider_trades(filed_date);

CREATE INDEX IF NOT EXISTS idx_congressional_trades_ticker ON congressional_trades(ticker);
CREATE INDEX IF NOT EXISTS idx_congressional_trades_date ON congressional_trades(disclosure_date);
