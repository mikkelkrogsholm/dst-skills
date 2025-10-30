"""
Comprehensive pytest tests for DST Skills API scripts.

Tests all API scripts with mocked responses, covering:
- CLI argument parsing
- Output to stdout and file
- Error handling
- Success and failure scenarios
"""

import sys
import json
import pytest
import responses
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from api import get_subjects, get_tables, get_tableinfo, fetch_data


# =============================================================================
# Test Data - Mock API Responses
# =============================================================================

MOCK_SUBJECTS_RESPONSE = [
    {
        "id": "1",
        "description": "Population and elections",
        "active": True,
        "hasSubjects": True
    },
    {
        "id": "2",
        "description": "Labour, income and wealth",
        "active": True,
        "hasSubjects": True
    }
]

MOCK_SUBJECTS_RECURSIVE_RESPONSE = [
    {
        "id": "1",
        "description": "Population and elections",
        "active": True,
        "hasSubjects": True,
        "subjects": [
            {
                "id": "02",
                "description": "Population",
                "active": True,
                "hasSubjects": False
            }
        ]
    }
]

MOCK_TABLES_RESPONSE = [
    {
        "id": "FOLK1A",
        "text": "Population at the first day of the quarter",
        "unit": "Number",
        "updated": "2024-01-15T09:00:00",
        "firstPeriod": "2008Q1",
        "latestPeriod": "2024Q1"
    },
    {
        "id": "FOLK2",
        "text": "Population 1. January by age and sex",
        "unit": "Number",
        "updated": "2024-01-10T09:00:00",
        "firstPeriod": "2008",
        "latestPeriod": "2024"
    }
]

MOCK_TABLEINFO_RESPONSE = {
    "id": "FOLK1A",
    "text": "Population at the first day of the quarter",
    "description": "Population statistics",
    "unit": "Number",
    "updated": "2024-01-15T09:00:00",
    "variables": [
        {
            "id": "OMRÅDE",
            "text": "area",
            "values": [
                {"id": "000", "text": "Whole country"},
                {"id": "101", "text": "Copenhagen"}
            ]
        },
        {
            "id": "TID",
            "text": "time",
            "values": [
                {"id": "2023Q4", "text": "2023Q4"},
                {"id": "2024Q1", "text": "2024Q1"}
            ]
        }
    ]
}

MOCK_DATA_RESPONSE = [
    {
        "OMRÅDE": "000",
        "TID": "2024Q1",
        "INDHOLD": 5900000
    },
    {
        "OMRÅDE": "101",
        "TID": "2024Q1",
        "INDHOLD": 650000
    }
]


# =============================================================================
# Test get_subjects.py
# =============================================================================

@pytest.mark.unit
def test_get_subjects_basic():
    """Test basic subject fetching without recursion."""
    with patch('api.get_subjects.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_subjects.return_value = MOCK_SUBJECTS_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        result = get_subjects.get_subjects(recursive=False)

        # Assertions
        assert result == MOCK_SUBJECTS_RESPONSE
        assert len(result) == 2
        assert result[0]["id"] == "1"
        mock_client.get_subjects.assert_called_once_with(recursive=False)


@pytest.mark.unit
def test_get_subjects_recursive():
    """Test subject fetching with recursive option."""
    with patch('api.get_subjects.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_subjects.return_value = MOCK_SUBJECTS_RECURSIVE_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        result = get_subjects.get_subjects(recursive=True)

        # Assertions
        assert result == MOCK_SUBJECTS_RECURSIVE_RESPONSE
        assert "subjects" in result[0]
        mock_client.get_subjects.assert_called_once_with(recursive=True)


@pytest.mark.unit
def test_get_subjects_api_error():
    """Test error handling when API fails."""
    with patch('api.get_subjects.DSTAPIClient') as mock_client_class:
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_subjects.side_effect = Exception("API connection failed")
        mock_client_class.return_value = mock_client

        # Test
        with pytest.raises(Exception) as exc_info:
            get_subjects.get_subjects()

        assert "API connection failed" in str(exc_info.value)


@pytest.mark.unit
def test_get_subjects_main_stdout(capsys):
    """Test main function output to stdout."""
    with patch('api.get_subjects.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_subjects.return_value = MOCK_SUBJECTS_RESPONSE
        mock_client_class.return_value = mock_client

        # Test with sys.argv
        with patch('sys.argv', ['get_subjects.py']):
            with pytest.raises(SystemExit) as exc_info:
                get_subjects.main()

            assert exc_info.value.code == 0

            # Check output
            captured = capsys.readouterr()
            output_data = json.loads(captured.out)
            assert len(output_data) == 2
            assert output_data[0]["id"] == "1"


@pytest.mark.unit
def test_get_subjects_main_to_file(temp_output_file):
    """Test main function output to file."""
    with patch('api.get_subjects.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_subjects.return_value = MOCK_SUBJECTS_RESPONSE
        mock_client_class.return_value = mock_client

        # Test with file output
        with patch('sys.argv', ['get_subjects.py', '--output', temp_output_file]):
            with pytest.raises(SystemExit) as exc_info:
                get_subjects.main()

            assert exc_info.value.code == 0

            # Check file was written
            output_path = Path(temp_output_file)
            assert output_path.exists()

            # Check content
            content = json.loads(output_path.read_text())
            assert len(content) == 2
            assert content[0]["id"] == "1"


@pytest.mark.unit
def test_get_subjects_main_recursive_flag():
    """Test main function with recursive flag."""
    with patch('api.get_subjects.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_subjects.return_value = MOCK_SUBJECTS_RECURSIVE_RESPONSE
        mock_client_class.return_value = mock_client

        # Test with recursive flag
        with patch('sys.argv', ['get_subjects.py', '--recursive']):
            with pytest.raises(SystemExit) as exc_info:
                get_subjects.main()

            assert exc_info.value.code == 0
            mock_client.get_subjects.assert_called_once_with(recursive=True)


@pytest.mark.unit
def test_get_subjects_main_error_handling(capsys):
    """Test main function error handling."""
    with patch('api.get_subjects.DSTAPIClient') as mock_client_class:
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_subjects.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['get_subjects.py']):
            with pytest.raises(SystemExit) as exc_info:
                get_subjects.main()

            assert exc_info.value.code == 1

            # Check error message
            captured = capsys.readouterr()
            assert "Error:" in captured.err
            assert "Network error" in captured.err


# =============================================================================
# Test get_tables.py
# =============================================================================

@pytest.mark.unit
def test_get_tables_all():
    """Test fetching all tables without filters."""
    with patch('api.get_tables.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_tables.return_value = MOCK_TABLES_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        result = get_tables.get_tables()

        # Assertions
        assert result == MOCK_TABLES_RESPONSE
        assert len(result) == 2
        assert result[0]["id"] == "FOLK1A"
        mock_client.get_tables.assert_called_once_with(subjects=None)


@pytest.mark.unit
def test_get_tables_by_subject(sample_subject_id):
    """Test fetching tables filtered by subject."""
    with patch('api.get_tables.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_tables.return_value = MOCK_TABLES_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        result = get_tables.get_tables(subject_id=sample_subject_id)

        # Assertions
        assert result == MOCK_TABLES_RESPONSE
        mock_client.get_tables.assert_called_once_with(subjects=sample_subject_id)


@pytest.mark.unit
def test_get_tables_with_search():
    """Test fetching tables with keyword search."""
    with patch('api.get_tables.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_tables.return_value = MOCK_TABLES_RESPONSE
        mock_client_class.return_value = mock_client

        # Test with search term that matches one table
        result = get_tables.get_tables(search_term="quarter")

        # Assertions - should filter to only tables matching "quarter"
        assert len(result) == 1
        assert result[0]["id"] == "FOLK1A"
        assert "quarter" in result[0]["text"].lower()


@pytest.mark.unit
def test_get_tables_search_no_results():
    """Test searching with term that matches no tables."""
    with patch('api.get_tables.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_tables.return_value = MOCK_TABLES_RESPONSE
        mock_client_class.return_value = mock_client

        # Test with search term that matches nothing
        result = get_tables.get_tables(search_term="nonexistent")

        # Assertions
        assert len(result) == 0


@pytest.mark.unit
def test_get_tables_api_error():
    """Test error handling when API fails."""
    with patch('api.get_tables.DSTAPIClient') as mock_client_class:
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_tables.side_effect = Exception("API error")
        mock_client_class.return_value = mock_client

        # Test
        with pytest.raises(Exception) as exc_info:
            get_tables.get_tables()

        assert "API error" in str(exc_info.value)


@pytest.mark.unit
def test_get_tables_main_stdout(capsys):
    """Test main function output to stdout."""
    with patch('api.get_tables.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_tables.return_value = MOCK_TABLES_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['get_tables.py']):
            with pytest.raises(SystemExit) as exc_info:
                get_tables.main()

            assert exc_info.value.code == 0

            # Check output
            captured = capsys.readouterr()
            output_data = json.loads(captured.out)
            assert len(output_data) == 2
            assert output_data[0]["id"] == "FOLK1A"


@pytest.mark.unit
def test_get_tables_main_with_subject_flag(sample_subject_id):
    """Test main function with subject filter."""
    with patch('api.get_tables.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_tables.return_value = MOCK_TABLES_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['get_tables.py', '--subject', sample_subject_id]):
            with pytest.raises(SystemExit) as exc_info:
                get_tables.main()

            assert exc_info.value.code == 0
            mock_client.get_tables.assert_called_once()


@pytest.mark.unit
def test_get_tables_main_with_search_flag(capsys):
    """Test main function with search filter."""
    with patch('api.get_tables.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_tables.return_value = MOCK_TABLES_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['get_tables.py', '--search', 'quarter']):
            with pytest.raises(SystemExit) as exc_info:
                get_tables.main()

            assert exc_info.value.code == 0

            # Check output is filtered
            captured = capsys.readouterr()
            output_data = json.loads(captured.out)
            assert len(output_data) == 1


@pytest.mark.unit
def test_get_tables_main_to_file(temp_output_file):
    """Test main function output to file."""
    with patch('api.get_tables.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_tables.return_value = MOCK_TABLES_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['get_tables.py', '--output', temp_output_file]):
            with pytest.raises(SystemExit) as exc_info:
                get_tables.main()

            assert exc_info.value.code == 0

            # Check file
            output_path = Path(temp_output_file)
            assert output_path.exists()
            content = json.loads(output_path.read_text())
            assert len(content) == 2


@pytest.mark.unit
def test_get_tables_main_error_handling(capsys):
    """Test main function error handling."""
    with patch('api.get_tables.DSTAPIClient') as mock_client_class:
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_tables.side_effect = Exception("Timeout error")
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['get_tables.py']):
            with pytest.raises(SystemExit) as exc_info:
                get_tables.main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "Error:" in captured.err


# =============================================================================
# Test get_tableinfo.py
# =============================================================================

@pytest.mark.unit
def test_get_tableinfo_basic(sample_table_id):
    """Test basic table info fetching."""
    with patch('api.get_tableinfo.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_table_info.return_value = MOCK_TABLEINFO_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        result = get_tableinfo.get_tableinfo(sample_table_id)

        # Assertions
        assert result == MOCK_TABLEINFO_RESPONSE
        assert result["id"] == sample_table_id
        assert "variables" in result
        assert len(result["variables"]) == 2
        mock_client.get_table_info.assert_called_once_with(sample_table_id)


@pytest.mark.unit
def test_get_tableinfo_api_error(sample_table_id):
    """Test error handling when API fails."""
    with patch('api.get_tableinfo.DSTAPIClient') as mock_client_class:
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_table_info.side_effect = Exception("Table not found")
        mock_client_class.return_value = mock_client

        # Test
        with pytest.raises(Exception) as exc_info:
            get_tableinfo.get_tableinfo(sample_table_id)

        assert "Table not found" in str(exc_info.value)


@pytest.mark.unit
def test_get_tableinfo_format_verbose_output():
    """Test verbose formatting of table info."""
    # Test the verbose formatter
    result = get_tableinfo.format_verbose_output(MOCK_TABLEINFO_RESPONSE)

    # Assertions
    assert isinstance(result, str)
    assert "FOLK1A" in result
    assert "Population at the first day of the quarter" in result
    assert "VARIABLES" in result
    assert "OMRÅDE" in result
    assert "TID" in result
    assert "Whole country" in result


@pytest.mark.unit
def test_get_tableinfo_main_json_output(sample_table_id, capsys):
    """Test main function with JSON output."""
    with patch('api.get_tableinfo.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_table_info.return_value = MOCK_TABLEINFO_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['get_tableinfo.py', '--table-id', sample_table_id]):
            with pytest.raises(SystemExit) as exc_info:
                get_tableinfo.main()

            assert exc_info.value.code == 0

            # Check output
            captured = capsys.readouterr()
            output_data = json.loads(captured.out)
            assert output_data["id"] == sample_table_id
            assert "variables" in output_data


@pytest.mark.unit
def test_get_tableinfo_main_verbose_output(sample_table_id, capsys):
    """Test main function with verbose output."""
    with patch('api.get_tableinfo.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_table_info.return_value = MOCK_TABLEINFO_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['get_tableinfo.py', '--table-id', sample_table_id, '--verbose']):
            with pytest.raises(SystemExit) as exc_info:
                get_tableinfo.main()

            assert exc_info.value.code == 0

            # Check output is verbose format
            captured = capsys.readouterr()
            assert "TABLE INFO:" in captured.out
            assert "VARIABLES" in captured.out
            assert "OMRÅDE" in captured.out


@pytest.mark.unit
def test_get_tableinfo_main_to_file(sample_table_id, temp_output_file):
    """Test main function output to file."""
    with patch('api.get_tableinfo.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_table_info.return_value = MOCK_TABLEINFO_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['get_tableinfo.py', '--table-id', sample_table_id, '--output', temp_output_file]):
            with pytest.raises(SystemExit) as exc_info:
                get_tableinfo.main()

            assert exc_info.value.code == 0

            # Check file
            output_path = Path(temp_output_file)
            assert output_path.exists()
            content = json.loads(output_path.read_text())
            assert content["id"] == sample_table_id


@pytest.mark.unit
def test_get_tableinfo_main_missing_table_id(capsys):
    """Test main function with missing required argument."""
    # Test missing --table-id argument
    with patch('sys.argv', ['get_tableinfo.py']):
        with pytest.raises(SystemExit) as exc_info:
            get_tableinfo.main()

        # Should exit with error code 2 (argparse error)
        assert exc_info.value.code == 2


@pytest.mark.unit
def test_get_tableinfo_main_error_handling(sample_table_id, capsys):
    """Test main function error handling."""
    with patch('api.get_tableinfo.DSTAPIClient') as mock_client_class:
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_table_info.side_effect = Exception("Invalid table ID")
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['get_tableinfo.py', '--table-id', sample_table_id]):
            with pytest.raises(SystemExit) as exc_info:
                get_tableinfo.main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "Error:" in captured.err


# =============================================================================
# Test fetch_data.py
# =============================================================================

@pytest.mark.unit
def test_fetch_data_basic(sample_table_id):
    """Test basic data fetching."""
    with patch('api.fetch_data.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_data.return_value = MOCK_DATA_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        result = fetch_data.fetch_data(sample_table_id)

        # Assertions
        assert result == MOCK_DATA_RESPONSE
        assert len(result) == 2
        assert result[0]["OMRÅDE"] == "000"
        mock_client.get_data.assert_called_once()


@pytest.mark.unit
def test_fetch_data_with_filters(sample_table_id):
    """Test data fetching with filters."""
    with patch('api.fetch_data.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_data.return_value = [MOCK_DATA_RESPONSE[0]]
        mock_client_class.return_value = mock_client

        # Test with filters
        filters = {"OMRÅDE": ["000"]}
        result = fetch_data.fetch_data(sample_table_id, filters=filters)

        # Assertions
        assert isinstance(result, list)
        mock_client.get_data.assert_called_once()


@pytest.mark.unit
def test_fetch_data_csv_format(sample_table_id):
    """Test data fetching with CSV format."""
    with patch('api.fetch_data.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_data.return_value = MOCK_DATA_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        result = fetch_data.fetch_data(sample_table_id, format='csv')

        # Assertions
        assert result == MOCK_DATA_RESPONSE
        mock_client.get_data.assert_called_once()


@pytest.mark.unit
def test_fetch_data_api_error(sample_table_id):
    """Test error handling when API fails."""
    with patch('api.fetch_data.DSTAPIClient') as mock_client_class:
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_data.side_effect = Exception("Data not available")
        mock_client_class.return_value = mock_client

        # Test
        with pytest.raises(Exception) as exc_info:
            fetch_data.fetch_data(sample_table_id)

        assert "Data not available" in str(exc_info.value)


@pytest.mark.unit
def test_data_to_csv_list_of_dicts():
    """Test CSV conversion for list of dictionaries."""
    data = [
        {"col1": "a", "col2": 1},
        {"col1": "b", "col2": 2}
    ]

    result = fetch_data.data_to_csv(data)

    # Assertions
    assert isinstance(result, str)
    assert "col1,col2" in result
    assert "a,1" in result
    assert "b,2" in result


@pytest.mark.unit
def test_data_to_csv_dict_with_data_key():
    """Test CSV conversion for dict with 'data' key."""
    data = {
        "data": [
            {"col1": "x", "col2": 10}
        ]
    }

    result = fetch_data.data_to_csv(data)

    # Assertions
    assert isinstance(result, str)
    assert "col1,col2" in result
    assert "x,10" in result


@pytest.mark.unit
def test_data_to_csv_single_dict():
    """Test CSV conversion for single dictionary."""
    data = {"col1": "value1", "col2": "value2"}

    result = fetch_data.data_to_csv(data)

    # Assertions
    assert isinstance(result, str)
    assert "col1,col2" in result
    assert "value1,value2" in result


@pytest.mark.unit
def test_data_to_csv_invalid_type():
    """Test CSV conversion error handling for invalid type."""
    data = "invalid_string_data"

    with pytest.raises(ValueError) as exc_info:
        fetch_data.data_to_csv(data)

    assert "Cannot convert data type" in str(exc_info.value)


@pytest.mark.unit
def test_fetch_data_main_json_output(sample_table_id, capsys):
    """Test main function with JSON output."""
    with patch('api.fetch_data.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_data.return_value = MOCK_DATA_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['fetch_data.py', '--table-id', sample_table_id]):
            with pytest.raises(SystemExit) as exc_info:
                fetch_data.main()

            assert exc_info.value.code == 0

            # Check output
            captured = capsys.readouterr()
            output_data = json.loads(captured.out)
            assert len(output_data) == 2
            assert output_data[0]["OMRÅDE"] == "000"


@pytest.mark.unit
def test_fetch_data_main_with_filters(sample_table_id, capsys):
    """Test main function with filter argument."""
    with patch('api.fetch_data.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_data.return_value = [MOCK_DATA_RESPONSE[0]]
        mock_client_class.return_value = mock_client

        # Test with filters
        filters_json = '{"OMRÅDE":["000"]}'
        with patch('sys.argv', ['fetch_data.py', '--table-id', sample_table_id, '--filters', filters_json]):
            with pytest.raises(SystemExit) as exc_info:
                fetch_data.main()

            assert exc_info.value.code == 0


@pytest.mark.unit
def test_fetch_data_main_invalid_filters(sample_table_id, capsys):
    """Test main function with invalid JSON filters."""
    # Test with invalid JSON
    with patch('sys.argv', ['fetch_data.py', '--table-id', sample_table_id, '--filters', 'invalid_json']):
        with pytest.raises(SystemExit) as exc_info:
            fetch_data.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Invalid JSON" in captured.err


@pytest.mark.unit
def test_fetch_data_main_csv_output(sample_table_id, capsys):
    """Test main function with CSV format."""
    with patch('api.fetch_data.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_data.return_value = MOCK_DATA_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['fetch_data.py', '--table-id', sample_table_id, '--format', 'csv']):
            with pytest.raises(SystemExit) as exc_info:
                fetch_data.main()

            assert exc_info.value.code == 0

            # Check CSV output
            captured = capsys.readouterr()
            assert "OMRÅDE" in captured.out
            assert "TID" in captured.out
            assert "000" in captured.out


@pytest.mark.unit
def test_fetch_data_main_to_file(sample_table_id, temp_output_file):
    """Test main function output to file."""
    with patch('api.fetch_data.DSTAPIClient') as mock_client_class:
        # Setup mock
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_data.return_value = MOCK_DATA_RESPONSE
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['fetch_data.py', '--table-id', sample_table_id, '--output', temp_output_file]):
            with pytest.raises(SystemExit) as exc_info:
                fetch_data.main()

            assert exc_info.value.code == 0

            # Check file
            output_path = Path(temp_output_file)
            assert output_path.exists()
            content = json.loads(output_path.read_text())
            assert len(content) == 2


@pytest.mark.unit
def test_fetch_data_main_missing_table_id(capsys):
    """Test main function with missing required argument."""
    # Test missing --table-id argument
    with patch('sys.argv', ['fetch_data.py']):
        with pytest.raises(SystemExit) as exc_info:
            fetch_data.main()

        # Should exit with error code 2 (argparse error)
        assert exc_info.value.code == 2


@pytest.mark.unit
def test_fetch_data_main_error_handling(sample_table_id, capsys):
    """Test main function error handling."""
    with patch('api.fetch_data.DSTAPIClient') as mock_client_class:
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_data.side_effect = Exception("Connection timeout")
        mock_client_class.return_value = mock_client

        # Test
        with patch('sys.argv', ['fetch_data.py', '--table-id', sample_table_id]):
            with pytest.raises(SystemExit) as exc_info:
                fetch_data.main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "Error:" in captured.err
            assert "Connection timeout" in captured.err


# =============================================================================
# Integration-style tests (API markers - would call real API if not mocked)
# =============================================================================

@pytest.mark.api
@responses.activate
def test_get_subjects_with_real_api_structure():
    """Test get_subjects with realistic API response structure."""
    # Mock the actual DST API endpoint
    responses.add(
        responses.GET,
        "https://api.statbank.dk/v1/subjects",
        json=MOCK_SUBJECTS_RESPONSE,
        status=200
    )

    with patch('api.get_subjects.DSTAPIClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_subjects.return_value = MOCK_SUBJECTS_RESPONSE
        mock_client_class.return_value = mock_client

        result = get_subjects.get_subjects()
        assert len(result) >= 1
        assert all("id" in subject for subject in result)


@pytest.mark.api
@responses.activate
def test_get_tables_with_real_api_structure(sample_subject_id):
    """Test get_tables with realistic API response structure."""
    # Mock the actual DST API endpoint
    responses.add(
        responses.GET,
        "https://api.statbank.dk/v1/tables",
        json=MOCK_TABLES_RESPONSE,
        status=200
    )

    with patch('api.get_tables.DSTAPIClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_tables.return_value = MOCK_TABLES_RESPONSE
        mock_client_class.return_value = mock_client

        result = get_tables.get_tables(subject_id=sample_subject_id)
        assert len(result) >= 1
        assert all("id" in table for table in result)


@pytest.mark.api
@responses.activate
def test_get_tableinfo_with_real_api_structure(sample_table_id):
    """Test get_tableinfo with realistic API response structure."""
    # Mock the actual DST API endpoint
    responses.add(
        responses.GET,
        f"https://api.statbank.dk/v1/tableinfo?id={sample_table_id}",
        json=MOCK_TABLEINFO_RESPONSE,
        status=200
    )

    with patch('api.get_tableinfo.DSTAPIClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_table_info.return_value = MOCK_TABLEINFO_RESPONSE
        mock_client_class.return_value = mock_client

        result = get_tableinfo.get_tableinfo(sample_table_id)
        assert result["id"] == sample_table_id
        assert "variables" in result


@pytest.mark.api
@responses.activate
def test_fetch_data_with_real_api_structure(sample_table_id):
    """Test fetch_data with realistic API response structure."""
    # Mock the actual DST API endpoint
    responses.add(
        responses.GET,
        f"https://api.statbank.dk/v1/data?id={sample_table_id}",
        json=MOCK_DATA_RESPONSE,
        status=200
    )

    with patch('api.fetch_data.DSTAPIClient') as mock_client_class:
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get_data.return_value = MOCK_DATA_RESPONSE
        mock_client_class.return_value = mock_client

        result = fetch_data.fetch_data(sample_table_id)
        assert isinstance(result, list)
        assert len(result) >= 1
