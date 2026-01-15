# Agent Workflow Guide - StockPulse

**Purpose:** This document defines when and how to use the 8 specialized agents throughout the 18-week StockPulse development timeline.

**Last Updated:** January 15, 2026

---

## Overview: The 8 Specialized Agents

| Agent | Expertise | Primary Role |
|-------|-----------|--------------|
| **project-lead** | Architecture & integration | Ensures components work together cohesively |
| **security-specialist** | Security & vulnerabilities | Prevents security issues before deployment |
| **code-reviewer** | Code quality & testing | Maintains high code standards and test coverage |
| **data-engineer** | ETL, database, data exploration | Designs and optimizes the data layer |
| **ml-specialist** | ML models & features | Prevents look-ahead bias, validates ML implementation |
| **backend-specialist** | API, DevOps, performance | Optimizes backend, API, and infrastructure |
| **frontend-specialist** | UI/UX, visualizations | Creates user-friendly, performant interfaces |
| **financial-expert** | Investment factors & methodology | Ensures financial soundness and defensibility |

---

## Phase 1: Foundation & MVP (Weeks 1-14)

### Week 1: Setup & Environment
**Goal:** Development environment ready

**Agents:** None needed yet (setup week)

---

### Week 2: Data Exploration ✅
**Goal:** Understand data sources and available metrics

**Agents to Use:**
1. **data-engineer** - Primary agent for this week
   - Test yfinance and Alpha Vantage APIs
   - Explore available fields and data structure
   - Identify data quality issues
   - Recommend data refresh frequency

2. **financial-expert** - Critical for metric selection
   - Which financial metrics actually matter for alpha generation?
   - Validate that P/E, ROE, dividend yield, etc. are sound choices
   - Recommend factor weighting strategy
   - Flag any metrics that are financially questionable

**Why Both:** `data-engineer` tells you WHAT data is available, `financial-expert` tells you what MATTERS financially.

**Expected Output:**
- List of viable financial metrics
- Data quality assessment
- Recommended scoring factors (validated by finance expert)
- Jupyter notebook with working calculations

---

### Week 3: Database Schema Design ✅
**Goal:** Design warehouse schema

**Agents to Use:**
1. **data-engineer** - Lead on schema design
   - Design bronze/silver/gold layer tables
   - Recommend indexing strategy
   - Validate data types and constraints
   - Check partitioning needs for large tables

2. **project-lead** - Architecture review
   - Does schema support all planned features?
   - Are relationships between tables clean?
   - Will this scale to 500 stocks?
   - Integration with ETL and API layers

**Expected Output:**
- `schema.sql` with all tables
- ERD diagram
- Index strategy documented
- Architectural approval from project-lead

---

### Week 4: Database Testing ✅
**Goal:** Programmatically interact with database

**Agents to Use:**
1. **data-engineer** - Database operations
   - Validate SQLAlchemy setup
   - Review connection pooling configuration
   - Check query performance
   - Verify data validation logic

2. **code-reviewer** - Code quality
   - Review helper functions
   - Check error handling
   - Validate test coverage
   - Ensure code is maintainable

**Expected Output:**
- Working database helper functions
- Unit tests passing
- Clean, documented code

---

### Week 5: Data Ingestion (Bronze Layer) ✅
**Goal:** Fetch 100+ stocks and save to database

**Agents to Use:**
1. **data-engineer** - ETL pipeline design
   - Review ingestion logic
   - Validate rate limit handling
   - Check error recovery and retry logic
   - Ensure data quality tracking
   - Verify idempotency

2. **code-reviewer** - Error handling review
   - Review exception handling
   - Check logging comprehensiveness
   - Validate retry mechanisms
   - Test edge cases

**Expected Output:**
- `ingest.py` fetching 100+ stocks reliably
- Comprehensive error handling
- Bronze layer data in database
- ETL run tracking

---

### Week 6: Data Transformation (Silver Layer)
**Goal:** Clean and normalize data

**Agents to Use:**
1. **data-engineer** - Transformation logic
   - Review data cleaning logic
   - Validate null handling strategy
   - Check data type conversions
   - Verify data quality metrics
   - Ensure referential integrity

2. **code-reviewer** (optional) - If transformation is complex
   - Review transformation functions
   - Check for potential bugs
   - Validate test coverage

**Expected Output:**
- `transform.py` producing clean data
- Silver layer populated
- Data quality metrics tracked

---

### Week 7: Scoring & Ranking (Gold Layer)
**Goal:** Complete ETL pipeline with scoring

**Agents to Use:**
1. **financial-expert** - Critical validation this week!
   - Review scoring methodology implementation
   - Validate factor calculations (P/E, ROE, etc.)
   - Check factor weights are defensible
   - Ensure sector-aware scoring if applicable
   - Verify methodology is interview-ready

2. **data-engineer** - Pipeline review
   - Review scoring logic implementation
   - Check performance (500 stocks processable?)
   - Validate database writes
   - Ensure pipeline is production-ready

3. **project-lead** - Phase checkpoint
   - ETL phase complete check
   - Ready to move to API development?
   - Any architectural concerns?
   - Integration points validated?

**Expected Output:**
- Complete ETL pipeline working
- 500 stocks scored and ranked
- Methodology validated by financial expert
- Phase 1 (ETL) approved by project-lead

---

### Week 8: FastAPI Backend Foundation
**Goal:** FastAPI setup and running

**Agents to Use:**
1. **backend-specialist** - API design
   - Review FastAPI project structure
   - Validate endpoint design patterns
   - Check Pydantic models
   - Review database integration approach

2. **security-specialist** - Initial security review
   - Check for hardcoded secrets
   - Validate environment variable usage
   - Review CORS configuration (if applicable)
   - Basic security best practices

**Expected Output:**
- FastAPI running on localhost:8000
- `/docs` endpoint accessible
- Basic security practices in place

---

### Week 9: API Endpoints & Database Integration
**Goal:** All API endpoints working

**Agents to Use:**
1. **backend-specialist** - Query optimization
   - Review all API endpoints
   - Check for N+1 query problems
   - Validate connection pooling
   - Optimize slow queries
   - Review response time

2. **code-reviewer** - API testing
   - Review endpoint logic
   - Check input validation
   - Validate error handling
   - Verify test coverage

3. **security-specialist** - Endpoint security
   - SQL injection vulnerabilities?
   - Input validation adequate?
   - Rate limiting needed?
   - Authentication/authorization if applicable

**Expected Output:**
- All endpoints working and tested
- No security vulnerabilities
- Optimized query performance

---

### Week 10: Frontend Foundation
**Goal:** Next.js/Streamlit with homepage working

**Agents to Use:**
1. **frontend-specialist** - UI design & performance
   - Review component structure
   - Check data fetching strategy
   - Validate loading states
   - Review performance (bundle size, render speed)

2. **code-reviewer** - Component review
   - Check component quality
   - Validate prop types
   - Review code organization

**Expected Output:**
- Working homepage showing live stock rankings
- Fast load times
- Clean component code

---

### Week 11: Dashboard Polish
**Goal:** All pages polished and responsive

**Agents to Use:**
1. **frontend-specialist** - Responsiveness & UX
   - Review mobile responsiveness
   - Check tablet layouts
   - Validate UX patterns
   - Review accessibility
   - Check visualization clarity

2. **code-reviewer** - Frontend code quality
   - Review all components
   - Check for code duplication
   - Validate naming conventions
   - Ensure maintainability

**Expected Output:**
- Fully responsive dashboard
- Great user experience
- High-quality frontend code

---

### Week 12: Integration Testing & Bug Fixes
**Goal:** Bug-free application ready for deployment

**Agents to Use:**
1. **code-reviewer** - Final code review
   - Review entire codebase
   - Identify potential bugs
   - Check test coverage
   - Validate error handling

2. **security-specialist** - Pre-deployment audit
   - Full security audit
   - Check for OWASP Top 10 vulnerabilities
   - Validate secrets management
   - Review API security
   - Check dependencies for known vulnerabilities

3. **project-lead** - Integration review
   - Do all components integrate properly?
   - Any architectural concerns before deployment?
   - Ready for production?

**Expected Output:**
- Zero known bugs
- Security audit passed
- Integration validated
- Ready to deploy

---

### Week 13: Deployment
**Goal:** Live site on internet

**Agents to Use:**
1. **backend-specialist** - Deployment & DevOps
   - Review deployment configuration
   - Check environment variables
   - Validate Docker setup (if applicable)
   - Review hosting configuration (AWS/Railway/Vercel)
   - Monitor deployment process

2. **security-specialist** - Production security check
   - Debug mode OFF?
   - Secrets not exposed?
   - HTTPS configured?
   - Security headers set?
   - Production-ready configuration?

**Expected Output:**
- Live site at production URL
- Secure production configuration
- Monitoring in place

---

### Week 14: Documentation & Portfolio
**Goal:** Polished portfolio piece

**Agents to Use:**
1. **project-lead** - Final MVP review
   - Is everything working cohesively?
   - Any remaining issues?
   - Ready to show employers?
   - Documentation complete?

2. **financial-expert** - Methodology documentation validation
   - Review scoring methodology documentation
   - Validate that explanations are clear
   - Ensure methodology is defensible in interviews
   - Check that financial reasoning is sound

**Expected Output:**
- Comprehensive README
- Clear methodology documentation
- Demo video/screenshots
- Portfolio-ready project

---

## Phase 2: ML & Data Lake (Weeks 15-18)

### Week 15: Data Lake Setup
**Goal:** S3/R2 with 3 years of historical data

**Agents to Use:**
1. **data-engineer** - Data lake architecture
   - Review bronze/silver/gold data lake design
   - Validate partitioning strategy
   - Check Parquet format implementation
   - Verify historical data completeness

2. **backend-specialist** - S3/R2 setup
   - Review cloud storage configuration
   - Check access credentials management
   - Validate cost optimization
   - Review backup strategy

**Expected Output:**
- Data lake with 3 years of data
- Cost-effective storage configuration
- Clean data lake architecture

---

### Week 16: ML Feature Engineering
**Goal:** Training dataset with 18,000 examples, 40 features

**Agents to Use:**
1. **ml-specialist** - Feature engineering (PRIMARY)
   - **Critical:** Check for look-ahead bias
   - Validate time-series data handling
   - Review feature calculations
   - Check train/val/test split strategy
   - Ensure point-in-time consistency

2. **financial-expert** - Feature financial validation (CRITICAL)
   - Are features financially meaningful?
   - Do feature definitions make sense?
   - Are we using appropriate financial metrics?
   - Factor selection reasonable?
   - Can features be explained in interviews?

3. **data-engineer** - Data quality
   - Validate historical data quality
   - Check for missing data handling
   - Verify data lineage
   - Ensure reproducibility

**Why All Three:** This is the most critical week for preventing look-ahead bias and ensuring features are both technically correct AND financially sound.

**Expected Output:**
- 18,000 training examples
- 40 features (validated technically + financially)
- NO look-ahead bias
- Defensible feature selection

---

### Week 17: Model Training & Evaluation
**Goal:** Trained XGBoost model with Sharpe > 1.0

**Agents to Use:**
1. **ml-specialist** - Model training & validation (PRIMARY)
   - Review XGBoost hyperparameters
   - Validate time-series cross-validation
   - Check for overfitting
   - Review evaluation metrics
   - Verify backtesting methodology

2. **financial-expert** - Backtest interpretation
   - Interpret Sharpe ratio in context
   - Validate benchmark comparison (vs S&P 500)
   - Check drawdown analysis
   - Ensure backtesting is realistic (costs, slippage)
   - Validate that results make financial sense

3. **code-reviewer** - ML code review
   - Review training code quality
   - Check model saving/versioning
   - Validate experiment tracking
   - Ensure reproducibility

**Expected Output:**
- Trained XGBoost model
- Sharpe > 1.0 (hopefully!)
- Financially sound backtesting
- Clean ML code

---

### Week 18: ML Integration & SHAP Explanations
**Goal:** Live app with ML predictions and SHAP

**Agents to Use:**
1. **ml-specialist** - SHAP implementation
   - Review SHAP calculation code
   - Validate SHAP value storage
   - Check inference pipeline
   - Ensure ML integration is correct

2. **financial-expert** - SHAP interpretation (CRITICAL)
   - Do SHAP values make financial sense?
   - How to explain SHAP results in interviews?
   - Are feature contributions reasonable?
   - Flag any financially questionable results
   - Validate methodology is defensible

3. **frontend-specialist** - SHAP visualization
   - Review SHAP visualization components
   - Check clarity of explanations
   - Validate user experience
   - Ensure mobile responsiveness

4. **project-lead** - Final review
   - Complete system integration check
   - All components working together?
   - ML + Rule-based + UI integrated?
   - Ready for final deployment?
   - Project complete and portfolio-ready?

**Expected Output:**
- Live app with ML predictions
- Clear SHAP explanations
- Financially sound and defensible
- Complete system working end-to-end

---

## Agent Collaboration Patterns

### Pattern 1: Technical + Financial Validation
**When:** ML feature engineering, scoring methodology, SHAP interpretation

**How it works:**
1. Technical agent (ml-specialist, data-engineer) validates implementation
2. financial-expert validates financial soundness
3. Both must approve before proceeding

**Example (Week 16):**
```
Step 1: ml-specialist checks for look-ahead bias → PASS
Step 2: financial-expert validates P/E feature makes sense → PASS
Step 3: Proceed with feature
```

### Pattern 2: Code Quality Gates
**When:** After implementing any significant code

**How it works:**
1. Implement feature
2. code-reviewer checks quality, bugs, tests
3. security-specialist checks security (if applicable)
4. Fix issues before proceeding

**Example (Week 9):**
```
Step 1: Implement API endpoints
Step 2: code-reviewer finds N+1 query issue
Step 3: Fix query issue
Step 4: security-specialist checks for SQL injection
Step 5: All clear → proceed
```

### Pattern 3: Phase Completion Review
**When:** End of major phases (Week 7, 12, 14, 18)

**How it works:**
1. Domain agents validate their areas
2. project-lead does integration review
3. Issues identified and addressed
4. Approval to move to next phase

**Example (Week 7 - ETL Complete):**
```
Step 1: data-engineer validates pipeline quality
Step 2: financial-expert validates scoring methodology
Step 3: project-lead checks architecture integration
Step 4: All approve → move to API development
```

---

## Quick Reference: Agent Checklist by Week

| Week | Primary Agents | Purpose |
|------|---------------|---------|
| W1 | None | Setup |
| W2 | data-engineer, financial-expert | Metric selection |
| W3 | data-engineer, project-lead | Schema design |
| W4 | data-engineer, code-reviewer | Database testing |
| W5 | data-engineer, code-reviewer | Ingestion |
| W6 | data-engineer | Transformation |
| W7 | financial-expert, data-engineer, project-lead | Scoring validation |
| W8 | backend-specialist, security-specialist | API foundation |
| W9 | backend-specialist, code-reviewer, security-specialist | API endpoints |
| W10 | frontend-specialist, code-reviewer | Frontend start |
| W11 | frontend-specialist, code-reviewer | Frontend polish |
| W12 | code-reviewer, security-specialist, project-lead | Pre-deployment |
| W13 | backend-specialist, security-specialist | Deployment |
| W14 | project-lead, financial-expert | Documentation |
| W15 | data-engineer, backend-specialist | Data lake |
| W16 | ml-specialist, financial-expert, data-engineer | Feature engineering |
| W17 | ml-specialist, financial-expert, code-reviewer | Model training |
| W18 | ml-specialist, financial-expert, frontend-specialist, project-lead | Final integration |

---

## How to Invoke Agents

### Method 1: Explicit Request to Claude
```
Use the data-engineer agent to review my ingest.py for data quality issues
```

### Method 2: Mention in Context
```
I've finished the ETL pipeline. Let's have it reviewed for:
- Data quality (data-engineer)
- Financial soundness (financial-expert)
- Architecture integration (project-lead)
```

### Method 3: Request Parallel Reviews
```
Run these agents in parallel:
1. code-reviewer on backend/main.py
2. security-specialist on API endpoints
3. data-engineer on ETL pipeline

Then summarize findings
```

---

## Special Notes

### financial-expert is CRITICAL at these moments:
- **Week 2:** Metric selection (prevents building on bad foundations)
- **Week 7:** Scoring validation (ensures defensibility)
- **Week 16:** Feature validation (prevents financially nonsensical ML features)
- **Week 17:** Backtest interpretation (ensures realistic expectations)
- **Week 18:** SHAP interpretation (makes explanations interview-ready)

### security-specialist is CRITICAL before:
- **Week 9:** API endpoints exposed
- **Week 12:** Pre-deployment audit
- **Week 13:** Production deployment

### project-lead is CRITICAL at:
- **Week 7:** ETL phase complete
- **Week 12:** MVP integration check
- **Week 14:** MVP final review
- **Week 18:** Complete system review

---

## Anti-Patterns (What NOT to Do)

❌ **Don't skip financial-expert on methodology decisions**
- Bad: Implement scoring without validation
- Good: Validate with financial-expert before implementing

❌ **Don't skip security-specialist before deployment**
- Bad: Deploy with untested security
- Good: Full security audit in Week 12

❌ **Don't use agents too early**
- Bad: Week 1 project-lead review of setup scripts
- Good: Wait for meaningful architecture to review

❌ **Don't use wrong agent for the domain**
- Bad: Ask frontend-specialist about database indexes
- Good: Use data-engineer for database topics

❌ **Don't skip project-lead at phase boundaries**
- Bad: Move from ETL to API without integration check
- Good: project-lead validates integration before proceeding

---

## Success Criteria

**You're using agents correctly if:**
- ✅ financial-expert validates all methodology decisions
- ✅ security-specialist audits before deployment
- ✅ code-reviewer catches bugs before they reach production
- ✅ project-lead ensures architectural coherence
- ✅ Domain experts (data-engineer, ml-specialist, backend-specialist, frontend-specialist) guide their respective areas
- ✅ Agents prevent mistakes BEFORE significant time is invested

**Remember:** Agents are your specialized team. Use them to prevent problems, not just fix them after the fact.

---

**Last Updated:** January 15, 2026
**Status:** Week 2 (Data Exploration)
**Next Agent Use:** data-engineer + financial-expert for metric selection
