#!/usr/bin/env python3
"""
API Configuration Module for DST Skills Project

This module provides configuration settings and utilities for interacting
with the DST API (Statistics Denmark).
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv
from urllib.parse import urlencode

# Load environment variables
load_dotenv()

# API Base URL
API_BASE_URL = os.getenv('DST_API_BASE_URL', 'https://api.statbank.dk/v1')

# Database path
DUCKDB_PATH = os.getenv('DUCKDB_PATH', './data/dst_data.duckdb')

# API Endpoints
API_ENDPOINTS: Dict[str, str] = {
    'subjects': '/subjects',
    'tables': '/tables',
    'tableinfo': '/tableinfo',
    'data': '/data'
}


def get_api_url(endpoint: str, params: Optional[Dict[str, str]] = None) -> str:
    """
    Construct a full API URL for a given endpoint.

    Args:
        endpoint: Name of the endpoint (from API_ENDPOINTS) or full path
        params: Optional dictionary of query parameters

    Returns:
        Complete URL with base URL, endpoint, and query parameters

    Examples:
        >>> get_api_url('subjects')
        'https://api.statbank.dk/v1/subjects'

        >>> get_api_url('tables', {'subjects': '02'})
        'https://api.statbank.dk/v1/tables?subjects=02'

        >>> get_api_url('/custom/path', {'format': 'json'})
        'https://api.statbank.dk/v1/custom/path?format=json'
    """
    # Get endpoint path
    if endpoint in API_ENDPOINTS:
        endpoint_path = API_ENDPOINTS[endpoint]
    else:
        # Assume it's a custom path
        endpoint_path = endpoint if endpoint.startswith('/') else f'/{endpoint}'

    # Build base URL
    url = f"{API_BASE_URL}{endpoint_path}"

    # Add query parameters if provided
    if params:
        query_string = urlencode(params)
        url = f"{url}?{query_string}"

    return url


def get_endpoint_path(endpoint: str) -> Optional[str]:
    """
    Get the path for a specific endpoint.

    Args:
        endpoint: Name of the endpoint

    Returns:
        Endpoint path or None if not found
    """
    return API_ENDPOINTS.get(endpoint)


def list_endpoints() -> Dict[str, str]:
    """
    Get a list of all available API endpoints.

    Returns:
        Dictionary of endpoint names and paths
    """
    return API_ENDPOINTS.copy()


# Example usage and testing
if __name__ == "__main__":
    print("Testing API configuration module...")
    print("="*60)

    print("\n1. API Base URL:")
    print(f"   {API_BASE_URL}")

    print("\n2. Database Path:")
    print(f"   {DUCKDB_PATH}")

    print("\n3. Available Endpoints:")
    for name, path in API_ENDPOINTS.items():
        print(f"   {name}: {path}")

    print("\n4. Testing get_api_url():")

    # Test basic endpoint
    url1 = get_api_url('subjects')
    print(f"   subjects: {url1}")
    assert url1 == f"{API_BASE_URL}/subjects", "Basic endpoint test failed"

    # Test endpoint with params
    url2 = get_api_url('tables', {'subjects': '02'})
    print(f"   tables with params: {url2}")
    assert 'subjects=02' in url2, "Endpoint with params test failed"

    # Test custom path
    url3 = get_api_url('/custom/path', {'format': 'json'})
    print(f"   custom path: {url3}")
    assert '/custom/path' in url3 and 'format=json' in url3, "Custom path test failed"

    # Test custom path without leading slash
    url4 = get_api_url('another/custom', {'limit': '10'})
    print(f"   custom without slash: {url4}")
    assert '/another/custom' in url4 and 'limit=10' in url4, "Custom path without slash test failed"

    print("\n5. Testing get_endpoint_path():")
    path = get_endpoint_path('tableinfo')
    print(f"   tableinfo: {path}")
    assert path == '/tableinfo', "get_endpoint_path test failed"

    print("\n6. Testing list_endpoints():")
    endpoints = list_endpoints()
    print(f"   Found {len(endpoints)} endpoints")
    assert len(endpoints) == 4, "list_endpoints test failed"

    print("\n" + "="*60)
    print("All API configuration tests passed!")
    print("="*60)
