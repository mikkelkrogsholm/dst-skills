# Getting Started with DST Skills

Welcome to the DST Skills project! This guide will get you up and running in about 10 minutes.

## What is DST Skills?

DST Skills is an AI-powered system for fetching and analyzing data from Statistics Denmark (Danmarks Statistik). It uses two intelligent agents:

- **DST Fetcher Agent**: Downloads data from the DST API
- **DST Analyst Agent**: Queries and analyzes stored data

All data is stored locally in DuckDB for fast, SQL-based analysis.

## Quick Start

### 1. Install Dependencies

```bash
# Navigate to project
cd /home/user/dst-skills

# Install Python packages
pip install -r requirements.txt
```

Required packages:
- duckdb >= 1.4.1
- httpx >= 0.28.1
- pandas >= 2.3.3
- numpy >= 2.3.4
- python-dotenv >= 1.2.1

### 2. Configure Environment

The `.env` file is already configured with defaults. Verify it exists:

```bash
cat .env
```

Default configuration:
```
DST_API_BASE_URL=https://api.statbank.dk/v1
DUCKDB_PATH=./data/dst_data.duckdb
LOG_LEVEL=INFO
```

### 3. Initialize Database

```bash
python scripts/db/init_db.py
```

Expected output:
```
✓ Database initialized successfully
✓ dst_metadata table created
```

### 4. Verify Setup

Test that everything works:

```bash
# Test database connection
python scripts/db/db_utils.py

# Check available skills
ls .claude/skills/
```

You should see 7 skills: dst-subjects, dst-tables, dst-tableinfo, dst-data, dst-list-tables, dst-check-freshness, dst-query

## First Data Fetch

Let's fetch your first dataset! Since we can't access the DST API in this environment, here's how you would do it when network is available:

### Using the Fetcher Agent

Simply ask in natural language:

```
"Fetch population data from DST"
```

The Fetcher Agent will:
1. Browse DST subjects to find population data
2. Identify relevant tables (e.g., FOLK1A)
3. Get table metadata
4. Fetch and store the data
5. Confirm success with record count

### Manual Script Execution

Or use scripts directly:

```bash
# 1. Browse subjects
python scripts/api/get_subjects.py

# 2. Find tables in a subject
python scripts/api/get_tables.py --subject 02

# 3. Get table info
python scripts/api/get_tableinfo.py --table-id FOLK1A

# 4. Fetch and store data
python scripts/fetch_and_store.py --table-id FOLK1A
```

## First Analysis

Once you have data, analyze it with the Analyst Agent:

```
"What's the population of Denmark?"
```

The Analyst Agent will:
1. Check if population data exists
2. Verify data freshness
3. Construct and run SQL query
4. Present the result

## System Requirements

- **Python**: 3.8 or higher
- **Disk Space**: At least 100 MB (more for large datasets)
- **Internet**: Required for fetching from DST API
- **OS**: Linux, macOS, or Windows

## Directory Structure

```
dst-skills/
├── .claude/
│   ├── agents/          # Agent configurations
│   └── skills/          # Agent skills
├── scripts/
│   ├── api/             # API interaction scripts
│   ├── db/              # Database scripts
│   └── fetch_and_store.py  # Combined workflow
├── data/
│   └── dst_data.duckdb  # Database file
├── logs/
│   └── dst_system.log   # System logs
└── docs/                # Documentation
```

## Next Steps

- **Learn the workflow**: Read `docs/workflows.md`
- **Understand agents**: Read `docs/user-guide.md`
- **Quick reference**: See `docs/quick-reference.md`
- **Got issues?**: Check `docs/troubleshooting.md`
- **Common questions**: See `docs/faq.md`

## Common First-Time Issues

### Python Version

**Problem**: Wrong Python version

**Solution**:
```bash
python3 --version  # Should be 3.8+
```

### Permission Errors

**Problem**: Can't create database

**Solution**:
```bash
# Ensure data directory exists
mkdir -p data

# Check permissions
ls -la data/
```

### Import Errors

**Problem**: Module not found

**Solution**:
```bash
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Getting Help

- **Documentation**: All docs in `docs/` directory
- **Logs**: Check `logs/dst_system.log` for errors
- **FAQ**: `docs/faq.md` for common questions
- **Issues**: Report at project repository

## What's Next?

Now that you're set up:

1. **Explore**: Ask Fetcher Agent to browse DST subjects
2. **Fetch**: Download a dataset you're interested in
3. **Analyze**: Ask Analyst Agent questions about your data
4. **Learn**: Try the workflows in `docs/workflows.md`

Welcome to DST Skills! 🎉
