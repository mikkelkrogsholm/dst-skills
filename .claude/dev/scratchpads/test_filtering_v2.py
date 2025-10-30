#!/usr/bin/env python3
"""
Comprehensive DST API /data endpoint filtering tests - Version 2
Uses correct variable codes for FOLK1A based on metadata inspection.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.api.client import DSTAPIClient


def print_section(title):
    """Print section header"""
    print("\n" + "="*80)
    print(title)
    print("="*80 + "\n")


def test_request(client, description, payload):
    """Make a test request and print results"""
    print(f"TEST: {description}")
    print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}\n")

    try:
        result = client._make_post_request('data', payload)

        if isinstance(result, str):
            lines = result.strip().split('\n')
            print(f"✓ SUCCESS: {len(lines)} lines")
            if len(lines) >= 1:
                print(f"  Header: {lines[0][:120]}")
            if len(lines) >= 2:
                print(f"  Row 1:  {lines[1][:120]}")
            if len(lines) >= 3:
                print(f"  Row 2:  {lines[2][:120]}")
            if len(lines) > 3:
                print(f"  Last:   {lines[-1][:120]}")
        else:
            print(f"✓ SUCCESS: {type(result).__name__}")
            if isinstance(result, dict):
                print(f"  Keys: {list(result.keys())}")
                if 'dataset' in result:
                    print(f"  Dataset keys: {list(result['dataset'].keys())}")

        return True, result

    except Exception as e:
        error_msg = str(e)
        # Extract Danish error message if present
        if '"message":"' in error_msg:
            try:
                import re
                match = re.search(r'"message":"([^"]+)"', error_msg)
                if match:
                    error_msg = match.group(1)
            except:
                pass

        print(f"✗ ERROR: {error_msg}\n")
        return False, error_msg


def main():
    """Run comprehensive filtering tests"""

    with DSTAPIClient() as client:

        # Get metadata first
        print_section("FOLK1A METADATA")
        metadata = client.get_table_info('FOLK1A')

        for var in metadata['variables']:
            print(f"{var['id']:12} - {var['text']:20} "
                  f"[elimination:{var.get('elimination', False):5}, "
                  f"time:{var.get('time', False):5}, "
                  f"values:{len(var.get('values', []))}]")

            values = var.get('values', [])
            if len(values) <= 10:
                print(f"             Values: {', '.join([v['id'] for v in values])}")
            else:
                first_3 = ', '.join([v['id'] for v in values[:3]])
                last_3 = ', '.join([v['id'] for v in values[-3:]])
                print(f"             Values: {first_3} ... {last_3}")

        # Base variables (all required for FOLK1A)
        base_vars = [
            {'code': 'OMRÅDE', 'values': ['000']},  # Denmark total
            {'code': 'KØN', 'values': ['TOT']},      # Total gender
            {'code': 'ALDER', 'values': ['IALT']},   # Total age
            {'code': 'CIVILSTAND', 'values': ['TOT']},  # Total marital status
            {'code': 'Tid', 'values': ['2024K1']}    # Q1 2024
        ]

        # =================================================================
        # TEST 1: Baseline - Specific values only
        # =================================================================
        print_section("TEST 1: Baseline - Specific Values")

        test_request(client, "1.1: Single specific values", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': base_vars
        })

        test_request(client, "1.2: Multiple specific values", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000', '101', '147']},
                {'code': 'KØN', 'values': ['1', '2']},  # Male, Female
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1', '2024K2', '2024K3']}
            ]
        })

        # =================================================================
        # TEST 2: Wildcard patterns
        # =================================================================
        print_section("TEST 2: Wildcard Patterns")

        test_request(client, "2.1: Wildcard '*' for all values", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['*']},      # All genders
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        test_request(client, "2.2: Prefix wildcard '1*' for ages", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['1*']},   # Ages 1, 10-19, 100-125
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        test_request(client, "2.3: Suffix wildcard '*K1' for Q1 periods", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['*K1']}     # All Q1 quarters
            ]
        })

        test_request(client, "2.4: Pattern '202*K1' for 2020s Q1", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['202*K1']}  # 2020-2029 Q1
            ]
        })

        # =================================================================
        # TEST 3: Time nth-rules
        # =================================================================
        print_section("TEST 3: Time Nth-Rules")

        test_request(client, "3.1: Latest value with '(1)'", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['(1)']}     # Latest
            ]
        })

        test_request(client, "3.2: Second newest with '(2)'", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['(2)']}
            ]
        })

        test_request(client, "3.3: Last 5 with '(-n+5)'", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['(-n+5)']}
            ]
        })

        # =================================================================
        # TEST 4: Range operators
        # =================================================================
        print_section("TEST 4: Range Operators")

        test_request(client, "4.1: Greater than or equal '>=2024K1'", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['>=2024K1']}
            ]
        })

        test_request(client, "4.2: Less than or equal '<=2020K1'", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['<=2020K1']}
            ]
        })

        test_request(client, "4.3: Between range '>=2023K1<=2024K2'", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['>=2023K1<=2024K2']}
            ]
        })

        # =================================================================
        # TEST 5: Combined patterns
        # =================================================================
        print_section("TEST 5: Combined Patterns")

        test_request(client, "5.1: Mix wildcards and nth-rules", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['*']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['*']},
                {'code': 'Tid', 'values': ['(-n+3)']}
            ]
        })

        test_request(client, "5.2: Mix specific and wildcard", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000', '101']},
                {'code': 'KØN', 'values': ['*']},
                {'code': 'ALDER', 'values': ['0', '1*']},  # 0 plus 1, 10-19, 100+
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        # =================================================================
        # TEST 6: Variable placement
        # =================================================================
        print_section("TEST 6: Variable Placement")

        test_request(client, "6.1: Stub placement (rows)", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000'], 'placement': 'stub'},
                {'code': 'KØN', 'values': ['1', '2'], 'placement': 'stub'},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1', '2024K2']}
            ]
        })

        test_request(client, "6.2: Head placement (columns)", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['1', '2'], 'placement': 'head'},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1', '2024K2'], 'placement': 'head'}
            ]
        })

        # =================================================================
        # TEST 7: Variable elimination
        # =================================================================
        print_section("TEST 7: Variable Elimination (Testing Which Are Required)")

        test_request(client, "7.1: Try without OMRÅDE", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        test_request(client, "7.2: Try without KØN", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        test_request(client, "7.3: Try without ALDER", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        test_request(client, "7.4: Try without CIVILSTAND", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        test_request(client, "7.5: Try without Tid", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']}
            ]
        })

        # =================================================================
        # TEST 8: valuePresentation
        # =================================================================
        print_section("TEST 8: Value Presentation")

        test_request(client, "8.1: valuePresentation='Code'", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000'], 'valuePresentation': 'Code'},
                {'code': 'KØN', 'values': ['1', '2'], 'valuePresentation': 'Code'},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        test_request(client, "8.2: valuePresentation='Value'", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000'], 'valuePresentation': 'Value'},
                {'code': 'KØN', 'values': ['1', '2'], 'valuePresentation': 'Value'},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        test_request(client, "8.3: valuePresentation='CodeAndValue'", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000'], 'valuePresentation': 'CodeAndValue'},
                {'code': 'KØN', 'values': ['1', '2'], 'valuePresentation': 'CodeAndValue'},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        # =================================================================
        # TEST 9: timeOrder (only for non-streaming formats)
        # =================================================================
        print_section("TEST 9: Time Order (Non-Streaming Formats Only)")

        test_request(client, "9.1: CSV with timeOrder='Ascending'", {
            'table': 'FOLK1A',
            'format': 'CSV',
            'timeOrder': 'Ascending',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1', '2024K2', '2024K3']}
            ]
        })

        test_request(client, "9.2: CSV with timeOrder='Descending'", {
            'table': 'FOLK1A',
            'format': 'CSV',
            'timeOrder': 'Descending',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1', '2024K2', '2024K3']}
            ]
        })

        test_request(client, "9.3: BULK with timeOrder (should fail)", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'timeOrder': 'Ascending',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1', '2024K2']}
            ]
        })

        # =================================================================
        # TEST 10: Error scenarios
        # =================================================================
        print_section("TEST 10: Error Scenarios")

        test_request(client, "10.1: Invalid variable code", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'INVALID_VAR', 'values': ['000']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        test_request(client, "10.2: Invalid value code", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['INVALID999']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        test_request(client, "10.3: Empty values array", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': []},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        # =================================================================
        # TEST 11: Format comparison
        # =================================================================
        print_section("TEST 11: Format Comparison")

        test_request(client, "11.1: BULK format (streaming, no limit)", {
            'table': 'FOLK1A',
            'format': 'BULK',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['*']},
                {'code': 'ALDER', 'values': ['*']},
                {'code': 'CIVILSTAND', 'values': ['*']},
                {'code': 'Tid', 'values': ['(-n+5)']}
            ]
        })

        test_request(client, "11.2: CSV format", {
            'table': 'FOLK1A',
            'format': 'CSV',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1', '2024K2']}
            ]
        })

        test_request(client, "11.3: JSONSTAT format (1M cell limit)", {
            'table': 'FOLK1A',
            'format': 'JSONSTAT',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['000']},
                {'code': 'KØN', 'values': ['TOT']},
                {'code': 'ALDER', 'values': ['IALT']},
                {'code': 'CIVILSTAND', 'values': ['TOT']},
                {'code': 'Tid', 'values': ['2024K1']}
            ]
        })

        test_request(client, "11.4: JSONSTAT exceeding 1M cells (should fail)", {
            'table': 'FOLK1A',
            'format': 'JSONSTAT',
            'variables': [
                {'code': 'OMRÅDE', 'values': ['*']},
                {'code': 'KØN', 'values': ['*']},
                {'code': 'ALDER', 'values': ['*']},
                {'code': 'CIVILSTAND', 'values': ['*']},
                {'code': 'Tid', 'values': ['*']}
            ]
        })


if __name__ == '__main__':
    main()
