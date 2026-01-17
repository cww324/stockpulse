"""
StockPulse Database Utilities

Connection management and configuration for PostgreSQL database.

Usage:
    from database.db_utils import get_connection, get_connection_pool

    # Single connection
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM processed_stocks")

    # Connection pool (for ETL)
    pool = get_connection_pool()
    conn = pool.getconn()
    # ... use connection ...
    pool.putconn(conn)
"""

import os
import logging
from contextlib import contextmanager
from typing import Optional, Generator
from functools import lru_cache

import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor, execute_values
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

def get_database_url() -> str:
    """Get database URL from environment or use default."""
    return os.getenv(
        'DATABASE_URL',
        'postgresql://stockpulse:stockpulse_dev@localhost:5433/stockpulse'
    )


def parse_database_url(url: str) -> dict:
    """Parse database URL into connection parameters."""
    # postgresql://user:password@host:port/database
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5433,
        'database': parsed.path.lstrip('/') or 'stockpulse',
        'user': parsed.username or 'stockpulse',
        'password': parsed.password or 'stockpulse_dev',
    }


# ============================================
# CONNECTION MANAGEMENT
# ============================================

@contextmanager
def get_connection(
    autocommit: bool = False,
    cursor_factory=RealDictCursor
) -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Get a database connection as a context manager.

    Args:
        autocommit: Whether to enable autocommit mode
        cursor_factory: Cursor factory to use (default: RealDictCursor)

    Yields:
        Database connection

    Usage:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM processed_stocks")
                rows = cur.fetchall()
    """
    conn = None
    try:
        db_params = parse_database_url(get_database_url())
        conn = psycopg2.connect(
            **db_params,
            cursor_factory=cursor_factory
        )
        conn.autocommit = autocommit
        yield conn
        if not autocommit:
            conn.commit()
    except Exception as e:
        if conn and not autocommit:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


# Connection pool singleton
_connection_pool: Optional[pool.ThreadedConnectionPool] = None


def get_connection_pool(
    minconn: int = 2,
    maxconn: int = 10
) -> pool.ThreadedConnectionPool:
    """
    Get or create a connection pool (singleton).

    Args:
        minconn: Minimum connections to maintain
        maxconn: Maximum connections allowed

    Returns:
        ThreadedConnectionPool instance

    Usage:
        pool = get_connection_pool()
        conn = pool.getconn()
        try:
            # use connection
        finally:
            pool.putconn(conn)
    """
    global _connection_pool

    if _connection_pool is None:
        db_params = parse_database_url(get_database_url())
        _connection_pool = pool.ThreadedConnectionPool(
            minconn,
            maxconn,
            **db_params
        )
        logger.info(f"Created connection pool (min={minconn}, max={maxconn})")

    return _connection_pool


def close_connection_pool():
    """Close the connection pool."""
    global _connection_pool
    if _connection_pool:
        _connection_pool.closeall()
        _connection_pool = None
        logger.info("Connection pool closed")


# ============================================
# HEALTH CHECK
# ============================================

def check_database_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                return cur.fetchone() is not None
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


def get_database_info() -> dict:
    """
    Get database information.

    Returns:
        Dict with database version and connection info
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()['version']

                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tables = [row['table_name'] for row in cur.fetchall()]

                return {
                    'connected': True,
                    'version': version,
                    'tables': tables,
                    'table_count': len(tables),
                }
    except Exception as e:
        return {
            'connected': False,
            'error': str(e),
        }


# ============================================
# UTILITY FUNCTIONS
# ============================================

def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                )
            """, (table_name,))
            return cur.fetchone()['exists']


def get_row_count(table_name: str) -> int:
    """Get row count for a table."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Use sql.Identifier to safely quote table name
            cur.execute(
                sql.SQL("SELECT COUNT(*) as count FROM {}").format(
                    sql.Identifier(table_name)
                )
            )
            return cur.fetchone()['count']


def execute_sql_file(filepath: str) -> None:
    """
    Execute a SQL file against the database.

    Args:
        filepath: Path to SQL file
    """
    with open(filepath, 'r') as f:
        sql_content = f.read()

    with get_connection(autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_content)
            logger.info(f"Executed SQL file: {filepath}")
