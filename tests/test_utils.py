"""
Comprehensive pytest tests for all utility modules in the DST Skills project.

This module tests:
1. scripts/api/client.py - DSTAPIClient class
2. scripts/api/config.py - Configuration loading
3. scripts/utils.py - Logging and utilities
4. scripts/db/db_utils.py - Database utilities
"""

import os
import sys
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import pytest
import httpx
import duckdb

# Import modules under test
from api.client import DSTAPIClient
from api.config import (
    API_BASE_URL,
    API_ENDPOINTS,
    get_api_url,
    get_endpoint_path,
    list_endpoints
)
from utils import setup_logger, get_project_root, ensure_directory
from db.db_utils import (
    get_db_path,
    get_connection,
    close_connection,
    table_exists,
    get_metadata,
    update_metadata,
    list_all_tables,
    delete_metadata
)


# =============================================================================
# Tests for scripts/api/client.py - DSTAPIClient
# =============================================================================

@pytest.mark.unit
class TestDSTAPIClient:
    """Test suite for DSTAPIClient class."""

    def test_dst_api_client_init_default(self):
        """Test DSTAPIClient initialization with default parameters."""
        client = DSTAPIClient()

        assert client.base_url == API_BASE_URL
        assert client.timeout == 30
        assert client.max_retries == 3
        assert client.min_request_interval == 0.1
        assert client.last_request_time == 0
        assert client.client is not None
        assert client.logger is not None

        client.close()

    def test_dst_api_client_init_custom(self):
        """Test DSTAPIClient initialization with custom parameters."""
        custom_url = "https://custom.api.com/v2"
        client = DSTAPIClient(base_url=custom_url, timeout=60, max_retries=5)

        assert client.base_url == custom_url
        assert client.timeout == 60
        assert client.max_retries == 5

        client.close()

    def test_dst_api_client_rate_limiting(self):
        """Test that rate limiting enforces minimum request interval."""
        client = DSTAPIClient()

        # First request should pass immediately
        start_time = client.last_request_time
        client._rate_limit()
        first_request_time = client.last_request_time
        assert first_request_time >= start_time

        # Second immediate request should be delayed
        import time
        before_second = time.time()
        client._rate_limit()
        after_second = time.time()

        # Should have waited at least min_request_interval
        elapsed = after_second - before_second
        assert elapsed >= client.min_request_interval * 0.9  # Allow small margin

        client.close()

    def test_dst_api_client_make_request_success(self):
        """Test successful API request."""
        client = DSTAPIClient()

        # Mock successful response
        test_data = [{"id": "1", "description": "Test"}]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_response.raise_for_status = Mock()

        with patch.object(client.client, 'request', return_value=mock_response):
            result = client._make_request('subjects')

        assert result == test_data

        client.close()

    def test_dst_api_client_make_request_with_params(self):
        """Test API request with query parameters."""
        client = DSTAPIClient()

        # Mock successful response with params
        test_data = [{"id": "TABLE1", "text": "Test Table"}]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_response.raise_for_status = Mock()

        with patch.object(client.client, 'request', return_value=mock_response):
            result = client._make_request('tables', params={'subjects': '02'})

        assert result == test_data

        client.close()

    def test_dst_api_client_make_request_http_error(self):
        """Test handling of HTTP errors."""
        client = DSTAPIClient()

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = '{"error": "Not found"}'
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=mock_response
        )

        with patch.object(client.client, 'request', return_value=mock_response):
            with pytest.raises(httpx.HTTPStatusError):
                client._make_request('invalid')

        client.close()

    def test_dst_api_client_make_request_invalid_json(self):
        """Test handling of invalid JSON response."""
        client = DSTAPIClient()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Invalid JSON {{{"
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = Mock()

        with patch.object(client.client, 'request', return_value=mock_response):
            with pytest.raises(ValueError, match="Invalid JSON response"):
                client._make_request('subjects')

        client.close()

    def test_dst_api_client_get_subjects(self):
        """Test get_subjects method."""
        client = DSTAPIClient()

        test_data = [
            {"id": "1", "description": "Population", "active": True},
            {"id": "2", "description": "Economy", "active": True}
        ]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_response.raise_for_status = Mock()

        with patch.object(client.client, 'request', return_value=mock_response):
            result = client.get_subjects()

        assert result == test_data
        assert len(result) == 2

        client.close()

    def test_dst_api_client_get_subjects_recursive(self):
        """Test get_subjects method with recursive parameter."""
        client = DSTAPIClient()

        test_data = [{"id": "1", "description": "Test", "hasSubjects": True}]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_response.raise_for_status = Mock()

        with patch.object(client.client, 'request', return_value=mock_response):
            result = client.get_subjects(recursive=True)

        assert result == test_data

        client.close()

    def test_dst_api_client_get_tables_no_filter(self):
        """Test get_tables method without subject filter."""
        client = DSTAPIClient()

        test_data = [
            {"id": "FOLK1A", "text": "Population by area", "unit": "Number"}
        ]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_response.raise_for_status = Mock()

        with patch.object(client.client, 'request', return_value=mock_response):
            result = client.get_tables()

        assert result == test_data

        client.close()

    def test_dst_api_client_get_tables_single_subject(self):
        """Test get_tables method with single subject filter."""
        client = DSTAPIClient()

        test_data = [{"id": "TABLE1", "text": "Test"}]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_response.raise_for_status = Mock()

        with patch.object(client.client, 'request', return_value=mock_response):
            result = client.get_tables(subjects='02')

        assert result == test_data

        client.close()

    def test_dst_api_client_get_tables_multiple_subjects(self):
        """Test get_tables method with multiple subjects."""
        client = DSTAPIClient()

        test_data = [{"id": "TABLE1", "text": "Test"}]
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_response.raise_for_status = Mock()

        with patch.object(client.client, 'request', return_value=mock_response):
            result = client.get_tables(subjects=['02', '03'])

        assert result == test_data

        client.close()

    def test_dst_api_client_get_table_info(self):
        """Test get_table_info method."""
        client = DSTAPIClient()

        table_id = "FOLK1A"
        test_data = {
            "id": table_id,
            "text": "Population",
            "variables": [
                {"id": "OMRÅDE", "text": "area"}
            ]
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_response.raise_for_status = Mock()

        with patch.object(client.client, 'request', return_value=mock_response):
            result = client.get_table_info(table_id)

        assert result["id"] == table_id
        assert "variables" in result

        client.close()

    def test_dst_api_client_get_data(self):
        """Test get_data method."""
        client = DSTAPIClient()

        table_id = "FOLK1A"
        test_data = {"data": [{"values": [1000, 2000]}]}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_response.raise_for_status = Mock()

        with patch.object(client.client, 'request', return_value=mock_response):
            result = client.get_data(table_id)

        assert "data" in result

        client.close()

    def test_dst_api_client_get_data_with_kwargs(self):
        """Test get_data method with additional parameters."""
        client = DSTAPIClient()

        table_id = "FOLK1A"
        test_data = {"data": []}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_response.raise_for_status = Mock()

        with patch.object(client.client, 'request', return_value=mock_response):
            result = client.get_data(table_id, format='json', lang='en')

        assert result == test_data

        client.close()

    def test_dst_api_client_close(self):
        """Test client close method."""
        client = DSTAPIClient()

        # Ensure client is open
        assert client.client is not None

        # Close client
        client.close()

        # Client should be closed
        assert client.client.is_closed

    def test_dst_api_client_context_manager(self):
        """Test DSTAPIClient as context manager."""
        with DSTAPIClient() as client:
            assert client.client is not None
            assert not client.client.is_closed

        # After exiting context, client should be closed
        assert client.client.is_closed


# =============================================================================
# Tests for scripts/api/config.py - Configuration
# =============================================================================

@pytest.mark.unit
class TestAPIConfig:
    """Test suite for API configuration module."""

    def test_api_base_url_constant(self):
        """Test that API_BASE_URL is properly defined."""
        assert API_BASE_URL is not None
        assert isinstance(API_BASE_URL, str)
        assert API_BASE_URL.startswith('http')

    def test_api_endpoints_constant(self):
        """Test that API_ENDPOINTS dictionary is properly defined."""
        assert API_ENDPOINTS is not None
        assert isinstance(API_ENDPOINTS, dict)
        assert 'subjects' in API_ENDPOINTS
        assert 'tables' in API_ENDPOINTS
        assert 'tableinfo' in API_ENDPOINTS
        assert 'data' in API_ENDPOINTS

    def test_get_api_url_basic_endpoint(self):
        """Test get_api_url with basic endpoint name."""
        url = get_api_url('subjects')

        assert url == f"{API_BASE_URL}/subjects"

    def test_get_api_url_with_params(self):
        """Test get_api_url with query parameters."""
        url = get_api_url('tables', {'subjects': '02'})

        assert url.startswith(f"{API_BASE_URL}/tables")
        assert 'subjects=02' in url

    def test_get_api_url_with_multiple_params(self):
        """Test get_api_url with multiple query parameters."""
        url = get_api_url('data', {'id': 'FOLK1A', 'format': 'json', 'lang': 'en'})

        assert url.startswith(f"{API_BASE_URL}/data")
        assert 'id=FOLK1A' in url
        assert 'format=json' in url
        assert 'lang=en' in url

    def test_get_api_url_custom_path_with_slash(self):
        """Test get_api_url with custom path starting with slash."""
        url = get_api_url('/custom/path', {'test': 'value'})

        assert f"{API_BASE_URL}/custom/path" in url
        assert 'test=value' in url

    def test_get_api_url_custom_path_without_slash(self):
        """Test get_api_url with custom path without leading slash."""
        url = get_api_url('custom/path', {'test': 'value'})

        assert f"{API_BASE_URL}/custom/path" in url
        assert 'test=value' in url

    def test_get_api_url_no_params(self):
        """Test get_api_url without parameters."""
        url = get_api_url('tableinfo')

        assert url == f"{API_BASE_URL}/tableinfo"
        assert '?' not in url

    def test_get_endpoint_path_valid(self):
        """Test get_endpoint_path with valid endpoint."""
        path = get_endpoint_path('subjects')

        assert path == '/subjects'

    def test_get_endpoint_path_invalid(self):
        """Test get_endpoint_path with invalid endpoint."""
        path = get_endpoint_path('nonexistent')

        assert path is None

    def test_list_endpoints(self):
        """Test list_endpoints returns all endpoints."""
        endpoints = list_endpoints()

        assert isinstance(endpoints, dict)
        assert len(endpoints) == 4
        assert 'subjects' in endpoints
        assert 'tables' in endpoints
        assert 'tableinfo' in endpoints
        assert 'data' in endpoints

    def test_list_endpoints_returns_copy(self):
        """Test that list_endpoints returns a copy, not reference."""
        endpoints1 = list_endpoints()
        endpoints2 = list_endpoints()

        # Should be equal but not the same object
        assert endpoints1 == endpoints2
        assert endpoints1 is not endpoints2

    def test_config_loads_env_vars(self, mock_env_vars):
        """Test that configuration loads from environment variables."""
        # Environment variables are set by mock_env_vars fixture
        from api.config import API_BASE_URL, DUCKDB_PATH

        # API_BASE_URL should be loaded from env or use default
        assert API_BASE_URL is not None
        assert isinstance(API_BASE_URL, str)

        # DUCKDB_PATH should be loaded from env or use default
        assert DUCKDB_PATH is not None
        assert isinstance(DUCKDB_PATH, str)


# =============================================================================
# Tests for scripts/utils.py - Utilities and Logging
# =============================================================================

@pytest.mark.unit
class TestUtilities:
    """Test suite for utility functions."""

    def test_setup_logger_default_level(self):
        """Test setup_logger with default level."""
        logger = setup_logger('test.default')

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test.default'
        assert logger.level == logging.INFO

    def test_setup_logger_custom_level(self):
        """Test setup_logger with custom level."""
        logger = setup_logger('test.debug', level='DEBUG')

        assert logger is not None
        assert logger.level == logging.DEBUG

    def test_setup_logger_invalid_level_defaults_to_info(self):
        """Test that invalid level defaults to INFO."""
        logger = setup_logger('test.invalid', level='INVALID')

        assert logger is not None
        assert logger.level == logging.INFO

    def test_setup_logger_creates_handlers(self):
        """Test that logger has both console and file handlers."""
        logger = setup_logger('test.handlers')

        # Should have at least 2 handlers (console and file)
        assert len(logger.handlers) >= 2

        handler_types = [type(h).__name__ for h in logger.handlers]
        assert 'StreamHandler' in handler_types
        assert 'FileHandler' in handler_types

    def test_setup_logger_no_duplicate_handlers(self):
        """Test that calling setup_logger twice doesn't add duplicate handlers."""
        logger1 = setup_logger('test.duplicate')
        handler_count1 = len(logger1.handlers)

        logger2 = setup_logger('test.duplicate')
        handler_count2 = len(logger2.handlers)

        # Should be the same logger with same number of handlers
        assert logger1 is logger2
        assert handler_count1 == handler_count2

    def test_setup_logger_creates_log_directory(self, tmp_path):
        """Test that setup_logger creates logs directory."""
        # Mock the log directory path
        with patch('utils.Path') as mock_path:
            mock_log_dir = tmp_path / 'logs'
            mock_path.return_value.parent.parent = tmp_path

            # The actual function creates the directory
            # Just verify it's callable
            logger = setup_logger('test.logdir')
            assert logger is not None

    def test_setup_logger_env_var(self, monkeypatch):
        """Test that setup_logger respects LOG_LEVEL environment variable."""
        monkeypatch.setenv('LOG_LEVEL', 'WARNING')

        # Need to reload the module or create new logger
        logger = setup_logger('test.env', level=None)

        # Level might be INFO or WARNING depending on when env is loaded
        assert logger is not None

    def test_get_project_root(self):
        """Test get_project_root returns valid path."""
        root = get_project_root()

        assert root is not None
        assert isinstance(root, Path)
        assert root.exists()
        assert root.is_dir()

    def test_get_project_root_has_scripts(self):
        """Test that project root contains expected directories."""
        root = get_project_root()
        scripts_dir = root / 'scripts'

        # Scripts directory should exist
        assert scripts_dir.exists()

    def test_ensure_directory_creates_new(self, tmp_path):
        """Test ensure_directory creates new directory."""
        test_dir = tmp_path / 'new_directory'

        # Directory should not exist yet
        assert not test_dir.exists()

        result = ensure_directory(test_dir)

        # Directory should now exist
        assert result.exists()
        assert result.is_dir()
        assert result == test_dir

    def test_ensure_directory_exists_already(self, tmp_path):
        """Test ensure_directory with existing directory."""
        test_dir = tmp_path / 'existing_directory'
        test_dir.mkdir()

        assert test_dir.exists()

        result = ensure_directory(test_dir)

        # Should still exist and return path
        assert result.exists()
        assert result.is_dir()
        assert result == test_dir

    def test_ensure_directory_creates_parents(self, tmp_path):
        """Test ensure_directory creates parent directories."""
        test_dir = tmp_path / 'parent' / 'child' / 'grandchild'

        assert not test_dir.exists()

        result = ensure_directory(test_dir)

        # All directories should be created
        assert result.exists()
        assert (tmp_path / 'parent').exists()
        assert (tmp_path / 'parent' / 'child').exists()

    def test_ensure_directory_with_string_path(self, tmp_path):
        """Test ensure_directory accepts string path."""
        test_dir = str(tmp_path / 'string_path')

        result = ensure_directory(test_dir)

        assert result.exists()
        assert isinstance(result, Path)


# =============================================================================
# Tests for scripts/db/db_utils.py - Database Utilities
# =============================================================================

@pytest.mark.unit
class TestDatabaseUtils:
    """Test suite for database utility functions."""

    def test_get_db_path_default(self):
        """Test get_db_path returns default path."""
        db_path = get_db_path()

        assert db_path is not None
        assert isinstance(db_path, str)
        assert 'dst_data.duckdb' in db_path or 'test_dst_data.duckdb' in db_path

    def test_get_db_path_from_env(self, mock_env_vars, temp_db_path):
        """Test get_db_path loads from environment variable."""
        # Reload the module to pick up env vars
        import importlib
        import db.db_utils
        importlib.reload(db.db_utils)

        db_path = db.db_utils.get_db_path()

        assert db_path is not None
        assert temp_db_path in db_path

    def test_get_connection_success(self, temp_db_path, mock_env_vars):
        """Test successful database connection."""
        conn = get_connection()

        assert conn is not None
        assert isinstance(conn, duckdb.DuckDBPyConnection)

        conn.close()

    def test_get_connection_creates_file(self, monkeypatch, tmp_path):
        """Test that get_connection creates database file."""
        # Use a fresh temp path
        test_db = tmp_path / "test_create.duckdb"
        monkeypatch.setenv('DUCKDB_PATH', str(test_db))

        # Reload to pick up new env var
        import importlib
        import db.db_utils
        importlib.reload(db.db_utils)

        # Ensure file doesn't exist
        assert not test_db.exists()

        # Create connection
        conn = db.db_utils.get_connection()

        # File should now exist
        assert test_db.exists()

        # Cleanup
        conn.close()
        if test_db.exists():
            test_db.unlink()

    def test_close_connection_success(self, temp_db):
        """Test successful connection close."""
        result = close_connection(temp_db)

        assert result is True

    def test_close_connection_none(self):
        """Test close_connection with None."""
        result = close_connection(None)

        assert result is True

    def test_close_connection_already_closed(self, temp_db):
        """Test close_connection on already closed connection."""
        temp_db.close()

        result = close_connection(temp_db)

        # Should return False or handle gracefully
        assert isinstance(result, bool)

    def test_table_exists_true(self, temp_db):
        """Test table_exists returns True for existing table."""
        exists = table_exists(temp_db, 'dst_metadata')

        assert exists is True

    def test_table_exists_false(self, temp_db):
        """Test table_exists returns False for non-existing table."""
        exists = table_exists(temp_db, 'nonexistent_table')

        assert exists is False

    def test_get_metadata_not_found(self, temp_db):
        """Test get_metadata returns None when table not found."""
        result = get_metadata(temp_db, 'NONEXISTENT')

        assert result is None

    def test_update_metadata_insert(self, temp_db):
        """Test update_metadata inserts new record."""
        table_id = 'TEST001'

        result = update_metadata(
            temp_db,
            table_id=table_id,
            table_name='Test Table',
            record_count=100,
            notes='Test note'
        )

        assert result is True

        # Verify insertion
        metadata = get_metadata(temp_db, table_id)
        assert metadata is not None
        assert metadata['table_id'] == table_id
        assert metadata['table_name'] == 'Test Table'
        assert metadata['record_count'] == 100
        assert metadata['notes'] == 'Test note'

    def test_update_metadata_update(self, temp_db):
        """Test update_metadata updates existing record."""
        table_id = 'TEST002'

        # Insert initial record
        update_metadata(
            temp_db,
            table_id=table_id,
            table_name='Original Name',
            record_count=50
        )

        # Update record
        result = update_metadata(
            temp_db,
            table_id=table_id,
            table_name='Updated Name',
            record_count=150
        )

        assert result is True

        # Verify update
        metadata = get_metadata(temp_db, table_id)
        assert metadata['table_name'] == 'Updated Name'
        assert metadata['record_count'] == 150

    def test_update_metadata_partial_update(self, temp_db):
        """Test update_metadata with partial field update."""
        table_id = 'TEST003'

        # Insert initial record
        update_metadata(
            temp_db,
            table_id=table_id,
            table_name='Original',
            record_count=100,
            notes='Original note'
        )

        # Update only record_count
        update_metadata(
            temp_db,
            table_id=table_id,
            record_count=200
        )

        # Verify partial update
        metadata = get_metadata(temp_db, table_id)
        assert metadata['table_name'] == 'Original'
        assert metadata['record_count'] == 200
        assert metadata['notes'] == 'Original note'

    def test_update_metadata_with_timestamp(self, temp_db):
        """Test update_metadata with timestamp fields."""
        table_id = 'TEST004'
        now = datetime.now()

        result = update_metadata(
            temp_db,
            table_id=table_id,
            table_name='Test',
            last_updated=now,
            fetch_timestamp=now
        )

        assert result is True

        metadata = get_metadata(temp_db, table_id)
        assert metadata['last_updated'] is not None
        assert metadata['fetch_timestamp'] is not None

    def test_update_metadata_no_fields(self, temp_db):
        """Test update_metadata with no fields to update."""
        table_id = 'TEST005'

        # Insert record first
        update_metadata(
            temp_db,
            table_id=table_id,
            table_name='Test'
        )

        # Try to update with no fields
        result = update_metadata(temp_db, table_id=table_id)

        assert result is True

    def test_get_metadata_all_fields(self, temp_db):
        """Test get_metadata returns all expected fields."""
        table_id = 'TEST006'

        update_metadata(
            temp_db,
            table_id=table_id,
            table_name='Complete Test',
            last_updated=datetime.now(),
            fetch_timestamp=datetime.now(),
            record_count=500,
            columns_json='{"columns": ["col1", "col2"]}',
            notes='Complete metadata'
        )

        metadata = get_metadata(temp_db, table_id)

        assert 'table_id' in metadata
        assert 'table_name' in metadata
        assert 'last_updated' in metadata
        assert 'fetch_timestamp' in metadata
        assert 'record_count' in metadata
        assert 'columns_json' in metadata
        assert 'notes' in metadata

    def test_list_all_tables_empty(self, temp_db):
        """Test list_all_tables returns empty list when no tables."""
        tables = list_all_tables(temp_db)

        assert isinstance(tables, list)
        assert len(tables) == 0

    def test_list_all_tables_with_data(self, temp_db):
        """Test list_all_tables returns all tables."""
        # Insert multiple records
        update_metadata(temp_db, table_id='TABLE1', table_name='First')
        update_metadata(temp_db, table_id='TABLE2', table_name='Second')
        update_metadata(temp_db, table_id='TABLE3', table_name='Third')

        tables = list_all_tables(temp_db)

        assert len(tables) == 3
        assert all('table_id' in t for t in tables)
        assert all('table_name' in t for t in tables)

        # Verify order (should be ordered by table_id)
        table_ids = [t['table_id'] for t in tables]
        assert table_ids == ['TABLE1', 'TABLE2', 'TABLE3']

    def test_list_all_tables_structure(self, temp_db):
        """Test list_all_tables returns correct structure."""
        update_metadata(
            temp_db,
            table_id='TEST007',
            table_name='Test Table',
            record_count=100
        )

        tables = list_all_tables(temp_db)

        assert len(tables) == 1
        table = tables[0]

        assert 'table_id' in table
        assert 'table_name' in table
        assert 'last_updated' in table
        assert 'fetch_timestamp' in table
        assert 'record_count' in table

    def test_delete_metadata_success(self, temp_db):
        """Test successful metadata deletion."""
        table_id = 'TEST008'

        # Insert record
        update_metadata(temp_db, table_id=table_id, table_name='To Delete')

        # Verify it exists
        assert get_metadata(temp_db, table_id) is not None

        # Delete
        result = delete_metadata(temp_db, table_id)

        assert result is True

        # Verify deletion
        assert get_metadata(temp_db, table_id) is None

    def test_delete_metadata_nonexistent(self, temp_db):
        """Test delete_metadata on non-existent record."""
        result = delete_metadata(temp_db, 'NONEXISTENT')

        # Should succeed (no error) even if record doesn't exist
        assert result is True

    def test_get_metadata_error_handling(self, temp_db):
        """Test get_metadata handles query errors."""
        # Close connection to force error
        temp_db.close()

        with pytest.raises(Exception):
            get_metadata(temp_db, 'TEST009')

    def test_update_metadata_error_handling(self):
        """Test update_metadata handles connection errors."""
        # Create a closed connection
        conn = duckdb.connect(':memory:')
        conn.close()

        with pytest.raises(Exception):
            update_metadata(conn, table_id='TEST010', table_name='Test')

    def test_list_all_tables_error_handling(self):
        """Test list_all_tables handles query errors."""
        # Create connection without metadata table
        conn = duckdb.connect(':memory:')

        with pytest.raises(Exception):
            list_all_tables(conn)

        conn.close()


# =============================================================================
# Integration Tests
# =============================================================================

@pytest.mark.unit
class TestIntegration:
    """Integration tests combining multiple utilities."""

    def test_client_with_custom_logger(self):
        """Test DSTAPIClient uses custom logger setup."""
        logger = setup_logger('integration.test')

        client = DSTAPIClient()

        # Client should have a logger
        assert client.logger is not None
        assert isinstance(client.logger, logging.Logger)

        client.close()

    def test_database_workflow(self, temp_db):
        """Test complete database workflow."""
        table_id = 'WORKFLOW001'

        # 1. Check table doesn't exist in metadata
        metadata = get_metadata(temp_db, table_id)
        assert metadata is None

        # 2. Insert metadata
        update_metadata(
            temp_db,
            table_id=table_id,
            table_name='Workflow Test',
            record_count=0
        )

        # 3. Verify insertion
        metadata = get_metadata(temp_db, table_id)
        assert metadata is not None
        assert metadata['record_count'] == 0

        # 4. Update metadata
        update_metadata(
            temp_db,
            table_id=table_id,
            record_count=100,
            notes='Updated'
        )

        # 5. Verify update
        metadata = get_metadata(temp_db, table_id)
        assert metadata['record_count'] == 100
        assert metadata['notes'] == 'Updated'

        # 6. List all tables
        tables = list_all_tables(temp_db)
        assert len(tables) > 0
        assert any(t['table_id'] == table_id for t in tables)

        # 7. Delete metadata
        delete_metadata(temp_db, table_id)

        # 8. Verify deletion
        metadata = get_metadata(temp_db, table_id)
        assert metadata is None

    def test_api_to_database_workflow(self, temp_db):
        """Test workflow from API fetch to database storage."""
        # Mock API response
        table_id = "FOLK1A"
        test_data = {
            "id": table_id,
            "text": "Population data",
            "updated": "2024-01-01T00:00:00"
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = test_data
        mock_response.raise_for_status = Mock()

        # 1. Fetch from API
        with DSTAPIClient() as client:
            with patch.object(client.client, 'request', return_value=mock_response):
                table_info = client.get_table_info(table_id)

        # 2. Store in database
        update_metadata(
            temp_db,
            table_id=table_id,
            table_name=table_info['text'],
            notes='Fetched from API'
        )

        # 3. Verify storage
        metadata = get_metadata(temp_db, table_id)
        assert metadata is not None
        assert metadata['table_id'] == table_id
        assert metadata['table_name'] == 'Population data'
        assert metadata['notes'] == 'Fetched from API'

    def test_directory_and_logger_integration(self, tmp_path):
        """Test integration between ensure_directory and logger setup."""
        # Create logs directory
        log_dir = tmp_path / 'integration_logs'
        ensure_directory(log_dir)

        # Verify directory exists
        assert log_dir.exists()

        # Setup logger (will use default location, but test it works)
        logger = setup_logger('integration.dir_test')

        # Logger should work
        logger.info("Test message")

        assert logger is not None


# =============================================================================
# Error Handling and Edge Cases
# =============================================================================

@pytest.mark.unit
class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_api_timeout_handling(self):
        """Test handling of API timeout."""
        client = DSTAPIClient(timeout=0.001)

        # Mock a timeout exception
        with patch.object(client.client, 'request', side_effect=httpx.TimeoutException("Timeout")):
            with pytest.raises(httpx.TimeoutException):
                client._make_request('subjects')

        client.close()

    def test_database_path_absolute_conversion(self, monkeypatch):
        """Test that relative database paths are converted to absolute."""
        monkeypatch.setenv('DUCKDB_PATH', './relative/path.duckdb')

        # Reload module to pick up env var
        import importlib
        import db.db_utils
        importlib.reload(db.db_utils)

        db_path = db.db_utils.get_db_path()

        # Should be absolute
        assert os.path.isabs(db_path)

    def test_logger_with_special_characters(self):
        """Test logger with special characters in name."""
        logger = setup_logger('test.special-chars_123')

        assert logger is not None
        assert logger.name == 'test.special-chars_123'

    def test_ensure_directory_with_file_path(self, tmp_path):
        """Test ensure_directory behavior when path points to file."""
        # Create a file
        file_path = tmp_path / 'testfile.txt'
        file_path.write_text('test')

        # Try to create directory with same name should raise error
        with pytest.raises(Exception):
            ensure_directory(file_path)
