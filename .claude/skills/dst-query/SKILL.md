---
name: DST Query
description: Execute SQL queries on Danmarks Statistik data stored in DuckDB. Use when user needs specific data analysis, filtering, aggregation, or joins. Also includes table summary functionality.
---

# DST Query Skill

## Purpose

Execute SQL queries to analyze DST data stored in DuckDB. This is the core skill for data analysis - enabling filtering, aggregation, joins, and extracting insights from stored statistical data.

## When to Use

- User asks analytical questions about the data
- Need to filter or aggregate data
- Joining multiple DST tables
- Extracting specific insights or trends
- Computing custom statistics
- Exploring table structure and contents (use table summary)

## Table Summary

### Purpose
Get a quick overview of table structure and statistics before detailed querying.

### Usage
```bash
python /home/user/dst-skills/scripts/db/table_summary.py --table-id <TABLE_ID>
```

### When to Use
- Before writing complex queries
- Understanding table structure
- Checking available columns
- Seeing sample data
- Getting quick statistics

### Output Includes
- Record count
- Column names and types
- Sample rows (first 5)
- Statistics for numeric columns (min, max, avg, median)
- Distinct value counts
- NULL counts
- Top values for categorical columns

## Running SQL Queries

### Basic Usage

Execute a SQL query:
```bash
python /home/user/dst-skills/scripts/db/query_data.py --sql "<QUERY>"
```

### Output Formats

**Table format** (default - console-friendly):
```bash
--format table
```

**JSON format** (for programmatic use):
```bash
--format json
```

**CSV format** (for exports):
```bash
--format csv
```

### Save to File

Save query results:
```bash
--output <file>
```

### Safety Limit

Add automatic LIMIT:
```bash
--limit 100
```

## Table Naming Convention

All DST tables in DuckDB follow this pattern:
- Format: `dst_{table_id}` (lowercase)
- Example: FOLK1A → `dst_folk1a`
- Example: AUP01 → `dst_aup01`

**Important:** Always use lowercase in queries.

## Common Query Patterns

### 1. Explore Data
```sql
SELECT * FROM dst_folk1a LIMIT 10
```

### 2. Count Records
```sql
SELECT COUNT(*) FROM dst_folk1a
```

### 3. Aggregation
```sql
SELECT region, SUM(population) as total_pop
FROM dst_folk1a
GROUP BY region
ORDER BY total_pop DESC
```

### 4. Time Series
```sql
SELECT year, value
FROM dst_folk1a
WHERE region = '000'
ORDER BY year
```

### 5. Filtering
```sql
SELECT *
FROM dst_folk1a
WHERE year >= 2020 AND region IN ('000', '101')
```

### 6. Multiple Aggregations
```sql
SELECT
  region,
  COUNT(*) as record_count,
  AVG(value) as avg_value,
  MAX(value) as max_value
FROM dst_folk1a
GROUP BY region
```

### 7. Join Tables
```sql
SELECT
  a.region,
  a.population,
  b.employment
FROM dst_folk1a a
JOIN dst_aup01 b ON a.region = b.region AND a.year = b.year
WHERE a.year = 2024
```

### 8. Percentages
```sql
SELECT
  region,
  value,
  100.0 * value / SUM(value) OVER () as percentage
FROM dst_folk1a
WHERE year = 2024
```

## Best Practices

### Query Development
1. **Start with table summary** to understand structure
2. **Use LIMIT** for exploratory queries
3. **Build incrementally** - test small queries first
4. **Check record counts** before expensive operations

### Performance
- Use WHERE clauses to filter early
- Add indexes if querying repeatedly (advanced)
- Aggregate before joining when possible
- Be mindful of large result sets

### Safety
- Queries are **READ-ONLY** (SELECT only)
- Cannot modify data (no INSERT/UPDATE/DELETE)
- Cannot alter schema (no DROP/CREATE/ALTER)
- Script validates queries before execution

### Data Quality
- Handle NULL values explicitly
- Use COALESCE for NULL handling
- Verify data types before operations
- Check for duplicates if unexpected

## Examples

### Example 1: Get table summary
```bash
python /home/user/dst-skills/scripts/db/table_summary.py --table-id FOLK1A
```

### Example 2: Simple exploration
```bash
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT * FROM dst_folk1a LIMIT 5"
```

### Example 3: Aggregation by year
```bash
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT year, SUM(population) as total FROM dst_folk1a GROUP BY year ORDER BY year"
```

### Example 4: Regional analysis
```bash
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT region, AVG(value) as avg_val FROM dst_folk1a WHERE year >= 2020 GROUP BY region"
```

### Example 5: Export to CSV
```bash
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT * FROM dst_folk1a" --format csv --output results.csv
```

### Example 6: JSON output
```bash
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT * FROM dst_folk1a LIMIT 100" --format json --output data.json
```

### Example 7: With safety limit
```bash
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT * FROM dst_folk1a" --limit 1000
```

## Advanced Queries

### Window Functions
```sql
SELECT
  year,
  value,
  LAG(value) OVER (ORDER BY year) as prev_year_value,
  value - LAG(value) OVER (ORDER BY year) as change
FROM dst_folk1a
WHERE region = '000'
ORDER BY year
```

### Pivoting Data
```sql
SELECT
  region,
  MAX(CASE WHEN year = 2023 THEN value END) as val_2023,
  MAX(CASE WHEN year = 2024 THEN value END) as val_2024
FROM dst_folk1a
GROUP BY region
```

### Percentiles
```sql
SELECT
  PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY value) as p25,
  PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY value) as median,
  PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY value) as p75
FROM dst_folk1a
```

### Complex Filtering
```sql
SELECT *
FROM dst_folk1a
WHERE year BETWEEN 2020 AND 2024
  AND region IN (SELECT DISTINCT region FROM dst_aup01 WHERE employment > 1000)
  AND value IS NOT NULL
ORDER BY value DESC
LIMIT 100
```

## Tips

### Before Querying
- Run table summary to see structure
- Check column names and types
- Review sample data
- Verify table has data

### Query Writing
- Use table aliases for clarity (a, b, etc.)
- Format SQL for readability
- Comment complex queries
- Test with LIMIT first

### Analysis Workflow
1. **Understand:** Get table summary
2. **Explore:** Simple SELECT with LIMIT
3. **Filter:** Add WHERE clauses
4. **Aggregate:** Use GROUP BY
5. **Refine:** Add ORDER BY, calculations
6. **Export:** Save final results

### Performance Tips
- Filter first, aggregate second
- Use specific columns, not SELECT *
- Add LIMIT for large tables
- Consider creating views for repeated queries (advanced)

## Troubleshooting

### "Table not found"
- Verify table exists: use dst-list-tables
- Check table name is lowercase
- Ensure format: dst_{table_id}

### "Column not found"
- Run table summary to see columns
- Check spelling and case
- Verify column exists in that table

### Large Result Sets
- Add LIMIT clause
- Use aggregation to reduce rows
- Export to file instead of console

### Slow Queries
- Check WHERE filters are effective
- Simplify joins
- Reduce columns selected
- Check data size with COUNT first

### Query Syntax Errors
- Verify SQL syntax
- Check quotes and brackets
- Test simple version first
- Review error message carefully

## Common Workflows

### Workflow 1: Explore New Table
```bash
# 1. Get summary
python /home/user/dst-skills/scripts/db/table_summary.py --table-id FOLK1A

# 2. See sample data
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT * FROM dst_folk1a LIMIT 5"

# 3. Check record count
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT COUNT(*) FROM dst_folk1a"

# 4. Explore key dimensions
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT DISTINCT region FROM dst_folk1a"
```

### Workflow 2: Trend Analysis
```bash
# 1. Get summary statistics
python /home/user/dst-skills/scripts/db/table_summary.py --table-id FOLK1A

# 2. Query time series
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT year, SUM(value) as total FROM dst_folk1a GROUP BY year ORDER BY year"

# 3. Calculate growth
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT year, value, value - LAG(value) OVER (ORDER BY year) as growth FROM dst_folk1a WHERE region = '000'"

# 4. Export results
python /home/user/dst-skills/scripts/db/query_data.py --sql "..." --format csv --output analysis.csv
```

### Workflow 3: Compare Regions
```bash
# 1. Get regional breakdown
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT region, COUNT(*) as records, AVG(value) as avg_value FROM dst_folk1a GROUP BY region ORDER BY avg_value DESC"

# 2. Top regions
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT region, SUM(value) as total FROM dst_folk1a WHERE year = 2024 GROUP BY region ORDER BY total DESC LIMIT 10"

# 3. Compare specific regions
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT year, region, value FROM dst_folk1a WHERE region IN ('000', '101', '147') ORDER BY year, region"
```

## SQL Reference

### Useful DuckDB Functions

**Aggregation:**
- COUNT, SUM, AVG, MIN, MAX
- MEDIAN, STDDEV, VARIANCE
- STRING_AGG (concatenate strings)

**String Functions:**
- UPPER, LOWER, TRIM
- SUBSTRING, CONCAT
- LIKE, ILIKE (case-insensitive)

**Date Functions:**
- CURRENT_DATE, CURRENT_TIMESTAMP
- DATE_DIFF, DATE_ADD
- EXTRACT (year, month, day)

**Window Functions:**
- ROW_NUMBER, RANK, DENSE_RANK
- LAG, LEAD
- FIRST_VALUE, LAST_VALUE

**Conditional:**
- CASE WHEN ... THEN ... END
- COALESCE (handle NULLs)
- NULLIF

## Best Practices Summary

1. **Always start with table summary**
2. **Use LIMIT during development**
3. **Build queries incrementally**
4. **Handle NULLs explicitly**
5. **Use clear aliases and formatting**
6. **Test before running on full dataset**
7. **Export results for further analysis**
8. **Document complex queries**
