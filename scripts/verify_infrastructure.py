#!/usr/bin/env python3
"""
Infrastructure Verification Script

This script performs comprehensive verification of the DST Skills infrastructure setup.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from db import db_utils
from api import config, client
import utils


def verify_directories():
    """Verify all required directories exist."""
    print("\n" + "="*60)
    print("DIRECTORY STRUCTURE VERIFICATION")
    print("="*60)

    project_root = Path(__file__).parent.parent
    required_dirs = [
        '.claude/agents',
        '.claude/skills',
        '.claude/commands',
        'scripts/api',
        'scripts/db',
        'data',
        'tests',
        'logs',
        'docs'
    ]

    all_exist = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        print(f"{status} {dir_path}")
        all_exist = all_exist and exists

    return all_exist


def verify_files():
    """Verify all required files exist."""
    print("\n" + "="*60)
    print("FILES VERIFICATION")
    print("="*60)

    project_root = Path(__file__).parent.parent
    required_files = [
        'requirements.txt',
        '.env.example',
        '.env',
        '.gitignore',
        'README.md',
        'docs/database-schema.md',
        'scripts/db/init_db.py',
        'scripts/db/db_utils.py',
        'scripts/api/config.py',
        'scripts/api/client.py',
        'scripts/utils.py',
        'data/dst_data.duckdb'
    ]

    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        size = f"({full_path.stat().st_size} bytes)" if exists else ""
        print(f"{status} {file_path} {size}")
        all_exist = all_exist and exists

    return all_exist


def verify_imports():
    """Verify all modules can be imported."""
    print("\n" + "="*60)
    print("MODULE IMPORTS VERIFICATION")
    print("="*60)

    modules = [
        ('db.db_utils', db_utils),
        ('api.config', config),
        ('api.client', client),
        ('utils', utils)
    ]

    all_imported = True
    for name, module in modules:
        try:
            print(f"✓ {name}")
        except Exception as e:
            print(f"✗ {name}: {e}")
            all_imported = False

    return all_imported


def verify_database():
    """Verify database connectivity and schema."""
    print("\n" + "="*60)
    print("DATABASE VERIFICATION")
    print("="*60)

    try:
        # Connect to database
        conn = db_utils.get_connection()
        print("✓ Database connection successful")

        # Check metadata table
        exists = db_utils.table_exists(conn, 'dst_metadata')
        print(f"✓ dst_metadata table exists: {exists}")

        # Check schema
        schema = conn.execute("DESCRIBE dst_metadata").fetchall()
        print(f"✓ dst_metadata has {len(schema)} columns:")
        for col in schema:
            print(f"    - {col[0]}: {col[1]}")

        # Close connection
        db_utils.close_connection(conn)
        print("✓ Database connection closed")

        return True
    except Exception as e:
        print(f"✗ Database verification failed: {e}")
        return False


def verify_environment():
    """Verify environment configuration."""
    print("\n" + "="*60)
    print("ENVIRONMENT CONFIGURATION VERIFICATION")
    print("="*60)

    from dotenv import load_dotenv
    load_dotenv()

    env_vars = [
        'DST_API_BASE_URL',
        'DUCKDB_PATH',
        'LOG_LEVEL'
    ]

    all_set = True
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {value}")
        else:
            print(f"✗ {var}: NOT SET")
            all_set = False

    return all_set


def verify_api_client():
    """Verify API client functionality."""
    print("\n" + "="*60)
    print("API CLIENT VERIFICATION")
    print("="*60)

    try:
        # Test client initialization
        api_client = client.DSTAPIClient()
        print("✓ API client initialized")

        # Test API endpoint
        subjects = api_client.get_subjects()
        print(f"✓ API connection successful: Retrieved {len(subjects)} subjects")

        api_client.close()
        print("✓ API client closed")

        return True
    except Exception as e:
        print(f"✗ API client verification failed: {e}")
        return False


def verify_logging():
    """Verify logging functionality."""
    print("\n" + "="*60)
    print("LOGGING VERIFICATION")
    print("="*60)

    try:
        logger = utils.setup_logger('verification')
        print("✓ Logger initialized")

        logger.info("Verification test message")
        print("✓ Logger can write messages")

        log_file = Path(__file__).parent.parent / 'logs' / 'dst_system.log'
        if log_file.exists():
            print(f"✓ Log file exists: {log_file}")
            print(f"  Size: {log_file.stat().st_size} bytes")
        else:
            print("✗ Log file not found")
            return False

        return True
    except Exception as e:
        print(f"✗ Logging verification failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("\n" + "#"*60)
    print("# DST SKILLS PROJECT - INFRASTRUCTURE VERIFICATION")
    print("#"*60)

    results = {
        'Directories': verify_directories(),
        'Files': verify_files(),
        'Imports': verify_imports(),
        'Database': verify_database(),
        'Environment': verify_environment(),
        'API Client': verify_api_client(),
        'Logging': verify_logging()
    }

    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)

    all_passed = True
    for check, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {check}")
        all_passed = all_passed and passed

    print("\n" + "#"*60)
    if all_passed:
        print("# ALL VERIFICATION CHECKS PASSED!")
        print("# Infrastructure setup is complete and operational.")
    else:
        print("# SOME VERIFICATION CHECKS FAILED!")
        print("# Please review the output above for details.")
    print("#"*60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
