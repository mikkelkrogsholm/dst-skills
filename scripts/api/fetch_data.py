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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.client import DSTAPIClient
from utils import setup_logger


def fetch_data(table_id, filters=None, format='json'):
    """
    Fetch data from DST API.

    Args:
        table_id: The table identifier
        filters: Optional dict of filter parameters
        format: Output format ('json' or 'csv')

    Returns:
        dict or str: Data in requested format

    Raises:
        Exception: If API request fails
    """
    logger = setup_logger(__name__)

    try:
        with DSTAPIClient() as client:
            logger.info(f"Fetching data for table: {table_id}")

            # Build request parameters
            params = {}
            if filters:
                # Filters should be passed as part of params
                # DST API expects specific format
                logger.info(f"Applying filters: {filters}")
                # Note: The actual filter format depends on DST API specification
                # This is a simplified version
                params.update(filters)

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

    except Exception as e:
        logger.error(f"Failed to fetch data: {e}")
        raise


def data_to_csv(data):
    """
    Convert data to CSV format.

    Args:
        data: Data structure from API

    Returns:
        str: CSV formatted data
    """
    import csv
    from io import StringIO

    output = StringIO()

    # Handle different data structures
    if isinstance(data, list) and len(data) > 0:
        # List of dicts
        if isinstance(data[0], dict):
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        else:
            # List of values
            writer = csv.writer(output)
            for row in data:
                writer.writerow([row])
    elif isinstance(data, dict):
        # Dict structure - try to find data array
        if 'data' in data:
            return data_to_csv(data['data'])
        else:
            # Convert dict to CSV
            writer = csv.DictWriter(output, fieldnames=data.keys())
            writer.writeheader()
            writer.writerow(data)
    else:
        raise ValueError(f"Cannot convert data type {type(data)} to CSV")

    return output.getvalue()


def main():
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

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
