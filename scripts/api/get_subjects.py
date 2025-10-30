#!/usr/bin/env python3
"""
Get DST Subjects Script

Fetches the subject hierarchy from Statistics Denmark API.
Subjects are the top-level organizational structure for DST data.

Usage:
    python get_subjects.py                    # Get all subjects
    python get_subjects.py --recursive        # Get complete hierarchy
    python get_subjects.py --output file.json # Save to file
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.client import DSTAPIClient
from utils import setup_logger


def get_subjects(recursive=False):
    """
    Fetch subjects from DST API.

    Args:
        recursive: If True, fetch all subject levels

    Returns:
        list: List of subject objects

    Raises:
        Exception: If API request fails
    """
    logger = setup_logger(__name__)

    try:
        with DSTAPIClient() as client:
            logger.info(f"Fetching subjects (recursive={recursive})")
            subjects = client.get_subjects(recursive=recursive)
            logger.info(f"Successfully retrieved {len(subjects)} subjects")
            return subjects
    except Exception as e:
        logger.error(f"Failed to fetch subjects: {e}")
        raise


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch Danmarks Statistik subject hierarchy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get all subjects
  python get_subjects.py

  # Get complete subject hierarchy
  python get_subjects.py --recursive

  # Save to file
  python get_subjects.py --output subjects.json

  # Recursive save to file
  python get_subjects.py --recursive --output subjects_full.json
        """
    )

    parser.add_argument(
        '--recursive',
        action='store_true',
        help='Get all subject levels recursively'
    )

    parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='Save output to JSON file'
    )

    args = parser.parse_args()

    try:
        # Fetch subjects
        subjects = get_subjects(recursive=args.recursive)

        # Format output
        output_json = json.dumps(subjects, indent=2, ensure_ascii=False)

        # Output to file or stdout
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output_json, encoding='utf-8')
            print(f"✓ Saved {len(subjects)} subjects to {args.output}")
        else:
            print(output_json)

        sys.exit(0)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
