#!/usr/bin/env python3
"""
Fetch and Store DST Data Script

Combined workflow that fetches data from DST API and stores it in DuckDB.
This is the recommended way to download and persist DST data.

Usage:
    python fetch_and_store.py --table-id FOLK1A
    python fetch_and_store.py --table-id FOLK1A --overwrite
    python fetch_and_store.py --table-id FOLK1A --skip-if-fresh --max-age-days 30
    python fetch_and_store.py --table-id FOLK1A --filters '{"OMRÅDE":["000"]}'
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api.client import DSTAPIClient
from api import fetch_data
from db import db_utils, store_data
from utils import setup_logger


def check_data_freshness(conn, table_id, max_age_days=30):
    """
    Check if locally stored data is fresh enough.

    Args:
        conn: Database connection
        table_id: Table identifier
        max_age_days: Maximum acceptable age in days

    Returns:
        tuple: (is_fresh, metadata_dict)
    """
    logger = setup_logger(__name__)

    try:
        metadata = db_utils.get_metadata(conn, table_id)

        if metadata is None:
            logger.info(f"No existing data for {table_id}")
            return False, None

        if metadata['fetch_timestamp'] is None:
            logger.info(f"No fetch timestamp for {table_id}")
            return False, metadata

        # Parse fetch timestamp
        if isinstance(metadata['fetch_timestamp'], str):
            fetch_time = datetime.fromisoformat(metadata['fetch_timestamp'])
        else:
            fetch_time = metadata['fetch_timestamp']

        # Calculate age
        age = datetime.now() - fetch_time
        age_days = age.days

        is_fresh = age_days <= max_age_days

        logger.info(
            f"Data age for {table_id}: {age_days} days "
            f"(threshold: {max_age_days} days) - "
            f"{'FRESH' if is_fresh else 'STALE'}"
        )

        return is_fresh, metadata

    except Exception as e:
        logger.error(f"Error checking freshness: {e}")
        return False, None


def fetch_and_store(table_id, filters=None, overwrite=False, skip_if_fresh=False, max_age_days=30):
    """
    Fetch data from DST API and store in DuckDB.

    Args:
        table_id: Table identifier
        filters: Optional filters for data fetch
        overwrite: Whether to overwrite existing data
        skip_if_fresh: Skip if data is fresh enough
        max_age_days: Freshness threshold in days

    Returns:
        dict: Result statistics

    Raises:
        Exception: If any step fails
    """
    logger = setup_logger(__name__)

    try:
        logger.info(f"Starting fetch and store workflow for {table_id}")

        # Step 1: Check freshness if requested
        if skip_if_fresh:
            conn = db_utils.get_connection()
            is_fresh, metadata = check_data_freshness(conn, table_id, max_age_days)
            db_utils.close_connection(conn)

            if is_fresh:
                logger.info(f"Data for {table_id} is fresh, skipping fetch")
                return {
                    'status': 'skipped',
                    'reason': 'data_is_fresh',
                    'table_id': table_id
                }

        # Step 2: Get table info for metadata
        logger.info("Fetching table info for metadata")
        with DSTAPIClient() as client:
            table_info = client.get_table_info(table_id)

        # Step 3: Fetch data
        logger.info("Fetching data from API")
        data = fetch_data.fetch_data(table_id, filters)

        # Step 4: Store in DuckDB
        logger.info("Storing data in DuckDB")
        store_result = store_data.store_data(
            table_id=table_id,
            data=data,
            overwrite=overwrite,
            update_metadata=True
        )

        # Step 5: Update additional metadata from table info
        logger.info("Updating metadata with table info")
        conn = db_utils.get_connection()

        # Parse last updated from table info if available
        last_updated = table_info.get('updated')
        table_name = table_info.get('text', table_id)

        db_utils.update_metadata(
            conn,
            table_id=table_id,
            table_name=table_name,
            last_updated=last_updated
        )

        db_utils.close_connection(conn)

        # Step 6: Build result
        result = {
            'status': 'success',
            'table_id': table_id,
            'table_name': store_result['table_name'],
            'record_count': store_result['record_count'],
            'overwritten': store_result['overwritten']
        }

        logger.info(f"Successfully completed fetch and store for {table_id}")
        return result

    except Exception as e:
        logger.error(f"Fetch and store failed: {e}")
        raise


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch DST data and store in DuckDB (combined workflow)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch and store table
  python fetch_and_store.py --table-id FOLK1A

  # Overwrite existing data
  python fetch_and_store.py --table-id FOLK1A --overwrite

  # Skip if data is less than 30 days old
  python fetch_and_store.py --table-id FOLK1A --skip-if-fresh --max-age-days 30

  # Fetch with filters
  python fetch_and_store.py --table-id FOLK1A --filters '{"OMRÅDE":["000"]}'

  # Combine options
  python fetch_and_store.py --table-id FOLK1A --overwrite --filters '{"TID":["2024*"]}'
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
        '--overwrite',
        action='store_true',
        help='Overwrite existing data if table exists'
    )

    parser.add_argument(
        '--skip-if-fresh',
        action='store_true',
        help='Skip fetch if data is fresh (within max-age-days)'
    )

    parser.add_argument(
        '--max-age-days',
        type=int,
        default=30,
        metavar='DAYS',
        help='Maximum acceptable data age in days (default: 30)'
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

        # Execute fetch and store
        result = fetch_and_store(
            table_id=args.table_id,
            filters=filters,
            overwrite=args.overwrite,
            skip_if_fresh=args.skip_if_fresh,
            max_age_days=args.max_age_days
        )

        # Print result
        if result['status'] == 'skipped':
            print(f"⊘ Skipped {result['table_id']}: {result['reason']}")
            sys.exit(2)  # Exit code 2 for skipped
        elif result['status'] == 'success':
            if result['overwritten']:
                print(f"✓ Updated table {result['table_name']} with {result['record_count']} records")
            else:
                print(f"✓ Created table {result['table_name']} with {result['record_count']} records")
            sys.exit(0)
        else:
            print(f"✗ Unknown status: {result['status']}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
