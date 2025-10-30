#!/usr/bin/env python3
"""
Utility Module for DST Skills Project

This module provides common utility functions including logging configuration.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Set up and return a configured logger.

    The logger will output to both console and a log file in the logs/ directory.

    Args:
        name: Name of the logger (typically __name__ of the calling module)
        level: Optional logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If not specified, uses LOG_LEVEL from environment or defaults to INFO

    Returns:
        Configured logger instance

    Examples:
        >>> logger = setup_logger(__name__)
        >>> logger.info("This is an info message")

        >>> logger = setup_logger(__name__, level='DEBUG')
        >>> logger.debug("This is a debug message")
    """
    # Get logging level from environment or use provided level
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO')

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    # Console handler - less verbose
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(simple_formatter)

    # File handler - more detailed
    log_file = log_dir / 'dst_system.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path object pointing to the project root
    """
    return Path(__file__).parent.parent


def ensure_directory(path: str | Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Path to the directory (string or Path object)

    Returns:
        Path object pointing to the directory

    Raises:
        Exception: If directory cannot be created
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


# Example usage and testing
if __name__ == "__main__":
    print("Testing utility functions...")
    print("="*60)

    # Test setup_logger with default level
    print("\n1. Testing setup_logger() with default level...")
    logger1 = setup_logger(__name__)
    logger1.info("This is an info message")
    logger1.warning("This is a warning message")
    logger1.error("This is an error message")

    # Test setup_logger with custom level
    print("\n2. Testing setup_logger() with DEBUG level...")
    logger2 = setup_logger(f"{__name__}.debug", level='DEBUG')
    logger2.debug("This is a debug message")
    logger2.info("This is an info message from debug logger")

    # Test get_project_root
    print("\n3. Testing get_project_root()...")
    project_root = get_project_root()
    print(f"   Project root: {project_root}")
    assert project_root.exists(), "Project root does not exist"

    # Test ensure_directory
    print("\n4. Testing ensure_directory()...")
    test_dir = project_root / 'logs' / 'test_subdir'
    result = ensure_directory(test_dir)
    print(f"   Created directory: {result}")
    assert result.exists(), "Directory was not created"

    # Clean up test directory
    if test_dir.exists():
        test_dir.rmdir()

    # Verify log file was created
    print("\n5. Verifying log file creation...")
    log_file = project_root / 'logs' / 'dst_system.log'
    if log_file.exists():
        print(f"   Log file exists: {log_file}")
        print(f"   Log file size: {log_file.stat().st_size} bytes")

        # Read last few lines of log file
        with open(log_file, 'r') as f:
            lines = f.readlines()
            print(f"   Total log lines: {len(lines)}")
            if lines:
                print(f"   Last log entry: {lines[-1].strip()}")
    else:
        print("   Warning: Log file was not created")

    print("\n" + "="*60)
    print("All utility tests completed!")
    print("Check console output above and logs/dst_system.log file")
    print("="*60)
