#!/usr/bin/env python3
"""
API Client Module for DST Skills Project

This module provides a client for interacting with the DST API (Statistics Denmark).
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import httpx

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.config import API_BASE_URL, get_api_url
from utils import setup_logger


class DSTAPIClient:
    """
    Client for interacting with the DST (Statistics Denmark) API.

    This client handles HTTP requests, error handling, rate limiting,
    and logging for all API interactions.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 30, max_retries: int = 3) -> None:
        """
        Initialize the DST API client.

        Args:
            base_url: Optional custom base URL for the API
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self.base_url = base_url or API_BASE_URL
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = setup_logger(__name__)

        # Set up client with retry strategy
        transport = httpx.HTTPTransport(retries=max_retries)
        self.client = httpx.Client(
            transport=transport,
            timeout=timeout,
            follow_redirects=True
        )

        # Rate limiting
        self.min_request_interval = 0.1  # Minimum time between requests (seconds)
        self.last_request_time = 0

        self.logger.info(f"Initialized DST API Client with base URL: {self.base_url}")

    def _rate_limit(self) -> None:
        """
        Implement rate limiting to avoid overwhelming the API.

        Ensures a minimum interval between consecutive requests.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _parse_response(self, response: httpx.Response) -> Union[Dict[str, Any], str]:
        """
        Parse API response, handling both JSON and text formats.

        Args:
            response: httpx Response object

        Returns:
            Parsed response data (dict for JSON, str for text)

        Raises:
            ValueError: If JSON parsing fails for JSON content-type
        """
        content_type = response.headers.get('content-type', '')

        # Check for JSON content type (both application/json and text/json)
        if 'json' in content_type.lower():
            # Parse JSON
            try:
                data = response.json()
                self.logger.debug(f"Response data type: {type(data)}")
                return data
            except ValueError as e:
                self.logger.error(f"Invalid JSON in response: {e}")
                self.logger.debug(f"Response text: {response.text[:500]}")
                raise ValueError(f"Invalid JSON response: {e}")
        else:
            # Return text for CSV/BULK formats
            self.logger.debug(f"Response content-type: {content_type}, returning text")
            return response.text

    def _handle_request_errors(self, response: Optional[httpx.Response], error: Exception) -> None:
        """
        Handle common HTTP request errors with consistent logging.

        Args:
            response: httpx Response object (may be None)
            error: Exception that occurred

        Raises:
            The original exception after logging
        """
        if isinstance(error, httpx.HTTPStatusError):
            self.logger.error(f"HTTP error occurred: {error}")
            if response:
                self.logger.error(f"Response status code: {response.status_code}")
                self.logger.error(f"Response text: {response.text[:500]}")
        elif isinstance(error, httpx.TimeoutException):
            self.logger.error(f"Request timeout after {self.timeout} seconds: {error}")
        elif isinstance(error, httpx.ConnectError):
            self.logger.error(f"Connection error: {error}")
        else:
            self.logger.error(f"Unexpected error during request: {error}")

        raise error

    def _make_request(self, endpoint: str, params: Optional[Dict[str, str]] = None, method: str = 'GET') -> Union[Dict[str, Any], str]:
        """
        Make a generic HTTP request to the API.

        Args:
            endpoint: API endpoint path or name
            params: Optional dictionary of query parameters
            method: HTTP method (GET, POST, etc.)

        Returns:
            Parsed response data (dict for JSON, str for text)

        Raises:
            httpx.HTTPStatusError: For HTTP errors
            httpx.TimeoutException: For timeout errors
            httpx.ConnectError: For connection errors
            ValueError: For invalid JSON responses
        """
        # Apply rate limiting
        self._rate_limit()

        # Build full URL
        url = get_api_url(endpoint, params)

        self.logger.info(f"Making {method} request to: {url}")

        response = None
        try:
            # Make request
            response = self.client.request(
                method=method,
                url=url
            )

            # Log response status
            self.logger.info(f"Response status: {response.status_code}")

            # Raise exception for bad status codes
            response.raise_for_status()

            # Parse and return response
            return self._parse_response(response)

        except Exception as e:
            self._handle_request_errors(response, e)

    def _make_post_request(self, endpoint: str, json_data: Dict[str, Any]) -> Union[Dict[str, Any], str]:
        """
        Make a POST request with JSON body to the API.

        Args:
            endpoint: API endpoint path or name
            json_data: Dictionary to send as JSON body

        Returns:
            Parsed response data (dict for JSON, str for text)

        Raises:
            httpx.HTTPStatusError: For HTTP errors
            httpx.TimeoutException: For timeout errors
            httpx.ConnectError: For connection errors
            ValueError: For invalid JSON responses
        """
        # Apply rate limiting
        self._rate_limit()

        # Build full URL (no query params for POST)
        url = get_api_url(endpoint)

        self.logger.info(f"Making POST request to: {url}")
        self.logger.debug(f"JSON payload: {json_data}")

        response = None
        try:
            # Make POST request with JSON body
            response = self.client.post(
                url=url,
                json=json_data
            )

            # Log response status
            self.logger.info(f"Response status: {response.status_code}")

            # Raise exception for bad status codes
            response.raise_for_status()

            # Parse and return response
            return self._parse_response(response)

        except Exception as e:
            self._handle_request_errors(response, e)

    def get_subjects(self, recursive: bool = False) -> List[Dict[str, Any]]:
        """
        Get list of all subjects from DST API.

        Args:
            recursive: If True, include all sub-subjects recursively

        Returns:
            List of subject objects
        """
        params = {}
        if recursive:
            params['recursive'] = 'true'

        self.logger.info(f"Fetching subjects (recursive={recursive})")
        return self._make_request('subjects', params)

    def get_tables(self, subjects: Optional[Union[str, List[str]]] = None) -> List[Dict[str, Any]]:
        """
        Get list of tables, optionally filtered by subject.

        Args:
            subjects: Optional subject ID or list of subject IDs

        Returns:
            List of table objects
        """
        params = {}
        if subjects:
            if isinstance(subjects, list):
                params['subjects'] = ','.join(subjects)
            else:
                params['subjects'] = str(subjects)

        self.logger.info(f"Fetching tables for subjects: {subjects}")
        return self._make_request('tables', params)

    def get_table_info(self, table_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific table.

        Args:
            table_id: ID of the table

        Returns:
            Table information including columns and metadata
        """
        self.logger.info(f"Fetching table info for: {table_id}")
        return self._make_request('tableinfo', {'id': table_id})

    def get_data(self, table_id: str, **kwargs: Any) -> Union[Dict[str, Any], str]:
        """
        Get data from a specific table.

        Args:
            table_id: ID of the table
            **kwargs: Additional parameters for the data request
                     (format, variables, etc.)

        Returns:
            Table data response (dict for JSON, str for CSV/BULK)
        """
        # DST API requires POST with JSON body for data requests
        # Build JSON payload
        # Note: Valid formats are CSV, JSONSTAT, BULK, XLSX, etc.
        # BULK returns semicolon-separated CSV (easy to parse, no cell limit)
        payload = {
            'table': table_id,
            'format': kwargs.get('format', 'BULK')
        }

        # Add optional parameters
        if 'variables' in kwargs:
            payload['variables'] = kwargs['variables']
        if 'filters' in kwargs:
            # Convert filters dict to variables format
            variables = []
            for var_code, values in kwargs['filters'].items():
                variables.append({
                    'code': var_code,
                    'values': values
                })
            payload['variables'] = variables

        self.logger.info(f"Fetching data for table: {table_id}")
        self.logger.debug(f"Request payload: {payload}")

        # Use POST request for data endpoint
        return self._make_post_request('data', payload)

    def close(self) -> None:
        """Close the client."""
        self.client.close()
        self.logger.info("API client closed")

    def __enter__(self) -> 'DSTAPIClient':
        """Support context manager protocol."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Support context manager protocol."""
        self.close()


# Example usage and testing
if __name__ == "__main__":
    print("Testing DST API Client...")
    print("="*60)

    try:
        # Create client
        print("\n1. Initializing client...")
        client = DSTAPIClient()
        print("✓ Client initialized successfully")

        # Test get_subjects
        print("\n2. Testing get_subjects()...")
        subjects = client.get_subjects()
        print(f"✓ Retrieved {len(subjects)} subjects")
        if subjects:
            print(f"   First subject: {subjects[0]}")

        # Test get_tables with a specific subject
        print("\n3. Testing get_tables()...")
        # Use the first subject ID from the subjects we just retrieved
        first_subject_id = subjects[0]['id'] if subjects else '1'
        tables = client.get_tables(subjects=first_subject_id)
        print(f"✓ Retrieved {len(tables)} tables for subject '{first_subject_id}'")
        if tables:
            print(f"   First table: {tables[0].get('id', 'N/A')} - {tables[0].get('text', 'N/A')}")

        # Test error handling with invalid endpoint
        print("\n4. Testing error handling with invalid endpoint...")
        try:
            client._make_request('/invalid/endpoint')
            print("✗ Should have raised an error")
        except httpx.HTTPStatusError:
            print("✓ HTTPStatusError raised as expected for invalid endpoint")

        # Test context manager
        print("\n5. Testing context manager...")
        with DSTAPIClient() as test_client:
            print("✓ Context manager working")

        # Close client
        print("\n6. Closing client...")
        client.close()
        print("✓ Client closed successfully")

        print("\n" + "="*60)
        print("All API client tests passed!")
        print("="*60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
