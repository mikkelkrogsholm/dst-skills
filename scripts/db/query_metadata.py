#!/usr/bin/env python3
"""
Query Metadata Script

Query and display metadata for DST tables stored in DuckDB.
Supports listing all tables, getting specific table metadata, and checking data freshness.

Usage:
    python query_metadata.py --list-all
    python query_metadata.py --table-id FOLK1A
    python query_metadata.py --table-id FOLK1A --check-freshness
    python query_metadata.py --table-id FOLK1A --check-freshness --max-age-days 30
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import db_utils
from utils import setup_logger


def calculate_age_string(timestamp):
    """
    Calculate human-readable age from timestamp.

    Args:
        timestamp: Datetime object or ISO string

    Returns:
        str: Human-readable age (e.g., "5 days ago", "2 hours ago")
    """
    if timestamp is None:
        return "Unknown"

    # Parse if string
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except:
            return "Invalid timestamp"

    # Calculate age
    age = datetime.now() - timestamp

    if age.days > 365:
        years = age.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif age.days > 30:
        months = age.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif age.days > 0:
        return f"{age.days} day{'s' if age.days > 1 else ''} ago"
    elif age.seconds > 3600:
        hours = age.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif age.seconds > 60:
        minutes = age.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


def list_all_tables(format='table'):
    """
    List all tables in metadata.

    Args:
        format: Output format ('table' or 'json')

    Returns:
        str or list: Formatted output
    """
    logger = setup_logger(__name__)

    try:
        conn = db_utils.get_connection()
        tables = db_utils.list_all_tables(conn)
        db_utils.close_connection(conn)

        # Add age calculation
        for table in tables:
            table['age'] = calculate_age_string(table['fetch_timestamp'])

        if format == 'json':
            return tables
        else:
            # Format as table
            lines = []
            lines.append("=" * 100)
            lines.append("DST TABLES IN LOCAL DATABASE")
            lines.append("=" * 100)

            if not tables:
                lines.append("\nNo tables found in database.")
            else:
                lines.append(f"\nFound {len(tables)} table(s):\n")
                lines.append(f"{'ID':<15} {'Name':<35} {'Records':<10} {'Age':<20}")
                lines.append("-" * 100)

                for table in tables:
                    table_id = table.get('table_id', 'N/A')[:15]
                    table_name = table.get('table_name', 'N/A')[:35]
                    record_count = table.get('record_count', 0)
                    age = table.get('age', 'Unknown')[:20]

                    lines.append(f"{table_id:<15} {table_name:<35} {record_count:<10} {age:<20}")

            lines.append("=" * 100)
            return '\n'.join(lines)

    except Exception as e:
        logger.error(f"Failed to list tables: {e}")
        raise


def get_metadata(table_id, format='table'):
    """
    Get metadata for specific table.

    Args:
        table_id: Table identifier
        format: Output format ('table' or 'json')

    Returns:
        str or dict: Formatted metadata
    """
    logger = setup_logger(__name__)

    try:
        conn = db_utils.get_connection()
        metadata = db_utils.get_metadata(conn, table_id)
        db_utils.close_connection(conn)

        if metadata is None:
            raise ValueError(f"Table {table_id} not found in metadata")

        # Add age calculation
        metadata['age'] = calculate_age_string(metadata.get('fetch_timestamp'))

        if format == 'json':
            return metadata
        else:
            # Format as readable text
            lines = []
            lines.append("=" * 70)
            lines.append(f"METADATA FOR TABLE: {table_id}")
            lines.append("=" * 70)
            lines.append(f"Table ID:        {metadata.get('table_id', 'N/A')}")
            lines.append(f"Table Name:      {metadata.get('table_name', 'N/A')}")
            lines.append(f"Record Count:    {metadata.get('record_count', 'N/A')}")
            lines.append(f"Last Updated:    {metadata.get('last_updated', 'N/A')}")
            lines.append(f"Fetch Timestamp: {metadata.get('fetch_timestamp', 'N/A')}")
            lines.append(f"Data Age:        {metadata.get('age', 'Unknown')}")
            if metadata.get('notes'):
                lines.append(f"Notes:           {metadata.get('notes')}")
            lines.append("=" * 70)
            return '\n'.join(lines)

    except Exception as e:
        logger.error(f"Failed to get metadata: {e}")
        raise


def check_freshness(table_id, max_age_days=None):
    """
    Check data freshness for a table.

    Args:
        table_id: Table identifier
        max_age_days: Optional age threshold in days

    Returns:
        str: Formatted freshness report
    """
    logger = setup_logger(__name__)

    try:
        conn = db_utils.get_connection()
        metadata = db_utils.get_metadata(conn, table_id)
        db_utils.close_connection(conn)

        if metadata is None:
            raise ValueError(f"Table {table_id} not found in metadata")

        fetch_timestamp = metadata.get('fetch_timestamp')
        if fetch_timestamp is None:
            return "✗ No fetch timestamp available"

        # Parse timestamp
        if isinstance(fetch_timestamp, str):
            fetch_time = datetime.fromisoformat(fetch_timestamp)
        else:
            fetch_time = fetch_timestamp

        # Calculate age
        age = datetime.now() - fetch_time
        age_days = age.days
        age_str = calculate_age_string(fetch_time)

        # Build report
        lines = []
        lines.append("=" * 70)
        lines.append(f"FRESHNESS CHECK FOR TABLE: {table_id}")
        lines.append("=" * 70)
        lines.append(f"Table Name:      {metadata.get('table_name', 'N/A')}")
        lines.append(f"Last Updated:    {metadata.get('last_updated', 'N/A')}")
        lines.append(f"Fetch Timestamp: {fetch_timestamp}")
        lines.append(f"Data Age:        {age_str} ({age_days} days)")

        if max_age_days is not None:
            is_fresh = age_days <= max_age_days
            lines.append(f"Threshold:       {max_age_days} days")
            lines.append(f"Status:          {'✓ FRESH' if is_fresh else '✗ STALE'}")

            if is_fresh:
                lines.append(f"\n→ Data is within acceptable age threshold")
            else:
                lines.append(f"\n→ Data exceeds age threshold - consider refreshing")

        lines.append("=" * 70)
        return '\n'.join(lines)

    except Exception as e:
        logger.error(f"Failed to check freshness: {e}")
        raise


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Query metadata for DST tables in DuckDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all stored tables
  python query_metadata.py --list-all

  # Get metadata for specific table
  python query_metadata.py --table-id FOLK1A

  # Check data freshness
  python query_metadata.py --table-id FOLK1A --check-freshness

  # Check freshness with 30-day threshold
  python query_metadata.py --table-id FOLK1A --check-freshness --max-age-days 30

  # JSON output
  python query_metadata.py --list-all --format json
        """
    )

    parser.add_argument(
        '--list-all',
        action='store_true',
        help='List all tables in metadata'
    )

    parser.add_argument(
        '--table-id',
        type=str,
        metavar='ID',
        help='Table identifier for specific query'
    )

    parser.add_argument(
        '--check-freshness',
        action='store_true',
        help='Check data freshness (requires --table-id)'
    )

    parser.add_argument(
        '--max-age-days',
        type=int,
        metavar='DAYS',
        help='Freshness threshold in days'
    )

    parser.add_argument(
        '--format',
        type=str,
        choices=['table', 'json'],
        default='table',
        help='Output format (default: table)'
    )

    args = parser.parse_args()

    try:
        # Validate arguments
        if args.check_freshness and not args.table_id:
            print("✗ Error: --check-freshness requires --table-id", file=sys.stderr)
            sys.exit(1)

        if args.max_age_days and not args.check_freshness:
            print("✗ Error: --max-age-days requires --check-freshness", file=sys.stderr)
            sys.exit(1)

        # Execute command
        if args.list_all:
            result = list_all_tables(format=args.format)
            if args.format == 'json':
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(result)

        elif args.check_freshness:
            result = check_freshness(args.table_id, args.max_age_days)
            print(result)

        elif args.table_id:
            result = get_metadata(args.table_id, format=args.format)
            if args.format == 'json':
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(result)

        else:
            parser.print_help()
            sys.exit(1)

        sys.exit(0)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
