"""Path utilities for consistent file organization."""

from pathlib import Path
from datetime import datetime
import os


def get_reports_dir() -> Path:
    """Get reports directory from env or default."""
    return Path(os.getenv("REPORTS_DIR", "reports"))


def create_report_folder(topic: str) -> Path:
    """
    Create organized report folder.

    Args:
        topic: Topic slug (e.g., "electric_vehicles")

    Returns:
        Path to reports/{topic}_{timestamp}/
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_clean = topic.lower().replace(" ", "_").replace("/", "_")

    folder = get_reports_dir() / f"{topic_clean}_{timestamp}"
    folder.mkdir(parents=True, exist_ok=True)

    return folder


def get_folder_timestamp() -> str:
    """Get filesystem-safe timestamp."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
