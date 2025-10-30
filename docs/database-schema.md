# Database Schema Documentation

## Overview

The DST Skills project uses DuckDB as its embedded database for storing and querying Danish statistics data. DuckDB provides SQL-based analytics capabilities with excellent performance for analytical queries.

**Database Location:** `/Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/data/dst_data.duckdb`

## Core Tables

### dst_metadata

The `dst_metadata` table stores metadata about DST tables that have been fetched and stored in the database.

#### Schema

| Column Name | Data Type | Constraints | Description |
|------------|-----------|-------------|-------------|
| `table_id` | VARCHAR | PRIMARY KEY | Unique identifier for the DST table (e.g., "FOLK1A") |
| `table_name` | VARCHAR | | Human-readable name/description of the table |
| `last_updated` | TIMESTAMP | | When the data was last updated in the DST system |
| `fetch_timestamp` | TIMESTAMP | | When we last fetched/updated the data |
| `record_count` | INTEGER | | Number of records in the data table |
| `columns_json` | VARCHAR | | JSON string containing column metadata |
| `notes` | VARCHAR | | Additional notes or metadata |

#### Indexes

- Primary key index on `table_id` (automatically created)
- Additional index: `idx_table_id` on `table_id`

#### Example Record

```sql
INSERT INTO dst_metadata (
    table_id,
    table_name,
    last_updated,
    fetch_timestamp,
    record_count,
    columns_json,
    notes
) VALUES (
    'FOLK1A',
    'Befolkningen den 1. i kvartalet',
    '2025-10-15 10:30:00',
    '2025-10-30 09:15:00',
    45231,
    '{"columns": ["område", "tid", "antal"]}',
    'Quarterly population statistics by region'
);
```

## Data Tables

### Naming Convention

Data tables follow the naming pattern: `dst_{table_id}`

For example:
- Table ID `FOLK1A` → Data table name `dst_folk1a`
- Table ID `NABB3` → Data table name `dst_nabb3`

All table names are lowercase for consistency.

### Structure

Each data table contains the actual statistical data from DST. The structure varies based on the specific dataset but typically includes:

- Dimension columns (e.g., geography, time period, categories)
- Value columns (e.g., counts, percentages, amounts)

The exact column structure is stored as JSON in the `columns_json` field of the `dst_metadata` table.

## Data Freshness Strategy

The system uses timestamps to track data freshness and avoid unnecessary API calls:

1. **last_updated**: Timestamp from DST indicating when they last updated the data
2. **fetch_timestamp**: Timestamp when we last fetched the data

### Freshness Check Logic

```sql
-- Check if we need to refresh a table
SELECT
    table_id,
    table_name,
    last_updated,
    fetch_timestamp,
    CASE
        WHEN fetch_timestamp IS NULL THEN 'NEVER_FETCHED'
        WHEN last_updated > fetch_timestamp THEN 'OUTDATED'
        WHEN CURRENT_TIMESTAMP - fetch_timestamp > INTERVAL 7 DAYS THEN 'STALE'
        ELSE 'FRESH'
    END as freshness_status
FROM dst_metadata
WHERE table_id = 'FOLK1A';
```

## Common Queries

### List All Tracked Tables

```sql
SELECT
    table_id,
    table_name,
    record_count,
    fetch_timestamp
FROM dst_metadata
ORDER BY fetch_timestamp DESC;
```

### Find Tables Needing Update

```sql
SELECT
    table_id,
    table_name,
    last_updated,
    fetch_timestamp
FROM dst_metadata
WHERE last_updated > fetch_timestamp
   OR fetch_timestamp IS NULL
   OR CURRENT_TIMESTAMP - fetch_timestamp > INTERVAL 30 DAYS;
```

### Get Table Statistics

```sql
SELECT
    COUNT(*) as total_tables,
    SUM(record_count) as total_records,
    AVG(record_count) as avg_records_per_table,
    MIN(fetch_timestamp) as oldest_fetch,
    MAX(fetch_timestamp) as newest_fetch
FROM dst_metadata;
```

### Check Specific Table Status

```sql
SELECT
    table_id,
    table_name,
    last_updated,
    fetch_timestamp,
    record_count,
    notes
FROM dst_metadata
WHERE table_id = 'FOLK1A';
```

## Database Operations

### Initialization

Initialize the database using the provided script:

```bash
python scripts/db/init_db.py
```

### Backup

Create a backup of the database:

```bash
cp data/dst_data.duckdb data/dst_data.duckdb.backup.$(date +%Y%m%d)
```

### Verify Integrity

```sql
-- Check table exists
SELECT COUNT(*) FROM information_schema.tables
WHERE table_name = 'dst_metadata';

-- Check record count
SELECT COUNT(*) FROM dst_metadata;

-- Verify schema
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'dst_metadata'
ORDER BY ordinal_position;
```

## Performance Considerations

1. **Primary Keys**: All metadata uses `table_id` as primary key for fast lookups
2. **Indexes**: Additional indexes can be added as needed for specific query patterns
3. **Data Types**: VARCHAR used for flexibility; consider specific types if performance issues arise
4. **Partitioning**: Not currently implemented but can be added if table grows large

## Future Enhancements

Potential schema improvements for future phases:

- Add `subject_id` column to link tables to DST subjects
- Add `update_frequency` to track expected update intervals
- Add `data_quality_score` for tracking data completeness
- Create separate table for tracking fetch history/audit log
- Add table for storing API response cache
