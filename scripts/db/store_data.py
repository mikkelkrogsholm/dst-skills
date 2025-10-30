#!/usr/bin/env python3
"""
Store DST Data Script

Stores DST data in DuckDB database with metadata tracking.
Reads data from JSON/CSV file and creates tables in DuckDB.

Usage:
    python store_data.py --table-id FOLK1A --data-file data.json
    python store_data.py --table-id FOLK1A --data-file data.json --overwrite
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import db_utils
from utils import setup_logger


def store_data(table_id, data, overwrite=False, update_metadata=True):
    """
    Store data in DuckDB.

    Args:
        table_id: The DST table identifier
        data: Data to store (list of dicts or pandas DataFrame)
        overwrite: Whether to overwrite existing table
        update_metadata: Whether to update metadata table

    Returns:
        dict: Statistics about storage operation

    Raises:
        Exception: If storage fails
    """
    logger = setup_logger(__name__)

    # Table name convention: dst_{table_id} (lowercase)
    db_table_name = f"dst_{table_id.lower()}"

    try:
        # Connect to database
        conn = db_utils.get_connection()

        # Check if table exists
        table_exists = db_utils.table_exists(conn, db_table_name)

        if table_exists and not overwrite:
            raise ValueError(
                f"Table {db_table_name} already exists. "
                f"Use --overwrite to replace it."
            )

        # Convert data to appropriate format for DuckDB
        if isinstance(data, list):
            # Assume list of dicts
            if not data:
                raise ValueError("Cannot store empty data")

            # Use pandas for easier loading
            import pandas as pd
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Check if data is wrapped in a 'data' key
            if 'data' in data and isinstance(data['data'], list):
                import pandas as pd
                df = pd.DataFrame(data['data'])
            else:
                # Try to convert dict to dataframe
                import pandas as pd
                df = pd.DataFrame([data])
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")

        # Drop table if it exists and overwrite is True
        if table_exists and overwrite:
            logger.info(f"Dropping existing table: {db_table_name}")
            conn.execute(f"DROP TABLE {db_table_name}")

        # Create and populate table
        logger.info(f"Creating table: {db_table_name}")
        conn.execute(f"CREATE TABLE {db_table_name} AS SELECT * FROM df")

        # Get record count
        result = conn.execute(f"SELECT COUNT(*) FROM {db_table_name}").fetchone()
        record_count = result[0] if result else 0

        logger.info(f"Stored {record_count} records in {db_table_name}")

        # Update metadata
        if update_metadata:
            logger.info("Updating metadata table")

            # Get column information
            columns_info = []
            for col_name, col_type in zip(df.columns, df.dtypes):
                columns_info.append({
                    'name': col_name,
                    'type': str(col_type)
                })
            columns_json = json.dumps(columns_info)

            # Insert or update metadata
            fetch_timestamp = datetime.now().isoformat()

            # Check if metadata exists
            existing_metadata = conn.execute(
                "SELECT COUNT(*) FROM dst_metadata WHERE table_id = ?",
                [table_id]
            ).fetchone()

            if existing_metadata and existing_metadata[0] > 0:
                # Update existing
                conn.execute("""
                    UPDATE dst_metadata
                    SET fetch_timestamp = ?,
                        record_count = ?,
                        columns_json = ?
                    WHERE table_id = ?
                """, [fetch_timestamp, record_count, columns_json, table_id])
            else:
                # Insert new
                conn.execute("""
                    INSERT INTO dst_metadata
                    (table_id, table_name, fetch_timestamp, record_count, columns_json)
                    VALUES (?, ?, ?, ?, ?)
                """, [table_id, table_id, fetch_timestamp, record_count, columns_json])

            logger.info("Metadata updated successfully")

        # Close connection
        db_utils.close_connection(conn)

        return {
            'table_name': db_table_name,
            'record_count': record_count,
            'overwritten': table_exists and overwrite
        }

    except Exception as e:
        logger.error(f"Failed to store data: {e}")
        # Try to close connection on error
        try:
            if 'conn' in locals():
                db_utils.close_connection(conn)
        except:
            pass
        raise


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Store DST data in DuckDB database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Store data from JSON file
  python store_data.py --table-id FOLK1A --data-file data.json

  # Overwrite existing table
  python store_data.py --table-id FOLK1A --data-file data.json --overwrite

  # Store without updating metadata
  python store_data.py --table-id FOLK1A --data-file data.json --no-update-metadata
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
        '--data-file',
        type=str,
        required=True,
        metavar='FILE',
        help='Path to data file (JSON or CSV)'
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite table if it already exists'
    )

    parser.add_argument(
        '--no-update-metadata',
        action='store_true',
        help='Do not update metadata table'
    )

    args = parser.parse_args()

    try:
        # Read data file
        data_path = Path(args.data_file)
        if not data_path.exists():
            print(f"✗ Error: File not found: {args.data_file}", file=sys.stderr)
            sys.exit(1)

        # Load data based on file extension
        if data_path.suffix.lower() == '.json':
            data = json.loads(data_path.read_text(encoding='utf-8'))
        elif data_path.suffix.lower() == '.csv':
            import pandas as pd
            data = pd.read_csv(data_path).to_dict('records')
        else:
            print(f"✗ Error: Unsupported file format: {data_path.suffix}", file=sys.stderr)
            print("   Supported formats: .json, .csv", file=sys.stderr)
            sys.exit(1)

        # Store data
        result = store_data(
            table_id=args.table_id,
            data=data,
            overwrite=args.overwrite,
            update_metadata=not args.no_update_metadata
        )

        # Print success message
        if result['overwritten']:
            print(f"✓ Replaced table {result['table_name']} with {result['record_count']} records")
        else:
            print(f"✓ Created table {result['table_name']} with {result['record_count']} records")

        sys.exit(0)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
