#!/usr/bin/env python3
"""
Database Initialization Script for DST Skills Project

This script creates the DuckDB database and initializes the metadata table
for storing information about DST tables.
"""

import os
import sys
from pathlib import Path
import duckdb
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()


def get_db_path():
    """Get the database path from environment or use default."""
    db_path = os.getenv('DUCKDB_PATH', './data/dst_data.duckdb')
    # Convert relative path to absolute if needed
    if not os.path.isabs(db_path):
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / db_path
    return str(db_path)


def create_database_connection(db_path):
    """
    Create a connection to the DuckDB database.

    Args:
        db_path: Path to the database file

    Returns:
        DuckDB connection object

    Raises:
        Exception: If connection fails
    """
    try:
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        conn = duckdb.connect(db_path)
        print(f"Successfully connected to database at: {db_path}")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise


def create_metadata_table(conn):
    """
    Create the dst_metadata table for storing table metadata.

    Args:
        conn: DuckDB connection object

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create metadata table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dst_metadata (
                table_id VARCHAR PRIMARY KEY,
                table_name VARCHAR,
                last_updated TIMESTAMP,
                fetch_timestamp TIMESTAMP,
                record_count INTEGER,
                columns_json VARCHAR,
                notes VARCHAR
            )
        """)

        # Create index on table_id (redundant with PRIMARY KEY but explicit)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_table_id ON dst_metadata(table_id)
        """)

        print("Successfully created dst_metadata table and index")
        return True
    except Exception as e:
        print(f"Error creating metadata table: {e}")
        return False


def verify_database_integrity(conn):
    """
    Verify that the database is properly initialized.

    Args:
        conn: DuckDB connection object

    Returns:
        bool: True if database is valid, False otherwise
    """
    try:
        # Check if table exists
        result = conn.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'dst_metadata'
        """).fetchone()

        if result[0] == 0:
            print("Error: dst_metadata table not found")
            return False

        # Check table schema
        schema = conn.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'dst_metadata'
            ORDER BY ordinal_position
        """).fetchall()

        expected_columns = {
            'table_id': 'VARCHAR',
            'table_name': 'VARCHAR',
            'last_updated': 'TIMESTAMP',
            'fetch_timestamp': 'TIMESTAMP',
            'record_count': 'INTEGER',
            'columns_json': 'VARCHAR',
            'notes': 'VARCHAR'
        }

        for col_name, col_type in schema:
            if col_name not in expected_columns:
                print(f"Warning: Unexpected column '{col_name}' in schema")
            elif expected_columns[col_name] != col_type:
                print(f"Warning: Column '{col_name}' has type '{col_type}', expected '{expected_columns[col_name]}'")

        print("Database integrity verification passed")
        print(f"Table schema: {len(schema)} columns")
        for col_name, col_type in schema:
            print(f"  - {col_name}: {col_type}")

        return True
    except Exception as e:
        print(f"Error verifying database integrity: {e}")
        return False


def main():
    """Main initialization function."""
    print("="*60)
    print("DST Skills Project - Database Initialization")
    print("="*60)

    try:
        # Get database path
        db_path = get_db_path()
        print(f"\nDatabase path: {db_path}")

        # Create connection
        conn = create_database_connection(db_path)

        # Create metadata table
        if not create_metadata_table(conn):
            print("\nDatabase initialization failed!")
            sys.exit(1)

        # Verify database integrity
        if not verify_database_integrity(conn):
            print("\nDatabase verification failed!")
            sys.exit(1)

        # Close connection
        conn.close()

        print("\n" + "="*60)
        print("Database initialized successfully!")
        print("="*60)

    except Exception as e:
        print(f"\nFatal error during initialization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
