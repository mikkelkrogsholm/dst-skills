#!/usr/bin/env python3
"""Validate DST data after fetching."""

import argparse
import duckdb
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


def validate_fetch(table_id: str) -> dict:
    """
    Validate data after fetch.

    Returns:
        dict with:
        - is_valid: bool
        - record_count: int
        - expected_count: int
        - issues: List[str]
        - warnings: List[str]
    """
    db_path = os.getenv('DUCKDB_PATH', 'data/dst.db')
    conn = duckdb.connect(db_path, read_only=True)

    table_name = f"dst_{table_id.lower()}"
    issues = []
    warnings = []

    # Check table exists
    try:
        result = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        record_count = result[0]
    except Exception as e:
        issues.append(f"Table not found: {table_name}")
        return {
            "is_valid": False,
            "record_count": 0,
            "expected_count": None,
            "issues": issues,
            "warnings": warnings
        }

    # Get expected count from metadata (if available)
    try:
        meta_result = conn.execute(
            f"SELECT row_count FROM dst_metadata WHERE table_id = '{table_id}'"
        ).fetchone()
        expected_count = meta_result[0] if meta_result else None
    except:
        expected_count = None

    # Check for NULL values in key columns
    try:
        null_check = conn.execute(f"""
            SELECT
                SUM(CASE WHEN INDHOLD IS NULL THEN 1 ELSE 0 END) as null_values
            FROM {table_name}
        """).fetchone()

        if null_check[0] > 0:
            warnings.append(f"Found {null_check[0]} NULL values in INDHOLD column")
    except:
        pass  # INDHOLD column may not exist

    # Check for suppressed values (..)
    try:
        suppressed_check = conn.execute(f"""
            SELECT COUNT(*)
            FROM {table_name}
            WHERE INDHOLD = '..'
        """).fetchone()

        if suppressed_check[0] > 0:
            warnings.append(f"Found {suppressed_check[0]} suppressed values ('..')")
    except:
        pass

    # Validate record count matches expected
    if expected_count and record_count != expected_count:
        issues.append(
            f"Record count mismatch: got {record_count}, expected {expected_count}"
        )

    conn.close()

    is_valid = len(issues) == 0

    return {
        "is_valid": is_valid,
        "record_count": record_count,
        "expected_count": expected_count,
        "issues": issues,
        "warnings": warnings
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate DST data")
    parser.add_argument("--table-id", required=True, help="DST table ID")

    args = parser.parse_args()

    result = validate_fetch(args.table_id)

    print(f"\n{'='*70}")
    print(f"VALIDATION REPORT: {args.table_id}")
    print(f"{'='*70}")
    print(f"Record Count: {result['record_count']}")
    if result['expected_count']:
        print(f"Expected Count: {result['expected_count']}")
    print(f"Status: {'✓ VALID' if result['is_valid'] else '✗ INVALID'}")

    if result['issues']:
        print(f"\nISSUES:")
        for issue in result['issues']:
            print(f"  ✗ {issue}")

    if result['warnings']:
        print(f"\nWARNINGS:")
        for warning in result['warnings']:
            print(f"  ⚠ {warning}")

    print(f"{'='*70}\n")

    exit(0 if result['is_valid'] else 1)
