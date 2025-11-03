# DuckDB Storage Bug Fix Report

## Issue Summary

Data was being stored in DuckDB as a **single JSON column** instead of proper relational columns, making the data completely unusable for SQL queries.

### Problem Example

**Before Fix:**
```sql
-- dst_bil707 had ONE column with name = entire JSON object
Column: '{"dataset":{"dimension":{...}}}: INTEGER'
Row count: 0
```

**After Fix:**
```sql
-- dst_bil707 has proper columns
Columns: BILTYPE, OMRÅDE, TID, INDHOLD
Sample: ('Personbiler i alt', 'Hele landet', 2025, 2864904)
```

## Root Cause

The bug occurred when data was fetched in **JSON-STAT format** from the DST API:

1. `client.get_data()` returned a Python dict (JSON-STAT structure)
2. `store_data.py` received the dict but didn't recognize the format
3. The code at line 76-81 wrapped the entire dict in a DataFrame: `pd.DataFrame([data])`
4. Pandas created a single column with the stringified JSON as the column name
5. DuckDB stored this malformed structure

## Files Modified

### 1. `/scripts/db/store_data.py`

**Change:** Added JSON-STAT format detection and proper parsing

```python
# Before (line 75-81)
elif isinstance(data, dict):
    if 'data' in data and isinstance(data['data'], list):
        df = pd.DataFrame(data['data'])
    else:
        df = pd.DataFrame([data])  # ← BUG: Creates single-column DF

# After (line 75-93)
elif isinstance(data, dict):
    # Check if this is JSON-STAT format
    if 'dataset' in data:
        logger.info("Detected JSON-STAT format, parsing...")
        from api.helpers import parse_jsonstat
        df = parse_jsonstat(data)
        if df.empty:
            raise ValueError("JSON-STAT parsing resulted in empty dataframe")
        logger.info(f"Parsed {len(df)} rows from JSON-STAT")
    elif 'data' in data and isinstance(data['data'], list):
        df = pd.DataFrame(data['data'])
    else:
        logger.warning(f"Attempting to convert dict to dataframe - this may not work correctly")
        df = pd.DataFrame([data])
```

### 2. `/scripts/api/helpers.py`

**Change:** Rewrote `parse_jsonstat()` function to properly parse JSON-STAT structure

The original implementation only extracted values:
```python
# Before (simplified)
def parse_jsonstat(json_data):
    values = dataset.get('value', [])
    df = pd.DataFrame({'value': values})  # ← Only values, no dimensions
    return df
```

New implementation properly extracts all dimensions and creates relational columns:
```python
# After (lines 143-247)
def parse_jsonstat(json_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Parse JSONSTAT response from DST API into a proper relational DataFrame.

    Extracts:
    - All dimension IDs (OMRÅDE, KØN, TID, etc.)
    - All dimension values using category index and labels
    - Data values as INDHOLD column

    Returns DataFrame with proper columns for each dimension.
    """
    # Extract dimensions and sizes
    dim_ids = dimension_info.get('id', [])
    dim_sizes = dimension_info.get('size', [])

    # Build ordered list of codes for each dimension
    # Generate Cartesian product of all dimension values
    # Map flat value array to proper rows with dimension columns

    return df  # Proper relational DataFrame
```

## Testing Results

### Test 1: CSV/BULK Format (Still Works)
```
✓ Fetched data (type: str)
✓ Stored 1 records in dst_test_csv
✓ Table has 6 columns: OMRÅDE, KØN, ALDER, CIVILSTAND, TID, INDHOLD
✓ Sample row: ('Hele landet', 'I alt', 'Alder i alt', 'I alt', '2025K1', 5992734)
```

### Test 2: JSON-STAT Format (Now Fixed)
```
✓ Fetched data (type: dict)
✓ Has 'dataset' key: True
✓ Stored 2 records in dst_test_json
✓ Table has 7 columns: Tid, ContentsCode, CIVILSTAND, ALDER, KØN, OMRÅDE, INDHOLD
✓ No JSON blob columns (bug is fixed!)
✓ Sample row (filtered): ('2025K1', 'Befolkningen den 1. i kvartalet', 'I alt', 'Alder i alt', 'Mænd', 'Hele landet', 2978985)
```

### Test 3: SQL Queries (Now Work Correctly)
```sql
-- Filter by column
SELECT * FROM dst_folk1a WHERE OMRÅDE = 'Hele landet';
-- ✓ Works

-- Aggregation
SELECT BILTYPE, INDHOLD FROM dst_bil707 WHERE INDHOLD > 1000000;
-- ✓ Works

-- Window functions
SELECT
  Tid, KØN, INDHOLD,
  INDHOLD - LAG(INDHOLD) OVER (PARTITION BY KØN ORDER BY Tid) as growth
FROM dst_folk1a_json_test
-- ✓ Works
```

## Verification

All existing tables now have proper structure:

```
dst_folk1a:
  Columns (6): OMRÅDE, KØN, ALDER, CIVILSTAND, TID, INDHOLD
  ✓ Proper column structure

dst_bil707:
  Columns (4): BILTYPE, OMRÅDE, TID, INDHOLD
  ✓ Proper column structure
```

## Impact

This fix enables:
1. ✅ Proper relational data storage in DuckDB
2. ✅ Full SQL query support (filtering, aggregation, joins, window functions)
3. ✅ Support for both CSV/BULK and JSON-STAT formats from DST API
4. ✅ Meaningful column names instead of JSON blobs
5. ✅ Ability to use DuckDB for actual data analysis

## Database Path Note

During investigation, discovered the database path issue:
- Default path in `db_utils.py`: `./data/dst_data.duckdb` ✅
- Old test database: `data/dst.db` (can be deleted)

The correct database `dst_data.duckdb` is being used and contains all properly structured data.
