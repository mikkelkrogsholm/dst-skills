#!/usr/bin/env python3
"""
DST API Helper Functions

Utility functions for common DST API operations.
Follows KISS principle: simple, focused, reusable functions.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.client import DSTAPIClient
from utils import setup_logger

logger = setup_logger(__name__)

# Cache directory for tableinfo metadata
CACHE_DIR = Path(__file__).parent.parent.parent / 'data' / 'cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cached_tableinfo(table_id: str, ttl_hours: int = 24, client: Optional[DSTAPIClient] = None) -> Dict[str, Any]:
    """
    Get table info with file-based caching.

    Args:
        table_id: Table identifier
        ttl_hours: Cache time-to-live in hours
        client: Optional DSTAPIClient instance

    Returns:
        dict: Table metadata

    Example:
        >>> metadata = get_cached_tableinfo('FOLK1A')
        >>> variables = metadata['variables']
    """
    cache_file = CACHE_DIR / f"tableinfo_{table_id.lower()}.json"

    # Check cache
    if cache_file.exists():
        import time
        from datetime import datetime, timedelta

        # Check age
        mtime = cache_file.stat().st_mtime
        age = datetime.now() - datetime.fromtimestamp(mtime)

        if age < timedelta(hours=ttl_hours):
            logger.debug(f"Using cached tableinfo for {table_id}")
            cached_data = json.loads(cache_file.read_text())

            # Defensive: If the cached data is a string (double-encoded), parse again
            if isinstance(cached_data, str):
                logger.warning(f"Cache for {table_id} was double-encoded, fixing...")
                cached_data = json.loads(cached_data)

            return cached_data

    # Fetch fresh data
    logger.debug(f"Fetching fresh tableinfo for {table_id}")

    if client is None:
        # Create new client - will be closed by context manager
        client = DSTAPIClient()
        with client:
            metadata = client.get_table_info(table_id)
    else:
        # Use existing client - don't close it
        metadata = client.get_table_info(table_id)

    # Defensive: If metadata is already a JSON string, parse it first
    if isinstance(metadata, str):
        logger.warning(f"API returned string instead of dict for {table_id}, parsing...")
        metadata = json.loads(metadata)

    # Cache it
    cache_file.write_text(json.dumps(metadata, indent=2, ensure_ascii=False))

    return metadata


def build_variable_spec(table_id: str, filters: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """
    Build variable specification from simple filters dict.

    Args:
        table_id: Table identifier
        filters: Dict mapping variable codes to value lists
                 e.g., {"OMRÅDE": ["000"], "KØN": ["*"]}

    Returns:
        List of variable specifications for API request

    Example:
        >>> filters = {"OMRÅDE": ["000"], "Tid": ["(1)"]}
        >>> variables = build_variable_spec('FOLK1A', filters)
        >>> # Result: [{"code": "OMRÅDE", "values": ["000"]}, ...]
    """
    variables = []

    for var_code, values in filters.items():
        variables.append({
            'code': var_code,
            'values': values
        })

    return variables


def parse_bulk_csv(csv_text: str) -> pd.DataFrame:
    """
    Parse BULK/CSV response from DST API.

    Note: DST API uses semicolon (;) as separator.

    Args:
        csv_text: CSV text from API response

    Returns:
        pd.DataFrame: Parsed data

    Example:
        >>> response = client.get_data('FOLK1A', format='BULK', ...)
        >>> df = parse_bulk_csv(response)
        >>> print(df.head())
    """
    import io

    df = pd.read_csv(io.StringIO(csv_text), sep=';')

    logger.debug(f"Parsed {len(df)} rows with {len(df.columns)} columns")

    return df


def parse_jsonstat(json_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Parse JSONSTAT response from DST API into a proper relational DataFrame.

    JSON-STAT format structure:
    {
      "dataset": {
        "dimension": {
          "id": ["VAR1", "VAR2", ...],
          "size": [n1, n2, ...],
          "VAR1": {"category": {"index": {...}, "label": {...}}},
          "VAR2": {...}
        },
        "value": [v1, v2, v3, ...]
      }
    }

    Args:
        json_data: JSON-stat data from API response

    Returns:
        pd.DataFrame: Parsed data with proper columns for each dimension

    Example:
        >>> response = client.get_data('FOLK1A', format='JSONSTAT', ...)
        >>> df = parse_jsonstat(response)
        >>> # Result has columns: OMRÅDE, KØN, ALDER, ..., INDHOLD
    """
    dataset = json_data.get('dataset', {})

    if not dataset:
        logger.warning("No dataset in JSONSTAT response")
        return pd.DataFrame()

    dimension_info = dataset.get('dimension', {})
    values = dataset.get('value', [])

    if not values:
        logger.warning("No values in JSONSTAT response")
        return pd.DataFrame()

    # Get dimension IDs and sizes
    dim_ids = dimension_info.get('id', [])
    dim_sizes = dimension_info.get('size', [])

    if not dim_ids or not dim_sizes:
        logger.error("Missing dimension IDs or sizes in JSONSTAT")
        return pd.DataFrame({'value': values})

    # Build index for each dimension
    dimension_values = []
    for dim_id in dim_ids:
        dim_data = dimension_info.get(dim_id, {})
        category = dim_data.get('category', {})
        index = category.get('index', {})
        label = category.get('label', {})

        # Get ordered list of codes for this dimension
        # index maps code -> position, we need position -> code
        if index:
            ordered_codes = sorted(index.keys(), key=lambda k: index[k])
        else:
            # Fallback: use labels if no index
            ordered_codes = list(label.keys()) if label else []

        dimension_values.append(ordered_codes)

    # Generate all combinations using the dimension sizes
    # This creates a Cartesian product of all dimension values
    rows = []
    total_cells = len(values)

    for i in range(total_cells):
        # Calculate position in each dimension using modular arithmetic
        row = {}
        idx = i

        for j in range(len(dim_ids) - 1, -1, -1):
            dim_id = dim_ids[j]
            dim_size = dim_sizes[j]

            # Get position within this dimension
            pos = idx % dim_size
            idx = idx // dim_size

            # Get the code for this position
            if j < len(dimension_values) and pos < len(dimension_values[j]):
                code = dimension_values[j][pos]

                # Use label if available, otherwise use code
                dim_data = dimension_info.get(dim_id, {})
                labels = dim_data.get('category', {}).get('label', {})
                row[dim_id] = labels.get(code, code)
            else:
                row[dim_id] = None

        # Add the value (typically named 'INDHOLD' in DST data)
        row['INDHOLD'] = values[i] if i < len(values) else None
        rows.append(row)

    df = pd.DataFrame(rows)

    logger.debug(f"Parsed {len(df)} rows with {len(df.columns)} columns from JSONSTAT")

    return df


def extract_variable_codes(metadata: Dict[str, Any]) -> List[str]:
    """
    Extract all variable codes from table metadata.

    Args:
        metadata: Table metadata from tableinfo

    Returns:
        List of variable codes

    Example:
        >>> metadata = get_cached_tableinfo('FOLK1A')
        >>> var_codes = extract_variable_codes(metadata)
        >>> # Result: ['OMRÅDE', 'KØN', 'ALDER', 'CIVILSTAND', 'Tid']
    """
    return [var['id'] for var in metadata.get('variables', [])]


def extract_value_codes(metadata: Dict[str, Any], variable_code: str) -> List[str]:
    """
    Extract value codes for a specific variable.

    Args:
        metadata: Table metadata
        variable_code: Variable to get values for

    Returns:
        List of value codes

    Example:
        >>> metadata = get_cached_tableinfo('FOLK1A')
        >>> genders = extract_value_codes(metadata, 'KØN')
        >>> # Result: ['TOT', '1', '2']
    """
    for var in metadata.get('variables', []):
        if var['id'] == variable_code:
            return [val['id'] for val in var.get('values', [])]

    return []


def get_time_variable(metadata: Dict[str, Any]) -> Optional[str]:
    """
    Find the time variable in table metadata.

    Args:
        metadata: Table metadata

    Returns:
        str: Time variable code, or None if not found

    Example:
        >>> metadata = get_cached_tableinfo('FOLK1A')
        >>> time_var = get_time_variable(metadata)
        >>> # Result: 'Tid'
    """
    for var in metadata.get('variables', []):
        if var.get('time', False):
            return var['id']

    return None


def get_eliminable_variables(metadata: Dict[str, Any]) -> List[str]:
    """
    Get list of variables that can be auto-eliminated.

    Args:
        metadata: Table metadata

    Returns:
        List of variable codes with elimination=true

    Example:
        >>> metadata = get_cached_tableinfo('FOLK1A')
        >>> eliminable = get_eliminable_variables(metadata)
    """
    eliminable = []

    for var in metadata.get('variables', []):
        if var.get('elimination', False):
            eliminable.append(var['id'])

    return eliminable


def format_value_count(count: int) -> str:
    """
    Format large numbers with thousand separators.

    Args:
        count: Number to format

    Returns:
        Formatted string

    Example:
        >>> print(format_value_count(1234567))
        >>> # Output: "1,234,567"
    """
    return f"{count:,}"


def clear_tableinfo_cache(table_id: Optional[str] = None) -> None:
    """
    Clear cached tableinfo metadata.

    Args:
        table_id: Optional specific table to clear, or None for all

    Example:
        >>> clear_tableinfo_cache('FOLK1A')  # Clear one
        >>> clear_tableinfo_cache()  # Clear all
    """
    if table_id:
        cache_file = CACHE_DIR / f"tableinfo_{table_id.lower()}.json"
        if cache_file.exists():
            cache_file.unlink()
            logger.info(f"Cleared cache for {table_id}")
    else:
        # Clear all
        for cache_file in CACHE_DIR.glob("tableinfo_*.json"):
            cache_file.unlink()
        logger.info("Cleared all tableinfo cache")
