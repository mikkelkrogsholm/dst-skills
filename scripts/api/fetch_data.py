#!/usr/bin/env python3
"""
Fetch DST Data Script

Fetches actual statistical data from a DST table.
Data can be filtered and exported in different formats.

Usage:
    python fetch_data.py --table-id FOLK1A
    python fetch_data.py --table-id FOLK1A --filters '{"OMRÅDE":["000"]}'
    python fetch_data.py --table-id FOLK1A --format csv --output data.csv
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.client import DSTAPIClient
from api.exceptions import (
    DSTAPIError,
    TableNotFoundError,
    VariableNotFoundError,
    CellLimitExceededError,
    parse_dst_error
)
from api.validator import validate_request
from api.helpers import (
    get_cached_tableinfo,
    build_variable_spec,
    parse_bulk_csv
)
from utils import setup_logger


def fetch_data(table_id: str, filters: Optional[Dict[str, List[str]]] = None, format: str = 'json') -> Union[Dict[str, Any], str]:
    """
    Fetch data from DST API.

    Args:
        table_id: The table identifier
        filters: Optional dict of filter parameters
        format: Output format ('json' or 'csv')

    Returns:
        Data in requested format (dict or str depending on format)

    Raises:
        DSTAPIError: If API request fails with specific error type
    """
    logger = setup_logger(__name__)

    try:
        with DSTAPIClient() as client:
            logger.info(f"Fetching data for table: {table_id}")

            # Build request parameters
            # Valid DST API formats: CSV, JSONSTAT, BULK, XLSX, etc.
            # Use BULK for large datasets (streaming, no cell limit)
            format_map = {
                'jsonstat': 'JSONSTAT',  # JSON-stat format (not plain JSON)
                'csv': 'CSV',
                'bulk': 'BULK'
            }
            api_format = format_map.get(format.lower(), 'BULK')

            # Build variable specification from filters
            variables = []
            if filters:
                logger.info(f"Applying filters: {filters}")
                variables = build_variable_spec(table_id, filters)
            else:
                # No filters - need to get all variables for validation
                logger.info("No filters specified, fetching metadata")
                metadata = get_cached_tableinfo(table_id, client=client)
                # For BULK format, we need all variables with wildcard
                from api.helpers import extract_variable_codes
                var_codes = extract_variable_codes(metadata)
                variables = [{'code': code, 'values': ['*']} for code in var_codes]

            # Validate request before making API call
            logger.info("Validating request...")
            is_valid, messages, info = validate_request(
                table_id=table_id,
                format_name=api_format,
                variables=variables,
                client=client
            )

            # Print validation messages
            for msg in messages:
                if msg.startswith('ERROR'):
                    logger.error(msg)
                elif msg.startswith('WARNING'):
                    logger.warning(msg)
                else:
                    logger.info(msg)

            # Exit if validation failed
            if not is_valid:
                raise ValueError("Request validation failed. See errors above.")

            # Build API request parameters
            params = {'format': api_format}

            if filters:
                # Pass filters as a nested dict, not as flat params
                params['filters'] = filters

            # Fetch data
            data = client.get_data(table_id, **params)

            # Log success
            if isinstance(data, list):
                logger.info(f"Successfully retrieved {len(data)} records")
            elif isinstance(data, dict) and 'data' in data:
                logger.info(f"Successfully retrieved data")
            else:
                logger.info(f"Successfully retrieved data (format: {type(data).__name__})")

            return data

    except DSTAPIError as e:
        # Specific DST API error
        logger.error(f"DST API Error [{e.error_code}]: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        raise


def data_to_csv(data: Union[List[Any], Dict[str, Any]]) -> str:
    """
    Convert data to CSV format.

    Note: DST API uses semicolon (;) as separator, not comma.

    Args:
        data: Data structure from API

    Returns:
        CSV formatted data with semicolon delimiter
    """
    import csv
    from io import StringIO

    output = StringIO()

    # Handle different data structures
    if isinstance(data, list) and len(data) > 0:
        # List of dicts
        if isinstance(data[0], dict):
            writer = csv.DictWriter(output, fieldnames=data[0].keys(), delimiter=';')
            writer.writeheader()
            writer.writerows(data)
        else:
            # List of values
            writer = csv.writer(output, delimiter=';')
            for row in data:
                writer.writerow([row])
    elif isinstance(data, dict):
        # Dict structure - try to find data array
        if 'data' in data:
            return data_to_csv(data['data'])
        else:
            # Convert dict to CSV
            writer = csv.DictWriter(output, fieldnames=data.keys(), delimiter=';')
            writer.writeheader()
            writer.writerow(data)
    else:
        raise ValueError(f"Cannot convert data type {type(data)} to CSV")

    return output.getvalue()


def main() -> None:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch data from a Danmarks Statistik table",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch all data from table
  python fetch_data.py --table-id FOLK1A

  # Fetch with filters (JSON format)
  python fetch_data.py --table-id FOLK1A --filters '{"OMRÅDE":["000"]}'

  # Export to CSV
  python fetch_data.py --table-id FOLK1A --format csv --output data.csv

  # Fetch and save as JSON
  python fetch_data.py --table-id FOLK1A --output data.json
        """
    )

    parser.add_argument(
        '--table-id',
        type=str,
        required=True,
        metavar='ID',
        help='Table identifier (e.g., FOLK1A)'
    )

    parser.add_argument(
        '--filters',
        type=str,
        metavar='JSON',
        help='Filter parameters as JSON string'
    )

    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )

    parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='Save output to file'
    )

    args = parser.parse_args()

    try:
        # Parse filters if provided
        filters = None
        if args.filters:
            try:
                filters = json.loads(args.filters)
            except json.JSONDecodeError as e:
                print(f"✗ Error: Invalid JSON in filters: {e}", file=sys.stderr)
                sys.exit(1)

        # Fetch data
        data = fetch_data(args.table_id, filters, args.format)

        # Format output
        if args.format == 'csv':
            output = data_to_csv(data)
        else:
            output = json.dumps(data, indent=2, ensure_ascii=False)

        # Output to file or stdout
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output, encoding='utf-8')
            print(f"✓ Saved data from {args.table_id} to {args.output}")
        else:
            print(output)

        sys.exit(0)

    except TableNotFoundError as e:
        print(f"✗ Table Error: Table '{e.table_id}' not found in DST database", file=sys.stderr)
        print(f"  Hint: Check table ID spelling or search available tables", file=sys.stderr)
        sys.exit(1)

    except VariableNotFoundError as e:
        print(f"✗ Variable Error: Variable '{e.variable_code}' not found", file=sys.stderr)
        if e.table_id:
            print(f"  in table '{e.table_id}'", file=sys.stderr)
        print(f"  Hint: Use tableinfo to see available variables", file=sys.stderr)
        sys.exit(1)

    except CellLimitExceededError as e:
        print(f"✗ Cell Limit Error: {e.message}", file=sys.stderr)
        print(f"  Hint: Use --format bulk or add more specific filters", file=sys.stderr)
        sys.exit(1)

    except DSTAPIError as e:
        print(f"✗ DST API Error [{e.error_code}]: {e.message}", file=sys.stderr)
        sys.exit(1)

    except ValueError as e:
        # Validation errors
        print(f"✗ Validation Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
