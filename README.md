# DST Skills Project

An AI-powered system for fetching and analyzing data from Statistics Denmark using intelligent agents and DuckDB storage.

## Overview

DST Skills provides a sophisticated, conversational interface for working with Danish statistical data. Using two specialized AI agents, you can discover, download, and analyze data from Statistics Denmark (DST) without wrestling with API documentation or writing complex queries.

### Key Features

- **🤖 Intelligent Agents**: Natural language interaction with data
- **📊 Complete Workflow**: From data discovery to analysis
- **💾 Local Storage**: Fast DuckDB database for offline analysis
- **🔄 Freshness Tracking**: Automatic data age monitoring
- **📈 SQL Analytics**: Powerful querying with simple or complex SQL
- **🎯 7 Specialized Skills**: Modular, focused capabilities
- **📝 Comprehensive Logging**: Full audit trail for debugging

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python scripts/db/init_db.py

# 3. Start using agents!
# Ask: "Fetch population data from DST"
# Or: "Analyze employment trends"
```

**→ See [Getting Started Guide](docs/getting-started.md) for detailed setup**

## Architecture

The system is built with a two-agent architecture:

### 1. dst-fetch-agent
**Purpose**: Data Acquisition

Discovers and downloads data from the DST API. Activates on keywords like: "fetch", "download", "retrieve", "get data"

**Capabilities**:
- Browse DST subjects and topics
- Search for relevant tables
- Fetch detailed table metadata
- Download and store data in DuckDB
- Verify successful storage

**Skills**: dst-subjects, dst-tables, dst-tableinfo, dst-data

### 2. dst-analyze-agent
**Purpose**: Data Analysis

Queries and analyzes stored data. Activates on keywords like: "analyze", "query", "show", "compare"

**Capabilities**:
- Check data availability and freshness
- Execute SQL queries
- Perform statistical analysis
- Join multiple tables
- Present insights clearly

**Skills**: dst-list-tables, dst-check-freshness, dst-query

### Technology Stack

- **Python 3.8+**: Core programming language
- **DuckDB**: Embedded analytics database
- **DST API**: Statistics Denmark REST API
- **Claude Code**: AI-powered development and agent framework

## Directory Structure

```
dst_skills/
├── .claude/                    # Claude Code configuration
│   ├── agents/                 # Agent definitions
│   ├── skills/                 # Custom skills
│   └── commands/               # Slash commands
├── scripts/                    # Core functionality
│   ├── api/                    # API client and configuration
│   │   ├── client.py          # DST API client
│   │   └── config.py          # API configuration
│   ├── db/                     # Database utilities
│   │   ├── init_db.py         # Database initialization
│   │   └── db_utils.py        # Database helper functions
│   └── utils.py               # Logging and utilities
├── data/                       # Database storage
│   └── dst_data.duckdb        # DuckDB database file
├── tests/                      # Test files
├── logs/                       # Application logs
│   └── dst_system.log         # Main log file
├── docs/                       # Documentation
│   └── database-schema.md     # Database schema documentation
├── .env                        # Environment configuration (local)
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Internet connection for API access

### 1. Clone or Navigate to Project

```bash
cd /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment

Copy the example environment file and adjust if needed:

```bash
cp .env.example .env
```

Default configuration:
- `DST_API_BASE_URL`: https://api.statbank.dk/v1
- `DUCKDB_PATH`: ./data/dst_data.duckdb
- `LOG_LEVEL`: INFO

### 6. Initialize Database

```bash
python scripts/db/init_db.py
```

You should see confirmation that the database was initialized successfully.

## Usage

### Database Utilities

Test database operations:

```bash
python scripts/db/db_utils.py
```

### API Client

Test API connectivity:

```bash
python scripts/api/client.py
```

### Working with the Database

```python
from scripts.db import db_utils

# Connect to database
conn = db_utils.get_connection()

# Get metadata for a table
metadata = db_utils.get_metadata(conn, 'FOLK1A')

# List all tables
tables = db_utils.list_all_tables(conn)

# Close connection
db_utils.close_connection(conn)
```

### Using the API Client

```python
from scripts.api.client import DSTAPIClient

# Create client
with DSTAPIClient() as client:
    # Get subjects
    subjects = client.get_subjects()

    # Get tables for a subject
    tables = client.get_tables(subjects='1')

    # Get table information
    table_info = client.get_table_info('FOLK1A')
```

## Development

### Running Tests

Each module includes built-in tests. Run them individually:

```bash
# Test database utilities
python scripts/db/db_utils.py

# Test API configuration
python scripts/api/config.py

# Test API client
python scripts/api/client.py

# Test logging utilities
python scripts/utils.py
```

### Logging

Logs are written to both console and file:
- **Console**: Simple format for quick viewing
- **File**: `logs/dst_system.log` with detailed timestamps

View logs:
```bash
tail -f logs/dst_system.log
```

### Environment Variables

- `DST_API_BASE_URL`: Base URL for DST API
- `DUCKDB_PATH`: Path to DuckDB database file
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Documentation

- [Database Schema](docs/database-schema.md) - Detailed database structure and query examples

## Design Principles

This project follows:

- **KISS (Keep It Simple)**: Minimal complexity, clear code
- **DRY (Don't Repeat Yourself)**: Reusable utility modules
- **YAGNI (You Aren't Gonna Need It)**: Only implement what's needed

## Usage Examples

### Example 1: Discover and Fetch Data
```
User: "Get me population data from DST"

→ Fetcher Agent activates
→ Browses DST subjects
→ Finds population tables
→ Downloads FOLK1A table
→ Confirms: "Stored 45,231 records in dst_folk1a"
```

### Example 2: Analyze Data
```
User: "What's the population of Denmark in 2024?"

→ Analyst Agent activates
→ Checks for population data
→ Verifies data freshness
→ Runs SQL query
→ Reports: "5,932,654 (data from 5 days ago)"
```

### Example 3: Complex Analysis
```
User: "Compare employment rates between regions over last 5 years"

→ Analyst Agent activates
→ Constructs time series query with regional grouping
→ Executes analysis
→ Presents trends with insights
```

## Documentation

Comprehensive documentation available in the `docs/` directory:

- **[Getting Started](docs/getting-started.md)** - Setup and first steps
- **[Quick Reference](docs/quick-reference.md)** - One-page cheat sheet
- **[Workflows](docs/workflows.md)** - Practical examples and patterns
- **[FAQ](docs/faq.md)** - Frequently asked questions
- **[Database Schema](docs/database-schema.md)** - Database structure reference

## Project Status

**✅ Phase 1: Infrastructure** - Complete
- Project structure, database, API client, utilities

**✅ Phase 2: Component Development** - Complete
- 9 Python scripts (API + database operations)
- 7 agent skills (modular capabilities)

**✅ Phase 3: Agent Configuration** - Complete
- dst-fetch-agent (data acquisition)
- dst-analyze-agent (data analysis)

**✅ Phase 4: Integration & Documentation** - Complete
- Comprehensive user documentation
- Usage examples and workflows
- FAQ and troubleshooting guides

## API Reference

### DST API

This project uses the Statistics Denmark (DST) API v1:
- Base URL: https://api.statbank.dk/v1
- Documentation: https://www.dst.dk/en/Statistik/brug-statistikken/muligheder-i-statistikbanken/api

### Available Endpoints

- `/subjects` - List of statistical subjects
- `/tables` - List of tables (optionally filtered by subject)
- `/tableinfo` - Detailed information about a specific table
- `/data` - Retrieve data from a table

## Troubleshooting

### Virtual Environment Issues

If venv activation fails, ensure Python 3.8+ is installed:
```bash
python3 --version
```

### Database Connection Issues

Verify database file exists:
```bash
ls -lh data/dst_data.duckdb
```

Reinitialize if needed:
```bash
python scripts/db/init_db.py
```

### API Connection Issues

Test API connectivity:
```bash
curl https://api.statbank.dk/v1/subjects
```

Check environment variables:
```bash
cat .env
```

## Contributing

This is a research project. For modifications:

1. Follow existing code style
2. Add tests for new functionality
3. Update documentation
4. Ensure all tests pass

## License

This project is for research and educational purposes.

## Acknowledgments

- Statistics Denmark (DST) for providing the API
- Claude Code for the agent framework
- DuckDB team for the excellent embedded database

## Contact

For questions or issues, please refer to project documentation or create an issue.
