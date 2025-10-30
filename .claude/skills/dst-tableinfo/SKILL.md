---
name: DST Table Info
description: Get detailed metadata for a specific Danmarks Statistik table including variables, dimensions, and structure. Use before fetching data to understand table schema.
---

# DST Table Info Skill

## Purpose

Get complete metadata and structure for a DST table. This is an essential step before fetching data - it tells you what dimensions are available, what filters you can apply, and what to expect in the data.

## When to Use

- Before fetching data to understand table structure
- To see available variables and dimensions
- To determine appropriate filters for data fetch
- To understand table updates and units of measurement
- User asks "what's in this table?"
- After finding a table ID with dst-tables skill

## How to Use

### Basic Usage (JSON output)

Get table metadata:
```bash
python /home/user/dst-skills/scripts/api/get_tableinfo.py --table-id <TABLE_ID>
```

### Verbose Format (Human-readable)

Get formatted, easy-to-read output:
```bash
python /home/user/dst-skills/scripts/api/get_tableinfo.py --table-id <TABLE_ID> --verbose
```

### Save to File

Save metadata for reference:
```bash
python /home/user/dst-skills/scripts/api/get_tableinfo.py --table-id <TABLE_ID> --output info.json
```

## Expected Output

The script returns complete table metadata including:

### Basic Information
- **id**: Table identifier
- **text**: Table name
- **description**: Detailed description
- **unit**: Unit of measurement
- **updated**: Last update timestamp

### Variables/Dimensions
- **id**: Variable identifier (e.g., "OMRÅDE", "TID")
- **text**: Variable description
- **values**: All available values for that variable
- **time**: Whether it's a time dimension

Example output structure:
```json
{
  "id": "FOLK1A",
  "text": "Population at the first day of the quarter",
  "description": "Population by region, age, and sex",
  "unit": "number",
  "updated": "2025-10-15T10:30:00",
  "variables": [
    {
      "id": "OMRÅDE",
      "text": "Region",
      "values": [
        {"id": "000", "text": "Whole country"},
        {"id": "101", "text": "Copenhagen"}
      ]
    },
    {
      "id": "TID",
      "text": "Time",
      "time": true,
      "values": [
        {"id": "2020Q1", "text": "2020Q1"},
        {"id": "2020Q2", "text": "2020Q2"}
      ]
    }
  ]
}
```

## Key Information to Extract

When analyzing table info, pay attention to:

1. **Table Description**: What data does it contain?
2. **Unit**: What do the numbers represent? (persons, kroner, percentage, etc.)
3. **Variables**: What dimensions can you filter by?
4. **Available Values**: What options exist for each variable?
5. **Time Coverage**: What time periods are available?
6. **Last Updated**: How fresh is the data?

## Next Steps

After understanding the table structure:

1. **Decide on filters** (optional): Based on variables and values
2. **Fetch the data** using dst-data skill:
   ```bash
   python /home/user/dst-skills/scripts/fetch_and_store.py --table-id <TABLE_ID>
   ```
3. **With filters** (if needed):
   ```bash
   python /home/user/dst-skills/scripts/fetch_and_store.py --table-id <TABLE_ID> --filters '{"OMRÅDE":["000"]}'
   ```

## Examples

### Example 1: Get table info for FOLK1A
```bash
python /home/user/dst-skills/scripts/api/get_tableinfo.py --table-id FOLK1A
```

### Example 2: Verbose, readable output
```bash
python /home/user/dst-skills/scripts/api/get_tableinfo.py --table-id FOLK1A --verbose
```

### Example 3: Save to file
```bash
python /home/user/dst-skills/scripts/api/get_tableinfo.py --table-id FOLK1A --output folk1a_structure.json
```

### Example 4: Check multiple tables
```bash
# Get info for population table
python /home/user/dst-skills/scripts/api/get_tableinfo.py --table-id FOLK1A --verbose

# Get info for employment table
python /home/user/dst-skills/scripts/api/get_tableinfo.py --table-id AUP01 --verbose
```

## Tips

- **Always check before fetching**: Large tables can take time to download
- **Note available filters**: Limit data size by filtering dimensions
- **Check date range**: Understand temporal coverage
- **Understand variables**: Know what you can group/filter by
- **Use verbose mode**: Easier to read when exploring interactively
- **Save JSON**: Keep machine-readable format for programmatic use

## Common Variables (Reference)

Typical DST variable names:
- **OMRÅDE**: Geographic region
- **TID**: Time period
- **ALDER**: Age
- **KØN**: Sex/Gender
- **BRANCHE**: Industry
- **UDDANNELSE**: Education level
- **INDKOMST**: Income bracket

Note: Variable names are usually in Danish.

## Understanding Values

Each variable has a set of possible values:
- **Hierarchical**: Some variables have parent-child relationships
- **Time values**: Usually format like "2020Q1", "2020M01", "2020"
- **Region codes**: Numeric codes like "000" (whole country), "101" (Copenhagen)
- **Categories**: Text or numeric codes for classifications

## Troubleshooting

- **Table not found**: Verify table ID is correct (case-sensitive)
- **Empty values**: Some tables may have limited options
- **Large output**: Use `--verbose` for summary or `--output` to save
- **Network errors**: Check internet connection and DST API status
