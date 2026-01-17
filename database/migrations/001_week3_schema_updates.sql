-- Migration 001: Week 3 Schema Updates
-- Date: January 17, 2026
-- Description: Add fields identified during Week 2 data exploration
--
-- Changes:
--   1. Add fifty_two_week_high, fifty_two_week_low, beta to processed_stocks
--   2. Add is_value_trap to stock_scores
--   3. Add performance indexes for ranking queries

-- ============================================
-- PROCESSED_STOCKS: Add 52-week range and beta
-- ============================================

ALTER TABLE processed_stocks
ADD COLUMN IF NOT EXISTS fifty_two_week_high DECIMAL(12, 4);

ALTER TABLE processed_stocks
ADD COLUMN IF NOT EXISTS fifty_two_week_low DECIMAL(12, 4);

ALTER TABLE processed_stocks
ADD COLUMN IF NOT EXISTS beta DECIMAL(6, 4);

-- ============================================
-- STOCK_SCORES: Add value trap detection
-- ============================================

ALTER TABLE stock_scores
ADD COLUMN IF NOT EXISTS is_value_trap BOOLEAN DEFAULT FALSE;

-- ============================================
-- NEW INDEXES: Performance optimization
-- ============================================

CREATE INDEX IF NOT EXISTS idx_stock_scores_composite
ON stock_scores(composite_score DESC);

CREATE INDEX IF NOT EXISTS idx_stock_scores_date_rank
ON stock_scores(snapshot_date, rank);

-- ============================================
-- COMMENTS: Document field mappings
-- ============================================

COMMENT ON COLUMN stock_scores.value_score IS 'Valuation score (30% weight) - maps to scoring_methodology.md v2.0';
COMMENT ON COLUMN stock_scores.profitability_score IS 'Profitability score (25% weight)';
COMMENT ON COLUMN stock_scores.growth_score IS 'Growth score (20% weight)';
COMMENT ON COLUMN stock_scores.momentum_score IS 'Momentum score (15% weight)';
COMMENT ON COLUMN stock_scores.quality_score IS 'Health/Quality score (10% weight)';
COMMENT ON COLUMN stock_scores.is_value_trap IS 'True if stock flagged as value trap (cheap + declining + falling)';

COMMENT ON COLUMN processed_stocks.fifty_two_week_high IS '52-week high price for valuation scoring';
COMMENT ON COLUMN processed_stocks.fifty_two_week_low IS '52-week low price for valuation scoring';
COMMENT ON COLUMN processed_stocks.beta IS 'Stock beta vs market (volatility measure)';

-- ============================================
-- VERIFICATION
-- ============================================

-- Run this to verify migration success:
-- SELECT column_name, data_type FROM information_schema.columns
-- WHERE table_name = 'processed_stocks' AND column_name IN ('fifty_two_week_high', 'fifty_two_week_low', 'beta');
--
-- SELECT column_name, data_type FROM information_schema.columns
-- WHERE table_name = 'stock_scores' AND column_name = 'is_value_trap';
