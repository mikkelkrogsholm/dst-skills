"""Simple file-based cache for DST API responses."""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_path(cache_key: str) -> Path:
    """Get cache file path."""
    return CACHE_DIR / f"{cache_key}.json"


def get_cached(cache_key: str, ttl_hours: int = 24) -> Optional[dict]:
    """
    Get cached data if valid.

    Args:
        cache_key: Unique cache identifier
        ttl_hours: Time-to-live in hours

    Returns:
        Cached data or None if expired/missing
    """
    cache_path = get_cache_path(cache_key)

    if not cache_path.exists():
        return None

    # Check age
    file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
    if datetime.now() - file_time > timedelta(hours=ttl_hours):
        return None

    with open(cache_path) as f:
        return json.load(f)


def cache_set(cache_key: str, data: dict):
    """Save data to cache."""
    cache_path = get_cache_path(cache_key)
    with open(cache_path, 'w') as f:
        json.dump(data, f, indent=2)


def get_cached_tableinfo(table_id: str) -> Optional[dict]:
    """Get cached tableinfo (24hr TTL)."""
    return get_cached(f"tableinfo_{table_id.lower()}", ttl_hours=24)


def cache_tableinfo(table_id: str, data: dict):
    """Cache tableinfo response."""
    cache_set(f"tableinfo_{table_id.lower()}", data)
