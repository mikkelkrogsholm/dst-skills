#!/usr/bin/env python3
"""
Query Data Script

Execute SQL queries on DST data stored in DuckDB.
Supports various output formats and safety features.

Usage:
    python query_data.py --sql "SELECT * FROM dst_folk1a LIMIT 10"
    python query_data.py --sql "SELECT * FROM dst_folk1a" --limit 100
    python query_data.py --sql "SELECT * FROM dst_folk1a" --format json
    python query_data.py --sql "SELECT * FROM dst_folk1a" --output results.csv --format csv
"""

import sys
import json
import argparse
from pathlib import Path
import csv
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import db_utils
from utils import setup_logger


def validate_query(sql):
    """
    Validate that query is safe (SELECT only).

    Args:
        sql: SQL query string

    Returns:
        tuple: (is_valid, error_message)
    """
    sql_upper = sql.strip().upper()

    # Check if it's a SELECT query
    if not sql_upper.startswith('SELECT'):
        return False, "Only SELECT queries are allowed (read-only)"

    # Check for dangerous keywords
    dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False, f"Query contains prohibited keyword: {keyword}"

    return True, None


def execute_query(sql, format='table', limit=None):
    """
    Execute SQL query on DuckDB.

    Args:
        sql: SQL query string
        format: Output format ('table', 'json', 'csv')
        limit: Optional result limit

    Returns:
        str or list: Query results in requested format

    Raises:
        Exception: If query fails
    """
    logger = setup_logger(__name__)

    # Validate query
    is_valid, error_msg = validate_query(sql)
    if not is_valid:
        raise ValueError(f"Invalid query: {error_msg}")

    # Add LIMIT if specified and not already present
    if limit and 'LIMIT' not in sql.upper():
        sql = f"{sql.rstrip(';')} LIMIT {limit}"
        logger.info(f"Added LIMIT {limit} to query")

    try:
        # Connect and execute
        conn = db_utils.get_connection()
        logger.info(f"Executing query: {sql}")

        result = conn.execute(sql).fetchall()
        columns = [desc[0] for desc in conn.execute(sql).description]

        db_utils.close_connection(conn)

        logger.info(f"Query returned {len(result)} rows")

        # Format output
        if format == 'json':
            # Convert to list of dicts
            output = []
            for row in result:
                output.append(dict(zip(columns, row)))
            return output

        elif format == 'csv':
            # Convert to CSV string
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(columns)
            writer.writerows(result)
            return output.getvalue()

        else:  # table format
            # Format as ASCII table
            if not result:
                return "No results returned."

            # Calculate column widths
            col_widths = []
            for i, col_name in enumerate(columns):
                max_width = len(col_name)
                for row in result:
                    val_str = str(row[i]) if row[i] is not None else "NULL"
                    max_width = max(max_width, len(val_str))
                col_widths.append(min(max_width, 50))  # Cap at 50 chars

            # Build table
            lines = []
            lines.append("=" * (sum(col_widths) + len(columns) * 3 + 1))

            # Header
            header = "| "
            for col_name, width in zip(columns, col_widths):
                header += f"{col_name:<{width}} | "
            lines.append(header)
            lines.append("-" * (sum(col_widths) + len(columns) * 3 + 1))

            # Rows
            for row in result[:1000]:  # Limit display to 1000 rows
                row_str = "| "
                for val, width in zip(row, col_widths):
                    val_str = str(val) if val is not None else "NULL"
                    if len(val_str) > width:
                        val_str = val_str[:width-3] + "..."
                    row_str += f"{val_str:<{width}} | "
                lines.append(row_str)

            if len(result) > 1000:
                lines.append(f"\n... and {len(result) - 1000} more rows")

            lines.append("=" * (sum(col_widths) + len(columns) * 3 + 1))
            lines.append(f"\n{len(result)} rows returned")

            return '\n'.join(lines)

    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Execute SQL queries on DST data in DuckDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple query
  python query_data.py --sql "SELECT * FROM dst_folk1a LIMIT 10"

  # Aggregation
  python query_data.py --sql "SELECT year, SUM(population) FROM dst_folk1a GROUP BY year"

  # With automatic limit
  python query_data.py --sql "SELECT * FROM dst_folk1a" --limit 100

  # JSON output
  python query_data.py --sql "SELECT * FROM dst_folk1a LIMIT 10" --format json

  # CSV output to file
  python query_data.py --sql "SELECT * FROM dst_folk1a" --format csv --output results.csv

Note: Only SELECT queries are allowed (read-only). Table names are dst_{table_id} in lowercase.
        """
    )

    parser.add_argument(
        '--sql',
        type=str,
        required=True,
        metavar='QUERY',
        help='SQL query to execute (must be SELECT)'
    )

    parser.add_argument(
        '--format',
        type=str,
        choices=['table', 'json', 'csv'],
        default='table',
        help='Output format (default: table)'
    )

    parser.add_argument(
        '--limit',
        type=int,
        metavar='N',
        help='Limit results to N rows (safety feature)'
    )

    parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='Save output to file'
    )

    args = parser.parse_args()

    try:
        # Execute query
        result = execute_query(args.sql, format=args.format, limit=args.limit)

        # Format output
        if args.format == 'json':
            output = json.dumps(result, indent=2, ensure_ascii=False, default=str)
        else:
            output = result

        # Write to file or stdout
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"✓ Query results saved to {args.output}")
        else:
            print(output)

        sys.exit(0)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
