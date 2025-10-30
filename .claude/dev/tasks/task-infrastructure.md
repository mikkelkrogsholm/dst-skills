# Task: Infrastructure Setup

## Objective
Set up the foundational project structure, DuckDB database schema, and base utilities for the DST research system.

## Prerequisites
- Python 3.8+ installed
- Access to create directories and files in project root
- Basic understanding of DuckDB and SQL

## Tasks

### Project Structure
- [ ] Create `.claude/` directory with subdirectories:
  - [ ] `.claude/agents/`
  - [ ] `.claude/skills/`
  - [ ] `.claude/commands/`
- [ ] Create `scripts/` directory with subdirectories:
  - [ ] `scripts/api/`
  - [ ] `scripts/db/`
- [ ] Create `data/` directory
- [ ] Create `tests/` directory
- [ ] Create `logs/` directory
- [ ] Verify all directories exist and are accessible

### Python Virtual Environment
- [ ] Create virtual environment: `python3 -m venv venv`
- [ ] Verify venv directory created
- [ ] Activate virtual environment:
  - [ ] macOS/Linux: `source venv/bin/activate`
  - [ ] Windows: `venv\Scripts\activate`
- [ ] Verify activation (should see `(venv)` in prompt)
- [ ] Upgrade pip: `pip install --upgrade pip`
- [ ] Add `venv/` to `.gitignore` if using git

### Python Environment Configuration
- [ ] Create `requirements.txt` with dependencies:
  ```
  duckdb>=1.4.1
  python-dotenv>=1.2.1
  pandas>=2.3.3
  numpy>=2.3.4
  httpx>=0.28.1
  ```
- [ ] Verify file exists with all dependencies listed
- [ ] Test installation: `pip install -r requirements.txt`

### Environment Configuration
- [ ] Create `.env.example` with:
  ```
  DST_API_BASE_URL=https://api.statbank.dk/v1
  DUCKDB_PATH=./data/dst_data.duckdb
  LOG_LEVEL=INFO
  ```
- [ ] Copy `.env.example` to `.env` for local use
- [ ] Verify environment variables load correctly

### Database Initialization Script
- [ ] Create `scripts/db/init_db.py` with:
  - [ ] Function to create database connection
  - [ ] SQL to create `dst_metadata` table with columns:
    - [ ] `table_id` (VARCHAR, PRIMARY KEY)
    - [ ] `table_name` (VARCHAR)
    - [ ] `last_updated` (TIMESTAMP)
    - [ ] `fetch_timestamp` (TIMESTAMP)
    - [ ] `record_count` (INTEGER)
    - [ ] `columns_json` (VARCHAR)
    - [ ] `notes` (VARCHAR)
  - [ ] SQL to create index on `table_id`
  - [ ] Function to verify database integrity
- [ ] Test: Run `python scripts/db/init_db.py`
- [ ] Verify database file created at DUCKDB_PATH
- [ ] Verify `dst_metadata` table exists and is queryable

### Database Utility Module
- [ ] Create `scripts/db/db_utils.py` with functions:
  - [ ] `get_connection()` - Returns DuckDB connection
  - [ ] `close_connection(conn)` - Closes connection safely
  - [ ] `table_exists(conn, table_name)` - Checks if table exists
  - [ ] `get_metadata(conn, table_id)` - Retrieves metadata for a table
  - [ ] `update_metadata(conn, table_id, **kwargs)` - Updates metadata record
- [ ] Test: Import module and verify no errors
- [ ] Test: Call each function with test data

### API Configuration Module
- [ ] Create `scripts/api/config.py` with:
  - [ ] Load environment variables using dotenv
  - [ ] Define `API_BASE_URL` constant
  - [ ] Define `DUCKDB_PATH` constant
  - [ ] Define `API_ENDPOINTS` dict with keys:
    - [ ] subjects
    - [ ] tables
    - [ ] tableinfo
    - [ ] data
  - [ ] `get_api_url(endpoint, params=None)` - Constructs full API URLs
- [ ] Test: Import module and verify constants accessible
- [ ] Test: Call `get_api_url()` and verify URL formation

### Logging Utility
- [ ] Create `scripts/utils.py` with:
  - [ ] Logger configuration using Python logging module
  - [ ] `setup_logger(name, level=None)` - Returns configured logger
  - [ ] Configure output to both console and file (`logs/dst_system.log`)
  - [ ] Create `logs/` directory if it doesn't exist
- [ ] Test: Import logger and write test message
- [ ] Verify log appears in both console and file
- [ ] Verify log file created in `logs/` directory

### API Base Client
- [ ] Create `scripts/api/client.py` with:
  - [ ] `DSTAPIClient` class
  - [ ] `__init__(self, base_url=None)` - Initialize with API URL
  - [ ] `_make_request(self, endpoint, params=None, method='GET')` - Generic request handler
  - [ ] Error handling for HTTP errors, timeouts, invalid JSON
  - [ ] Logging for all requests and responses
  - [ ] Rate limiting consideration
- [ ] Test: Instantiate client
- [ ] Test: Make test request to DST API
- [ ] Verify error handling with invalid endpoint

### Documentation
- [ ] Create `docs/` directory
- [ ] Create `docs/database-schema.md` documenting:
  - [ ] `dst_metadata` table schema with column descriptions
  - [ ] Table naming convention: `dst_{table_id}`
  - [ ] Data freshness strategy (using timestamps)
  - [ ] Example queries for common operations
- [ ] Create `README.md` with:
  - [ ] Project overview
  - [ ] Directory structure explanation
  - [ ] Setup instructions (venv, requirements, .env)
  - [ ] Architecture overview (two agents, DuckDB storage)
  - [ ] Links to other documentation
- [ ] Verify documentation is clear and complete

### Final Verification
- [ ] All directories created and accessible
- [ ] All utility modules import without errors
- [ ] Database initializes successfully
- [ ] Can connect to database and query metadata table
- [ ] Environment configuration loads correctly
- [ ] Logger writes to both console and file
- [ ] API client can make requests
- [ ] Documentation provides clear onboarding path

## Success Criteria
- All directories created
- Python dependencies documented
- DuckDB database initialized with metadata table
- Utility modules created and importable
- Documentation files exist
- Can successfully connect to database and query metadata table

## Notes
- **KISS**: Start with minimal schema, can extend later
- **DRY**: Utility modules will be reused by all scripts
- **YAGNI**: Only create infrastructure needed for core functionality
