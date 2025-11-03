#!/usr/bin/env python3
"""
Comprehensive DST API /data endpoint filtering tests.

Tests all filtering patterns, variable selection, placement, and error scenarios.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.api.client import DSTAPIClient
import httpx


def test_info(test_name):
    """Print test header"""
    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print("="*80)


def make_data_request(client, table_id, variables, description):
    """Make a data request and display results"""
    print(f"\n{description}")
    print(f"Variables: {json.dumps(variables, indent=2)}")

    try:
        payload = {
            'table': table_id,
            'format': 'BULK',  # Use BULK to avoid 1M cell limit
            'variables': variables
        }

        result = client._make_post_request('data', payload)

        # Count lines in result
        if isinstance(result, str):
            lines = result.strip().split('\n')
            print(f"✓ SUCCESS: {len(lines)} lines returned")
            print(f"  First line: {lines[0][:100]}...")
            if len(lines) > 1:
                print(f"  Second line: {lines[1][:100]}...")
            if len(lines) > 2:
                print(f"  Last line: {lines[-1][:100]}...")
        else:
            print(f"✓ SUCCESS: {type(result).__name__}")
            print(f"  Data: {str(result)[:200]}...")

        return True, result

    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False, str(e)


def main():
    """Run all filtering tests"""

    # First, get table metadata
    print("="*80)
    print("GETTING FOLK1A METADATA")
    print("="*80)

    with DSTAPIClient() as client:
        metadata = client.get_table_info('FOLK1A')

        print("\nVARIABLES IN FOLK1A:")
        for var in metadata['variables']:
            print(f"\n{var['id']} - {var['text']}")
            print(f"  Elimination: {var.get('elimination', False)}")
            print(f"  Time: {var.get('time', False)}")
            print(f"  Values: {len(var.get('values', []))} items")

            # Show first few values
            values = var.get('values', [])
            if len(values) <= 10:
                print(f"  All values: {[v['id'] for v in values]}")
            else:
                print(f"  First 5: {[v['id'] for v in values[:5]]}")
                print(f"  Last 5: {[v['id'] for v in values[-5:]]}")

        # ===================================================================
        # TEST 1: Wildcard patterns
        # ===================================================================
        test_info("Wildcard Patterns")

        # Test 1.1: All values with "*"
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},  # Denmark only
                {'code': 'KØN', 'values': ['*']},       # All genders
                {'code': 'ALDER', 'values': ['IALT']},  # Total age
                {'code': 'Tid', 'values': ['2024K1']}   # Q1 2024
            ],
            "Test 1.1: Wildcard '*' for all values"
        )

        # Test 1.2: Prefix wildcard
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['10*']},   # Ages starting with 10
                {'code': 'Tid', 'values': ['2024K1']}
            ],
            "Test 1.2: Prefix wildcard '10*' (ages 10, 100-109)"
        )

        # Test 1.3: Suffix wildcard
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['*K1']}      # All Q1 quarters
            ],
            "Test 1.3: Suffix wildcard '*K1' (all Q1 quarters)"
        )

        # Test 1.4: Middle wildcard pattern
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['20*K1']}    # Q1 in 2000s
            ],
            "Test 1.4: Pattern '20*K1' (Q1 in 2000s)"
        )

        # ===================================================================
        # TEST 2: Time nth-rules
        # ===================================================================
        test_info("Time Nth-Rules")

        # Test 2.1: Latest value
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['(1)']}      # Latest
            ],
            "Test 2.1: Latest value '(1)'"
        )

        # Test 2.2: Last 3 values
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['(-n+3)']}   # Last 3
            ],
            "Test 2.2: Last 3 values '(-n+3)'"
        )

        # Test 2.3: Second newest
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['(2)']}      # Second newest
            ],
            "Test 2.3: Second newest '(2)'"
        )

        # Test 2.4: Last 10 values
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['(-n+10)']}  # Last 10
            ],
            "Test 2.4: Last 10 values '(-n+10)'"
        )

        # ===================================================================
        # TEST 3: Range operators
        # ===================================================================
        test_info("Range Operators")

        # Test 3.1: Greater than or equal
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['>=2024K1']}  # From 2024K1
            ],
            "Test 3.1: Range '>=2024K1'"
        )

        # Test 3.2: Less than or equal
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['<=2024K2']}  # Up to 2024K2
            ],
            "Test 3.2: Range '<=2024K2'"
        )

        # Test 3.3: Between range
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['>=2023K1<=2024K2']}  # Between
            ],
            "Test 3.3: Range '>=2023K1<=2024K2'"
        )

        # ===================================================================
        # TEST 4: Multiple specific values
        # ===================================================================
        test_info("Multiple Specific Values")

        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000', '101', '147']},  # Multiple areas
                {'code': 'KØN', 'values': ['M', 'K']},                # Male and Female
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['2024K1', '2024K2']}       # Q1 and Q2
            ],
            "Test 4.1: Multiple specific values (arrays)"
        )

        # ===================================================================
        # TEST 5: Combined patterns
        # ===================================================================
        test_info("Combined Patterns")

        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['*']},                    # Wildcard
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['2024*', '(1)']}          # Pattern + nth
            ],
            "Test 5.1: Mixed patterns (wildcard + nth-rule)"
        )

        # ===================================================================
        # TEST 6: Variable placement
        # ===================================================================
        test_info("Variable Placement")

        # Test 6.1: Default placement
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['M', 'K']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['2024K1', '2024K2']}
            ],
            "Test 6.1: Default placement (no specification)"
        )

        # Test 6.2: Stub placement
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000'], 'placement': 'stub'},
                {'code': 'KØN', 'values': ['M', 'K'], 'placement': 'stub'},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['2024K1', '2024K2']}
            ],
            "Test 6.2: Stub placement (rows)"
        )

        # Test 6.3: Head placement
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['M', 'K'], 'placement': 'head'},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['2024K1', '2024K2'], 'placement': 'head'}
            ],
            "Test 6.3: Head placement (columns)"
        )

        # ===================================================================
        # TEST 7: Variable elimination
        # ===================================================================
        test_info("Variable Elimination")

        # Test 7.1: Try eliminating all optional variables
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'Tid', 'values': ['2024K1']}  # Only time dimension
            ],
            "Test 7.1: Minimal variables (time only)"
        )

        # Test 7.2: Try with just demographic dimensions
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ],
            "Test 7.2: Without OMRÅDE (should use default total)"
        )

        # Test 7.3: Try eliminating time (should fail or use default)
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['IALT']}
            ],
            "Test 7.3: Without Tid (might fail)"
        )

        # ===================================================================
        # TEST 8: valuePresentation
        # ===================================================================
        test_info("Value Presentation")

        # Test 8.1: Code only
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000'], 'valuePresentation': 'Code'},
                {'code': 'KØN', 'values': ['M', 'K'], 'valuePresentation': 'Code'},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ],
            "Test 8.1: valuePresentation='Code'"
        )

        # Test 8.2: Value only
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000'], 'valuePresentation': 'Value'},
                {'code': 'KØN', 'values': ['M', 'K'], 'valuePresentation': 'Value'},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ],
            "Test 8.2: valuePresentation='Value'"
        )

        # Test 8.3: CodeAndValue
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['000'], 'valuePresentation': 'CodeAndValue'},
                {'code': 'KØN', 'values': ['M', 'K'], 'valuePresentation': 'CodeAndValue'},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ],
            "Test 8.3: valuePresentation='CodeAndValue'"
        )

        # ===================================================================
        # TEST 9: timeOrder
        # ===================================================================
        test_info("Time Order")

        # Test 9.1: Ascending
        payload_asc = {
            'table': 'FOLK1A',
            'format': 'BULK',
            'timeOrder': 'Ascending',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['(-n+5)']}
            ]
        }
        print("\nTest 9.1: timeOrder='Ascending'")
        print(f"Payload: {json.dumps(payload_asc, indent=2)}")
        try:
            result = client._make_post_request('data', payload_asc)
            if isinstance(result, str):
                lines = result.strip().split('\n')
                print(f"✓ SUCCESS: {len(lines)} lines")
                print(f"  First data: {lines[1][:100] if len(lines) > 1 else 'N/A'}")
                print(f"  Last data: {lines[-1][:100]}")
        except Exception as e:
            print(f"✗ ERROR: {e}")

        # Test 9.2: Descending
        payload_desc = {
            'table': 'FOLK1A',
            'format': 'BULK',
            'timeOrder': 'Descending',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['IALT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['(-n+5)']}
            ]
        }
        print("\nTest 9.2: timeOrder='Descending'")
        print(f"Payload: {json.dumps(payload_desc, indent=2)}")
        try:
            result = client._make_post_request('data', payload_desc)
            if isinstance(result, str):
                lines = result.strip().split('\n')
                print(f"✓ SUCCESS: {len(lines)} lines")
                print(f"  First data: {lines[1][:100] if len(lines) > 1 else 'N/A'}")
                print(f"  Last data: {lines[-1][:100]}")
        except Exception as e:
            print(f"✗ ERROR: {e}")

        # ===================================================================
        # TEST 10: Error scenarios
        # ===================================================================
        test_info("Error Scenarios")

        # Test 10.1: Invalid variable code
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'INVALID_VAR', 'values': ['000']},
                {'code': 'Tid', 'values': ['2024K1']}
            ],
            "Test 10.1: Invalid variable code"
        )

        # Test 10.2: Invalid value code
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': ['INVALID_VALUE']},
                {'code': 'Tid', 'values': ['2024K1']}
            ],
            "Test 10.2: Invalid value code"
        )

        # Test 10.3: Empty values array
        make_data_request(
            client, 'FOLK1A',
            [
                {'code': 'OMRÅDE', 'values': []},
                {'code': 'Tid', 'values': ['2024K1']}
            ],
            "Test 10.3: Empty values array"
        )

        # Test 10.4: Too many cells (non-streaming)
        print("\nTest 10.4: Too many cells with JSONSTAT format (1M limit)")
        try:
            payload_large = {
                'table': 'FOLK1A',
                'format': 'JSONSTAT',  # Has 1M cell limit
                'variables': [
                    {'code': 'OMRÅDE', 'values': ['*']},     # All areas
                    {'code': 'KØN', 'values': ['*']},        # All genders
                    {'code': 'ALDER', 'values': ['*']},      # All ages
                    {'code': 'Tid', 'values': ['*']}         # All time periods
                ]
            }
            result = client._make_post_request('data', payload_large)
            print(f"✓ Surprisingly succeeded: {type(result).__name__}")
        except Exception as e:
            print(f"✗ Expected error: {e}")

        # ===================================================================
        # TEST 11: Streaming vs non-streaming
        # ===================================================================
        test_info("Streaming vs Non-Streaming Formats")

        # Test 11.1: BULK format (streaming, no limit)
        print("\nTest 11.1: BULK format (streaming)")
        try:
            payload_bulk = {
                'table': 'FOLK1A',
                'format': 'BULK',
                'variables': [
                    {'code': 'OMRÅDE', 'values': ['000']},
                    {'code': 'KØN', 'values': ['*']},
                    {'code': 'ALDER', 'values': ['*']},
                    {'code': 'Tid', 'values': ['(-n+10)']}
                ]
            }
            result = client._make_post_request('data', payload_bulk)
            if isinstance(result, str):
                lines = result.strip().split('\n')
                print(f"✓ SUCCESS: {len(lines)} lines (BULK has no cell limit)")
        except Exception as e:
            print(f"✗ ERROR: {e}")

        # Test 11.2: JSONSTAT format (non-streaming, 1M limit)
        print("\nTest 11.2: JSONSTAT format (non-streaming, 1M limit)")
        try:
            payload_json = {
                'table': 'FOLK1A',
                'format': 'JSONSTAT',
                'variables': [
                    {'code': 'OMRÅDE', 'values': ['000']},
                    {'code': 'KØN', 'values': ['IALT']},
                    {'code': 'ALDER', 'values': ['IALT']},
                    {'code': 'Tid', 'values': ['2024K1']}
                ]
            }
            result = client._make_post_request('data', payload_json)
            print(f"✓ SUCCESS: {type(result).__name__}")
            if isinstance(result, dict):
                print(f"  Keys: {list(result.keys())}")
        except Exception as e:
            print(f"✗ ERROR: {e}")

        # Test 11.3: CSV format
        print("\nTest 11.3: CSV format")
        try:
            payload_csv = {
                'table': 'FOLK1A',
                'format': 'CSV',
                'variables': [
                    {'code': 'OMRÅDE', 'values': ['000']},
                    {'code': 'KØN', 'values': ['IALT']},
                    {'code': 'ALDER', 'values': ['IALT']},
                    {'code': 'Tid', 'values': ['2024K1', '2024K2']}
                ]
            }
            result = client._make_post_request('data', payload_csv)
            if isinstance(result, str):
                lines = result.strip().split('\n')
                print(f"✓ SUCCESS: {len(lines)} lines")
                print(f"  Header: {lines[0][:100]}")
        except Exception as e:
            print(f"✗ ERROR: {e}")


if __name__ == '__main__':
    main()
