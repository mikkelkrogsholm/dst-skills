"""
Integration Tests for DST Skills Project

This module contains integration tests for the main workflow scripts:
- fetch_and_store.py: Complete fetch and store workflow
- init_db.py: Database initialization

These tests verify end-to-end workflows using real DuckDB databases
and mocked API calls.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pytest
import duckdb

# Add scripts to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "scripts"))

from fetch_and_store import (
    fetch_and_store,
    check_data_freshness,
    main as fetch_and_store_main
)
from db.init_db import (
    get_db_path,
    create_database_connection,
    create_metadata_table,
    verify_database_integrity,
    main as init_db_main
)


# ============================================================================
# Database Initialization Tests
# ============================================================================

@pytest.mark.integration
class TestDatabaseInitialization:
    """Test suite for database initialization script."""

    def test_get_db_path_from_env(self, mock_env_vars, temp_db_path):
        """Test database path retrieval from environment variable."""
        db_path = get_db_path()
        assert db_path == temp_db_path
        assert os.path.isabs(db_path)

    def test_get_db_path_default(self, monkeypatch):
        """Test database path uses default when env var not set."""
        monkeypatch.delenv("DUCKDB_PATH", raising=False)
        db_path = get_db_path()
        assert "dst_data.duckdb" in db_path

    def test_create_database_connection_success(self, temp_db_path):
        """Test successful database connection creation."""
        conn = create_database_connection(temp_db_path)
        assert conn is not None

        # Verify connection is working
        result = conn.execute("SELECT 1").fetchone()
        assert result[0] == 1

        conn.close()

    def test_create_database_connection_creates_directory(self, tmp_path):
        """Test that database connection creates parent directory if missing."""
        db_path = tmp_path / "new_dir" / "test.duckdb"

        # Directory should not exist yet
        assert not db_path.parent.exists()

        conn = create_database_connection(str(db_path))

        # Directory should now exist
        assert db_path.parent.exists()
        assert conn is not None

        conn.close()

    def test_create_metadata_table(self, temp_db):
        """Test metadata table creation."""
        result = create_metadata_table(temp_db)
        assert result is True

        # Verify table exists
        tables = temp_db.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name = 'dst_metadata'
        """).fetchall()

        assert len(tables) == 1
        assert tables[0][0] == "dst_metadata"

    def test_create_metadata_table_schema(self, temp_db):
        """Test metadata table has correct schema."""
        create_metadata_table(temp_db)

        # Get column information
        columns = temp_db.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'dst_metadata'
            ORDER BY ordinal_position
        """).fetchall()

        expected_columns = {
            'table_id': 'VARCHAR',
            'table_name': 'VARCHAR',
            'last_updated': 'TIMESTAMP',
            'fetch_timestamp': 'TIMESTAMP',
            'record_count': 'INTEGER',
            'columns_json': 'VARCHAR',
            'notes': 'VARCHAR'
        }

        assert len(columns) == len(expected_columns)

        for col_name, col_type in columns:
            assert col_name in expected_columns
            assert expected_columns[col_name] == col_type

    def test_create_metadata_table_idempotent(self, temp_db):
        """Test that creating metadata table multiple times is safe."""
        result1 = create_metadata_table(temp_db)
        result2 = create_metadata_table(temp_db)

        assert result1 is True
        assert result2 is True

        # Verify only one table exists
        count = temp_db.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'dst_metadata'
        """).fetchone()[0]

        assert count == 1

    def test_verify_database_integrity_success(self, temp_db):
        """Test database integrity verification passes for valid database."""
        create_metadata_table(temp_db)
        result = verify_database_integrity(temp_db)
        assert result is True

    def test_verify_database_integrity_missing_table(self, tmp_path):
        """Test database integrity verification fails when table missing."""
        # Create a fresh connection without the metadata table
        test_db_path = tmp_path / "empty_test.duckdb"

        conn = duckdb.connect(str(test_db_path))
        result = verify_database_integrity(conn)
        assert result is False
        conn.close()

    def test_init_db_main_success(self, mock_env_vars, temp_db_path, capsys):
        """Test full database initialization workflow."""
        # Run main initialization (it doesn't raise SystemExit on success)
        init_db_main()

        # Verify output
        captured = capsys.readouterr()
        assert "Database initialized successfully" in captured.out

        # Verify database was created
        assert os.path.exists(temp_db_path)

        # Verify table exists
        conn = duckdb.connect(temp_db_path)
        result = conn.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'dst_metadata'
        """).fetchone()[0]

        assert result == 1
        conn.close()


# ============================================================================
# Fetch and Store Integration Tests
# ============================================================================

@pytest.mark.integration
class TestFetchAndStoreIntegration:
    """Test suite for fetch and store workflow."""

    @pytest.fixture
    def mock_api_data(self):
        """Fixture providing mock API response data."""
        return [
            {"area": "000", "population": 5800000, "year": "2024"},
            {"area": "101", "population": 600000, "year": "2024"},
            {"area": "147", "population": 750000, "year": "2024"}
        ]

    @pytest.fixture
    def mock_table_info(self):
        """Fixture providing mock table info response."""
        return {
            "id": "FOLK1A",
            "text": "Population by Area",
            "updated": "2024-01-15T10:30:00",
            "unit": "number",
            "variables": [
                {"id": "OMRÅDE", "text": "area"},
                {"id": "TID", "text": "time"}
            ]
        }

    def test_check_data_freshness_no_data(self, temp_db):
        """Test freshness check when no data exists."""
        is_fresh, metadata = check_data_freshness(temp_db, "FOLK1A")

        assert is_fresh is False
        assert metadata is None

    def test_check_data_freshness_fresh_data(self, temp_db):
        """Test freshness check with fresh data."""
        # Insert fresh metadata
        timestamp = datetime.now().isoformat()
        temp_db.execute("""
            INSERT INTO dst_metadata
            (table_id, table_name, fetch_timestamp, record_count)
            VALUES (?, ?, ?, ?)
        """, ["FOLK1A", "Population", timestamp, 100])

        is_fresh, metadata = check_data_freshness(temp_db, "FOLK1A", max_age_days=30)

        assert is_fresh is True
        assert metadata is not None
        assert metadata['table_id'] == "FOLK1A"

    def test_check_data_freshness_stale_data(self, temp_db):
        """Test freshness check with stale data."""
        # Insert old metadata (60 days ago)
        old_timestamp = (datetime.now() - timedelta(days=60)).isoformat()
        temp_db.execute("""
            INSERT INTO dst_metadata
            (table_id, table_name, fetch_timestamp, record_count)
            VALUES (?, ?, ?, ?)
        """, ["FOLK1A", "Population", old_timestamp, 100])

        is_fresh, metadata = check_data_freshness(temp_db, "FOLK1A", max_age_days=30)

        assert is_fresh is False
        assert metadata is not None

    def test_check_data_freshness_no_timestamp(self, temp_db):
        """Test freshness check when metadata has no timestamp."""
        temp_db.execute("""
            INSERT INTO dst_metadata
            (table_id, table_name, record_count)
            VALUES (?, ?, ?)
        """, ["FOLK1A", "Population", 100])

        is_fresh, metadata = check_data_freshness(temp_db, "FOLK1A")

        assert is_fresh is False
        assert metadata is not None

    @patch('fetch_and_store.DSTAPIClient')
    @patch('fetch_and_store.fetch_data')
    def test_fetch_and_store_success(
        self,
        mock_fetch_data,
        mock_api_client_class,
        temp_db,
        mock_env_vars,
        mock_api_data,
        mock_table_info
    ):
        """Test successful fetch and store workflow."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.get_table_info.return_value = mock_table_info
        mock_api_client_class.return_value = mock_client

        mock_fetch_data.fetch_data.return_value = mock_api_data

        # Execute fetch and store
        result = fetch_and_store(
            table_id="FOLK1A",
            filters=None,
            overwrite=False
        )

        # Verify result
        assert result['status'] == 'success'
        assert result['table_id'] == 'FOLK1A'
        assert result['table_name'] == 'dst_folk1a'
        assert result['record_count'] == 3
        assert result['overwritten'] is False

        # Verify data was stored
        conn = duckdb.connect(os.getenv('DUCKDB_PATH'))
        count = conn.execute("SELECT COUNT(*) FROM dst_folk1a").fetchone()[0]
        assert count == 3

        # Verify metadata was updated
        metadata_count = conn.execute(
            "SELECT COUNT(*) FROM dst_metadata WHERE table_id = ?",
            ["FOLK1A"]
        ).fetchone()[0]
        assert metadata_count == 1

        conn.close()

    @patch('fetch_and_store.DSTAPIClient')
    @patch('fetch_and_store.fetch_data')
    def test_fetch_and_store_with_filters(
        self,
        mock_fetch_data,
        mock_api_client_class,
        temp_db,
        mock_env_vars,
        mock_table_info
    ):
        """Test fetch and store with filters applied."""
        # Setup mocks
        filtered_data = [{"area": "000", "population": 5800000, "year": "2024"}]

        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.get_table_info.return_value = mock_table_info
        mock_api_client_class.return_value = mock_client

        mock_fetch_data.fetch_data.return_value = filtered_data

        # Execute with filters
        filters = {"OMRÅDE": ["000"]}
        result = fetch_and_store(
            table_id="FOLK1A",
            filters=filters,
            overwrite=False
        )

        # Verify filters were passed
        mock_fetch_data.fetch_data.assert_called_once_with("FOLK1A", filters)

        assert result['status'] == 'success'
        assert result['record_count'] == 1

    @patch('fetch_and_store.DSTAPIClient')
    @patch('fetch_and_store.fetch_data')
    def test_fetch_and_store_overwrite(
        self,
        mock_fetch_data,
        mock_api_client_class,
        temp_db,
        mock_env_vars,
        mock_api_data,
        mock_table_info
    ):
        """Test fetch and store with overwrite flag."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.get_table_info.return_value = mock_table_info
        mock_api_client_class.return_value = mock_client

        mock_fetch_data.fetch_data.return_value = mock_api_data

        # First call - create table
        result1 = fetch_and_store(
            table_id="FOLK1A",
            overwrite=False
        )
        assert result1['overwritten'] is False

        # Second call - overwrite table
        result2 = fetch_and_store(
            table_id="FOLK1A",
            overwrite=True
        )

        assert result2['status'] == 'success'
        assert result2['overwritten'] is True
        assert result2['record_count'] == 3

    @patch('fetch_and_store.DSTAPIClient')
    @patch('fetch_and_store.fetch_data')
    def test_fetch_and_store_skip_if_fresh(
        self,
        mock_fetch_data,
        mock_api_client_class,
        temp_db,
        mock_env_vars,
        mock_api_data,
        mock_table_info
    ):
        """Test fetch and store skips when data is fresh."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.get_table_info.return_value = mock_table_info
        mock_api_client_class.return_value = mock_client

        mock_fetch_data.fetch_data.return_value = mock_api_data

        # First call - create data
        result1 = fetch_and_store(table_id="FOLK1A")
        assert result1['status'] == 'success'

        # Second call - should skip because data is fresh
        result2 = fetch_and_store(
            table_id="FOLK1A",
            skip_if_fresh=True,
            max_age_days=30
        )

        assert result2['status'] == 'skipped'
        assert result2['reason'] == 'data_is_fresh'
        assert result2['table_id'] == 'FOLK1A'

        # Verify fetch was only called once
        assert mock_fetch_data.fetch_data.call_count == 1

    @patch('fetch_and_store.DSTAPIClient')
    @patch('fetch_and_store.fetch_data')
    def test_fetch_and_store_metadata_update(
        self,
        mock_fetch_data,
        mock_api_client_class,
        temp_db,
        mock_env_vars,
        mock_api_data,
        mock_table_info
    ):
        """Test that metadata is properly updated during fetch and store."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.get_table_info.return_value = mock_table_info
        mock_api_client_class.return_value = mock_client

        mock_fetch_data.fetch_data.return_value = mock_api_data

        # Execute
        result = fetch_and_store(table_id="FOLK1A_META")

        # Verify metadata was updated
        conn = duckdb.connect(os.getenv('DUCKDB_PATH'))
        metadata = conn.execute("""
            SELECT table_id, table_name, last_updated, fetch_timestamp, record_count
            FROM dst_metadata
            WHERE table_id = ?
        """, ["FOLK1A_META"]).fetchone()

        assert metadata is not None
        assert metadata[0] == "FOLK1A_META"
        assert metadata[1] == "Population by Area"
        # last_updated may be converted to datetime object by DuckDB
        assert str(metadata[2]).startswith("2024-01-15")
        assert metadata[3] is not None  # fetch_timestamp
        assert metadata[4] == 3  # record_count

        conn.close()

    @patch('fetch_and_store.DSTAPIClient')
    @patch('fetch_and_store.fetch_data')
    def test_fetch_and_store_api_failure(
        self,
        mock_fetch_data,
        mock_api_client_class,
        mock_env_vars
    ):
        """Test fetch and store handles API failures gracefully."""
        # Setup mocks to raise exception
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.get_table_info.side_effect = Exception("API connection failed")
        mock_api_client_class.return_value = mock_client

        # Execute and expect exception
        with pytest.raises(Exception) as exc_info:
            fetch_and_store(table_id="FOLK1A")

        assert "API connection failed" in str(exc_info.value)

    @patch('fetch_and_store.DSTAPIClient')
    @patch('fetch_and_store.fetch_data')
    def test_fetch_and_store_empty_data(
        self,
        mock_fetch_data,
        mock_api_client_class,
        mock_env_vars,
        mock_table_info
    ):
        """Test fetch and store handles empty data gracefully."""
        # Setup mocks with empty data
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.get_table_info.return_value = mock_table_info
        mock_api_client_class.return_value = mock_client

        mock_fetch_data.fetch_data.return_value = []

        # Execute and expect exception
        with pytest.raises(ValueError) as exc_info:
            fetch_and_store(table_id="FOLK1A_EMPTY")

        assert "Cannot store empty data" in str(exc_info.value)


# ============================================================================
# CLI Argument Tests
# ============================================================================

@pytest.mark.integration
class TestFetchAndStoreCLI:
    """Test suite for fetch_and_store CLI interface."""

    @patch('fetch_and_store.fetch_and_store')
    def test_cli_basic_args(self, mock_fetch_and_store):
        """Test CLI with basic arguments."""
        mock_fetch_and_store.return_value = {
            'status': 'success',
            'table_id': 'FOLK1A',
            'table_name': 'dst_folk1a',
            'record_count': 100,
            'overwritten': False
        }

        test_args = ['fetch_and_store.py', '--table-id', 'FOLK1A']

        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                fetch_and_store_main()

            assert exc_info.value.code == 0
            mock_fetch_and_store.assert_called_once_with(
                table_id='FOLK1A',
                filters=None,
                overwrite=False,
                skip_if_fresh=False,
                max_age_days=30
            )

    @patch('fetch_and_store.fetch_and_store')
    def test_cli_with_filters(self, mock_fetch_and_store):
        """Test CLI with JSON filters."""
        mock_fetch_and_store.return_value = {
            'status': 'success',
            'table_id': 'FOLK1A',
            'table_name': 'dst_folk1a',
            'record_count': 100,
            'overwritten': False
        }

        filters_json = '{"OMRÅDE":["000"]}'
        test_args = [
            'fetch_and_store.py',
            '--table-id', 'FOLK1A',
            '--filters', filters_json
        ]

        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                fetch_and_store_main()

            assert exc_info.value.code == 0
            call_args = mock_fetch_and_store.call_args
            assert call_args[1]['filters'] == {"OMRÅDE": ["000"]}

    @patch('fetch_and_store.fetch_and_store')
    def test_cli_with_overwrite(self, mock_fetch_and_store):
        """Test CLI with overwrite flag."""
        mock_fetch_and_store.return_value = {
            'status': 'success',
            'table_id': 'FOLK1A',
            'table_name': 'dst_folk1a',
            'record_count': 100,
            'overwritten': True
        }

        test_args = [
            'fetch_and_store.py',
            '--table-id', 'FOLK1A',
            '--overwrite'
        ]

        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                fetch_and_store_main()

            assert exc_info.value.code == 0
            call_args = mock_fetch_and_store.call_args
            assert call_args[1]['overwrite'] is True

    @patch('fetch_and_store.fetch_and_store')
    def test_cli_skip_if_fresh(self, mock_fetch_and_store):
        """Test CLI with skip-if-fresh option."""
        mock_fetch_and_store.return_value = {
            'status': 'skipped',
            'reason': 'data_is_fresh',
            'table_id': 'FOLK1A'
        }

        test_args = [
            'fetch_and_store.py',
            '--table-id', 'FOLK1A',
            '--skip-if-fresh',
            '--max-age-days', '7'
        ]

        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                fetch_and_store_main()

            assert exc_info.value.code == 2  # Exit code 2 for skipped
            call_args = mock_fetch_and_store.call_args
            assert call_args[1]['skip_if_fresh'] is True
            assert call_args[1]['max_age_days'] == 7

    def test_cli_invalid_json_filters(self):
        """Test CLI with invalid JSON filters."""
        test_args = [
            'fetch_and_store.py',
            '--table-id', 'FOLK1A',
            '--filters', 'invalid-json{'
        ]

        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                fetch_and_store_main()

            assert exc_info.value.code == 1

    @patch('fetch_and_store.fetch_and_store')
    def test_cli_error_handling(self, mock_fetch_and_store):
        """Test CLI error handling."""
        mock_fetch_and_store.side_effect = Exception("Database connection failed")

        test_args = ['fetch_and_store.py', '--table-id', 'FOLK1A']

        with patch('sys.argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                fetch_and_store_main()

            assert exc_info.value.code == 1


# ============================================================================
# End-to-End Workflow Tests
# ============================================================================

@pytest.mark.integration
class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""

    @patch('fetch_and_store.DSTAPIClient')
    @patch('fetch_and_store.fetch_data')
    def test_complete_workflow_init_fetch_store(
        self,
        mock_fetch_data,
        mock_api_client_class,
        mock_env_vars,
        temp_db_path
    ):
        """Test complete workflow: initialize DB, fetch data, store data."""
        # Step 1: Initialize database
        conn = create_database_connection(temp_db_path)
        create_metadata_table(conn)
        assert verify_database_integrity(conn) is True
        conn.close()

        # Step 2: Setup mocks for fetch and store
        mock_data = [
            {"region": "DK", "value": 100},
            {"region": "EU", "value": 200}
        ]
        mock_info = {
            "id": "TEST1",
            "text": "Test Table",
            "updated": "2024-01-01T00:00:00"
        }

        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_client.get_table_info.return_value = mock_info
        mock_api_client_class.return_value = mock_client

        mock_fetch_data.fetch_data.return_value = mock_data

        # Step 3: Fetch and store data
        result = fetch_and_store(table_id="TEST1")

        assert result['status'] == 'success'
        assert result['record_count'] == 2

        # Step 4: Verify data is queryable
        conn = duckdb.connect(temp_db_path)

        # Check data table
        data = conn.execute("SELECT * FROM dst_test1").fetchall()
        assert len(data) == 2

        # Check metadata
        metadata = conn.execute(
            "SELECT * FROM dst_metadata WHERE table_id = ?",
            ["TEST1"]
        ).fetchone()
        assert metadata is not None

        conn.close()

    @patch('fetch_and_store.DSTAPIClient')
    @patch('fetch_and_store.fetch_data')
    def test_workflow_multiple_tables(
        self,
        mock_fetch_data,
        mock_api_client_class,
        mock_env_vars,
        tmp_path
    ):
        """Test storing multiple tables in the same database."""
        # Create a fresh database for this test
        fresh_db_path = tmp_path / "multi_table_test.duckdb"

        # Override the environment variable for this test
        os.environ['DUCKDB_PATH'] = str(fresh_db_path)

        # Initialize database
        conn = create_database_connection(str(fresh_db_path))
        create_metadata_table(conn)
        conn.close()

        # Setup mocks
        mock_client = MagicMock()
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)
        mock_api_client_class.return_value = mock_client

        # Store first table
        mock_client.get_table_info.return_value = {
            "id": "TABLE1",
            "text": "Table One",
            "updated": "2024-01-01T00:00:00"
        }
        mock_fetch_data.fetch_data.return_value = [{"col1": "a", "col2": 1}]

        result1 = fetch_and_store(table_id="TABLE1")
        assert result1['status'] == 'success'

        # Store second table
        mock_client.get_table_info.return_value = {
            "id": "TABLE2",
            "text": "Table Two",
            "updated": "2024-01-01T00:00:00"
        }
        mock_fetch_data.fetch_data.return_value = [{"col3": "b", "col4": 2}]

        result2 = fetch_and_store(table_id="TABLE2")
        assert result2['status'] == 'success'

        # Verify both tables exist
        conn = duckdb.connect(str(fresh_db_path))

        tables = conn.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name LIKE 'dst_%'
        """).fetchall()

        table_names = [t[0] for t in tables]
        assert 'dst_table1' in table_names
        assert 'dst_table2' in table_names

        # Verify metadata for both tables
        metadata_count = conn.execute(
            "SELECT COUNT(*) FROM dst_metadata"
        ).fetchone()[0]
        assert metadata_count == 2

        conn.close()
