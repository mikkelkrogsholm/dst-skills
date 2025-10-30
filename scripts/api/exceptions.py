#!/usr/bin/env python3
"""
DST API Exceptions Module

Defines specific exception classes for different DST API error codes.
Based on comprehensive API testing and error code documentation.
"""

from typing import Optional, Any


class DSTAPIError(Exception):
    """
    Base exception for all DST API errors.

    Attributes:
        error_code: DST error code (e.g., "EXTRACT-NOTFOUND")
        message: Human-readable error message
        response: Original HTTP response object (optional)
    """

    def __init__(self, error_code: str, message: str, response: Optional[Any] = None) -> None:
        self.error_code = error_code
        self.message = message
        self.response = response
        super().__init__(f"{error_code}: {message}")


class TableNotFoundError(DSTAPIError):
    """
    Raised when a table ID is not found in the DST database.

    Error code: EXTRACT-NOTFOUND
    Common causes:
    - Invalid table ID
    - Typo in table name
    - Table has been removed
    """

    def __init__(self, table_id: str, message: Optional[str] = None, response: Optional[Any] = None) -> None:
        self.table_id = table_id
        default_message = f"Table '{table_id}' not found in DST database"
        super().__init__(
            "EXTRACT-NOTFOUND",
            message or default_message,
            response
        )


class VariableNotFoundError(DSTAPIError):
    """
    Raised when a variable code is not found in the specified table.

    Error code: EXTRACT-NOTFOUND
    Common causes:
    - Invalid variable code
    - Variable doesn't exist in this table
    - Typo in variable name
    """

    def __init__(self, variable_code: str, table_id: Optional[str] = None, message: Optional[str] = None, response: Optional[Any] = None) -> None:
        self.variable_code = variable_code
        self.table_id = table_id
        default_message = f"Variable '{variable_code}' not found"
        if table_id:
            default_message += f" in table '{table_id}'"
        super().__init__(
            "EXTRACT-NOTFOUND",
            message or default_message,
            response
        )


class ValueNotFoundError(DSTAPIError):
    """
    Raised when a value code is not found for a variable.

    Error code: EXTRACT-NOTFOUND
    Common causes:
    - Invalid value code
    - Value doesn't exist for this variable
    - Typo in value code
    """

    def __init__(self, value_code: str, variable_code: Optional[str] = None, message: Optional[str] = None, response: Optional[Any] = None) -> None:
        self.value_code = value_code
        self.variable_code = variable_code
        default_message = f"Value '{value_code}' not found"
        if variable_code:
            default_message += f" for variable '{variable_code}'"
        super().__init__(
            "EXTRACT-NOTFOUND",
            message or default_message,
            response
        )


class RequiredParameterMissingError(DSTAPIError):
    """
    Raised when a required parameter is missing from the request.

    Error code: REQUEST-MISSING
    Common causes:
    - Missing 'table' parameter
    - Missing 'format' parameter
    - Missing required variable selection
    """

    def __init__(self, parameter: str, message: Optional[str] = None, response: Optional[Any] = None) -> None:
        self.parameter = parameter
        default_message = f"Required parameter '{parameter}' is missing"
        super().__init__(
            "REQUEST-MISSING",
            message or default_message,
            response
        )


class MalformedRequestError(DSTAPIError):
    """
    Raised when the request is malformed or empty.

    Error code: REQUEST-EMPTY
    Common causes:
    - Invalid JSON syntax
    - Empty request body
    - Incorrect encoding
    """

    def __init__(self, message: str = "Request is malformed or empty", response: Optional[Any] = None) -> None:
        super().__init__(
            "REQUEST-EMPTY",
            message,
            response
        )


class RequiredVariableMissingError(DSTAPIError):
    """
    Raised when required variable values are not specified.

    Error code: EXTRACT-NOTALLOWED
    Common causes:
    - Variable has elimination=false but no values specified
    - Using BULK format without specifying all variables
    - Required variable selection missing
    """

    def __init__(self, variable_code: str, message: Optional[str] = None, response: Optional[Any] = None) -> None:
        self.variable_code = variable_code
        default_message = f"Values must be specified for variable '{variable_code}'"
        super().__init__(
            "EXTRACT-NOTALLOWED",
            message or default_message,
            response
        )


class CellLimitExceededError(DSTAPIError):
    """
    Raised when the request exceeds the 1,000,000 cell limit.

    Error code: REQUEST-LIMIT
    Common causes:
    - Too many variables selected with wildcards
    - Using non-streaming format for large dataset
    - Need to use BULK format instead

    Solution:
    - Use BULK format (no cell limit)
    - Add more specific filters
    - Reduce number of selected values
    """

    def __init__(self, estimated_cells: Optional[int] = None, message: Optional[str] = None, response: Optional[Any] = None) -> None:
        self.estimated_cells = estimated_cells
        default_message = "Request returns too many observations (>1,000,000 cells)"
        if estimated_cells:
            default_message = f"Request returns ~{estimated_cells:,} cells (limit: 1,000,000)"
            default_message += ". Use BULK format for unlimited cells."
        super().__init__(
            "REQUEST-LIMIT",
            message or default_message,
            response
        )


class InvalidFormatError(DSTAPIError):
    """
    Raised when an invalid format is specified.

    Common causes:
    - Using 'JSON' instead of 'JSONSTAT'
    - Invalid format name
    - Format not supported by DST API

    Valid formats: CSV, JSONSTAT, BULK, XLSX, HTML, DSTML,
                  SDMXCOMPACT, SDMXGENERIC, PX, PNG
    """

    def __init__(self, format_name: str, message: Optional[str] = None, response: Optional[Any] = None) -> None:
        self.format_name = format_name
        default_message = f"Format '{format_name}' is not valid"
        default_message += ". Valid formats: CSV, JSONSTAT, BULK, XLSX, HTML, etc."
        super().__init__(
            "REQUEST-MISSING",
            message or default_message,
            response
        )


class EndpointNotFoundError(DSTAPIError):
    """
    Raised when the API endpoint doesn't exist (HTTP 404).

    Common causes:
    - Typo in endpoint URL
    - Wrong API version
    - Endpoint has been removed
    """

    def __init__(self, endpoint: str, message: Optional[str] = None, response: Optional[Any] = None) -> None:
        self.endpoint = endpoint
        default_message = f"Endpoint '{endpoint}' not found"
        super().__init__(
            "REQUEST-NOTFOUND",
            message or default_message,
            response
        )


class TimeSortingNotAllowedError(DSTAPIError):
    """
    Raised when trying to use time sorting with streaming formats.

    Error code: EXTRACT-NOTALLOWED
    Common cause:
    - Using timeOrder parameter with BULK format
    - Time sorting only works with CSV, JSONSTAT, etc.

    Solution:
    - Remove timeOrder parameter when using BULK
    - Use CSV format if time sorting is required
    """

    def __init__(self, format_name: Optional[str] = None, message: Optional[str] = None, response: Optional[Any] = None) -> None:
        self.format_name = format_name
        default_message = "Time sorting cannot be used with streaming formats"
        if format_name:
            default_message = f"Time sorting not allowed with {format_name} format"
        super().__init__(
            "EXTRACT-NOTALLOWED",
            message or default_message,
            response
        )


def parse_dst_error(response: Any) -> DSTAPIError:
    """
    Parse DST API error response and return appropriate exception.

    Args:
        response: httpx Response object with error

    Returns:
        Specific DSTAPIError subclass based on error code

    Example:
        >>> try:
        >>>     response = client.post(url, json=data)
        >>>     response.raise_for_status()
        >>> except httpx.HTTPStatusError as e:
        >>>     raise parse_dst_error(e.response)
    """
    try:
        error_data = response.json()
        error_code = error_data.get('errorTypeCode', 'UNKNOWN')
        message = error_data.get('message', 'Unknown error')

        # Map error codes to specific exceptions
        if error_code == 'EXTRACT-NOTFOUND':
            # Try to determine what wasn't found from the message
            if 'tabel' in message.lower() or 'table' in message.lower():
                return TableNotFoundError('unknown', message, response)
            elif 'variabel' in message.lower() or 'variable' in message.lower():
                return VariableNotFoundError('unknown', message=message, response=response)
            elif 'værdi' in message.lower() or 'value' in message.lower():
                return ValueNotFoundError('unknown', message=message, response=response)
            else:
                return DSTAPIError(error_code, message, response)

        elif error_code == 'REQUEST-MISSING':
            # Try to determine what's missing
            if 'format' in message.lower():
                return InvalidFormatError('unknown', message, response)
            elif 'tabel' in message.lower() or 'table' in message.lower():
                return RequiredParameterMissingError('table', message, response)
            else:
                return RequiredParameterMissingError('unknown', message, response)

        elif error_code == 'REQUEST-EMPTY':
            return MalformedRequestError(message, response)

        elif error_code == 'EXTRACT-NOTALLOWED':
            # Try to determine the issue
            if 'sortering' in message.lower() or 'sorting' in message.lower():
                return TimeSortingNotAllowedError(message=message, response=response)
            elif 'variabel' in message.lower() or 'variable' in message.lower():
                # Extract variable name if possible
                import re
                match = re.search(r'variabel[:\s]+([A-Z\u00C6\u00D8\u00C5]+)', message, re.IGNORECASE)
                variable = match.group(1) if match else 'unknown'
                return RequiredVariableMissingError(variable, message, response)
            else:
                return DSTAPIError(error_code, message, response)

        elif error_code == 'REQUEST-LIMIT':
            return CellLimitExceededError(message=message, response=response)

        elif error_code == 'REQUEST-NOTFOUND':
            return EndpointNotFoundError('unknown', message, response)

        else:
            # Unknown error code, return base exception
            return DSTAPIError(error_code, message, response)

    except (ValueError, KeyError):
        # Not a JSON error response or missing fields
        return DSTAPIError(
            'HTTP_ERROR',
            f"HTTP {response.status_code}: {response.text[:200]}",
            response
        )


# Danish to English error message translations
ERROR_TRANSLATIONS: dict[str, str] = {
    'Tabellen blev ikke fundet': 'Table not found',
    'Tabel ikke angivet': 'Table not specified',
    'Format ikke angivet, eller ikke gyldigt': 'Format not specified or invalid',
    'Variablen blev ikke fundet': 'Variable not found',
    'Værdien blev ikke fundet': 'Value not found',
    'Der skal vælges værdier for variabel': 'Values must be selected for variable',
    'Forespørgslen returnerer for mange observationer': 'Request returns too many observations',
    'Forespørgslen er tom': 'Request is empty',
    'Der kan ikke vælges sortering af tid for streamede formater': 'Time sorting cannot be used with streaming formats',
}


def translate_error_message(danish_message: str) -> str:
    """
    Translate Danish error message to English.

    Args:
        danish_message: Error message in Danish

    Returns:
        Translated message, or original if no translation found
    """
    for danish, english in ERROR_TRANSLATIONS.items():
        if danish.lower() in danish_message.lower():
            return english
    return danish_message
