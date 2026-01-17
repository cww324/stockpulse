"""
StockPulse Database Tests

Unit tests for database operations.
Uses mocking for unit tests and real database for integration tests.

Run unit tests only:
    pytest tests/test_database.py -m "not integration"

Run all tests (requires Docker database):
    pytest tests/test_database.py

Run with coverage:
    pytest tests/test_database.py --cov=database --cov-report=html
"""

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock
from uuid import uuid4

# ============================================
# UNIT TESTS (no database required)
# ============================================


class TestModels:
    """Test Pydantic model validation."""

    def test_processed_stock_ticker_uppercase(self):
        """ProcessedStock should uppercase ticker."""
        from database.models import ProcessedStock

        stock = ProcessedStock(ticker="aapl", snapshot_date=date.today())
        assert stock.ticker == "AAPL"

    def test_processed_stock_optional_fields(self):
        """ProcessedStock should allow None for optional fields."""
        from database.models import ProcessedStock

        stock = ProcessedStock(
            ticker="AAPL",
            snapshot_date=date.today(),
            pe_ratio=None,
            roe=None,
        )
        assert stock.pe_ratio is None
        assert stock.roe is None

    def test_processed_stock_all_fields(self):
        """ProcessedStock should accept all fields."""
        from database.models import ProcessedStock

        stock = ProcessedStock(
            ticker="AAPL",
            company_name="Apple Inc.",
            sector="Technology",
            industry="Consumer Electronics",
            market_cap=3000000000000,
            current_price=175.50,
            price_change_1d=1.25,
            price_change_6m=15.5,
            price_change_1y=25.0,
            pe_ratio=28.5,
            pb_ratio=45.2,
            roe=0.165,
            roa=0.085,
            fifty_two_week_high=199.62,
            fifty_two_week_low=124.17,
            beta=1.25,
            snapshot_date=date.today(),
        )
        assert stock.ticker == "AAPL"
        assert stock.company_name == "Apple Inc."
        assert stock.beta == 1.25

    def test_stock_score_validation(self):
        """StockScore should validate score ranges."""
        from database.models import StockScore
        from pydantic import ValidationError

        # Valid scores
        score = StockScore(
            ticker="AAPL",
            snapshot_date=date.today(),
            value_score=75.5,
            composite_score=80.0,
        )
        assert score.value_score == 75.5

        # Invalid score (>100)
        with pytest.raises(ValidationError):
            StockScore(
                ticker="AAPL",
                snapshot_date=date.today(),
                value_score=150.0,  # Too high
            )

        # Invalid score (<0)
        with pytest.raises(ValidationError):
            StockScore(
                ticker="AAPL",
                snapshot_date=date.today(),
                value_score=-10.0,  # Negative
            )

    def test_stock_score_ticker_uppercase(self):
        """StockScore should uppercase ticker."""
        from database.models import StockScore

        score = StockScore(ticker="msft", snapshot_date=date.today())
        assert score.ticker == "MSFT"

    def test_etl_run_defaults(self):
        """ETLRun should have correct defaults."""
        from database.models import ETLRun

        run = ETLRun(id=str(uuid4()), run_type="ingest")
        assert run.status == "running"
        assert run.stocks_processed == 0

    def test_default_factor_weights(self):
        """DEFAULT_FACTOR_WEIGHTS should sum to 1.0."""
        from database.models import DEFAULT_FACTOR_WEIGHTS

        total = sum(DEFAULT_FACTOR_WEIGHTS.values())
        assert abs(total - 1.0) < 0.001  # Allow for floating point


class TestDbUtils:
    """Test database utility functions."""

    def test_parse_database_url(self):
        """parse_database_url should parse connection string."""
        from database.db_utils import parse_database_url

        url = "postgresql://user:pass@host:5432/dbname"
        params = parse_database_url(url)

        assert params["host"] == "host"
        assert params["port"] == 5432
        assert params["database"] == "dbname"
        assert params["user"] == "user"
        assert params["password"] == "pass"

    def test_parse_database_url_defaults(self):
        """parse_database_url should use defaults for missing parts."""
        from database.db_utils import parse_database_url

        url = "postgresql://localhost/stockpulse"
        params = parse_database_url(url)

        assert params["host"] == "localhost"
        assert params["port"] == 5433  # Our default
        assert params["database"] == "stockpulse"

    @patch("database.db_utils.psycopg2.connect")
    def test_get_connection_success(self, mock_connect):
        """get_connection should yield connection and commit."""
        from database.db_utils import get_connection

        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with get_connection() as conn:
            assert conn == mock_conn

        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("database.db_utils.psycopg2.connect")
    def test_get_connection_autocommit(self, mock_connect):
        """get_connection with autocommit should not call commit."""
        from database.db_utils import get_connection

        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with get_connection(autocommit=True) as conn:
            assert conn == mock_conn

        mock_conn.commit.assert_not_called()

    @patch("database.db_utils.psycopg2.connect")
    def test_get_connection_rollback_on_error(self, mock_connect):
        """get_connection should rollback on exception."""
        from database.db_utils import get_connection

        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        with pytest.raises(ValueError):
            with get_connection() as conn:
                raise ValueError("Test error")

        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()


class TestHelpersUnit:
    """Unit tests for helper functions with mocked database."""

    @patch("database.helpers.get_connection")
    def test_insert_raw_stock_data(self, mock_get_connection):
        """insert_raw_stock_data should insert and return ID."""
        from database.helpers import insert_raw_stock_data

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"id": 42}
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_connection.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_get_connection.return_value.__exit__ = MagicMock(return_value=False)

        result = insert_raw_stock_data(
            ticker="aapl",
            data_source="yfinance",
            raw_json={"price": 175.50},
            run_id=str(uuid4()),
        )

        assert result == 42
        mock_cursor.execute.assert_called_once()

    @patch("database.helpers.get_connection")
    def test_get_processed_stock(self, mock_get_connection):
        """get_processed_stock should return stock dict."""
        from database.helpers import get_processed_stock

        expected = {"ticker": "AAPL", "pe_ratio": 28.5}
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = expected
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_connection.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_get_connection.return_value.__exit__ = MagicMock(return_value=False)

        result = get_processed_stock("AAPL", date.today())

        assert result == expected

    @patch("database.helpers.get_connection")
    def test_get_processed_stock_not_found(self, mock_get_connection):
        """get_processed_stock should return None if not found."""
        from database.helpers import get_processed_stock

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_connection.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_get_connection.return_value.__exit__ = MagicMock(return_value=False)

        result = get_processed_stock("INVALID", date.today())

        assert result is None

    def test_update_factor_weight_validation(self):
        """update_factor_weight should validate weight range."""
        from database.helpers import update_factor_weight

        with pytest.raises(ValueError, match="between 0 and 1"):
            update_factor_weight("valuation", 1.5)

        with pytest.raises(ValueError, match="between 0 and 1"):
            update_factor_weight("valuation", -0.1)

    @patch("database.helpers.get_connection")
    def test_create_etl_run(self, mock_get_connection):
        """create_etl_run should create and return UUID."""
        from database.helpers import create_etl_run

        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_connection.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_get_connection.return_value.__exit__ = MagicMock(return_value=False)

        result = create_etl_run("ingest", {"source": "yfinance"})

        assert len(result) == 36  # UUID length
        mock_cursor.execute.assert_called_once()

    @patch("database.helpers.get_connection")
    def test_bulk_upsert_empty_list(self, mock_get_connection):
        """bulk_upsert should return 0 for empty list."""
        from database.helpers import bulk_upsert_processed_stocks

        result = bulk_upsert_processed_stocks([])

        assert result == 0
        mock_get_connection.assert_not_called()


# ============================================
# INTEGRATION TESTS (requires Docker database)
# ============================================


@pytest.fixture
def db_connection():
    """Get real database connection for integration tests."""
    from database.db_utils import check_database_connection, get_connection

    if not check_database_connection():
        pytest.skip("Database not available")

    return get_connection


@pytest.fixture
def cleanup_test_data(db_connection):
    """Clean up test data after each test."""
    yield

    # Clean up test data
    try:
        with db_connection() as conn:
            with conn.cursor() as cur:
                # Delete test stocks
                cur.execute(
                    "DELETE FROM stock_scores WHERE ticker LIKE 'TEST%'"
                )
                cur.execute(
                    "DELETE FROM processed_stocks WHERE ticker LIKE 'TEST%'"
                )
                cur.execute(
                    "DELETE FROM raw_stock_data WHERE ticker LIKE 'TEST%'"
                )
    except Exception:
        pass


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests that require a running database."""

    def test_database_connection(self, db_connection):
        """Test that we can connect to the database."""
        from database.db_utils import check_database_connection

        assert check_database_connection() is True

    def test_database_info(self, db_connection):
        """Test that we can get database info."""
        from database.db_utils import get_database_info

        info = get_database_info()

        assert info["connected"] is True
        assert "PostgreSQL" in info["version"]
        assert "tables" in info
        assert isinstance(info["table_count"], int)

    def test_table_exists(self, db_connection):
        """Test table_exists function."""
        from database.db_utils import table_exists

        assert table_exists("processed_stocks") is True
        assert table_exists("stock_scores") is True
        assert table_exists("nonexistent_table") is False

    def test_upsert_processed_stock_insert(
        self, db_connection, cleanup_test_data
    ):
        """Test inserting a new processed stock."""
        from database.helpers import upsert_processed_stock, get_processed_stock

        test_date = date.today()
        stock_data = {
            "ticker": "TESTAAPL",
            "company_name": "Test Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "market_cap": 3000000000000,
            "current_price": 175.50,
            "price_change_1d": 1.25,
            "price_change_1w": None,
            "price_change_1m": None,
            "price_change_3m": None,
            "price_change_6m": 15.5,
            "price_change_1y": 25.0,
            "pe_ratio": 28.5,
            "pb_ratio": 45.2,
            "ps_ratio": None,
            "peg_ratio": None,
            "fifty_two_week_high": 199.62,
            "fifty_two_week_low": 124.17,
            "profit_margin": 0.255,
            "operating_margin": 0.30,
            "roe": 0.165,
            "roa": 0.085,
            "roic": None,
            "revenue_growth_yoy": 0.08,
            "earnings_growth_yoy": 0.12,
            "debt_to_equity": 1.8,
            "current_ratio": 1.0,
            "quick_ratio": None,
            "free_cash_flow": 100000000000,
            "dividend_yield": 0.005,
            "payout_ratio": None,
            "beta": 1.25,
            "snapshot_date": test_date,
        }

        record_id = upsert_processed_stock(stock_data)
        assert record_id is not None

        # Verify data was inserted
        result = get_processed_stock("TESTAAPL", test_date)
        assert result is not None
        assert result["ticker"] == "TESTAAPL"
        assert result["company_name"] == "Test Apple Inc."
        assert float(result["pe_ratio"]) == 28.5

    def test_upsert_processed_stock_update(
        self, db_connection, cleanup_test_data
    ):
        """Test updating an existing processed stock."""
        from database.helpers import upsert_processed_stock, get_processed_stock

        test_date = date.today()
        base_data = {
            "ticker": "TESTMSFT",
            "company_name": "Test Microsoft",
            "sector": "Technology",
            "industry": None,
            "market_cap": None,
            "current_price": 400.00,
            "price_change_1d": None,
            "price_change_1w": None,
            "price_change_1m": None,
            "price_change_3m": None,
            "price_change_6m": None,
            "price_change_1y": None,
            "pe_ratio": 35.0,
            "pb_ratio": None,
            "ps_ratio": None,
            "peg_ratio": None,
            "fifty_two_week_high": None,
            "fifty_two_week_low": None,
            "profit_margin": None,
            "operating_margin": None,
            "roe": None,
            "roa": None,
            "roic": None,
            "revenue_growth_yoy": None,
            "earnings_growth_yoy": None,
            "debt_to_equity": None,
            "current_ratio": None,
            "quick_ratio": None,
            "free_cash_flow": None,
            "dividend_yield": None,
            "payout_ratio": None,
            "beta": None,
            "snapshot_date": test_date,
        }

        # Insert
        upsert_processed_stock(base_data)

        # Update
        base_data["current_price"] = 420.00
        base_data["pe_ratio"] = 37.0
        upsert_processed_stock(base_data)

        # Verify update
        result = get_processed_stock("TESTMSFT", test_date)
        assert float(result["current_price"]) == 420.00
        assert float(result["pe_ratio"]) == 37.0

    def test_upsert_stock_score(self, db_connection, cleanup_test_data):
        """Test inserting and updating stock scores."""
        from database.helpers import (
            upsert_processed_stock,
            upsert_stock_score,
            get_stock_score,
        )

        test_date = date.today()

        # First insert a processed stock (required for FK)
        stock_data = {
            "ticker": "TESTNVDA",
            "company_name": "Test NVIDIA",
            "sector": "Technology",
            "industry": None,
            "market_cap": None,
            "current_price": 900.00,
            "price_change_1d": None,
            "price_change_1w": None,
            "price_change_1m": None,
            "price_change_3m": None,
            "price_change_6m": None,
            "price_change_1y": None,
            "pe_ratio": None,
            "pb_ratio": None,
            "ps_ratio": None,
            "peg_ratio": None,
            "fifty_two_week_high": None,
            "fifty_two_week_low": None,
            "profit_margin": None,
            "operating_margin": None,
            "roe": None,
            "roa": None,
            "roic": None,
            "revenue_growth_yoy": None,
            "earnings_growth_yoy": None,
            "debt_to_equity": None,
            "current_ratio": None,
            "quick_ratio": None,
            "free_cash_flow": None,
            "dividend_yield": None,
            "payout_ratio": None,
            "beta": None,
            "snapshot_date": test_date,
        }
        upsert_processed_stock(stock_data)

        # Insert score
        score_data = {
            "ticker": "TESTNVDA",
            "snapshot_date": test_date,
            "value_score": 65.5,
            "growth_score": 85.0,
            "profitability_score": 78.5,
            "momentum_score": 92.0,
            "quality_score": 70.0,
            "composite_score": 80.5,
            "rank": 5,
            "percentile": 95.0,
            "is_value_trap": False,
            "value_explanation": "Good P/E ratio",
            "growth_explanation": "Strong revenue growth",
            "profitability_explanation": "High margins",
            "momentum_explanation": "Strong 6-month performance",
            "quality_explanation": "Healthy balance sheet",
        }

        record_id = upsert_stock_score(score_data)
        assert record_id is not None

        # Verify
        result = get_stock_score("TESTNVDA", test_date)
        assert result is not None
        assert float(result["composite_score"]) == 80.5
        assert result["rank"] == 5
        assert result["is_value_trap"] is False

    def test_get_top_stocks(self, db_connection, cleanup_test_data):
        """Test getting top ranked stocks."""
        from database.helpers import (
            upsert_processed_stock,
            upsert_stock_score,
            get_top_stocks,
        )

        test_date = date.today()

        # Create test stocks and scores
        for i, ticker in enumerate(["TESTA", "TESTB", "TESTC"]):
            stock_data = {
                "ticker": ticker,
                "company_name": f"Test Company {ticker}",
                "sector": "Technology",
                "industry": None,
                "market_cap": None,
                "current_price": 100.0 + i * 10,
                "price_change_1d": 1.0 + i * 0.5,
                "price_change_1w": None,
                "price_change_1m": None,
                "price_change_3m": None,
                "price_change_6m": None,
                "price_change_1y": None,
                "pe_ratio": None,
                "pb_ratio": None,
                "ps_ratio": None,
                "peg_ratio": None,
                "fifty_two_week_high": None,
                "fifty_two_week_low": None,
                "profit_margin": None,
                "operating_margin": None,
                "roe": None,
                "roa": None,
                "roic": None,
                "revenue_growth_yoy": None,
                "earnings_growth_yoy": None,
                "debt_to_equity": None,
                "current_ratio": None,
                "quick_ratio": None,
                "free_cash_flow": None,
                "dividend_yield": None,
                "payout_ratio": None,
                "beta": None,
                "snapshot_date": test_date,
            }
            upsert_processed_stock(stock_data)

            score_data = {
                "ticker": ticker,
                "snapshot_date": test_date,
                "value_score": 50.0 + i * 10,
                "growth_score": None,
                "profitability_score": None,
                "momentum_score": None,
                "quality_score": None,
                "composite_score": 50.0 + i * 10,
                "rank": i + 1,
                "percentile": None,
                "is_value_trap": ticker == "TESTC",  # Mark one as value trap
                "value_explanation": None,
                "growth_explanation": None,
                "profitability_explanation": None,
                "momentum_explanation": None,
                "quality_explanation": None,
            }
            upsert_stock_score(score_data)

        # Get top stocks excluding value traps
        top_stocks = get_top_stocks(test_date, limit=10, exclude_value_traps=True)
        tickers = [s["ticker"] for s in top_stocks]
        assert "TESTC" not in tickers  # Value trap excluded
        assert "TESTA" in tickers
        assert "TESTB" in tickers

        # Get top stocks including value traps
        all_stocks = get_top_stocks(test_date, limit=10, exclude_value_traps=False)
        tickers = [s["ticker"] for s in all_stocks]
        assert "TESTC" in tickers  # Value trap included

    def test_etl_run_lifecycle(self, db_connection):
        """Test ETL run create and update."""
        from database.helpers import (
            create_etl_run,
            update_etl_run,
            get_latest_etl_run,
        )

        # Create run
        run_id = create_etl_run("ingest", {"source": "yfinance", "test": True})
        assert len(run_id) == 36

        # Get latest
        run = get_latest_etl_run("ingest")
        assert run is not None
        assert run["status"] == "running"

        # Update with success
        update_etl_run(run_id, "success", stocks_processed=100)

        # Verify update
        run = get_latest_etl_run("ingest")
        assert run["status"] == "success"
        assert run["stocks_processed"] == 100

    def test_sector_medians(self, db_connection, cleanup_test_data):
        """Test sector median calculations."""
        from database.helpers import (
            upsert_processed_stock,
            get_sector_medians,
        )

        test_date = date.today()

        # Create multiple stocks in same sector
        for i, ticker in enumerate(["TESTTECH1", "TESTTECH2", "TESTTECH3"]):
            stock_data = {
                "ticker": ticker,
                "company_name": f"Test Tech {i+1}",
                "sector": "TestTechnology",
                "industry": None,
                "market_cap": None,
                "current_price": 100.0,
                "price_change_1d": None,
                "price_change_1w": None,
                "price_change_1m": None,
                "price_change_3m": None,
                "price_change_6m": None,
                "price_change_1y": None,
                "pe_ratio": 20.0 + i * 10,  # 20, 30, 40
                "pb_ratio": None,
                "ps_ratio": None,
                "peg_ratio": None,
                "fifty_two_week_high": None,
                "fifty_two_week_low": None,
                "profit_margin": None,
                "operating_margin": None,
                "roe": 0.10 + i * 0.05,  # 0.10, 0.15, 0.20
                "roa": None,
                "roic": None,
                "revenue_growth_yoy": None,
                "earnings_growth_yoy": None,
                "debt_to_equity": None,
                "current_ratio": None,
                "quick_ratio": None,
                "free_cash_flow": None,
                "dividend_yield": None,
                "payout_ratio": None,
                "beta": None,
                "snapshot_date": test_date,
            }
            upsert_processed_stock(stock_data)

        # Get medians
        medians = get_sector_medians("TestTechnology", test_date)
        assert medians is not None
        assert float(medians["pe_median"]) == 30.0  # Median of 20, 30, 40
        assert float(medians["roe_median"]) == 0.15  # Median of 0.10, 0.15, 0.20
        assert medians["stock_count"] == 3


