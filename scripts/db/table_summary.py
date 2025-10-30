#!/usr/bin/env python3
"""
Table Summary Script

Generate comprehensive summary statistics for DST tables in DuckDB.
Shows structure, sample data, and statistics.

Usage:
    python table_summary.py --table-id FOLK1A
    python table_summary.py --table-id FOLK1A --format json
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import db_utils
from utils import setup_logger


def get_table_summary(table_id):
    """
    Generate comprehensive summary of a table.

    Args:
        table_id: DST table identifier

    Returns:
        dict: Summary statistics and information

    Raises:
        Exception: If table doesn't exist or query fails
    """
    logger = setup_logger(__name__)

    # Table name convention
    db_table_name = f"dst_{table_id.lower()}"

    try:
        conn = db_utils.get_connection()

        # Check table exists
        if not db_utils.table_exists(conn, db_table_name):
            raise ValueError(f"Table {db_table_name} does not exist in database")

        logger.info(f"Generating summary for {db_table_name}")

        summary = {
            'table_id': table_id,
            'table_name': db_table_name
        }

        # Get metadata if available
        metadata = db_utils.get_metadata(conn, table_id)
        if metadata:
            summary['metadata'] = {
                'record_count': metadata.get('record_count'),
                'fetch_timestamp': metadata.get('fetch_timestamp'),
                'last_updated': metadata.get('last_updated')
            }

        # Get record count
        result = conn.execute(f"SELECT COUNT(*) FROM {db_table_name}").fetchone()
        summary['record_count'] = result[0]

        # Get column information
        columns_info = conn.execute(f"DESCRIBE {db_table_name}").fetchall()
        summary['columns'] = []
        for col in columns_info:
            summary['columns'].append({
                'name': col[0],
                'type': col[1],
                'nullable': col[2]
            })

        # Get sample rows (first 5)
        sample_result = conn.execute(f"SELECT * FROM {db_table_name} LIMIT 5").fetchall()
        col_names = [col[0] for col in columns_info]
        summary['sample_rows'] = []
        for row in sample_result:
            summary['sample_rows'].append(dict(zip(col_names, row)))

        # Get statistics for numeric columns
        summary['statistics'] = {}
        for col_info in columns_info:
            col_name = col_info[0]
            col_type = col_info[1].upper()

            # Check if numeric type
            if any(t in col_type for t in ['INT', 'DOUBLE', 'FLOAT', 'DECIMAL', 'NUMBER']):
                try:
                    stats_query = f"""
                        SELECT
                            MIN({col_name}) as min_val,
                            MAX({col_name}) as max_val,
                            AVG({col_name}) as avg_val,
                            MEDIAN({col_name}) as median_val,
                            COUNT(DISTINCT {col_name}) as distinct_count,
                            COUNT(*) - COUNT({col_name}) as null_count
                        FROM {db_table_name}
                    """
                    stats_result = conn.execute(stats_query).fetchone()

                    summary['statistics'][col_name] = {
                        'min': stats_result[0],
                        'max': stats_result[1],
                        'avg': stats_result[2],
                        'median': stats_result[3],
                        'distinct_count': stats_result[4],
                        'null_count': stats_result[5]
                    }
                except:
                    # Skip if stats fail
                    pass

            # For string/categorical columns, get distinct count
            elif any(t in col_type for t in ['VARCHAR', 'TEXT', 'STRING']):
                try:
                    distinct_query = f"""
                        SELECT
                            COUNT(DISTINCT {col_name}) as distinct_count,
                            COUNT(*) - COUNT({col_name}) as null_count
                        FROM {db_table_name}
                    """
                    distinct_result = conn.execute(distinct_query).fetchone()

                    summary['statistics'][col_name] = {
                        'distinct_count': distinct_result[0],
                        'null_count': distinct_result[1]
                    }

                    # Get top values if reasonable number
                    if distinct_result[0] <= 100:
                        top_values_query = f"""
                            SELECT {col_name}, COUNT(*) as count
                            FROM {db_table_name}
                            WHERE {col_name} IS NOT NULL
                            GROUP BY {col_name}
                            ORDER BY count DESC
                            LIMIT 10
                        """
                        top_values = conn.execute(top_values_query).fetchall()
                        summary['statistics'][col_name]['top_values'] = [
                            {'value': v[0], 'count': v[1]} for v in top_values
                        ]
                except:
                    # Skip if stats fail
                    pass

        db_utils.close_connection(conn)
        logger.info(f"Summary generated successfully")

        return summary

    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")
        if 'conn' in locals():
            db_utils.close_connection(conn)
        raise


def format_summary_text(summary):
    """
    Format summary as human-readable text.

    Args:
        summary: Summary dict

    Returns:
        str: Formatted text
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"TABLE SUMMARY: {summary['table_id']} ({summary['table_name']})")
    lines.append("=" * 80)

    # Metadata
    if 'metadata' in summary and summary['metadata']:
        lines.append("\nMETADATA:")
        lines.append(f"  Record Count:    {summary['metadata'].get('record_count', 'N/A')}")
        lines.append(f"  Fetch Timestamp: {summary['metadata'].get('fetch_timestamp', 'N/A')}")
        lines.append(f"  Last Updated:    {summary['metadata'].get('last_updated', 'N/A')}")

    # Basic info
    lines.append(f"\nRECORD COUNT: {summary['record_count']}")

    # Columns
    lines.append(f"\nCOLUMNS ({len(summary['columns'])}):")
    lines.append(f"  {'Name':<30} {'Type':<20} {'Nullable':<10}")
    lines.append("  " + "-" * 60)
    for col in summary['columns']:
        nullable = "Yes" if col['nullable'] == "YES" else "No"
        lines.append(f"  {col['name']:<30} {col['type']:<20} {nullable:<10}")

    # Statistics
    if summary.get('statistics'):
        lines.append(f"\nSTATISTICS:")
        for col_name, stats in summary['statistics'].items():
            lines.append(f"\n  {col_name}:")
            if 'min' in stats:
                lines.append(f"    Min:             {stats['min']}")
                lines.append(f"    Max:             {stats['max']}")
                lines.append(f"    Average:         {stats['avg']}")
                lines.append(f"    Median:          {stats['median']}")
            lines.append(f"    Distinct values: {stats['distinct_count']}")
            lines.append(f"    NULL count:      {stats['null_count']}")

            if 'top_values' in stats:
                lines.append(f"    Top values:")
                for tv in stats['top_values'][:5]:
                    lines.append(f"      {tv['value']}: {tv['count']}")

    # Sample rows
    if summary.get('sample_rows'):
        lines.append(f"\nSAMPLE ROWS (first 5):")
        for i, row in enumerate(summary['sample_rows'], 1):
            lines.append(f"\n  Row {i}:")
            for key, value in row.items():
                val_str = str(value)[:60]
                lines.append(f"    {key}: {val_str}")

    lines.append("\n" + "=" * 80)

    return '\n'.join(lines)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Generate summary statistics for DST tables in DuckDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get table summary
  python table_summary.py --table-id FOLK1A

  # JSON output
  python table_summary.py --table-id FOLK1A --format json

  # Save to file
  python table_summary.py --table-id FOLK1A --output summary.txt
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
        '--format',
        type=str,
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )

    parser.add_argument(
        '--output',
        type=str,
        metavar='FILE',
        help='Save output to file'
    )

    args = parser.parse_args()

    try:
        # Generate summary
        summary = get_table_summary(args.table_id)

        # Format output
        if args.format == 'json':
            output = json.dumps(summary, indent=2, ensure_ascii=False, default=str)
        else:
            output = format_summary_text(summary)

        # Write to file or stdout
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"✓ Summary saved to {args.output}")
        else:
            print(output)

        sys.exit(0)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
