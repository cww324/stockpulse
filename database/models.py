"""
StockPulse Database Models

Pydantic models for data validation and serialization.
Maps to database schema defined in schema.sql.

Usage:
    from database.models import ProcessedStock, StockScore

    stock = ProcessedStock(ticker="AAPL", company_name="Apple Inc.", ...)
    stock_dict = stock.model_dump()
"""

from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal


# ============================================
# SILVER LAYER: Processed Stock Data
# ============================================

class ProcessedStock(BaseModel):
    """
    Cleaned stock data ready for scoring.
    Maps to: processed_stocks table
    """
    # Identifiers
    ticker: str = Field(..., max_length=10)
    company_name: Optional[str] = Field(None, max_length=255)
    sector: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    market_cap: Optional[int] = None

    # Price data
    current_price: Optional[float] = None
    price_change_1d: Optional[float] = None
    price_change_1w: Optional[float] = None
    price_change_1m: Optional[float] = None
    price_change_3m: Optional[float] = None
    price_change_6m: Optional[float] = None  # Used for momentum scoring
    price_change_1y: Optional[float] = None   # Used for 12-month momentum

    # Valuation ratios
    pe_ratio: Optional[float] = None          # Trailing P/E
    pb_ratio: Optional[float] = None          # Price-to-Book
    ps_ratio: Optional[float] = None          # Price-to-Sales
    peg_ratio: Optional[float] = None

    # 52-week range (for valuation scoring)
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None

    # Profitability
    profit_margin: Optional[float] = None     # Net profit margin
    operating_margin: Optional[float] = None
    roe: Optional[float] = None               # Return on Equity
    roa: Optional[float] = None               # Return on Assets (NEW)
    roic: Optional[float] = None              # Return on Invested Capital

    # Growth
    revenue_growth_yoy: Optional[float] = None
    earnings_growth_yoy: Optional[float] = None

    # Financial health
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    free_cash_flow: Optional[int] = None

    # Dividend
    dividend_yield: Optional[float] = None    # Used in valuation scoring
    payout_ratio: Optional[float] = None

    # Risk
    beta: Optional[float] = None

    # Metadata
    snapshot_date: date

    @field_validator('ticker')
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        return v.upper()

    class Config:
        from_attributes = True  # Allow ORM mode


class ProcessedStockCreate(ProcessedStock):
    """Schema for creating a new processed stock record."""
    pass


class ProcessedStockInDB(ProcessedStock):
    """Schema for processed stock with database fields."""
    id: int
    updated_at: datetime


# ============================================
# GOLD LAYER: Stock Scores
# ============================================

class StockScore(BaseModel):
    """
    Calculated scores for a stock.
    Maps to: stock_scores table

    Factor weights (from scoring_methodology.md v2.0):
        - value_score (valuation): 30%
        - profitability_score: 25%
        - growth_score: 20%
        - momentum_score: 15%
        - quality_score (health): 10%
    """
    # Identifiers
    ticker: str = Field(..., max_length=10)
    snapshot_date: date

    # Individual factor scores (0-100)
    value_score: Optional[float] = Field(None, ge=0, le=100)
    profitability_score: Optional[float] = Field(None, ge=0, le=100)
    growth_score: Optional[float] = Field(None, ge=0, le=100)
    momentum_score: Optional[float] = Field(None, ge=0, le=100)
    quality_score: Optional[float] = Field(None, ge=0, le=100)  # = health_score

    # Composite
    composite_score: Optional[float] = Field(None, ge=0, le=100)
    rank: Optional[int] = Field(None, ge=1)
    percentile: Optional[float] = Field(None, ge=0, le=100)

    # Value trap detection
    is_value_trap: bool = False

    # Explanations
    value_explanation: Optional[str] = None
    growth_explanation: Optional[str] = None
    profitability_explanation: Optional[str] = None
    momentum_explanation: Optional[str] = None
    quality_explanation: Optional[str] = None

    @field_validator('ticker')
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        return v.upper()

    class Config:
        from_attributes = True


class StockScoreCreate(StockScore):
    """Schema for creating a new stock score record."""
    pass


class StockScoreInDB(StockScore):
    """Schema for stock score with database fields."""
    id: int
    updated_at: datetime


# ============================================
# BRONZE LAYER: Raw Data
# ============================================

class RawStockData(BaseModel):
    """
    Raw API response data.
    Maps to: raw_stock_data table
    """
    ticker: str = Field(..., max_length=10)
    data_source: str = Field(..., max_length=50)  # 'yfinance', 'alpha_vantage'
    raw_json: dict
    run_id: str  # UUID as string

    @field_validator('ticker')
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        return v.upper()


class RawStockDataInDB(RawStockData):
    """Schema for raw stock data with database fields."""
    id: int
    fetched_at: datetime


# ============================================
# ETL TRACKING
# ============================================

class ETLRun(BaseModel):
    """
    ETL run tracking.
    Maps to: etl_runs table
    """
    id: str  # UUID as string
    run_type: str  # 'ingest', 'transform', 'score', 'ml_inference'
    status: str = 'running'  # 'running', 'success', 'failed'
    stocks_processed: int = 0
    error_message: Optional[str] = None
    metadata: Optional[dict] = None


class ETLRunInDB(ETLRun):
    """Schema for ETL run with database fields."""
    started_at: datetime
    completed_at: Optional[datetime] = None


# ============================================
# ML PREDICTIONS
# ============================================

class MLPrediction(BaseModel):
    """
    ML model predictions.
    Maps to: ml_predictions table
    """
    ticker: str = Field(..., max_length=10)
    snapshot_date: date
    model_version: str = Field(..., max_length=50)

    predicted_return_3m: Optional[float] = None
    prediction_confidence: Optional[float] = Field(None, ge=0, le=1)
    ml_score: Optional[float] = Field(None, ge=0, le=100)
    ml_rank: Optional[int] = Field(None, ge=1)

    class Config:
        from_attributes = True


# ============================================
# RESPONSE MODELS (for API)
# ============================================

class StockRanking(BaseModel):
    """Stock ranking for API response."""
    rank: int
    ticker: str
    company_name: Optional[str]
    sector: Optional[str]
    composite_score: float
    value_score: Optional[float]
    profitability_score: Optional[float]
    growth_score: Optional[float]
    momentum_score: Optional[float]
    quality_score: Optional[float]
    is_value_trap: bool = False
    current_price: Optional[float]
    price_change_1d: Optional[float]


class StockDetail(BaseModel):
    """Detailed stock information for API response."""
    # Basic info
    ticker: str
    company_name: Optional[str]
    sector: Optional[str]
    industry: Optional[str]
    market_cap: Optional[int]
    current_price: Optional[float]

    # Scores
    composite_score: Optional[float]
    rank: Optional[int]
    value_score: Optional[float]
    profitability_score: Optional[float]
    growth_score: Optional[float]
    momentum_score: Optional[float]
    quality_score: Optional[float]
    is_value_trap: bool = False

    # Key metrics
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    roe: Optional[float]
    roa: Optional[float]
    profit_margin: Optional[float]
    revenue_growth_yoy: Optional[float]
    debt_to_equity: Optional[float]
    dividend_yield: Optional[float]

    # Price performance
    price_change_1d: Optional[float]
    price_change_1w: Optional[float]
    price_change_1m: Optional[float]
    price_change_6m: Optional[float]
    price_change_1y: Optional[float]

    # Explanations
    value_explanation: Optional[str]
    profitability_explanation: Optional[str]
    growth_explanation: Optional[str]
    momentum_explanation: Optional[str]
    quality_explanation: Optional[str]


class SectorSummary(BaseModel):
    """Sector summary for API response."""
    sector: str
    avg_score: float
    stock_count: int
    top_3_tickers: List[str]


# ============================================
# FACTOR WEIGHTS CONFIG
# ============================================

class FactorWeight(BaseModel):
    """
    Factor weight configuration.
    Maps to: factor_weights table

    Default weights (from scoring_methodology.md v2.0):
        - valuation: 0.30 (30%)
        - profitability: 0.25 (25%)
        - growth: 0.20 (20%)
        - momentum: 0.15 (15%)
        - health: 0.10 (10%)
    """
    factor_name: str = Field(..., max_length=50)
    weight: float = Field(..., ge=0, le=1)
    description: Optional[str] = None
    active: bool = True


# Default factor weights
DEFAULT_FACTOR_WEIGHTS = {
    'valuation': 0.30,
    'profitability': 0.25,
    'growth': 0.20,
    'momentum': 0.15,
    'health': 0.10,
}
