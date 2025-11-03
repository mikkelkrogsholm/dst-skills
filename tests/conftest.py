"""
Pytest configuration and shared fixtures for DST Skills tests.
"""

import os
import sys
import tempfile
from pathlib import Path
import pytest
import duckdb

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "scripts"))

# Test database path
TEST_DB_PATH = project_root / "tests" / "test_dst_data.duckdb"


@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root path."""
    return project_root


@pytest.fixture(scope="function")
def temp_db():
    """Create a temporary test database."""
    # Create temp database
    db_path = TEST_DB_PATH

    # Remove if exists
    if db_path.exists():
        db_path.unlink()

    # Create connection
    conn = duckdb.connect(str(db_path))

    # Create metadata table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dst_metadata (
            table_id VARCHAR PRIMARY KEY,
            table_name VARCHAR,
            last_updated TIMESTAMP,
            fetch_timestamp TIMESTAMP,
            record_count INTEGER,
            columns_json VARCHAR,
            notes VARCHAR
        )
    """)

    yield conn

    # Cleanup
    conn.close()
    if db_path.exists():
        db_path.unlink()


@pytest.fixture(scope="function")
def temp_db_path(temp_db):
    """Return path to temporary test database."""
    return str(TEST_DB_PATH)


@pytest.fixture(scope="function")
def mock_env_vars(monkeypatch, temp_db_path):
    """Set up test environment variables."""
    monkeypatch.setenv("DST_API_BASE_URL", "https://api.statbank.dk/v1")
    monkeypatch.setenv("DUCKDB_PATH", temp_db_path)
    monkeypatch.setenv("LOG_LEVEL", "INFO")


@pytest.fixture(scope="function")
def temp_output_file():
    """Create a temporary output file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture(scope="session")
def sample_table_id():
    """Return a sample table ID for testing."""
    return "FOLK1A"


@pytest.fixture(scope="session")
def sample_subject_id():
    """Return a sample subject ID for testing."""
    return "1"


@pytest.fixture
def mock_api_response():
    """Mock API response data."""
    return {
        "subjects": [
            {"id": "1", "description": "Test Subject", "active": True, "hasSubjects": False}
        ],
        "tables": [
            {"id": "FOLK1A", "text": "Test Table", "unit": "Number", "updated": "2024-01-01"}
        ],
        "tableinfo": {
            "id": "FOLK1A",
            "text": "Test Table",
            "variables": [
                {"id": "OMRÅDE", "text": "area", "values": [{"id": "000", "text": "Whole country"}]}
            ]
        }
    }
