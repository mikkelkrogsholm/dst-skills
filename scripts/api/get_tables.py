#!/usr/bin/env python3
"""
Get DST Tables Script

Search and list DST tables by subject or keyword.
Tables contain the actual statistical data organized by subjects.

Usage:
    python get_tables.py                           # List all tables
    python get_tables.py --subject 02             # Tables in subject 02
    python get_tables.py --search "population"     # Search by keyword
    python get_tables.py --subject 02 --search "age"  # Combined filter
    python get_tables.py --output tables.json      # Save to file
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.client import DSTAPIClient
from utils import setup_logger


def get_tables(subject_id=None, search_term=None):
    """
    Fetch tables from DST API, optionally filtered.

    Args:
        subject_id: Optional subject ID to filter by
        search_term: Optional keyword to search for

    Returns:
        list: List of table objects

    Raises:
        Exception: If API request fails
    """
    logger = setup_logger(__name__)

    try:
        with DSTAPIClient() as client:
            # Get tables from API
            tables = client.get_tables(subjects=subject_id)

            # Apply keyword search filter if specified
            if search_term:
                search_lower = search_term.lower()
                filtered_tables = []
                for table in tables:
                    text = table.get('text', '').lower()
                    description = table.get('description', '').lower()
                    if search_lower in text or search_lower in description:
                        filtered_tables.append(table)
                tables = filtered_tables
                logger.info(f"Filtered to {len(tables)} tables matching '{search_term}'")
            else:
                logger.info(f"Successfully retrieved {len(tables)} tables")

            return tables

    except Exception as e:
        logger.error(f"Failed to fetch tables: {e}")
        raise


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Search and list Danmarks Statistik tables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all tables
  python get_tables.py

  # Tables in subject 02 (Labour, income and wealth)
  python get_tables.py --subject 02

  # Search for tables about population
  python get_tables.py --search "population"

  # Combined: subject and keyword
  python get_tables.py --subject 02 --search "age"

  # Save to file
  python get_tables.py --subject 02 --output tables.json
        """
    )

    parser.add_argument(
        '--subject',
        type=str,
        metavar='ID',
        help='Filter by subject ID (e.g., 02)'
    )

    parser.add_argument(
        '--search',
        type=str,
        metavar='TERM',
        help='Search by keyword in table name or description'
    )

    parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='Save output to JSON file'
    )

    args = parser.parse_args()

    try:
        # Fetch tables
        tables = get_tables(
            subject_id=args.subject,
            search_term=args.search
        )

        # Format output
        output_json = json.dumps(tables, indent=2, ensure_ascii=False)

        # Output to file or stdout
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output_json, encoding='utf-8')
            print(f"✓ Saved {len(tables)} tables to {args.output}")
        else:
            print(output_json)

        sys.exit(0)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
