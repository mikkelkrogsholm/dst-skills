---
name: DST Data
description: Fetch actual data from Danmarks Statistik API and store in DuckDB. Use when user wants to download and store specific DST table data for analysis.
---

# DST Data Skill

## Purpose

Fetch statistical data from Danmarks Statistik API and persist it in the local DuckDB database for analysis. This is the final step in the data acquisition workflow, transforming remote API data into queryable local tables.

## When to Use

- User requests specific table data to be downloaded
- Ready to download data after reviewing table structure (tableinfo)
- Need to refresh existing data with latest from DST
- Want to store data for offline analysis
- Building a local data repository from DST

## How to Use - Recommended (Combined Workflow)

The `fetch_and_store.py` script combines fetching and storing in one command. This is the **recommended approach**.

### Basic Usage

Fetch and store a complete table:
```bash
python /home/user/dst-skills/scripts/fetch_and_store.py --table-id <TABLE_ID>
```

### With Filters

Fetch only specific data using filters:
```bash
python /home/user/dst-skills/scripts/fetch_and_store.py --table-id <TABLE_ID> --filters '<JSON>'
```

Example filters:
```bash
# Filter by region
--filters '{"OMRÅDE":["000"]}'

# Filter by time period
--filters '{"TID":["2024*"]}'

# Multiple filters
--filters '{"OMRÅDE":["000","101"],"TID":["2024*"]}'
```

### Overwrite Existing Data

Replace existing table:
```bash
python /home/user/dst-skills/scripts/fetch_and_store.py --table-id <TABLE_ID> --overwrite
```

### Skip if Fresh

Only fetch if data is older than threshold:
```bash
python /home/user/dst-skills/scripts/fetch_and_store.py --table-id <TABLE_ID> --skip-if-fresh --max-age-days 30
```

## How to Use - Advanced (Separate Steps)

For advanced users who need more control, fetch and store can be done separately.

### Step 1: Fetch Data

Download data from API:
```bash
python /home/user/dst-skills/scripts/api/fetch_data.py --table-id <TABLE_ID> --output data.json
```

### Step 2: Store Data

Save to DuckDB:
```bash
python /home/user/dst-skills/scripts/db/store_data.py --table-id <TABLE_ID> --data-file data.json
```

## Expected Output

### Data Storage
- Data stored in table named `dst_{table_id}` (lowercase)
- Example: Table FOLK1A → `dst_folk1a`
- Metadata updated in `dst_metadata` table

### Success Message
```
✓ Created table dst_folk1a with 45231 records
```

### If Skipped (Fresh Data)
```
⊘ Skipped FOLK1A: data_is_fresh
```

Exit codes:
- 0: Success
- 1: Error
- 2: Skipped (when using --skip-if-fresh)

## Important Considerations

### Data Size
- Large tables may take significant time to download
- Check table info first to estimate size
- Use filters to limit data volume when possible

### Existing Data
- Default behavior: Fail if table already exists
- Use `--overwrite` to replace existing data
- Overwrites completely - no partial updates

### Network and Time
- Requires stable internet connection
- Large downloads may timeout - retry if needed
- API may have rate limits

### Filters Format
- Filters must be valid JSON
- Keys are variable IDs from table info
- Values are arrays of allowed values
- Use wildcards where supported (e.g., "2024*")

## Verification Steps

After storing data, verify success:

### 1. Check Metadata
```bash
python /home/user/dst-skills/scripts/db/query_metadata.py --table-id <TABLE_ID>
```

### 2. Spot Check Data
```bash
python /home/user/dst-skills/scripts/db/query_data.py --sql "SELECT * FROM dst_<table_id> LIMIT 5"
```

### 3. Verify Record Count
Compare record count in metadata with table info expectations.

## Next Steps

After successfully storing data:

1. **Data is ready for analysis**
2. **Switch to DST Analyst Agent** for querying and analysis
3. **Run SQL queries** using dst-query skill
4. **Create summaries** using table_summary script

Example:
```bash
python /home/user/dst-skills/scripts/db/table_summary.py --table-id FOLK1A
```

## Examples

### Example 1: Simple fetch and store
```bash
python /home/user/dst-skills/scripts/fetch_and_store.py --table-id FOLK1A
```

### Example 2: Overwrite existing data
```bash
python /home/user/dst-skills/scripts/fetch_and_store.py --table-id FOLK1A --overwrite
```

### Example 3: Fetch with regional filter
```bash
python /home/user/dst-skills/scripts/fetch_and_store.py --table-id FOLK1A --filters '{"OMRÅDE":["000","101"]}'
```

### Example 4: Skip if recently fetched
```bash
python /home/user/dst-skills/scripts/fetch_and_store.py --table-id FOLK1A --skip-if-fresh --max-age-days 7
```

### Example 5: Advanced - separate steps
```bash
# Step 1: Fetch
python /home/user/dst-skills/scripts/api/fetch_data.py --table-id FOLK1A --output folk1a.json

# Step 2: Store
python /home/user/dst-skills/scripts/db/store_data.py --table-id FOLK1A --data-file folk1a.json
```

### Example 6: Export to CSV
```bash
python /home/user/dst-skills/scripts/api/fetch_data.py --table-id FOLK1A --format csv --output data.csv
```

## Tips

### Before Large Downloads
1. **Check table info** to understand data size
2. **Use filters** to limit to needed data
3. **Test with small filter** first

### For Regular Updates
1. **Use --skip-if-fresh** to avoid unnecessary downloads
2. **Set appropriate max-age-days** based on update frequency
3. **Use --overwrite** when refresh is needed

### Performance
- Filter at API level (not after download)
- Monitor disk space for large datasets
- Consider time of day (API load varies)

### Data Quality
- Always verify after storage
- Check record counts match expectations
- Spot check data values for sanity

## Common Filter Patterns

### Time Filters
```bash
# Specific year
--filters '{"TID":["2024"]}'

# Year range (wildcard)
--filters '{"TID":["202*"]}'

# Specific quarters
--filters '{"TID":["2024Q1","2024Q2"]}'
```

### Geographic Filters
```bash
# Whole country
--filters '{"OMRÅDE":["000"]}'

# Specific regions
--filters '{"OMRÅDE":["101","147"]}'

# Region codes: 000=Denmark, 101=Copenhagen, etc.
```

### Combined Filters
```bash
--filters '{"OMRÅDE":["000"],"TID":["202*"],"KØN":["M","K"]}'
```

## Troubleshooting

### "Table already exists"
- Use `--overwrite` flag to replace existing data
- Or query existing data first to check if refresh needed

### "Network timeout"
- Large table - try with filters to reduce size
- Retry the operation
- Check internet connection

### "Invalid filters"
- Verify JSON syntax is correct
- Check variable IDs match table info
- Ensure values exist in table info

### "No data returned"
- Filters may be too restrictive
- Verify table has data for requested filters
- Check table info for available values

### Disk Space Issues
- Monitor available space before large downloads
- Clean up old/unused tables
- Use filters to limit data volume
