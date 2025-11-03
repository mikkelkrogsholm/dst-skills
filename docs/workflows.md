# DST Skills Workflows

Practical workflows for common tasks with DST Skills.

## Table of Contents

1. [Exploring New Topics](#workflow-1-exploring-new-topics)
2. [Fetching Specific Data](#workflow-2-fetching-specific-data)
3. [Basic Analysis](#workflow-3-basic-analysis)
4. [Time Series Analysis](#workflow-4-time-series-analysis)
5. [Regional Comparisons](#workflow-5-regional-comparisons)
6. [Data Refresh](#workflow-6-data-refresh)
7. [Joining Multiple Tables](#workflow-7-joining-multiple-tables)
8. [Exporting Results](#workflow-8-exporting-results)

---

## Workflow 1: Exploring New Topics

**Goal**: Discover what data is available about a topic

**Example**: "I want to explore housing statistics"

### Steps

1. **Ask Fetcher Agent to browse subjects**:
   ```
   "Show me what housing data is available from DST"
   ```

2. **Fetcher browses subjects**:
   ```bash
   python scripts/api/get_subjects.py
   ```
   Finds subject 09: Housing and construction

3. **Search for housing tables**:
   ```bash
   python scripts/api/get_tables.py --subject 09
   # Or by keyword:
   python scripts/api/get_tables.py --search "bolig"
   ```

4. **Review interesting tables**:
   - Note table IDs (e.g., BOLIG1, BOLIG2)
   - Read descriptions to understand content

5. **Get detailed info for specific table**:
   ```bash
   python scripts/api/get_tableinfo.py --table-id BOLIG1
   ```

### Expected Results
- List of available housing-related subjects
- Multiple tables with descriptions
- Detailed metadata for chosen table
- Understanding of what variables are available

### Tips
- Start broad (subjects), then narrow (tables)
- Read table descriptions carefully
- Check table info before fetching large datasets
- Save interesting table IDs for later

---

## Workflow 2: Fetching Specific Data

**Goal**: Download a known table

**Example**: "Get the FOLK1A table"

### Steps

1. **Get table information first**:
   ```bash
   python scripts/api/get_tableinfo.py --table-id FOLK1A
   ```

2. **Review structure**:
   - Check number of records
   - Note available variables
   - Decide if filtering is needed

3. **Fetch and store (simple)**:
   ```bash
   python scripts/fetch_and_store.py --table-id FOLK1A
   ```

4. **Or with filters (advanced)**:
   ```bash
   # Only fetch data for whole country
   python scripts/fetch_and_store.py --table-id FOLK1A --filters '{"OMRÅDE":["000"]}'
   ```

5. **Verify storage**:
   ```bash
   python scripts/db/query_metadata.py --table-id FOLK1A
   ```

### Expected Results
- Data downloaded from DST
- Stored in `dst_folk1a` table
- Metadata updated with record count and timestamp
- Confirmation message with statistics

### Tips
- Always check tableinfo first
- Use filters for large tables to save space
- Verify record count matches expectations
- Note the table name format: `dst_{id}` lowercase

---

## Workflow 3: Basic Analysis

**Goal**: Answer simple question

**Example**: "What's the total population of Denmark in 2024?"

### Steps

1. **Ensure data exists**:
   ```bash
   python scripts/db/query_metadata.py --list-all
   ```

2. **If missing, fetch first** (see Workflow 2)

3. **Get table summary**:
   ```bash
   python scripts/db/table_summary.py --table-id FOLK1A
   ```

4. **Check freshness**:
   ```bash
   python scripts/db/query_metadata.py --table-id FOLK1A --check-freshness
   ```

5. **Run query**:
   ```bash
   python scripts/db/query_data.py --sql "
   SELECT SUM(population) as total_population
   FROM dst_folk1a
   WHERE year = 2024 AND region = '000'
   "
   ```

### Expected Results
- Single number: total population
- Clear, formatted output
- Data age disclaimer if old

### Tips
- Use table summary to understand structure first
- Check freshness before important analyses
- Use appropriate aggregation (SUM, AVG, COUNT)
- Filter to relevant rows (WHERE clause)

---

## Workflow 4: Time Series Analysis

**Goal**: Analyze trends over time

**Example**: "Show employment rate trends from 2020-2024"

### Steps

1. **Get employment data** (if not already fetched)

2. **Explore data**:
   ```bash
   python scripts/db/table_summary.py --table-id AUP01
   ```

3. **Query time series**:
   ```bash
   python scripts/db/query_data.py --sql "
   SELECT
     year,
     AVG(employment_rate) as avg_rate,
     COUNT(*) as data_points
   FROM dst_aup01
   WHERE year BETWEEN 2020 AND 2024
   GROUP BY year
   ORDER BY year
   "
   ```

4. **Calculate changes**:
   ```bash
   python scripts/db/query_data.py --sql "
   SELECT
     year,
     employment_rate,
     LAG(employment_rate) OVER (ORDER BY year) as prev_year,
     employment_rate - LAG(employment_rate) OVER (ORDER BY year) as change
   FROM dst_aup01
   WHERE year BETWEEN 2020 AND 2024 AND region = '000'
   ORDER BY year
   "
   ```

5. **Export for visualization**:
   ```bash
   python scripts/db/query_data.py \
     --sql "SELECT year, employment_rate FROM dst_aup01 WHERE year >= 2020" \
     --format csv \
     --output employment_trends.csv
   ```

### Expected Results
- Yearly employment rates
- Year-over-year changes
- CSV file ready for charts

### Tips
- Use GROUP BY for aggregation by time
- ORDER BY year for chronological view
- Use window functions (LAG, LEAD) for changes
- Export to CSV for plotting in Excel/Python

---

## Workflow 5: Regional Comparisons

**Goal**: Compare statistics across regions

**Example**: "Compare population across Danish regions"

### Steps

1. **Get population data with regional breakdown**

2. **Query by region**:
   ```bash
   python scripts/db/query_data.py --sql "
   SELECT
     region,
     SUM(population) as total_pop,
     ROUND(100.0 * SUM(population) / SUM(SUM(population)) OVER (), 2) as percentage
   FROM dst_folk1a
   WHERE year = 2024
   GROUP BY region
   ORDER BY total_pop DESC
   LIMIT 10
   "
   ```

3. **Top regions**:
   ```bash
   python scripts/db/query_data.py --sql "
   SELECT
     region,
     region_name,
     population
   FROM dst_folk1a
   WHERE year = 2024
   ORDER BY population DESC
   LIMIT 10
   "
   ```

4. **Regional growth**:
   ```bash
   python scripts/db/query_data.py --sql "
   SELECT
     region,
     MIN(CASE WHEN year = 2020 THEN population END) as pop_2020,
     MAX(CASE WHEN year = 2024 THEN population END) as pop_2024,
     MAX(CASE WHEN year = 2024 THEN population END) -
       MIN(CASE WHEN year = 2020 THEN population END) as growth
   FROM dst_folk1a
   WHERE year IN (2020, 2024)
   GROUP BY region
   ORDER BY growth DESC
   "
   ```

### Expected Results
- Population by region
- Percentages and rankings
- Growth comparisons

### Tips
- Use GROUP BY region for aggregation
- Calculate percentages with window functions
- Use CASE statements for pivoting
- ORDER BY DESC for rankings

---

## Workflow 6: Data Refresh

**Goal**: Update old data with latest from DST

**Example**: "Update population data and recalculate trends"

### Steps

1. **Check current data age**:
   ```bash
   python scripts/db/query_metadata.py --table-id FOLK1A --check-freshness --max-age-days 30
   ```

2. **If stale, refresh**:
   ```bash
   python scripts/fetch_and_store.py --table-id FOLK1A --overwrite
   ```

3. **Verify fresh data**:
   ```bash
   python scripts/db/query_metadata.py --table-id FOLK1A
   ```

4. **Re-run previous analysis**:
   ```bash
   python scripts/db/query_data.py --sql "YOUR PREVIOUS QUERY"
   ```

5. **Compare old vs. new results**:
   - Save old results before refresh
   - Compare totals, trends
   - Note any significant changes

### Expected Results
- Fresh data from DST
- Updated analysis
- Comparison of before/after

### Tips
- Check freshness regularly
- Use --overwrite to replace old data
- Document data age in analysis results
- Keep backups before major refreshes

---

## Workflow 7: Joining Multiple Tables

**Goal**: Combine data from multiple sources

**Example**: "Compare population and employment data"

### Steps

1. **Ensure both tables exist**:
   ```bash
   python scripts/db/query_metadata.py --list-all
   ```

2. **Understand table structures**:
   ```bash
   python scripts/db/table_summary.py --table-id FOLK1A
   python scripts/db/table_summary.py --table-id AUP01
   ```

3. **Identify join keys** (usually region, year, etc.)

4. **Simple join**:
   ```bash
   python scripts/db/query_data.py --sql "
   SELECT
     a.year,
     a.region,
     a.population,
     b.employment_count
   FROM dst_folk1a a
   INNER JOIN dst_aup01 b
     ON a.region = b.region
     AND a.year = b.year
   WHERE a.year >= 2020
   LIMIT 100
   "
   ```

5. **Calculate ratios**:
   ```bash
   python scripts/db/query_data.py --sql "
   SELECT
     a.region,
     a.year,
     ROUND(100.0 * b.employment_count / a.population, 2) as employment_rate_pct
   FROM dst_folk1a a
   INNER JOIN dst_aup01 b
     ON a.region = b.region
     AND a.year = b.year
   WHERE a.year = 2024
   ORDER BY employment_rate_pct DESC
   "
   ```

### Expected Results
- Combined data from multiple sources
- Calculated metrics and ratios
- Comprehensive analysis

### Tips
- Use INNER JOIN for matching records only
- Join on common keys (region, year)
- Check for NULL values
- Test joins with LIMIT first

---

## Workflow 8: Exporting Results

**Goal**: Save analysis results for use elsewhere

**Example**: "Export regional statistics to Excel"

### Steps

1. **Run analysis query**

2. **Export to CSV**:
   ```bash
   python scripts/db/query_data.py \
     --sql "SELECT region, population, employment_rate FROM ..." \
     --format csv \
     --output regional_stats.csv
   ```

3. **Export to JSON**:
   ```bash
   python scripts/db/query_data.py \
     --sql "SELECT * FROM dst_folk1a WHERE year = 2024" \
     --format json \
     --output population_2024.json
   ```

4. **Large export with formatting**:
   ```bash
   python scripts/db/query_data.py \
     --sql "SELECT * FROM dst_folk1a" \
     --format csv \
     --output complete_population_data.csv
   ```

5. **Open in spreadsheet**:
   - CSV files open directly in Excel, Google Sheets
   - JSON files can be imported into many tools

### Expected Results
- Structured data file (CSV or JSON)
- Ready for visualization tools
- Easy to share or archive

### Tips
- CSV for spreadsheets and visualization
- JSON for web applications and APIs
- Use --output to specify filename
- Test with LIMIT first for large exports

---

## General Workflow Tips

### Start Every Session

1. Check what data you have: `--list-all`
2. Check data freshness: `--check-freshness`
3. Get table summary before querying
4. Build queries incrementally (LIMIT first)

### When Things Go Wrong

1. Check logs: `logs/dst_system.log`
2. Verify table exists: `--list-all`
3. Check data structure: `table_summary`
4. Test simple query first
5. Add complexity gradually

### Performance Best Practices

1. Use LIMIT for exploration
2. Filter with WHERE early
3. Aggregate before joining
4. Index frequently-queried columns (advanced)
5. Monitor database size: `du -sh data/`

### Documentation

1. Save your queries in `.sql` files
2. Document workflow steps
3. Note data sources and dates
4. Keep change log of refreshes

---

**Need More Examples?**

- See `examples/` directory for complete workflows
- Check skill documentation for specific patterns
- Review `docs/sql-recipes.md` for query templates
