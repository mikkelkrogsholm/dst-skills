#!/usr/bin/env python3
"""
Get DST Table Info Script

Fetches detailed metadata for a specific DST table including structure,
variables, dimensions, and available values.

Usage:
    python get_tableinfo.py --table-id FOLK1A
    python get_tableinfo.py --table-id FOLK1A --verbose
    python get_tableinfo.py --table-id FOLK1A --output info.json
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.client import DSTAPIClient
from utils import setup_logger


def get_tableinfo(table_id):
    """
    Fetch detailed metadata for a DST table.

    Args:
        table_id: The table identifier

    Returns:
        dict: Table metadata including structure and variables

    Raises:
        Exception: If API request fails
    """
    logger = setup_logger(__name__)

    try:
        with DSTAPIClient() as client:
            logger.info(f"Fetching table info for: {table_id}")
            info = client.get_table_info(table_id)
            logger.info(f"Successfully retrieved metadata for table {table_id}")
            return info
    except Exception as e:
        logger.error(f"Failed to fetch table info: {e}")
        raise


def format_verbose_output(info):
    """
    Format table info as human-readable text.

    Args:
        info: Table metadata dict

    Returns:
        str: Formatted text output
    """
    lines = []
    lines.append("=" * 70)
    lines.append(f"TABLE INFO: {info.get('id', 'N/A')}")
    lines.append("=" * 70)

    # Basic info
    lines.append(f"\nName: {info.get('text', 'N/A')}")
    lines.append(f"Description: {info.get('description', 'N/A')}")
    lines.append(f"Unit: {info.get('unit', 'N/A')}")
    lines.append(f"Updated: {info.get('updated', 'N/A')}")

    # Variables
    variables = info.get('variables', [])
    if variables:
        lines.append(f"\n{'-' * 70}")
        lines.append(f"VARIABLES ({len(variables)}):")
        lines.append(f"{'-' * 70}")

        for var in variables:
            var_id = var.get('id', 'N/A')
            var_text = var.get('text', 'N/A')
            values = var.get('values', [])
            lines.append(f"\n  • {var_id}: {var_text}")
            lines.append(f"    Values: {len(values)} options")

            # Show first few values as examples
            if values and len(values) > 0:
                lines.append(f"    Examples:")
                for val in values[:5]:  # Show first 5
                    val_id = val.get('id', 'N/A')
                    val_text = val.get('text', 'N/A')
                    lines.append(f"      - {val_id}: {val_text}")
                if len(values) > 5:
                    lines.append(f"      ... and {len(values) - 5} more")

    lines.append(f"\n{'=' * 70}")

    return '\n'.join(lines)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Get detailed metadata for a Danmarks Statistik table",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get table info (JSON output)
  python get_tableinfo.py --table-id FOLK1A

  # Get table info with verbose formatting
  python get_tableinfo.py --table-id FOLK1A --verbose

  # Save to file
  python get_tableinfo.py --table-id FOLK1A --output folk1a_info.json

  # Verbose and save
  python get_tableinfo.py --table-id FOLK1A --verbose --output info.txt
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
        '--verbose',
        action='store_true',
        help='Display formatted, human-readable output'
    )

    parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='Save output to file'
    )

    args = parser.parse_args()

    try:
        # Fetch table info
        info = get_tableinfo(args.table_id)

        # Format output
        if args.verbose:
            output = format_verbose_output(info)
        else:
            output = json.dumps(info, indent=2, ensure_ascii=False)

        # Output to file or stdout
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output, encoding='utf-8')
            print(f"✓ Saved table info for {args.table_id} to {args.output}")
        else:
            print(output)

        sys.exit(0)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
