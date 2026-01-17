"""
StockPulse Database Helpers

CRUD operations for all database tables.
Uses parameterized queries to prevent SQL injection.

Usage:
    from database.helpers import (
        upsert_processed_stock,
        get_processed_stock,
        get_top_stocks,
    )

    # Insert/update a stock
    upsert_processed_stock(stock_data)

    # Get stock data
    stock = get_processed_stock("AAPL", date.today())

    # Get top ranked stocks
    top_25 = get_top_stocks(date.today(), limit=25)
"""

import logging
from datetime import date
from typing import Optional, List, Dict, Any
from uuid import uuid4
import json

from psycopg2.extras import execute_values

from database.db_utils import get_connection
from database.models import (
    ProcessedStock,
    StockScore,
    RawStockData,
    ETLRun,
    StockRanking,
    StockDetail,
)

logger = logging.getLogger(__name__)


# ============================================
# BRONZE LAYER: Raw Stock Data
# ============================================

def insert_raw_stock_data(
    ticker: str,
    data_source: str,
    raw_json: dict,
    run_id: str
) -> int:
    """
    Insert raw API response data.

    Args:
        ticker: Stock ticker symbol
        data_source: Source of data ('yfinance', 'alpha_vantage')
        raw_json: Raw API response as dict
        run_id: UUID of the ETL run

    Returns:
        ID of inserted record
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO raw_stock_data (ticker, data_source, raw_json, run_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (ticker.upper(), data_source, json.dumps(raw_json), run_id))
            return cur.fetchone()['id']


def get_raw_stock_data(
    ticker: str,
    snapshot_date: Optional[date] = None
) -> Optional[dict]:
    """
    Get raw stock data for a ticker.

    Args:
        ticker: Stock ticker symbol
        snapshot_date: Optional date filter

    Returns:
        Raw data dict or None
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            if snapshot_date:
                cur.execute("""
                    SELECT * FROM raw_stock_data
                    WHERE ticker = %s AND DATE(fetched_at) = %s
                    ORDER BY fetched_at DESC
                    LIMIT 1
                """, (ticker.upper(), snapshot_date))
            else:
                cur.execute("""
                    SELECT * FROM raw_stock_data
                    WHERE ticker = %s
                    ORDER BY fetched_at DESC
                    LIMIT 1
                """, (ticker.upper(),))
            return cur.fetchone()


# ============================================
# SILVER LAYER: Processed Stocks
# ============================================

def upsert_processed_stock(stock_data: dict) -> int:
    """
    Insert or update a processed stock record.

    Uses INSERT ... ON CONFLICT DO UPDATE for upsert behavior.

    Args:
        stock_data: Dict with stock data fields

    Returns:
        ID of upserted record
    """
    # Ensure ticker is uppercase
    stock_data['ticker'] = stock_data['ticker'].upper()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO processed_stocks (
                    ticker, company_name, sector, industry, market_cap,
                    current_price, price_change_1d, price_change_1w,
                    price_change_1m, price_change_3m, price_change_6m, price_change_1y,
                    pe_ratio, pb_ratio, ps_ratio, peg_ratio,
                    fifty_two_week_high, fifty_two_week_low,
                    profit_margin, operating_margin, roe, roa, roic,
                    revenue_growth_yoy, earnings_growth_yoy,
                    debt_to_equity, current_ratio, quick_ratio, free_cash_flow,
                    dividend_yield, payout_ratio, beta,
                    snapshot_date
                ) VALUES (
                    %(ticker)s, %(company_name)s, %(sector)s, %(industry)s, %(market_cap)s,
                    %(current_price)s, %(price_change_1d)s, %(price_change_1w)s,
                    %(price_change_1m)s, %(price_change_3m)s, %(price_change_6m)s, %(price_change_1y)s,
                    %(pe_ratio)s, %(pb_ratio)s, %(ps_ratio)s, %(peg_ratio)s,
                    %(fifty_two_week_high)s, %(fifty_two_week_low)s,
                    %(profit_margin)s, %(operating_margin)s, %(roe)s, %(roa)s, %(roic)s,
                    %(revenue_growth_yoy)s, %(earnings_growth_yoy)s,
                    %(debt_to_equity)s, %(current_ratio)s, %(quick_ratio)s, %(free_cash_flow)s,
                    %(dividend_yield)s, %(payout_ratio)s, %(beta)s,
                    %(snapshot_date)s
                )
                ON CONFLICT (ticker, snapshot_date)
                DO UPDATE SET
                    company_name = EXCLUDED.company_name,
                    sector = EXCLUDED.sector,
                    industry = EXCLUDED.industry,
                    market_cap = EXCLUDED.market_cap,
                    current_price = EXCLUDED.current_price,
                    price_change_1d = EXCLUDED.price_change_1d,
                    price_change_1w = EXCLUDED.price_change_1w,
                    price_change_1m = EXCLUDED.price_change_1m,
                    price_change_3m = EXCLUDED.price_change_3m,
                    price_change_6m = EXCLUDED.price_change_6m,
                    price_change_1y = EXCLUDED.price_change_1y,
                    pe_ratio = EXCLUDED.pe_ratio,
                    pb_ratio = EXCLUDED.pb_ratio,
                    ps_ratio = EXCLUDED.ps_ratio,
                    peg_ratio = EXCLUDED.peg_ratio,
                    fifty_two_week_high = EXCLUDED.fifty_two_week_high,
                    fifty_two_week_low = EXCLUDED.fifty_two_week_low,
                    profit_margin = EXCLUDED.profit_margin,
                    operating_margin = EXCLUDED.operating_margin,
                    roe = EXCLUDED.roe,
                    roa = EXCLUDED.roa,
                    roic = EXCLUDED.roic,
                    revenue_growth_yoy = EXCLUDED.revenue_growth_yoy,
                    earnings_growth_yoy = EXCLUDED.earnings_growth_yoy,
                    debt_to_equity = EXCLUDED.debt_to_equity,
                    current_ratio = EXCLUDED.current_ratio,
                    quick_ratio = EXCLUDED.quick_ratio,
                    free_cash_flow = EXCLUDED.free_cash_flow,
                    dividend_yield = EXCLUDED.dividend_yield,
                    payout_ratio = EXCLUDED.payout_ratio,
                    beta = EXCLUDED.beta,
                    updated_at = NOW()
                RETURNING id
            """, stock_data)
            return cur.fetchone()['id']


def get_processed_stock(ticker: str, snapshot_date: date) -> Optional[dict]:
    """
    Get processed stock data for a specific date.

    Args:
        ticker: Stock ticker symbol
        snapshot_date: Date to get data for

    Returns:
        Stock data dict or None
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM processed_stocks
                WHERE ticker = %s AND snapshot_date = %s
            """, (ticker.upper(), snapshot_date))
            return cur.fetchone()


def get_all_processed_stocks(snapshot_date: date) -> List[dict]:
    """
    Get all processed stocks for a specific date.

    Args:
        snapshot_date: Date to get data for

    Returns:
        List of stock data dicts
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM processed_stocks
                WHERE snapshot_date = %s
                ORDER BY ticker
            """, (snapshot_date,))
            return cur.fetchall()


def get_stocks_by_sector(sector: str, snapshot_date: date) -> List[dict]:
    """
    Get all stocks in a sector for a specific date.

    Args:
        sector: Sector name
        snapshot_date: Date to get data for

    Returns:
        List of stock data dicts
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM processed_stocks
                WHERE sector = %s AND snapshot_date = %s
                ORDER BY ticker
            """, (sector, snapshot_date))
            return cur.fetchall()


def get_sector_medians(sector: str, snapshot_date: date) -> dict:
    """
    Get median values for key metrics in a sector.

    Used for sector-relative scoring.

    Args:
        sector: Sector name
        snapshot_date: Date to calculate medians for

    Returns:
        Dict with median values
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pe_ratio) as pe_median,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY pb_ratio) as pb_median,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ps_ratio) as ps_median,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY roe) as roe_median,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY roa) as roa_median,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY profit_margin) as profit_margin_median,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY operating_margin) as operating_margin_median,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY debt_to_equity) as debt_to_equity_median,
                    COUNT(*) as stock_count
                FROM processed_stocks
                WHERE sector = %s AND snapshot_date = %s
                AND pe_ratio IS NOT NULL
            """, (sector, snapshot_date))
            return cur.fetchone()


def get_all_sectors(snapshot_date: date) -> List[str]:
    """
    Get list of all sectors for a specific date.

    Args:
        snapshot_date: Date to get sectors for

    Returns:
        List of sector names
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT sector
                FROM processed_stocks
                WHERE snapshot_date = %s AND sector IS NOT NULL
                ORDER BY sector
            """, (snapshot_date,))
            return [row['sector'] for row in cur.fetchall()]


# ============================================
# GOLD LAYER: Stock Scores
# ============================================

def upsert_stock_score(score_data: dict) -> int:
    """
    Insert or update a stock score record.

    Args:
        score_data: Dict with score data fields

    Returns:
        ID of upserted record
    """
    score_data['ticker'] = score_data['ticker'].upper()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO stock_scores (
                    ticker, snapshot_date,
                    value_score, growth_score, profitability_score,
                    momentum_score, quality_score,
                    composite_score, rank, percentile, is_value_trap,
                    value_explanation, growth_explanation, profitability_explanation,
                    momentum_explanation, quality_explanation
                ) VALUES (
                    %(ticker)s, %(snapshot_date)s,
                    %(value_score)s, %(growth_score)s, %(profitability_score)s,
                    %(momentum_score)s, %(quality_score)s,
                    %(composite_score)s, %(rank)s, %(percentile)s, %(is_value_trap)s,
                    %(value_explanation)s, %(growth_explanation)s, %(profitability_explanation)s,
                    %(momentum_explanation)s, %(quality_explanation)s
                )
                ON CONFLICT (ticker, snapshot_date)
                DO UPDATE SET
                    value_score = EXCLUDED.value_score,
                    growth_score = EXCLUDED.growth_score,
                    profitability_score = EXCLUDED.profitability_score,
                    momentum_score = EXCLUDED.momentum_score,
                    quality_score = EXCLUDED.quality_score,
                    composite_score = EXCLUDED.composite_score,
                    rank = EXCLUDED.rank,
                    percentile = EXCLUDED.percentile,
                    is_value_trap = EXCLUDED.is_value_trap,
                    value_explanation = EXCLUDED.value_explanation,
                    growth_explanation = EXCLUDED.growth_explanation,
                    profitability_explanation = EXCLUDED.profitability_explanation,
                    momentum_explanation = EXCLUDED.momentum_explanation,
                    quality_explanation = EXCLUDED.quality_explanation,
                    updated_at = NOW()
                RETURNING id
            """, score_data)
            return cur.fetchone()['id']


def get_stock_score(ticker: str, snapshot_date: date) -> Optional[dict]:
    """
    Get score for a specific stock and date.

    Args:
        ticker: Stock ticker symbol
        snapshot_date: Date to get score for

    Returns:
        Score dict or None
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM stock_scores
                WHERE ticker = %s AND snapshot_date = %s
            """, (ticker.upper(), snapshot_date))
            return cur.fetchone()


def get_top_stocks(
    snapshot_date: date,
    limit: int = 25,
    exclude_value_traps: bool = True
) -> List[dict]:
    """
    Get top ranked stocks for a specific date.

    Args:
        snapshot_date: Date to get rankings for
        limit: Number of stocks to return
        exclude_value_traps: Whether to exclude value trap stocks

    Returns:
        List of score dicts ordered by rank
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            if exclude_value_traps:
                cur.execute("""
                    SELECT s.*, p.company_name, p.sector, p.current_price, p.price_change_1d
                    FROM stock_scores s
                    JOIN processed_stocks p ON s.ticker = p.ticker AND s.snapshot_date = p.snapshot_date
                    WHERE s.snapshot_date = %s AND s.is_value_trap = FALSE
                    ORDER BY s.rank ASC
                    LIMIT %s
                """, (snapshot_date, limit))
            else:
                cur.execute("""
                    SELECT s.*, p.company_name, p.sector, p.current_price, p.price_change_1d
                    FROM stock_scores s
                    JOIN processed_stocks p ON s.ticker = p.ticker AND s.snapshot_date = p.snapshot_date
                    WHERE s.snapshot_date = %s
                    ORDER BY s.rank ASC
                    LIMIT %s
                """, (snapshot_date, limit))
            return cur.fetchall()


def get_all_stock_scores(snapshot_date: date) -> List[dict]:
    """
    Get all stock scores for a specific date.

    Args:
        snapshot_date: Date to get scores for

    Returns:
        List of score dicts
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM stock_scores
                WHERE snapshot_date = %s
                ORDER BY rank ASC
            """, (snapshot_date,))
            return cur.fetchall()


# ============================================
# ETL TRACKING
# ============================================

def create_etl_run(run_type: str, metadata: Optional[dict] = None) -> str:
    """
    Create a new ETL run record.

    Args:
        run_type: Type of run ('ingest', 'transform', 'score', 'ml_inference')
        metadata: Optional metadata dict

    Returns:
        UUID of created run
    """
    run_id = str(uuid4())

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO etl_runs (id, run_type, metadata)
                VALUES (%s, %s, %s)
            """, (run_id, run_type, json.dumps(metadata) if metadata else None))

    return run_id


def update_etl_run(
    run_id: str,
    status: str,
    stocks_processed: int = 0,
    error_message: Optional[str] = None
) -> None:
    """
    Update an ETL run record.

    Args:
        run_id: UUID of the run
        status: New status ('success', 'failed')
        stocks_processed: Number of stocks processed
        error_message: Optional error message
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE etl_runs
                SET status = %s,
                    completed_at = NOW(),
                    stocks_processed = %s,
                    error_message = %s
                WHERE id = %s
            """, (status, stocks_processed, error_message, run_id))


def get_latest_etl_run(run_type: Optional[str] = None) -> Optional[dict]:
    """
    Get the most recent ETL run.

    Args:
        run_type: Optional filter by run type

    Returns:
        ETL run dict or None
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            if run_type:
                cur.execute("""
                    SELECT * FROM etl_runs
                    WHERE run_type = %s
                    ORDER BY started_at DESC
                    LIMIT 1
                """, (run_type,))
            else:
                cur.execute("""
                    SELECT * FROM etl_runs
                    ORDER BY started_at DESC
                    LIMIT 1
                """)
            return cur.fetchone()


# ============================================
# FACTOR WEIGHTS
# ============================================

def get_factor_weights() -> dict:
    """
    Get current factor weights.

    Returns:
        Dict mapping factor names to weights
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT factor_name, weight
                FROM factor_weights
                WHERE active = TRUE
            """)
            rows = cur.fetchall()
            return {row['factor_name']: float(row['weight']) for row in rows}


def update_factor_weight(factor_name: str, weight: float) -> None:
    """
    Update a factor weight.

    Args:
        factor_name: Name of the factor
        weight: New weight value (0-1)
    """
    if not 0 <= weight <= 1:
        raise ValueError("Weight must be between 0 and 1")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE factor_weights
                SET weight = %s, updated_at = NOW()
                WHERE factor_name = %s
            """, (weight, factor_name))


# ============================================
# BULK OPERATIONS (for ETL)
# ============================================

def bulk_upsert_processed_stocks(stocks: List[dict]) -> int:
    """
    Bulk upsert processed stocks for ETL performance.

    Args:
        stocks: List of stock data dicts

    Returns:
        Number of stocks upserted
    """
    if not stocks:
        return 0

    # Ensure all tickers are uppercase
    for stock in stocks:
        stock['ticker'] = stock['ticker'].upper()

    columns = [
        'ticker', 'company_name', 'sector', 'industry', 'market_cap',
        'current_price', 'price_change_1d', 'price_change_1w',
        'price_change_1m', 'price_change_3m', 'price_change_6m', 'price_change_1y',
        'pe_ratio', 'pb_ratio', 'ps_ratio', 'peg_ratio',
        'fifty_two_week_high', 'fifty_two_week_low',
        'profit_margin', 'operating_margin', 'roe', 'roa', 'roic',
        'revenue_growth_yoy', 'earnings_growth_yoy',
        'debt_to_equity', 'current_ratio', 'quick_ratio', 'free_cash_flow',
        'dividend_yield', 'payout_ratio', 'beta',
        'snapshot_date'
    ]

    values = [
        tuple(stock.get(col) for col in columns)
        for stock in stocks
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(
                cur,
                f"""
                INSERT INTO processed_stocks ({', '.join(columns)})
                VALUES %s
                ON CONFLICT (ticker, snapshot_date)
                DO UPDATE SET
                    company_name = EXCLUDED.company_name,
                    sector = EXCLUDED.sector,
                    current_price = EXCLUDED.current_price,
                    updated_at = NOW()
                """,
                values
            )
            return len(stocks)


def bulk_upsert_stock_scores(scores: List[dict]) -> int:
    """
    Bulk upsert stock scores for ETL performance.

    Args:
        scores: List of score data dicts

    Returns:
        Number of scores upserted
    """
    if not scores:
        return 0

    for score in scores:
        score['ticker'] = score['ticker'].upper()

    columns = [
        'ticker', 'snapshot_date',
        'value_score', 'growth_score', 'profitability_score',
        'momentum_score', 'quality_score',
        'composite_score', 'rank', 'percentile', 'is_value_trap'
    ]

    values = [
        tuple(score.get(col) for col in columns)
        for score in scores
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(
                cur,
                f"""
                INSERT INTO stock_scores ({', '.join(columns)})
                VALUES %s
                ON CONFLICT (ticker, snapshot_date)
                DO UPDATE SET
                    value_score = EXCLUDED.value_score,
                    growth_score = EXCLUDED.growth_score,
                    profitability_score = EXCLUDED.profitability_score,
                    momentum_score = EXCLUDED.momentum_score,
                    quality_score = EXCLUDED.quality_score,
                    composite_score = EXCLUDED.composite_score,
                    rank = EXCLUDED.rank,
                    percentile = EXCLUDED.percentile,
                    is_value_trap = EXCLUDED.is_value_trap,
                    updated_at = NOW()
                """,
                values
            )
            return len(scores)
