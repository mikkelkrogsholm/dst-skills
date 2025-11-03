#!/usr/bin/env python3
"""
Comprehensive DST API Error Handling and Limits Testing v2
Fixed format parameter issues
"""

import httpx
import time
import json
from typing import Dict, List, Tuple
from datetime import datetime

BASE_URL = "https://api.statbank.dk/v1"
TIMEOUT = 120.0

class APITester:
    def __init__(self):
        self.results = {
            "rate_limiting": [],
            "cell_limits": [],
            "error_types": [],
            "timeouts": [],
            "encoding": []
        }

    def log(self, category: str, test: str, result: Dict):
        """Log test result"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "test": test,
            "result": result
        }
        self.results[category].append(entry)
        status = result.get('status_code', result.get('status', 'N/A'))
        print(f"[{category}] {test}: {status}")

    def test_cell_limits_fixed(self):
        """Test 2: Cell Limits - CORRECTED VERSION"""
        print("\n=== TEST 2: CELL LIMITS (FIXED) ===")

        # First, get FOLK1A metadata to calculate cells
        resp = httpx.get(f"{BASE_URL}/tableinfo/FOLK1A", timeout=10.0)
        metadata = resp.json()

        # Calculate dimensions
        variables = metadata.get("variables", [])
        dimensions = []
        for var in variables:
            values = var.get("values", [])
            dimensions.append({
                "id": var.get("id"),
                "text": var.get("text"),
                "value_count": len(values)
            })

        # Calculate total cells (all values for all variables)
        total_cells = 1
        for dim in dimensions:
            total_cells *= dim["value_count"]

        print(f"FOLK1A dimensions: {[f'{d['id']}={d['value_count']}' for d in dimensions]}")
        print(f"Total possible cells: {total_cells:,}")

        self.log("cell_limits", "folk1a_dimensions", {
            "status": "analyzed",
            "dimensions": dimensions,
            "total_possible_cells": total_cells
        })

        # Test 2a: Request with JSONSTAT format (correct format)
        print("Testing full table request in JSONSTAT format...")
        try:
            payload = {
                "table": "FOLK1A",
                "format": "JSONSTAT"
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=TIMEOUT)

            self.log("cell_limits", "full_table_jsonstat", {
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
                "response_size_bytes": len(resp.content),
                "error": resp.text[:500] if resp.status_code != 200 else None
            })
        except Exception as e:
            self.log("cell_limits", "full_table_jsonstat", {
                "status": "error",
                "error": str(e)
            })

        # Test 2b: Request with BULK format (CSV-like, requires value selection)
        print("Testing subset in BULK format...")
        try:
            payload = {
                "table": "FOLK1A",
                "format": "BULK",
                "variables": [
                    {"code": "OMRÅDE", "values": ["000", "101"]},  # 2 regions
                    {"code": "KØN", "values": ["*"]},  # All genders
                    {"code": "ALDER", "values": ["IALT"]},  # Total age
                    {"code": "CIVILSTAND", "values": ["TOT"]},  # Total civil status
                    {"code": "Tid", "values": ["2020K1", "2021K1", "2022K1"]}  # 3 quarters
                ]
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=30.0)

            cell_count = 2 * 3 * 3  # 2 regions * 3 genders * 3 time periods (simplified)

            self.log("cell_limits", "subset_bulk", {
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
                "expected_cells": cell_count,
                "response_size_bytes": len(resp.content),
                "first_200_chars": resp.text[:200] if resp.status_code == 200 else None
            })
        except Exception as e:
            self.log("cell_limits", "subset_bulk", {
                "status": "error",
                "error": str(e)
            })

        # Test 2c: Small subset in JSONSTAT
        print("Testing small subset (< 1M cells) in JSONSTAT...")
        try:
            payload = {
                "table": "FOLK1A",
                "format": "JSONSTAT",
                "variables": [
                    {"code": "OMRÅDE", "values": ["000", "101", "147"]},  # 3 regions
                    {"code": "KØN", "values": ["*"]},  # 3 values
                    {"code": "ALDER", "values": ["IALT"]},  # 1 value
                    {"code": "CIVILSTAND", "values": ["TOT"]},  # 1 value
                    {"code": "Tid", "values": ["2020K1", "2021K1", "2022K1"]}  # 3 quarters
                ]
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=30.0)

            cell_count = 3 * 3 * 1 * 1 * 3  # 27 cells

            self.log("cell_limits", "subset_jsonstat", {
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
                "expected_cells": cell_count,
                "response_size_bytes": len(resp.content)
            })
        except Exception as e:
            self.log("cell_limits", "subset_jsonstat", {
                "status": "error",
                "error": str(e)
            })

    def test_error_types_fixed(self):
        """Test 3: All Error Types - CORRECTED VERSION"""
        print("\n=== TEST 3: ERROR TYPES (FIXED) ===")

        # 3a: Invalid table ID
        print("Testing invalid table ID...")
        resp = httpx.get(f"{BASE_URL}/tableinfo/INVALIDTABLE999", timeout=10.0)
        self.log("error_types", "invalid_table_id", {
            "status_code": resp.status_code,
            "response": resp.text,
            "json": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else None
        })

        # 3b: Invalid format
        print("Testing invalid format...")
        try:
            payload = {"table": "FOLK1A", "format": "INVALIDFORMAT"}
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=10.0)
            self.log("error_types", "invalid_format", {
                "status_code": resp.status_code,
                "response": resp.text[:500],
                "json": resp.json() if resp.status_code == 400 else None
            })
        except Exception as e:
            self.log("error_types", "invalid_format", {"error": str(e)})

        # 3c: Missing table parameter
        print("Testing missing table parameter...")
        try:
            payload = {"format": "JSONSTAT"}
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=10.0)
            self.log("error_types", "missing_table_param", {
                "status_code": resp.status_code,
                "response": resp.text[:500],
                "json": resp.json() if resp.status_code == 400 else None
            })
        except Exception as e:
            self.log("error_types", "missing_table_param", {"error": str(e)})

        # 3d: Invalid variable code
        print("Testing invalid variable code...")
        try:
            payload = {
                "table": "FOLK1A",
                "format": "JSONSTAT",
                "variables": [
                    {"code": "INVALIDVAR", "values": ["*"]}
                ]
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=10.0)
            self.log("error_types", "invalid_variable_code", {
                "status_code": resp.status_code,
                "response": resp.text[:500],
                "json": resp.json() if resp.status_code == 400 else None
            })
        except Exception as e:
            self.log("error_types", "invalid_variable_code", {"error": str(e)})

        # 3e: Invalid value code
        print("Testing invalid value code...")
        try:
            payload = {
                "table": "FOLK1A",
                "format": "JSONSTAT",
                "variables": [
                    {"code": "OMRÅDE", "values": ["999999"]}  # Invalid region code
                ]
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=10.0)
            self.log("error_types", "invalid_value_code", {
                "status_code": resp.status_code,
                "response": resp.text[:500],
                "json": resp.json() if resp.status_code == 400 else None
            })
        except Exception as e:
            self.log("error_types", "invalid_value_code", {"error": str(e)})

        # 3f: Malformed JSON
        print("Testing malformed JSON...")
        try:
            resp = httpx.post(
                f"{BASE_URL}/data",
                content="{invalid json}",
                headers={"content-type": "application/json"},
                timeout=10.0
            )
            self.log("error_types", "malformed_json", {
                "status_code": resp.status_code,
                "response": resp.text[:500],
                "json": resp.json() if resp.status_code == 400 else None
            })
        except Exception as e:
            self.log("error_types", "malformed_json", {"error": str(e)})

        # 3g: Wrong HTTP method (GET on /data)
        print("Testing GET on /data endpoint...")
        try:
            resp = httpx.get(f"{BASE_URL}/data?table=FOLK1A", timeout=10.0)
            self.log("error_types", "wrong_http_method", {
                "status_code": resp.status_code,
                "response": resp.text[:500]
            })
        except Exception as e:
            self.log("error_types", "wrong_http_method", {"error": str(e)})

        # 3h: Non-existent endpoint
        print("Testing non-existent endpoint...")
        resp = httpx.get(f"{BASE_URL}/nonexistent", timeout=10.0)
        self.log("error_types", "nonexistent_endpoint", {
            "status_code": resp.status_code,
            "response": resp.text[:500],
            "json": resp.json() if resp.status_code == 404 else None
        })

        # 3i: Empty POST body
        print("Testing empty POST body...")
        try:
            resp = httpx.post(f"{BASE_URL}/data", json={}, timeout=10.0)
            self.log("error_types", "empty_post_body", {
                "status_code": resp.status_code,
                "response": resp.text[:500],
                "json": resp.json() if resp.status_code == 400 else None
            })
        except Exception as e:
            self.log("error_types", "empty_post_body", {"error": str(e)})

    def test_timeouts_fixed(self):
        """Test 4: Timeout Scenarios - CORRECTED VERSION"""
        print("\n=== TEST 4: TIMEOUT SCENARIOS (FIXED) ===")

        # Test small request timing
        print("Testing small request (3 regions, 3 time periods)...")
        start = time.time()
        try:
            payload = {
                "table": "FOLK1A",
                "format": "JSONSTAT",
                "variables": [
                    {"code": "OMRÅDE", "values": ["000", "101", "147"]},
                    {"code": "KØN", "values": ["*"]},
                    {"code": "ALDER", "values": ["IALT"]},
                    {"code": "CIVILSTAND", "values": ["TOT"]},
                    {"code": "Tid", "values": ["2020K1", "2021K1", "2022K1"]}
                ]
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=30.0)
            elapsed = time.time() - start

            self.log("timeouts", "small_request", {
                "status_code": resp.status_code,
                "elapsed_seconds": elapsed,
                "response_size_bytes": len(resp.content)
            })
        except Exception as e:
            elapsed = time.time() - start
            self.log("timeouts", "small_request", {
                "error": str(e),
                "elapsed_seconds": elapsed
            })

        # Test medium request timing
        print("Testing medium request (10 regions, 1 year quarterly)...")
        start = time.time()
        try:
            payload = {
                "table": "FOLK1A",
                "format": "BULK",
                "variables": [
                    {"code": "OMRÅDE", "values": [str(i).zfill(3) for i in range(0, 10)]},
                    {"code": "KØN", "values": ["*"]},
                    {"code": "ALDER", "values": ["IALT"]},
                    {"code": "CIVILSTAND", "values": ["TOT"]},
                    {"code": "Tid", "values": [f"2022K{q}" for q in range(1, 5)]}
                ]
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=60.0)
            elapsed = time.time() - start

            self.log("timeouts", "medium_request", {
                "status_code": resp.status_code,
                "elapsed_seconds": elapsed,
                "response_size_bytes": len(resp.content)
            })
        except Exception as e:
            elapsed = time.time() - start
            self.log("timeouts", "medium_request", {
                "error": str(e),
                "elapsed_seconds": elapsed
            })

        # Test large request timing (many time periods)
        print("Testing large request (all quarters 2018-2023)...")
        start = time.time()
        try:
            payload = {
                "table": "FOLK1A",
                "format": "JSONSTAT",
                "variables": [
                    {"code": "OMRÅDE", "values": ["000"]},
                    {"code": "KØN", "values": ["*"]},
                    {"code": "ALDER", "values": ["IALT"]},
                    {"code": "CIVILSTAND", "values": ["TOT"]},
                    {"code": "Tid", "values": [
                        f"{year}K{q}"
                        for year in range(2018, 2024)
                        for q in range(1, 5)
                    ]}
                ]
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=60.0)
            elapsed = time.time() - start

            self.log("timeouts", "large_request", {
                "status_code": resp.status_code,
                "elapsed_seconds": elapsed,
                "response_size_bytes": len(resp.content)
            })
        except Exception as e:
            elapsed = time.time() - start
            self.log("timeouts", "large_request", {
                "error": str(e),
                "elapsed_seconds": elapsed
            })

        # Test tableinfo timing
        print("Testing tableinfo request...")
        start = time.time()
        resp = httpx.get(f"{BASE_URL}/tableinfo/FOLK1A", timeout=10.0)
        elapsed = time.time() - start

        self.log("timeouts", "tableinfo_request", {
            "status_code": resp.status_code,
            "elapsed_seconds": elapsed,
            "response_size_bytes": len(resp.content)
        })

    def test_encoding_fixed(self):
        """Test 5: Character Encoding - CORRECTED VERSION"""
        print("\n=== TEST 5: CHARACTER ENCODING (FIXED) ===")

        # Test Danish characters in search
        print("Testing Danish characters in subject text...")
        resp = httpx.get(f"{BASE_URL}/subjects", timeout=10.0)
        subjects = resp.json()

        # Find subjects with Danish characters
        danish_chars = []
        for subject in subjects:
            text = subject.get("text", "")
            if any(char in text for char in "æøåÆØÅ"):
                danish_chars.append({
                    "id": subject.get("id"),
                    "text": text,
                    "has_danish": True
                })

        self.log("encoding", "danish_chars_in_subjects", {
            "status": "analyzed",
            "total_subjects": len(subjects),
            "subjects_with_danish": len(danish_chars),
            "examples": danish_chars[:5]
        })

        # Test Danish characters in table metadata
        print("Testing Danish characters in table metadata...")
        resp = httpx.get(f"{BASE_URL}/tableinfo/FOLK1A", timeout=10.0)
        metadata = resp.json()

        text_fields = {
            "title": metadata.get("text"),
            "description": metadata.get("description"),
            "unit": metadata.get("unit")
        }

        has_danish = {
            field: any(char in (value or "") for char in "æøåÆØÅ")
            for field, value in text_fields.items()
        }

        self.log("encoding", "danish_chars_in_metadata", {
            "status": "analyzed",
            "text_fields": text_fields,
            "has_danish_chars": has_danish
        })

        # Test actual data with Danish characters
        print("Testing data retrieval with Danish characters...")
        try:
            payload = {
                "table": "FOLK1A",
                "format": "JSONSTAT",
                "variables": [
                    {"code": "OMRÅDE", "values": ["000"]},  # København (has Ø in label)
                    {"code": "KØN", "values": ["*"]},  # køn has ø
                    {"code": "ALDER", "values": ["IALT"]},
                    {"code": "CIVILSTAND", "values": ["TOT"]},
                    {"code": "Tid", "values": ["2022K1"]}
                ]
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=10.0)

            self.log("encoding", "data_with_danish_chars", {
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
                "response_size_bytes": len(resp.content)
            })
        except Exception as e:
            self.log("encoding", "data_with_danish_chars", {"error": str(e)})

    def save_results(self, output_path: str):
        """Save all results to JSON file"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_path}")

def main():
    print("DST API Comprehensive Error & Limits Testing v2")
    print("=" * 60)

    tester = APITester()

    try:
        tester.test_cell_limits_fixed()
        tester.test_error_types_fixed()
        tester.test_timeouts_fixed()
        tester.test_encoding_fixed()

        # Save results
        output_path = "/Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/.claude/dev/scratchpads/api_test_results_v2.json"
        tester.save_results(output_path)

        print("\n" + "=" * 60)
        print("TESTING COMPLETE")
        print(f"Results saved to: {output_path}")

    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user")
        output_path = "/Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/.claude/dev/scratchpads/api_test_results_v2_partial.json"
        tester.save_results(output_path)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
