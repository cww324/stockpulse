"""
StockPulse Database Package

Provides database utilities, models, and helper functions.

Usage:
    from database.db_utils import get_connection
    from database.models import ProcessedStock, StockScore
    from database.helpers import upsert_processed_stock, get_top_stocks
"""

from database.db_utils import (
    get_connection,
    get_connection_pool,
    close_connection_pool,
    check_database_connection,
    get_database_info,
    table_exists,
    get_row_count,
)

from database.models import (
    ProcessedStock,
    StockScore,
    RawStockData,
    ETLRun,
    StockRanking,
    StockDetail,
    DEFAULT_FACTOR_WEIGHTS,
)

__all__ = [
    # db_utils
    "get_connection",
    "get_connection_pool",
    "close_connection_pool",
    "check_database_connection",
    "get_database_info",
    "table_exists",
    "get_row_count",
    # models
    "ProcessedStock",
    "StockScore",
    "RawStockData",
    "ETLRun",
    "StockRanking",
    "StockDetail",
    "DEFAULT_FACTOR_WEIGHTS",
]
