# Quick Reference - DST Skills

A one-page reference for working with DST Skills.

## Agent Activation

### DST Fetcher Agent
**Activates on**: fetch, download, retrieve, get data from DST

**Examples**:
- "Fetch population data from DST"
- "Download table FOLK1A"
- "Get me employment statistics"

### DST Analyst Agent
**Activates on**: analyze, query, explore, show insights

**Examples**:
- "Analyze population trends"
- "What's the total population?"
- "Compare employment rates by region"

## Essential Commands

### Data Acquisition

```bash
# Browse DST subjects
python scripts/api/get_subjects.py

# Search for tables
python scripts/api/get_tables.py --subject 02
python scripts/api/get_tables.py --search "population"

# Get table info
python scripts/api/get_tableinfo.py --table-id FOLK1A

# Fetch and store (RECOMMENDED)
python scripts/fetch_and_store.py --table-id FOLK1A
python scripts/fetch_and_store.py --table-id FOLK1A --overwrite
```

### Data Analysis

```bash
# List stored tables
python scripts/db/query_metadata.py --list-all

# Check freshness
python scripts/db/query_metadata.py --table-id FOLK1A --check-freshness

# Get table summary
python scripts/db/table_summary.py --table-id FOLK1A

# Run SQL query
python scripts/db/query_data.py --sql "SELECT * FROM dst_folk1a LIMIT 10"
```

## Common SQL Patterns

```sql
-- Explore table
SELECT * FROM dst_folk1a LIMIT 10;

-- Count records
SELECT COUNT(*) FROM dst_folk1a;

-- Aggregate by group
SELECT region, SUM(population) as total
FROM dst_folk1a
GROUP BY region
ORDER BY total DESC;

-- Time series
SELECT year, AVG(value) as avg_val
FROM dst_folk1a
WHERE year >= 2020
GROUP BY year
ORDER BY year;

-- Join tables
SELECT a.region, a.population, b.employment
FROM dst_folk1a a
JOIN dst_aup01 b ON a.region = b.region AND a.year = b.year;
```

## Table Naming Convention

- **DST Table ID**: FOLK1A
- **Database Table**: `dst_folk1a` (lowercase, prefix with `dst_`)
- **Always use lowercase** in SQL queries

## Data Freshness Thresholds

| Update Frequency | Recommended Threshold |
|-----------------|----------------------|
| Daily | 1-2 days |
| Weekly | 7 days |
| Monthly | 30 days |
| Quarterly | 90 days |
| Annually | 365 days |

## File Locations

| Item | Location |
|------|----------|
| Database | `./data/dst_data.duckdb` |
| Logs | `./logs/dst_system.log` |
| Scripts | `./scripts/` |
| Skills | `./.claude/skills/` |
| Agents | `./.claude/agents/` |

## Quick Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| "Table not found" | Check `dst_metadata`, table may not be fetched yet |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Connection error" | Check internet connection, DST API may be down |
| "Table exists" | Use `--overwrite` flag or check if refresh needed |
| Agent doesn't activate | Use clearer trigger words (fetch/analyze) |

## Exit Codes

- **0**: Success
- **1**: Error (check logs)
- **2**: Skipped (when using `--skip-if-fresh`)

## Environment Variables

```bash
DST_API_BASE_URL=https://api.statbank.dk/v1
DUCKDB_PATH=./data/dst_data.duckdb
LOG_LEVEL=INFO
```

## Typical Workflow

1. **Browse** → Find data topic with Fetcher Agent
2. **Fetch** → Download table to DuckDB
3. **Verify** → Check table exists and is fresh
4. **Analyze** → Query with Analyst Agent
5. **Export** → Save results if needed

## Output Formats

Most scripts support:
- `--format table` (console-friendly)
- `--format json` (machine-readable)
- `--format csv` (spreadsheet-ready)
- `--output <file>` (save to file)

## Getting Help

- **Docs**: `docs/` directory
- **Logs**: `logs/dst_system.log`
- **FAQ**: `docs/faq.md`
- **Workflows**: `docs/workflows.md`
- **Troubleshooting**: `docs/troubleshooting.md`

---

**Pro Tip**: Use `--help` with any script to see all options:
```bash
python scripts/fetch_and_store.py --help
```
