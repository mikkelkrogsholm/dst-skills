#!/usr/bin/env python3
"""
Database Utility Module for DST Skills Project

This module provides utility functions for interacting with the DuckDB database.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import duckdb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_db_path() -> str:
    """
    Get the database path from environment or use default.

    Returns:
        Absolute path to the database file
    """
    db_path = os.getenv('DUCKDB_PATH', './data/dst_data.duckdb')
    # Convert relative path to absolute if needed
    if not os.path.isabs(db_path):
        project_root = Path(__file__).parent.parent.parent
        db_path = project_root / db_path
    return str(db_path)


def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Create and return a connection to the DuckDB database.

    Returns:
        Database connection object

    Raises:
        Exception: If connection fails
    """
    try:
        db_path = get_db_path()
        conn = duckdb.connect(db_path)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise


def close_connection(conn: Optional[duckdb.DuckDBPyConnection]) -> bool:
    """
    Safely close a database connection.

    Args:
        conn: DuckDB connection object to close

    Returns:
        True if successful, False otherwise
    """
    try:
        if conn is not None:
            conn.close()
        return True
    except Exception as e:
        print(f"Error closing connection: {e}")
        return False


def table_exists(conn: duckdb.DuckDBPyConnection, table_name: str) -> bool:
    """
    Check if a table exists in the database.

    Args:
        conn: DuckDB connection object
        table_name: Name of the table to check

    Returns:
        True if table exists, False otherwise
    """
    try:
        result = conn.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = ?
        """, [table_name]).fetchone()

        return result[0] > 0
    except Exception as e:
        print(f"Error checking if table exists: {e}")
        return False


def get_metadata(conn: duckdb.DuckDBPyConnection, table_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve metadata for a specific DST table.

    Args:
        conn: DuckDB connection object
        table_id: ID of the table to retrieve metadata for

    Returns:
        Dictionary containing metadata fields, or None if not found

    Raises:
        Exception: If query fails
    """
    try:
        result = conn.execute("""
            SELECT
                table_id,
                table_name,
                last_updated,
                fetch_timestamp,
                record_count,
                columns_json,
                notes
            FROM dst_metadata
            WHERE table_id = ?
        """, [table_id]).fetchone()

        if result is None:
            return None

        return {
            'table_id': result[0],
            'table_name': result[1],
            'last_updated': result[2],
            'fetch_timestamp': result[3],
            'record_count': result[4],
            'columns_json': result[5],
            'notes': result[6]
        }
    except Exception as e:
        print(f"Error retrieving metadata for table '{table_id}': {e}")
        raise


def update_metadata(conn: duckdb.DuckDBPyConnection, table_id: str, **kwargs: Any) -> bool:
    """
    Update or insert metadata for a DST table.

    Args:
        conn: DuckDB connection object
        table_id: ID of the table to update
        **kwargs: Metadata fields to update (table_name, last_updated, fetch_timestamp,
                  record_count, columns_json, notes)

    Returns:
        True if successful, False otherwise

    Raises:
        Exception: If update fails
    """
    try:
        # Check if record exists
        exists = conn.execute("""
            SELECT COUNT(*)
            FROM dst_metadata
            WHERE table_id = ?
        """, [table_id]).fetchone()[0] > 0

        if exists:
            # Update existing record
            update_fields = []
            params = []

            for field in ['table_name', 'last_updated', 'fetch_timestamp',
                          'record_count', 'columns_json', 'notes']:
                if field in kwargs:
                    update_fields.append(f"{field} = ?")
                    params.append(kwargs[field])

            if not update_fields:
                print("Warning: No fields to update")
                return True

            params.append(table_id)
            query = f"""
                UPDATE dst_metadata
                SET {', '.join(update_fields)}
                WHERE table_id = ?
            """
            conn.execute(query, params)

        else:
            # Insert new record
            conn.execute("""
                INSERT INTO dst_metadata (
                    table_id,
                    table_name,
                    last_updated,
                    fetch_timestamp,
                    record_count,
                    columns_json,
                    notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                table_id,
                kwargs.get('table_name'),
                kwargs.get('last_updated'),
                kwargs.get('fetch_timestamp', datetime.now()),
                kwargs.get('record_count'),
                kwargs.get('columns_json'),
                kwargs.get('notes')
            ])

        return True
    except Exception as e:
        print(f"Error updating metadata for table '{table_id}': {e}")
        raise


def list_all_tables(conn: duckdb.DuckDBPyConnection) -> List[Dict[str, Any]]:
    """
    Get a list of all DST tables tracked in metadata.

    Args:
        conn: DuckDB connection object

    Returns:
        List of dictionaries containing table metadata
    """
    try:
        result = conn.execute("""
            SELECT
                table_id,
                table_name,
                last_updated,
                fetch_timestamp,
                record_count
            FROM dst_metadata
            ORDER BY table_id
        """).fetchall()

        return [
            {
                'table_id': row[0],
                'table_name': row[1],
                'last_updated': row[2],
                'fetch_timestamp': row[3],
                'record_count': row[4]
            }
            for row in result
        ]
    except Exception as e:
        print(f"Error listing tables: {e}")
        raise


def delete_metadata(conn: duckdb.DuckDBPyConnection, table_id: str) -> bool:
    """
    Delete metadata for a specific DST table.

    Args:
        conn: DuckDB connection object
        table_id: ID of the table to delete metadata for

    Returns:
        True if successful, False otherwise
    """
    try:
        conn.execute("""
            DELETE FROM dst_metadata
            WHERE table_id = ?
        """, [table_id])
        return True
    except Exception as e:
        print(f"Error deleting metadata for table '{table_id}': {e}")
        return False


# Example usage and testing
if __name__ == "__main__":
    print("Testing database utility functions...")

    try:
        # Test connection
        print("\n1. Testing get_connection()...")
        conn = get_connection()
        print("✓ Connection successful")

        # Test table_exists
        print("\n2. Testing table_exists()...")
        exists = table_exists(conn, 'dst_metadata')
        print(f"✓ dst_metadata table exists: {exists}")

        # Test update_metadata (insert)
        print("\n3. Testing update_metadata() - insert...")
        update_metadata(
            conn,
            table_id='TEST001',
            table_name='Test Table',
            record_count=100,
            notes='Test metadata entry'
        )
        print("✓ Metadata inserted")

        # Test get_metadata
        print("\n4. Testing get_metadata()...")
        metadata = get_metadata(conn, 'TEST001')
        print(f"✓ Retrieved metadata: {metadata}")

        # Test update_metadata (update)
        print("\n5. Testing update_metadata() - update...")
        update_metadata(
            conn,
            table_id='TEST001',
            record_count=200,
            notes='Updated test metadata'
        )
        metadata = get_metadata(conn, 'TEST001')
        print(f"✓ Updated metadata: record_count={metadata['record_count']}")

        # Test list_all_tables
        print("\n6. Testing list_all_tables()...")
        tables = list_all_tables(conn)
        print(f"✓ Found {len(tables)} table(s)")

        # Test delete_metadata
        print("\n7. Testing delete_metadata()...")
        delete_metadata(conn, 'TEST001')
        metadata = get_metadata(conn, 'TEST001')
        print(f"✓ Metadata deleted: {metadata is None}")

        # Test close_connection
        print("\n8. Testing close_connection()...")
        result = close_connection(conn)
        print(f"✓ Connection closed: {result}")

        print("\n" + "="*60)
        print("All database utility tests passed!")
        print("="*60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
