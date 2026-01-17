# Week 3: Database Schema Design

**Goal:** Update database schema based on Week 2 findings and create helper functions

**Duration:** 14 hours (2 hrs/day × 7 days)

**Status:** IN PROGRESS (~80% complete)

---

## 🎯 Week Objective

By the end of this week, you should:
- Have an updated database schema that supports all scoring methodology fields
- Have working database helper functions (CRUD operations)
- Have proper indexes for common queries
- Be ready to build the ETL pipeline (Week 5-7)

---

## 📋 Detailed Checklist

### 1. Review Current Schema (2 hours) ✅ COMPLETED

- [x] Read current `database/schema.sql`
- [x] Compare against Week 2 findings (scoring_methodology.md, data_sources.md)
- [x] Identify missing fields:
  - `return_on_assets` (ROA) - NEW from financial-expert
  - `dividend_yield` - NEW from financial-expert
  - `return_12m` - NEW (momentum factor)
  - Any other missing fields from yfinance mapping

**Deliverable:** List of schema changes needed

---

### 2. Update Database Schema (3 hours) ✅ COMPLETED

- [x] **Update `processed_stocks` table** with new fields:
  ```sql
  ALTER TABLE processed_stocks ADD COLUMN IF NOT EXISTS return_on_assets NUMERIC;
  ALTER TABLE processed_stocks ADD COLUMN IF NOT EXISTS dividend_yield NUMERIC;
  ALTER TABLE processed_stocks ADD COLUMN IF NOT EXISTS return_12m NUMERIC;
  ALTER TABLE processed_stocks ADD COLUMN IF NOT EXISTS gross_margin NUMERIC;
  ALTER TABLE processed_stocks ADD COLUMN IF NOT EXISTS free_cashflow BIGINT;
  ```

- [x] **Update `stock_scores` table** if needed:
  - Verify all factor scores have columns
  - Add `is_value_trap` boolean column

- [x] **Add indexes** for common queries:
  ```sql
  CREATE INDEX IF NOT EXISTS idx_processed_stocks_ticker ON processed_stocks(ticker);
  CREATE INDEX IF NOT EXISTS idx_processed_stocks_sector ON processed_stocks(sector);
  CREATE INDEX IF NOT EXISTS idx_processed_stocks_date ON processed_stocks(analysis_date);
  CREATE INDEX IF NOT EXISTS idx_stock_scores_rank ON stock_scores(rank);
  CREATE INDEX IF NOT EXISTS idx_stock_scores_total ON stock_scores(total_score DESC);
  ```

- [ ] **Test schema changes** in Docker PostgreSQL ⏳ (REMAINING)

**Deliverable:** Updated `database/schema.sql` with all changes ✅ DONE

---

### 3. Create Database Helper Functions (4 hours) ✅ COMPLETED

- [x] **Create `database/helpers.py`** with:

  ```python
  # Connection management
  def get_db_connection()
  def close_connection(conn)

  # Bronze layer operations
  def insert_raw_stock_data(ticker, data_source, raw_json)
  def get_raw_stock_data(ticker, date)

  # Silver layer operations
  def upsert_processed_stock(stock_data: dict)
  def get_processed_stock(ticker, date)
  def get_all_processed_stocks(date)
  def get_stocks_by_sector(sector, date)

  # Gold layer operations
  def upsert_stock_score(score_data: dict)
  def get_stock_scores(date, limit=25)
  def get_stock_score(ticker, date)

  # Utility functions
  def get_sector_medians(sector, date)
  def get_all_sectors()
  ```

- [ ] **Use SQLAlchemy** or raw psycopg2 (your choice)
- [ ] **Add proper error handling** and logging
- [ ] **Use parameterized queries** (prevent SQL injection)

**Deliverable:** Working `database/helpers.py` with all CRUD operations

---

### 4. Create Database Models (2 hours)

- [ ] **Create `database/models.py`** with Pydantic models:

  ```python
  from pydantic import BaseModel
  from datetime import date
  from typing import Optional

  class ProcessedStock(BaseModel):
      ticker: str
      analysis_date: date
      company_name: str
      sector: str
      # Valuation
      trailing_pe: Optional[float]
      price_to_book: Optional[float]
      price_to_sales: Optional[float]
      dividend_yield: Optional[float]
      # Profitability
      return_on_equity: Optional[float]
      return_on_assets: Optional[float]
      profit_margin: Optional[float]
      operating_margin: Optional[float]
      # Growth
      revenue_growth: Optional[float]
      earnings_growth: Optional[float]
      # Health
      debt_to_equity: Optional[float]
      current_ratio: Optional[float]
      # Market
      current_price: float
      market_cap: int
      # Momentum
      return_6m: Optional[float]
      return_12m: Optional[float]

  class StockScore(BaseModel):
      ticker: str
      analysis_date: date
      valuation_score: float
      profitability_score: float
      growth_score: float
      momentum_score: float
      health_score: float
      total_score: float
      rank: int
      is_value_trap: bool = False
  ```

**Deliverable:** Working `database/models.py` with validation

---

### 5. Write Unit Tests (2 hours)

- [ ] **Create `tests/test_database.py`**:

  ```python
  def test_connection()
  def test_insert_processed_stock()
  def test_get_processed_stock()
  def test_upsert_updates_existing()
  def test_get_sector_medians()
  def test_insert_stock_score()
  def test_get_top_stocks()
  ```

- [ ] **Test with real Docker database**
- [ ] **Clean up test data** after each test

**Deliverable:** Passing test suite for database operations

---

### 6. Documentation (1 hour)

- [ ] **Update `docs/database_schema.md`** with:
  - Complete table definitions
  - Field descriptions
  - Index explanations
  - Example queries

- [ ] **Document helper function usage** in docstrings

**Deliverable:** Updated database documentation

---

## 🤖 Agents to Use This Week

### Primary Agents

1. **data-engineer** (Primary for this week)
   - Schema design review
   - Indexing strategy
   - Query optimization
   - Data type recommendations

2. **project-lead** (Architecture check)
   - Does schema support all planned features?
   - Will this integrate well with ETL pipeline?
   - Any architectural concerns?

3. **code-reviewer** (After writing helper functions)
   - Review database code quality
   - Check for SQL injection vulnerabilities
   - Verify error handling
   - Review test coverage

### How to Use Them

```
# After designing schema updates:
"Use the data-engineer agent to review my schema changes"

# After writing helper functions:
"Use the code-reviewer agent to check database/helpers.py"

# Before moving to Week 4:
"Use the project-lead agent to verify the database layer is ready for ETL"
```

---

## 📊 Expected Outputs

By end of Week 3, you should have:

1. ✅ **Updated `database/schema.sql`**
   - All new fields added
   - Indexes created
   - Tested in Docker

2. ✅ **`database/helpers.py`**
   - CRUD operations for all tables
   - Connection management
   - Error handling

3. ✅ **`database/models.py`**
   - Pydantic models for validation
   - Type hints

4. ✅ **`tests/test_database.py`**
   - Unit tests for all operations
   - Tests passing

5. ✅ **Updated documentation**

---

## 💡 Tips & Tricks

### Avoid These Pitfalls

❌ **Don't skip indexes** - They're critical for query performance
❌ **Don't use string concatenation for SQL** - Use parameterized queries
❌ **Don't forget to close connections** - Use context managers
❌ **Don't skip error handling** - Database operations can fail

### Do These Instead

✅ **Use connection pooling** - Better performance for ETL
✅ **Use upsert patterns** - `INSERT ... ON CONFLICT DO UPDATE`
✅ **Add created_at timestamps** - Track when records were created
✅ **Test with real data** - Use the 5 test stocks from Week 2

---

## 🚧 Blockers & Solutions

### Common Issues

**Issue:** Schema change fails on existing data
- **Solution:** Use `IF NOT EXISTS` for new columns
- **Solution:** Back up data before schema changes

**Issue:** Connection timeouts
- **Solution:** Use connection pooling
- **Solution:** Add retry logic

**Issue:** Slow queries
- **Solution:** Add proper indexes
- **Solution:** Use EXPLAIN ANALYZE to diagnose

---

## ✅ Definition of Done

**This week is DONE when:**

- [ ] Schema updated with all new fields from Week 2
- [ ] Indexes created for common queries
- [ ] Helper functions working for all CRUD operations
- [ ] Pydantic models validating data
- [ ] Unit tests passing
- [ ] Can insert and retrieve the 5 test stocks from Week 2
- [ ] Documentation updated
- [ ] Code reviewed by code-reviewer agent
- [ ] Schema approved by data-engineer agent

**Ready to move to Week 4:** Database testing and edge cases

---

## 📚 Key Files to Create/Update

| File | Action | Description |
|------|--------|-------------|
| `database/schema.sql` | UPDATE | Add new fields and indexes |
| `database/helpers.py` | CREATE | CRUD operations |
| `database/models.py` | CREATE | Pydantic models |
| `tests/test_database.py` | CREATE | Unit tests |
| `docs/database_schema.md` | UPDATE | Documentation |

---

## 🔗 References

- Week 2 outputs:
  - `docs/scoring_methodology.md` - Fields needed for scoring
  - `docs/data_sources.md` - yfinance field mapping
  - `WEEK2_REPORT.md` - ETL architecture design

- Existing files:
  - `database/schema.sql` - Current schema
  - `database/seed.sql` - Factor weights

---

**Next Week:** Week 4 - Database Testing & Edge Cases
**See:** `docs/weeks/week-04-database-testing.md` (when you get there)
