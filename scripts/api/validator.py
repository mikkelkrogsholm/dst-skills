#!/usr/bin/env python3
"""
DST API Validator Module

Provides pre-flight validation for DST API requests to catch errors early.
Validates table IDs, variable codes, value codes, and estimates cell counts.
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.client import DSTAPIClient
from api.exceptions import (
    TableNotFoundError,
    VariableNotFoundError,
    ValueNotFoundError,
    CellLimitExceededError,
    RequiredVariableMissingError
)
from utils import setup_logger

logger = setup_logger(__name__)

# Valid DST API formats
VALID_FORMATS: Set[str] = {
    'CSV', 'JSONSTAT', 'BULK', 'XLSX', 'HTML', 'DSTML',
    'SDMXCOMPACT', 'SDMXGENERIC', 'PX', 'PNG'
}

# Streaming formats (no cell limit)
STREAMING_FORMATS: Set[str] = {'BULK', 'SDMXCOMPACT', 'SDMXGENERIC'}

# Cell limit for non-streaming formats
CELL_LIMIT: int = 1_000_000


def validate_format(format_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that format is supported by DST API.

    Args:
        format_name: Format to validate (e.g., 'CSV', 'BULK')

    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, None)
        If invalid: (False, "Error message")

    Example:
        >>> valid, error = validate_format('JSON')
        >>> if not valid:
        >>>     print(error)  # "Format 'JSON' is not valid..."
    """
    format_upper = format_name.upper()

    if format_upper not in VALID_FORMATS:
        valid_list = ', '.join(sorted(VALID_FORMATS))
        return False, (
            f"Format '{format_name}' is not valid. "
            f"Valid formats: {valid_list}. "
            f"Note: Use 'JSONSTAT' not 'JSON'."
        )

    return True, None


def validate_table_exists(table_id: str, client: Optional[DSTAPIClient] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate that table exists in DST database.

    Args:
        table_id: Table identifier to validate
        client: Optional DSTAPIClient instance (creates new if not provided)

    Returns:
        Tuple of (exists, error_message)
        If exists: (True, None)
        If not: (False, "Error message")

    Example:
        >>> exists, error = validate_table_exists('FOLK1A')
        >>> if not exists:
        >>>     print(error)
    """
    try:
        if client is None:
            # Create and manage our own client
            client = DSTAPIClient()
            with client:
                metadata = client.get_table_info(table_id)
        else:
            # Use the passed-in client without closing it
            metadata = client.get_table_info(table_id)

        # If we got here, table exists
        return True, None

    except Exception as e:
        error_msg = str(e)
        if 'not found' in error_msg.lower() or 'ikke fundet' in error_msg.lower():
            return False, f"Table '{table_id}' not found in DST database"
        else:
            return False, f"Error validating table '{table_id}': {error_msg}"


def validate_variables(
    table_id: str,
    variables: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None,
    client: Optional[DSTAPIClient] = None
) -> List[str]:
    """
    Validate variable specifications against table metadata.

    Args:
        table_id: Table identifier
        variables: List of variable specifications
                  [{"code": "KØN", "values": ["1", "2"]}, ...]
        metadata: Optional pre-fetched table metadata
        client: Optional DSTAPIClient instance

    Returns:
        List of error messages (empty list if all valid)

    Example:
        >>> variables = [{"code": "INVALID", "values": ["1"]}]
        >>> errors = validate_variables('FOLK1A', variables)
        >>> if errors:
        >>>     for error in errors:
        >>>         print(error)
    """
    errors = []

    # Get metadata if not provided
    if metadata is None:
        if client is None:
            # Create and manage our own client
            client = DSTAPIClient()
            try:
                with client:
                    metadata = client.get_table_info(table_id)
            except Exception as e:
                errors.append(f"Could not fetch table metadata: {e}")
                return errors
        else:
            # Use the passed-in client without closing it
            try:
                metadata = client.get_table_info(table_id)
            except Exception as e:
                errors.append(f"Could not fetch table metadata: {e}")
                return errors

    # Build lookup dict of valid variables
    valid_variables = {var['id']: var for var in metadata.get('variables', [])}

    # Validate each variable
    for var_spec in variables:
        var_code = var_spec.get('code')
        var_values = var_spec.get('values', [])

        # Check variable exists
        if var_code not in valid_variables:
            errors.append(
                f"Variable '{var_code}' not found in table '{table_id}'. "
                f"Valid variables: {', '.join(valid_variables.keys())}"
            )
            continue

        var_metadata = valid_variables[var_code]

        # Check if values are specified (skip wildcards and nth-rules)
        if not var_values:
            errors.append(f"No values specified for variable '{var_code}'")
            continue

        # Skip validation for wildcards and patterns
        if any(v in ['*', '(-n+1)', '(1)'] or v.startswith('>=') or v.startswith('<=')
               for v in var_values):
            continue

        # Validate specific values
        valid_values = {val['id'] for val in var_metadata.get('values', [])}

        for value in var_values:
            # Skip special patterns
            if '*' in value or '(' in value or '>=' in value or '<=' in value:
                continue

            if value not in valid_values:
                errors.append(
                    f"Value '{value}' not valid for variable '{var_code}'. "
                    f"Check tableinfo for valid values."
                )

    return errors


def estimate_cell_count(
    table_id: str,
    variables: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None,
    client: Optional[DSTAPIClient] = None
) -> int:
    """
    Estimate number of cells in the result set.

    Formula: cells = var1_count × var2_count × ... × varN_count

    Args:
        table_id: Table identifier
        variables: List of variable specifications
        metadata: Optional pre-fetched table metadata
        client: Optional DSTAPIClient instance

    Returns:
        int: Estimated cell count (0 if unable to estimate)

    Example:
        >>> variables = [
        >>>     {"code": "OMRÅDE", "values": ["000"]},  # 1 value
        >>>     {"code": "KØN", "values": ["*"]},       # 3 values
        >>>     {"code": "Tid", "values": ["2020*"]}    # ~4 quarters
        >>> ]
        >>> cells = estimate_cell_count('FOLK1A', variables)
        >>> print(f"Estimated {cells:,} cells")
    """
    # Get metadata if not provided
    if metadata is None:
        if client is None:
            # Create and manage our own client
            client = DSTAPIClient()
            try:
                with client:
                    metadata = client.get_table_info(table_id)
            except Exception:
                logger.warning(f"Could not fetch metadata for cell count estimation")
                return 0
        else:
            # Use the passed-in client without closing it
            try:
                metadata = client.get_table_info(table_id)
            except Exception:
                logger.warning(f"Could not fetch metadata for cell count estimation")
                return 0

    # Build lookup dict
    var_lookup = {var['id']: var for var in metadata.get('variables', [])}

    total_cells = 1

    for var_spec in variables:
        var_code = var_spec.get('code')
        var_values = var_spec.get('values', [])

        if var_code not in var_lookup:
            # Unknown variable, can't estimate
            return 0

        var_metadata = var_lookup[var_code]

        # Estimate count for this variable
        if '*' in var_values or not var_values:
            # Wildcard or empty - use all values
            count = len(var_metadata.get('values', []))
        elif any(v.startswith('>=') or v.startswith('<=') for v in var_values):
            # Range operator - estimate conservatively (half of all values)
            count = len(var_metadata.get('values', [])) // 2
        elif any('*' in v for v in var_values):
            # Pattern - estimate conservatively (quarter of all values per pattern)
            patterns = [v for v in var_values if '*' in v]
            count = len(patterns) * (len(var_metadata.get('values', [])) // 4)
        elif any('(' in v for v in var_values):
            # Nth-rule - count how many
            count = len([v for v in var_values if '(' in v])
        else:
            # Explicit values
            count = len(var_values)

        total_cells *= max(count, 1)

    return total_cells


def recommend_format(
    estimated_cells: int,
    prefer_streaming: bool = False
) -> str:
    """
    Recommend format based on estimated cell count.

    Args:
        estimated_cells: Estimated number of cells
        prefer_streaming: If True, always recommend BULK

    Returns:
        str: Recommended format ('BULK' or 'CSV')

    Example:
        >>> cells = estimate_cell_count(table_id, variables)
        >>> format = recommend_format(cells)
        >>> print(f"Use {format} format for {cells:,} cells")
    """
    if prefer_streaming or estimated_cells > CELL_LIMIT:
        return 'BULK'
    else:
        return 'CSV'


def validate_format_requirements(
    format_name: str,
    variables: List[Dict[str, Any]],
    table_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    client: Optional[DSTAPIClient] = None
) -> List[str]:
    """
    Validate format-specific requirements.

    BULK format requires ALL variables to be specified.
    Other formats allow auto-elimination.

    Args:
        format_name: Format being used
        variables: Variable specifications
        table_id: Table identifier
        metadata: Optional pre-fetched metadata
        client: Optional DSTAPIClient instance

    Returns:
        List of error/warning messages

    Example:
        >>> errors = validate_format_requirements('BULK', variables, 'FOLK1A')
        >>> if errors:
        >>>     for error in errors:
        >>>         print(error)
    """
    messages = []

    format_upper = format_name.upper()

    # Get metadata if needed for BULK format
    if format_upper in STREAMING_FORMATS:
        if metadata is None:
            if client is None:
                # Create and manage our own client
                client = DSTAPIClient()
                try:
                    with client:
                        metadata = client.get_table_info(table_id)
                except Exception as e:
                    messages.append(f"Could not fetch metadata: {e}")
                    return messages
            else:
                # Use the passed-in client without closing it
                try:
                    metadata = client.get_table_info(table_id)
                except Exception as e:
                    messages.append(f"Could not fetch metadata: {e}")
                    return messages

        # BULK requires all variables
        all_var_codes = {var['id'] for var in metadata.get('variables', [])}
        specified_vars = {v['code'] for v in variables}

        missing_vars = all_var_codes - specified_vars

        if missing_vars:
            messages.append(
                f"BULK format requires ALL variables to be specified. "
                f"Missing: {', '.join(missing_vars)}. "
                f"Add these variables with wildcard '*' if you want all values."
            )

    return messages


def validate_request(
    table_id: str,
    format_name: str,
    variables: List[Dict[str, Any]],
    client: Optional[DSTAPIClient] = None
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Complete validation of a data request.

    Performs all validation checks and returns comprehensive results.

    Args:
        table_id: Table identifier
        format_name: Desired format
        variables: Variable specifications
        client: Optional DSTAPIClient instance

    Returns:
        Tuple of (is_valid, errors/warnings, info_dict)
        - is_valid: True if request should proceed
        - errors: List of error/warning messages
        - info: Dict with estimated_cells, recommended_format, metadata

    Example:
        >>> valid, messages, info = validate_request(
        >>>     'FOLK1A', 'CSV', variables
        >>> )
        >>> if not valid:
        >>>     for msg in messages:
        >>>         print(f"ERROR: {msg}")
        >>> else:
        >>>     print(f"Request OK. Estimated {info['estimated_cells']:,} cells")
    """
    messages = []
    info = {}

    # 1. Validate format
    format_valid, format_error = validate_format(format_name)
    if not format_valid:
        messages.append(f"ERROR: {format_error}")
        return False, messages, info

    # 2. Validate table exists and get metadata
    own_client = False
    if client is None:
        # Create and manage our own client
        client = DSTAPIClient()
        own_client = True

    try:
        if own_client:
            # Use context manager for our own client
            with client:
                metadata = client.get_table_info(table_id)
        else:
            # Use the passed-in client without closing it
            metadata = client.get_table_info(table_id)
        info['metadata'] = metadata
    except Exception as e:
        messages.append(f"ERROR: Could not fetch table metadata: {e}")
        return False, messages, info

    # 3. Validate variables
    var_errors = validate_variables(table_id, variables, metadata, client)
    if var_errors:
        messages.extend([f"ERROR: {err}" for err in var_errors])
        return False, messages, info

    # 4. Estimate cell count
    estimated_cells = estimate_cell_count(table_id, variables, metadata, client)
    info['estimated_cells'] = estimated_cells

    # 5. Check cell limit
    if estimated_cells > CELL_LIMIT and format_name.upper() not in STREAMING_FORMATS:
        messages.append(
            f"WARNING: Estimated {estimated_cells:,} cells exceeds limit ({CELL_LIMIT:,}). "
            f"Use BULK format for unlimited cells."
        )
        info['recommended_format'] = 'BULK'
        # This is a warning, not an error - request might still work if estimate is high

    # 6. Validate format-specific requirements
    format_errors = validate_format_requirements(format_name, variables, table_id, metadata, client)
    if format_errors:
        messages.extend([f"ERROR: {err}" for err in format_errors])
        return False, messages, info

    # If we got here, validation passed
    if not messages:
        messages.append(f"✓ Validation passed. Estimated {estimated_cells:,} cells.")

    return True, messages, info


# Convenience function for simple validation
def quick_validate(table_id: str, format_name: str = 'BULK') -> bool:
    """
    Quick validation of table and format.

    Args:
        table_id: Table to validate
        format_name: Format to validate

    Returns:
        bool: True if valid, False otherwise

    Example:
        >>> if quick_validate('FOLK1A', 'BULK'):
        >>>     # proceed with request
        >>>     pass
    """
    format_valid, _ = validate_format(format_name)
    if not format_valid:
        return False

    table_valid, _ = validate_table_exists(table_id)
    return table_valid
