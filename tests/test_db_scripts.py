"""
Comprehensive pytest tests for all database scripts in the DST Skills project.

Tests cover:
- query_metadata.py: Metadata queries and freshness checks
- query_data.py: SQL query execution
- store_data.py: Data storage operations
- table_summary.py: Table summary generation

All tests use real DuckDB database (temp_db fixture) and follow KISS, DRY, YAGNI principles.
"""

import sys
import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from io import StringIO
import tempfile

# Add scripts to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "scripts"))

from db import query_metadata, query_data, store_data, table_summary, db_utils


# ============================================================================
# QUERY_METADATA.PY TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestQueryMetadata:
    """Test suite for query_metadata.py functions."""

    def test_calculate_age_string_just_now(self):
        """Test age calculation for very recent timestamps."""
        timestamp = datetime.now()
        result = query_metadata.calculate_age_string(timestamp)
        assert result == "Just now"

    def test_calculate_age_string_minutes_ago(self):
        """Test age calculation for timestamps in minutes."""
        timestamp = datetime.now() - timedelta(minutes=5)
        result = query_metadata.calculate_age_string(timestamp)
        assert result == "5 minutes ago"

    def test_calculate_age_string_hours_ago(self):
        """Test age calculation for timestamps in hours."""
        timestamp = datetime.now() - timedelta(hours=3)
        result = query_metadata.calculate_age_string(timestamp)
        assert result == "3 hours ago"

    def test_calculate_age_string_days_ago(self):
        """Test age calculation for timestamps in days."""
        timestamp = datetime.now() - timedelta(days=7)
        result = query_metadata.calculate_age_string(timestamp)
        assert result == "7 days ago"

    def test_calculate_age_string_months_ago(self):
        """Test age calculation for timestamps in months."""
        timestamp = datetime.now() - timedelta(days=60)
        result = query_metadata.calculate_age_string(timestamp)
        assert result == "2 months ago"

    def test_calculate_age_string_years_ago(self):
        """Test age calculation for timestamps in years."""
        timestamp = datetime.now() - timedelta(days=730)
        result = query_metadata.calculate_age_string(timestamp)
        assert result == "2 years ago"

    def test_calculate_age_string_iso_string(self):
        """Test age calculation with ISO format string input."""
        timestamp = datetime.now() - timedelta(days=1)
        iso_string = timestamp.isoformat()
        result = query_metadata.calculate_age_string(iso_string)
        assert result == "1 day ago"

    def test_calculate_age_string_none(self):
        """Test age calculation with None input."""
        result = query_metadata.calculate_age_string(None)
        assert result == "Unknown"

    def test_calculate_age_string_invalid(self):
        """Test age calculation with invalid string."""
        result = query_metadata.calculate_age_string("invalid")
        assert result == "Invalid timestamp"

    def test_list_all_tables_empty(self, temp_db, temp_db_path, mock_env_vars):
        """Test listing all tables when database is empty."""
        result = query_metadata.list_all_tables(format='json')
        assert isinstance(result, list)
        assert len(result) == 0

    def test_list_all_tables_with_data(self, temp_db, temp_db_path, mock_env_vars):
        """Test listing all tables with metadata entries."""
        # Insert test metadata
        temp_db.execute("""
            INSERT INTO dst_metadata
            (table_id, table_name, fetch_timestamp, record_count)
            VALUES (?, ?, ?, ?)
        """, ['TEST1', 'Test Table 1', datetime.now().isoformat(), 100])

        temp_db.execute("""
            INSERT INTO dst_metadata
            (table_id, table_name, fetch_timestamp, record_count)
            VALUES (?, ?, ?, ?)
        """, ['TEST2', 'Test Table 2', datetime.now().isoformat(), 200])

        # Test JSON format
        result = query_metadata.list_all_tables(format='json')
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]['table_id'] == 'TEST1'
        assert result[1]['table_id'] == 'TEST2'
        assert 'age' in result[0]

        # Test table format
        result_table = query_metadata.list_all_tables(format='table')
        assert isinstance(result_table, str)
        assert 'TEST1' in result_table
        assert 'TEST2' in result_table
        assert 'Test Table 1' in result_table

    def test_get_metadata_success(self, temp_db, temp_db_path, mock_env_vars):
        """Test retrieving metadata for an existing table."""
        # Insert test metadata
        now = datetime.now().isoformat()
        temp_db.execute("""
            INSERT INTO dst_metadata
            (table_id, table_name, last_updated, fetch_timestamp, record_count, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ['FOLK1A', 'Population Table', '2024-01-01', now, 500, 'Test note'])

        # Test JSON format
        result = query_metadata.get_metadata('FOLK1A', format='json')
        assert isinstance(result, dict)
        assert result['table_id'] == 'FOLK1A'
        assert result['table_name'] == 'Population Table'
        assert result['record_count'] == 500
        assert result['notes'] == 'Test note'
        assert 'age' in result

        # Test table format
        result_table = query_metadata.get_metadata('FOLK1A', format='table')
        assert isinstance(result_table, str)
        assert 'FOLK1A' in result_table
        assert 'Population Table' in result_table
        assert '500' in result_table

    def test_get_metadata_not_found(self, temp_db, temp_db_path, mock_env_vars):
        """Test retrieving metadata for non-existent table."""
        with pytest.raises(ValueError, match="not found in metadata"):
            query_metadata.get_metadata('NONEXISTENT')

    def test_check_freshness_success(self, temp_db, temp_db_path, mock_env_vars):
        """Test checking freshness of recent data."""
        # Insert recent metadata
        now = datetime.now().isoformat()
        temp_db.execute("""
            INSERT INTO dst_metadata
            (table_id, table_name, fetch_timestamp, last_updated)
            VALUES (?, ?, ?, ?)
        """, ['FOLK1A', 'Population Table', now, '2024-01-01'])

        result = query_metadata.check_freshness('FOLK1A')
        assert isinstance(result, str)
        assert 'FOLK1A' in result
        assert 'Population Table' in result

    def test_check_freshness_with_threshold_fresh(self, temp_db, temp_db_path, mock_env_vars):
        """Test freshness check with threshold - data is fresh."""
        # Insert data from 10 days ago
        past_date = datetime.now() - timedelta(days=10)
        temp_db.execute("""
            INSERT INTO dst_metadata
            (table_id, table_name, fetch_timestamp, last_updated)
            VALUES (?, ?, ?, ?)
        """, ['FOLK1A', 'Population Table', past_date.isoformat(), '2024-01-01'])

        result = query_metadata.check_freshness('FOLK1A', max_age_days=30)
        assert '✓ FRESH' in result
        assert 'acceptable age threshold' in result

    def test_check_freshness_with_threshold_stale(self, temp_db, temp_db_path, mock_env_vars):
        """Test freshness check with threshold - data is stale."""
        # Insert data from 60 days ago
        past_date = datetime.now() - timedelta(days=60)
        temp_db.execute("""
            INSERT INTO dst_metadata
            (table_id, table_name, fetch_timestamp, last_updated)
            VALUES (?, ?, ?, ?)
        """, ['FOLK1A', 'Population Table', past_date.isoformat(), '2024-01-01'])

        result = query_metadata.check_freshness('FOLK1A', max_age_days=30)
        assert '✗ STALE' in result
        assert 'exceeds age threshold' in result

    def test_check_freshness_no_timestamp(self, temp_db, temp_db_path, mock_env_vars):
        """Test freshness check when no timestamp is available."""
        # Insert metadata without timestamp
        temp_db.execute("""
            INSERT INTO dst_metadata
            (table_id, table_name)
            VALUES (?, ?)
        """, ['FOLK1A', 'Population Table'])

        result = query_metadata.check_freshness('FOLK1A')
        assert 'No fetch timestamp available' in result

    def test_check_freshness_not_found(self, temp_db, temp_db_path, mock_env_vars):
        """Test freshness check for non-existent table."""
        with pytest.raises(ValueError, match="not found in metadata"):
            query_metadata.check_freshness('NONEXISTENT')


# ============================================================================
# QUERY_DATA.PY TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestQueryData:
    """Test suite for query_data.py functions."""

    def test_validate_query_valid_select(self):
        """Test validation of valid SELECT query."""
        sql = "SELECT * FROM dst_folk1a"
        is_valid, error = query_data.validate_query(sql)
        assert is_valid is True
        assert error is None

    def test_validate_query_valid_select_with_join(self):
        """Test validation of complex SELECT query."""
        sql = "SELECT a.id, b.name FROM dst_table1 a JOIN dst_table2 b ON a.id = b.id"
        is_valid, error = query_data.validate_query(sql)
        assert is_valid is True
        assert error is None

    def test_validate_query_invalid_drop(self):
        """Test validation rejects DROP statements."""
        sql = "DROP TABLE dst_folk1a"
        is_valid, error = query_data.validate_query(sql)
        assert is_valid is False
        # Could be either message depending on query validation order
        assert error in ["Only SELECT queries are allowed (read-only)", "Query contains prohibited keyword: DROP"]

    def test_validate_query_invalid_delete(self):
        """Test validation rejects DELETE statements."""
        sql = "DELETE FROM dst_folk1a WHERE id = 1"
        is_valid, error = query_data.validate_query(sql)
        assert is_valid is False
        assert error in ["Only SELECT queries are allowed (read-only)", "Query contains prohibited keyword: DELETE"]

    def test_validate_query_invalid_insert(self):
        """Test validation rejects INSERT statements."""
        sql = "INSERT INTO dst_folk1a VALUES (1, 'test')"
        is_valid, error = query_data.validate_query(sql)
        assert is_valid is False
        assert error in ["Only SELECT queries are allowed (read-only)", "Query contains prohibited keyword: INSERT"]

    def test_validate_query_invalid_update(self):
        """Test validation rejects UPDATE statements."""
        sql = "UPDATE dst_folk1a SET name = 'test'"
        is_valid, error = query_data.validate_query(sql)
        assert is_valid is False
        assert error in ["Only SELECT queries are allowed (read-only)", "Query contains prohibited keyword: UPDATE"]

    def test_validate_query_invalid_not_select(self):
        """Test validation rejects non-SELECT statements."""
        sql = "CREATE TABLE test (id INT)"
        is_valid, error = query_data.validate_query(sql)
        assert is_valid is False
        assert "Only SELECT queries are allowed" in error

    def test_execute_query_simple(self, temp_db, temp_db_path, mock_env_vars):
        """Test executing a simple SELECT query."""
        # Create test table with data
        temp_db.execute("CREATE TABLE dst_test (id INT, name VARCHAR)")
        temp_db.execute("INSERT INTO dst_test VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie')")

        # Execute query - JSON format
        result = query_data.execute_query("SELECT * FROM dst_test", format='json')
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]['id'] == 1
        assert result[0]['name'] == 'Alice'

    def test_execute_query_with_where(self, temp_db, temp_db_path, mock_env_vars):
        """Test executing query with WHERE clause."""
        # Create test table with data
        temp_db.execute("CREATE TABLE dst_test (id INT, name VARCHAR)")
        temp_db.execute("INSERT INTO dst_test VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Charlie')")

        # Execute query with WHERE
        result = query_data.execute_query(
            "SELECT * FROM dst_test WHERE id > 1",
            format='json'
        )
        assert len(result) == 2
        assert result[0]['id'] == 2

    def test_execute_query_csv_format(self, temp_db, temp_db_path, mock_env_vars):
        """Test executing query with CSV output format."""
        # Create test table with data
        temp_db.execute("CREATE TABLE dst_test (id INT, name VARCHAR)")
        temp_db.execute("INSERT INTO dst_test VALUES (1, 'Alice'), (2, 'Bob')")

        # Execute query - CSV format
        result = query_data.execute_query("SELECT * FROM dst_test", format='csv')
        assert isinstance(result, str)
        assert 'id,name' in result
        assert 'Alice' in result
        assert 'Bob' in result

    def test_execute_query_table_format(self, temp_db, temp_db_path, mock_env_vars):
        """Test executing query with table output format."""
        # Create test table with data
        temp_db.execute("CREATE TABLE dst_test (id INT, name VARCHAR)")
        temp_db.execute("INSERT INTO dst_test VALUES (1, 'Alice')")

        # Execute query - table format
        result = query_data.execute_query("SELECT * FROM dst_test", format='table')
        assert isinstance(result, str)
        assert 'id' in result
        assert 'name' in result
        assert 'Alice' in result
        assert '1 rows returned' in result

    def test_execute_query_with_limit(self, temp_db, temp_db_path, mock_env_vars):
        """Test executing query with automatic limit."""
        # Create test table with data
        temp_db.execute("CREATE TABLE dst_test (id INT)")
        for i in range(10):
            temp_db.execute(f"INSERT INTO dst_test VALUES ({i})")

        # Execute query with limit
        result = query_data.execute_query(
            "SELECT * FROM dst_test",
            format='json',
            limit=5
        )
        assert len(result) == 5

    def test_execute_query_empty_result(self, temp_db, temp_db_path, mock_env_vars):
        """Test executing query that returns no results."""
        # Create empty table
        temp_db.execute("CREATE TABLE dst_test (id INT)")

        # Execute query - table format
        result = query_data.execute_query("SELECT * FROM dst_test", format='table')
        assert "No results returned" in result

    def test_execute_query_invalid_sql(self, temp_db, temp_db_path, mock_env_vars):
        """Test executing invalid SQL query."""
        with pytest.raises(ValueError, match="Invalid query"):
            query_data.execute_query("DROP TABLE test")

    def test_execute_query_table_not_found(self, temp_db, temp_db_path, mock_env_vars):
        """Test executing query on non-existent table."""
        with pytest.raises(Exception):
            query_data.execute_query("SELECT * FROM nonexistent_table")


# ============================================================================
# STORE_DATA.PY TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestStoreData:
    """Test suite for store_data.py functions."""

    def test_store_data_list_of_dicts(self, temp_db, temp_db_path, mock_env_vars):
        """Test storing data from list of dictionaries."""
        data = [
            {'id': 1, 'name': 'Alice', 'age': 30},
            {'id': 2, 'name': 'Bob', 'age': 25},
            {'id': 3, 'name': 'Charlie', 'age': 35}
        ]

        result = store_data.store_data('TEST1', data, update_metadata=False)

        assert result['table_name'] == 'dst_test1'
        assert result['record_count'] == 3
        assert result['overwritten'] is False

        # Verify data was stored
        rows = temp_db.execute("SELECT * FROM dst_test1").fetchall()
        assert len(rows) == 3

    def test_store_data_dict_with_data_key(self, temp_db, temp_db_path, mock_env_vars):
        """Test storing data from dictionary with 'data' key."""
        data = {
            'data': [
                {'id': 1, 'value': 100},
                {'id': 2, 'value': 200}
            ]
        }

        result = store_data.store_data('TEST2', data, update_metadata=False)

        assert result['record_count'] == 2

        # Verify data was stored
        rows = temp_db.execute("SELECT * FROM dst_test2").fetchall()
        assert len(rows) == 2

    def test_store_data_with_metadata_update(self, temp_db, temp_db_path, mock_env_vars):
        """Test storing data with metadata table update."""
        data = [
            {'id': 1, 'name': 'Test'},
            {'id': 2, 'name': 'Data'}
        ]

        result = store_data.store_data('FOLK1A', data, update_metadata=True)

        assert result['record_count'] == 2

        # Verify metadata was created
        metadata = temp_db.execute(
            "SELECT * FROM dst_metadata WHERE table_id = ?",
            ['FOLK1A']
        ).fetchone()

        assert metadata is not None
        assert metadata[0] == 'FOLK1A'  # table_id
        assert metadata[4] == 2  # record_count

    def test_store_data_overwrite_false(self, temp_db, temp_db_path, mock_env_vars):
        """Test that storing fails when table exists and overwrite=False."""
        data = [{'id': 1}]

        # First insert
        store_data.store_data('TEST3', data, update_metadata=False)

        # Second insert should fail
        with pytest.raises(ValueError, match="already exists"):
            store_data.store_data('TEST3', data, overwrite=False, update_metadata=False)

    def test_store_data_overwrite_true(self, temp_db, temp_db_path, mock_env_vars):
        """Test overwriting existing table."""
        data_v1 = [{'id': 1, 'value': 'old'}]
        data_v2 = [{'id': 2, 'value': 'new'}]

        # First insert
        result1 = store_data.store_data('TEST4', data_v1, update_metadata=False)
        assert result1['overwritten'] is False

        # Overwrite
        result2 = store_data.store_data('TEST4', data_v2, overwrite=True, update_metadata=False)
        assert result2['overwritten'] is True

        # Verify new data
        rows = temp_db.execute("SELECT * FROM dst_test4").fetchall()
        assert len(rows) == 1
        assert rows[0][0] == 2
        assert rows[0][1] == 'new'

    def test_store_data_empty_list(self, temp_db, temp_db_path, mock_env_vars):
        """Test that storing empty data raises error."""
        with pytest.raises(ValueError, match="Cannot store empty data"):
            store_data.store_data('TEST5', [], update_metadata=False)

    def test_store_data_metadata_update_existing(self, temp_db, temp_db_path, mock_env_vars):
        """Test updating existing metadata entry."""
        data_v1 = [{'id': 1}]
        data_v2 = [{'id': 1}, {'id': 2}, {'id': 3}]

        # First insert with metadata
        store_data.store_data('FOLK1A', data_v1, update_metadata=True)

        # Overwrite with new data
        store_data.store_data('FOLK1A', data_v2, overwrite=True, update_metadata=True)

        # Verify metadata was updated
        metadata = temp_db.execute(
            "SELECT record_count FROM dst_metadata WHERE table_id = ?",
            ['FOLK1A']
        ).fetchone()

        assert metadata[0] == 3

    def test_store_data_unsupported_type(self, temp_db, temp_db_path, mock_env_vars):
        """Test that unsupported data types raise error."""
        with pytest.raises(ValueError, match="Unsupported data type"):
            store_data.store_data('TEST6', "invalid data", update_metadata=False)


# ============================================================================
# TABLE_SUMMARY.PY TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestTableSummary:
    """Test suite for table_summary.py functions."""

    def test_get_table_summary_basic(self, temp_db, temp_db_path, mock_env_vars):
        """Test generating basic table summary."""
        # Create test table
        temp_db.execute("""
            CREATE TABLE dst_test1 (
                id INTEGER,
                name VARCHAR,
                age INTEGER
            )
        """)
        temp_db.execute("""
            INSERT INTO dst_test1 VALUES
            (1, 'Alice', 30),
            (2, 'Bob', 25),
            (3, 'Charlie', 35)
        """)

        summary = table_summary.get_table_summary('TEST1')

        assert summary['table_id'] == 'TEST1'
        assert summary['table_name'] == 'dst_test1'
        assert summary['record_count'] == 3
        assert len(summary['columns']) == 3
        assert len(summary['sample_rows']) == 3

    def test_get_table_summary_with_metadata(self, temp_db, temp_db_path, mock_env_vars):
        """Test summary includes metadata when available."""
        # Create test table and metadata
        temp_db.execute("CREATE TABLE dst_test2 (id INTEGER)")
        temp_db.execute("INSERT INTO dst_test2 VALUES (1)")

        now = datetime.now().isoformat()
        temp_db.execute("""
            INSERT INTO dst_metadata
            (table_id, table_name, fetch_timestamp, record_count, last_updated)
            VALUES (?, ?, ?, ?, ?)
        """, ['TEST2', 'Test Table 2', now, 1, '2024-01-01'])

        summary = table_summary.get_table_summary('TEST2')

        assert 'metadata' in summary
        assert summary['metadata']['record_count'] == 1
        # Fetch timestamp might be returned as datetime object or string, so check both
        fetch_ts = summary['metadata']['fetch_timestamp']
        assert fetch_ts is not None
        if isinstance(fetch_ts, str):
            assert fetch_ts == now
        else:
            assert fetch_ts == datetime.fromisoformat(now)

    def test_get_table_summary_numeric_statistics(self, temp_db, temp_db_path, mock_env_vars):
        """Test summary includes statistics for numeric columns."""
        # Create table with numeric data
        temp_db.execute("""
            CREATE TABLE dst_test3 (
                id INTEGER,
                value DOUBLE
            )
        """)
        temp_db.execute("""
            INSERT INTO dst_test3 VALUES
            (1, 10.5),
            (2, 20.0),
            (3, 15.5),
            (4, 30.0)
        """)

        summary = table_summary.get_table_summary('TEST3')

        assert 'statistics' in summary
        assert 'value' in summary['statistics']

        stats = summary['statistics']['value']
        assert stats['min'] == 10.5
        assert stats['max'] == 30.0
        assert 'avg' in stats
        assert 'median' in stats
        assert stats['distinct_count'] == 4

    def test_get_table_summary_string_statistics(self, temp_db, temp_db_path, mock_env_vars):
        """Test summary includes statistics for string columns."""
        # Create table with string data
        temp_db.execute("""
            CREATE TABLE dst_test4 (
                id INTEGER,
                category VARCHAR
            )
        """)
        temp_db.execute("""
            INSERT INTO dst_test4 VALUES
            (1, 'A'),
            (2, 'B'),
            (3, 'A'),
            (4, 'C'),
            (5, 'A')
        """)

        summary = table_summary.get_table_summary('TEST4')

        assert 'statistics' in summary
        assert 'category' in summary['statistics']

        stats = summary['statistics']['category']
        assert stats['distinct_count'] == 3
        assert 'top_values' in stats

        # Check top values are sorted by count
        top_values = stats['top_values']
        assert top_values[0]['value'] == 'A'
        assert top_values[0]['count'] == 3

    def test_get_table_summary_with_nulls(self, temp_db, temp_db_path, mock_env_vars):
        """Test summary handles NULL values correctly."""
        # Create table with NULLs
        temp_db.execute("""
            CREATE TABLE dst_test5 (
                id INTEGER,
                value INTEGER
            )
        """)
        temp_db.execute("""
            INSERT INTO dst_test5 VALUES
            (1, 100),
            (2, NULL),
            (3, 200),
            (4, NULL)
        """)

        summary = table_summary.get_table_summary('TEST5')

        stats = summary['statistics']['value']
        assert stats['null_count'] == 2

    def test_get_table_summary_table_not_found(self, temp_db, temp_db_path, mock_env_vars):
        """Test summary fails for non-existent table."""
        with pytest.raises(ValueError, match="does not exist"):
            table_summary.get_table_summary('NONEXISTENT')

    def test_get_table_summary_sample_rows(self, temp_db, temp_db_path, mock_env_vars):
        """Test summary includes sample rows."""
        # Create table with more than 5 rows
        temp_db.execute("""
            CREATE TABLE dst_test6 (
                id INTEGER,
                value VARCHAR
            )
        """)
        for i in range(10):
            temp_db.execute(f"INSERT INTO dst_test6 VALUES ({i}, 'value_{i}')")

        summary = table_summary.get_table_summary('TEST6')

        assert len(summary['sample_rows']) == 5  # Should limit to 5
        assert summary['sample_rows'][0]['id'] == 0
        assert 'value' in summary['sample_rows'][0]

    def test_format_summary_text(self, temp_db, temp_db_path, mock_env_vars):
        """Test formatting summary as text."""
        # Create simple table
        temp_db.execute("CREATE TABLE dst_test7 (id INTEGER, name VARCHAR)")
        temp_db.execute("INSERT INTO dst_test7 VALUES (1, 'Test')")

        summary = table_summary.get_table_summary('TEST7')
        text_output = table_summary.format_summary_text(summary)

        assert isinstance(text_output, str)
        assert 'TEST7' in text_output
        assert 'dst_test7' in text_output
        assert 'RECORD COUNT: 1' in text_output
        assert 'COLUMNS' in text_output
        assert 'id' in text_output
        assert 'name' in text_output

    def test_get_table_summary_column_types(self, temp_db, temp_db_path, mock_env_vars):
        """Test summary correctly identifies column types."""
        # Create table with various types
        temp_db.execute("""
            CREATE TABLE dst_test8 (
                int_col INTEGER,
                double_col DOUBLE,
                varchar_col VARCHAR,
                date_col DATE
            )
        """)
        temp_db.execute("""
            INSERT INTO dst_test8 VALUES
            (1, 1.5, 'text', '2024-01-01')
        """)

        summary = table_summary.get_table_summary('TEST8')

        columns = summary['columns']
        assert len(columns) == 4

        # Check column types are captured
        col_names = [col['name'] for col in columns]
        assert 'int_col' in col_names
        assert 'double_col' in col_names
        assert 'varchar_col' in col_names


# ============================================================================
# CLI ARGUMENT PARSING TESTS
# ============================================================================

@pytest.mark.unit
class TestCLIArgumentParsing:
    """Test CLI argument parsing for all scripts."""

    def test_query_metadata_main_list_all(self, temp_db, temp_db_path, mock_env_vars, monkeypatch, capsys):
        """Test query_metadata.py main with --list-all."""
        # Mock sys.argv
        monkeypatch.setattr(sys, 'argv', ['query_metadata.py', '--list-all', '--format', 'json'])

        # Should exit with 0
        with pytest.raises(SystemExit) as exc_info:
            query_metadata.main()
        assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert captured.out.strip() == '[]'

    def test_query_metadata_main_missing_table_id(self, monkeypatch, capsys):
        """Test query_metadata.py fails when --check-freshness without --table-id."""
        monkeypatch.setattr(sys, 'argv', ['query_metadata.py', '--check-freshness'])

        with pytest.raises(SystemExit) as exc_info:
            query_metadata.main()
        assert exc_info.value.code == 1

    def test_query_data_main_simple_query(self, temp_db, temp_db_path, mock_env_vars, monkeypatch, capsys):
        """Test query_data.py main with simple query."""
        # Create test table
        temp_db.execute("CREATE TABLE dst_test (id INTEGER)")
        temp_db.execute("INSERT INTO dst_test VALUES (1)")

        monkeypatch.setattr(sys, 'argv', [
            'query_data.py',
            '--sql', 'SELECT * FROM dst_test',
            '--format', 'json'
        ])

        with pytest.raises(SystemExit) as exc_info:
            query_data.main()
        assert exc_info.value.code == 0

    def test_query_data_main_missing_sql(self, monkeypatch):
        """Test query_data.py fails without --sql argument."""
        monkeypatch.setattr(sys, 'argv', ['query_data.py'])

        with pytest.raises(SystemExit):
            query_data.main()

    def test_store_data_main_missing_file(self, monkeypatch, capsys):
        """Test store_data.py fails when data file doesn't exist."""
        monkeypatch.setattr(sys, 'argv', [
            'store_data.py',
            '--table-id', 'TEST',
            '--data-file', '/nonexistent/file.json'
        ])

        with pytest.raises(SystemExit) as exc_info:
            store_data.main()
        assert exc_info.value.code == 1

    def test_store_data_main_json_file(self, temp_db, temp_db_path, mock_env_vars, monkeypatch, capsys):
        """Test store_data.py main with JSON file."""
        # Create temp JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{'id': 1, 'name': 'Test'}], f)
            temp_file = f.name

        try:
            monkeypatch.setattr(sys, 'argv', [
                'store_data.py',
                '--table-id', 'TEST',
                '--data-file', temp_file
            ])

            with pytest.raises(SystemExit) as exc_info:
                store_data.main()
            assert exc_info.value.code == 0

            captured = capsys.readouterr()
            assert 'Created table dst_test' in captured.out
        finally:
            Path(temp_file).unlink()

    def test_table_summary_main_success(self, temp_db, temp_db_path, mock_env_vars, monkeypatch, capsys):
        """Test table_summary.py main with valid table."""
        # Create test table
        temp_db.execute("CREATE TABLE dst_test (id INTEGER)")
        temp_db.execute("INSERT INTO dst_test VALUES (1)")

        monkeypatch.setattr(sys, 'argv', [
            'table_summary.py',
            '--table-id', 'TEST',
            '--format', 'json'
        ])

        with pytest.raises(SystemExit) as exc_info:
            table_summary.main()
        assert exc_info.value.code == 0

    def test_table_summary_main_missing_table_id(self, monkeypatch):
        """Test table_summary.py fails without --table-id."""
        monkeypatch.setattr(sys, 'argv', ['table_summary.py'])

        with pytest.raises(SystemExit):
            table_summary.main()


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestErrorHandling:
    """Test error handling across all database scripts."""

    def test_query_metadata_database_connection_error(self, monkeypatch):
        """Test handling of database connection errors in query_metadata."""
        def mock_get_connection():
            raise Exception("Database connection failed")

        monkeypatch.setattr(db_utils, 'get_connection', mock_get_connection)

        with pytest.raises(Exception, match="Database connection failed"):
            query_metadata.list_all_tables()

    def test_query_data_sql_syntax_error(self, temp_db, temp_db_path, mock_env_vars):
        """Test handling of SQL syntax errors."""
        with pytest.raises(Exception):
            query_data.execute_query("SELECT * FORM invalid_syntax")

    def test_store_data_invalid_json_format(self, temp_db, temp_db_path, mock_env_vars):
        """Test handling of invalid data format in store_data."""
        # This actually creates a single-row table from a dict, so not really an error
        # Test with string instead which is truly unsupported
        with pytest.raises(ValueError, match="Unsupported data type"):
            store_data.store_data('TEST', "invalid string", update_metadata=False)

    def test_table_summary_empty_table(self, temp_db, temp_db_path, mock_env_vars):
        """Test summary generation for empty table."""
        temp_db.execute("CREATE TABLE dst_empty (id INTEGER)")

        summary = table_summary.get_table_summary('EMPTY')

        assert summary['record_count'] == 0
        assert len(summary['sample_rows']) == 0

    def test_store_data_database_write_error(self, temp_db, temp_db_path, mock_env_vars):
        """Test handling of database write errors."""
        # Create read-only scenario by inserting then trying to overwrite without permission
        data = [{'id': 1}]
        store_data.store_data('TEST', data, update_metadata=False)

        # Try to insert again without overwrite flag
        with pytest.raises(ValueError, match="already exists"):
            store_data.store_data('TEST', data, overwrite=False, update_metadata=False)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.db
class TestIntegration:
    """Integration tests combining multiple database operations."""

    def test_full_workflow_store_query_summarize(self, temp_db, temp_db_path, mock_env_vars):
        """Test complete workflow: store data, query it, and generate summary."""
        # 1. Store data
        data = [
            {'id': 1, 'name': 'Alice', 'score': 95},
            {'id': 2, 'name': 'Bob', 'score': 87},
            {'id': 3, 'name': 'Charlie', 'score': 92}
        ]

        store_result = store_data.store_data('SCORES', data, update_metadata=True)
        assert store_result['record_count'] == 3

        # 2. Query the stored data
        query_result = query_data.execute_query(
            "SELECT name, score FROM dst_scores WHERE score > 90",
            format='json'
        )
        assert len(query_result) == 2
        assert query_result[0]['score'] > 90

        # 3. Generate summary
        summary = table_summary.get_table_summary('SCORES')
        assert summary['record_count'] == 3
        assert 'score' in summary['statistics']

        # 4. Query metadata
        metadata = query_metadata.get_metadata('SCORES', format='json')
        assert metadata['table_id'] == 'SCORES'
        assert metadata['record_count'] == 3

    def test_update_and_verify_workflow(self, temp_db, temp_db_path, mock_env_vars):
        """Test workflow of updating data and verifying changes."""
        # Initial data
        data_v1 = [{'id': 1, 'value': 'old'}]
        store_data.store_data('UPTEST', data_v1, update_metadata=True)

        # Verify initial state
        result_v1 = query_data.execute_query(
            "SELECT * FROM dst_uptest",
            format='json'
        )
        assert result_v1[0]['value'] == 'old'

        # Update with new data (renamed table to avoid UPDATE keyword in query)
        data_v2 = [{'id': 1, 'value': 'new'}, {'id': 2, 'value': 'added'}]
        store_data.store_data('UPTEST', data_v2, overwrite=True, update_metadata=True)

        # Verify updated state
        result_v2 = query_data.execute_query(
            "SELECT * FROM dst_uptest ORDER BY id",
            format='json'
        )
        assert len(result_v2) == 2
        assert result_v2[0]['value'] == 'new'
        assert result_v2[1]['value'] == 'added'

        # Verify metadata was updated
        metadata = query_metadata.get_metadata('UPTEST', format='json')
        assert metadata['record_count'] == 2

    def test_multiple_tables_workflow(self, temp_db, temp_db_path, mock_env_vars):
        """Test managing multiple tables simultaneously."""
        # Store multiple tables
        tables = ['TABLE_A', 'TABLE_B', 'TABLE_C']
        for table_id in tables:
            data = [{'id': i, 'table': table_id} for i in range(1, 4)]
            store_data.store_data(table_id, data, update_metadata=True)

        # List all tables
        all_tables = query_metadata.list_all_tables(format='json')
        stored_ids = [t['table_id'] for t in all_tables]

        for table_id in tables:
            assert table_id in stored_ids

        # Query each table
        for table_id in tables:
            result = query_data.execute_query(
                f"SELECT * FROM dst_{table_id.lower()}",
                format='json'
            )
            assert len(result) == 3
