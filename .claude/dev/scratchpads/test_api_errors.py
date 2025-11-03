#!/usr/bin/env python3
"""
Comprehensive DST API Error Handling and Limits Testing
Tests rate limits, cell limits, error types, timeouts, and encoding
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
        print(f"[{category}] {test}: {result.get('status', 'N/A')}")

    def test_rate_limiting(self):
        """Test 1: Rate Limiting - Make rapid requests"""
        print("\n=== TEST 1: RATE LIMITING ===")

        # Test rapid GET requests
        start = time.time()
        responses = []

        for i in range(20):
            try:
                resp = httpx.get(f"{BASE_URL}/tableinfo/FOLK1A", timeout=10.0)
                responses.append({
                    "request_num": i + 1,
                    "status_code": resp.status_code,
                    "elapsed_ms": (time.time() - start) * 1000,
                    "headers": dict(resp.headers),
                    "has_rate_limit_headers": any(
                        'rate' in k.lower() or 'limit' in k.lower()
                        for k in resp.headers.keys()
                    )
                })
            except Exception as e:
                responses.append({
                    "request_num": i + 1,
                    "error": str(e),
                    "elapsed_ms": (time.time() - start) * 1000
                })

        total_time = time.time() - start

        self.log("rate_limiting", "rapid_20_requests", {
            "status": "completed",
            "total_requests": 20,
            "total_time_seconds": total_time,
            "avg_time_per_request_ms": (total_time / 20) * 1000,
            "responses": responses,
            "rate_limit_headers_found": any(r.get("has_rate_limit_headers") for r in responses)
        })

        # Test with delays
        print("Testing with 500ms delays...")
        responses_delayed = []
        for i in range(5):
            resp = httpx.get(f"{BASE_URL}/tableinfo/FOLK1A", timeout=10.0)
            responses_delayed.append({
                "request_num": i + 1,
                "status_code": resp.status_code
            })
            time.sleep(0.5)

        self.log("rate_limiting", "delayed_requests_500ms", {
            "status": "completed",
            "responses": responses_delayed
        })

    def test_cell_limits(self):
        """Test 2: Cell Limits - Test 1M boundary"""
        print("\n=== TEST 2: CELL LIMITS ===")

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

        print(f"FOLK1A dimensions: {dimensions}")
        print(f"Total possible cells: {total_cells:,}")

        self.log("cell_limits", "folk1a_dimensions", {
            "status": "analyzed",
            "dimensions": dimensions,
            "total_possible_cells": total_cells
        })

        # Test 2a: Request all data in JSON format (may exceed 1M)
        print("Testing full table request in JSON format...")
        try:
            payload = {
                "table": "FOLK1A",
                "format": "JSON"
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=TIMEOUT)

            self.log("cell_limits", "full_table_json", {
                "status": resp.status_code,
                "success": resp.status_code == 200,
                "response_size_bytes": len(resp.content),
                "error": resp.text if resp.status_code != 200 else None
            })
        except Exception as e:
            self.log("cell_limits", "full_table_json", {
                "status": "error",
                "error": str(e)
            })

        # Test 2b: Request with BULK format (should handle large datasets)
        print("Testing full table request in BULK format...")
        try:
            payload = {
                "table": "FOLK1A",
                "format": "BULK"
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=TIMEOUT)

            self.log("cell_limits", "full_table_bulk", {
                "status": resp.status_code,
                "success": resp.status_code == 200,
                "response_size_bytes": len(resp.content),
                "first_100_chars": resp.text[:100] if resp.status_code == 200 else None,
                "error": resp.text if resp.status_code != 200 else None
            })
        except Exception as e:
            self.log("cell_limits", "full_table_bulk", {
                "status": "error",
                "error": str(e)
            })

        # Test 2c: Request subset to stay under 1M
        print("Testing subset request (< 1M cells)...")
        try:
            payload = {
                "table": "FOLK1A",
                "format": "JSON",
                "variables": [
                    {"code": "OMRÅDE", "values": ["000", "101", "147"]},  # 3 regions
                    {"code": "TID", "values": ["2020K1", "2021K1", "2022K1"]}  # 3 quarters
                ]
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=30.0)

            cell_count = 3 * 3  # 9 cells
            data = resp.json() if resp.status_code == 200 else None
            actual_rows = len(data) if data else 0

            self.log("cell_limits", "subset_request", {
                "status": resp.status_code,
                "success": resp.status_code == 200,
                "expected_cells": cell_count,
                "actual_rows": actual_rows,
                "response_size_bytes": len(resp.content)
            })
        except Exception as e:
            self.log("cell_limits", "subset_request", {
                "status": "error",
                "error": str(e)
            })

    def test_error_types(self):
        """Test 3: All Error Types"""
        print("\n=== TEST 3: ERROR TYPES ===")

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
                "response": resp.text[:500]
            })
        except Exception as e:
            self.log("error_types", "invalid_format", {"error": str(e)})

        # 3c: Missing required parameters
        print("Testing missing table parameter...")
        try:
            payload = {"format": "JSON"}
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=10.0)
            self.log("error_types", "missing_table_param", {
                "status_code": resp.status_code,
                "response": resp.text[:500]
            })
        except Exception as e:
            self.log("error_types", "missing_table_param", {"error": str(e)})

        # 3d: Invalid variable code
        print("Testing invalid variable code...")
        try:
            payload = {
                "table": "FOLK1A",
                "format": "JSON",
                "variables": [
                    {"code": "INVALIDVAR", "values": ["*"]}
                ]
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=10.0)
            self.log("error_types", "invalid_variable_code", {
                "status_code": resp.status_code,
                "response": resp.text[:500]
            })
        except Exception as e:
            self.log("error_types", "invalid_variable_code", {"error": str(e)})

        # 3e: Invalid value code
        print("Testing invalid value code...")
        try:
            payload = {
                "table": "FOLK1A",
                "format": "JSON",
                "variables": [
                    {"code": "OMRÅDE", "values": ["999999"]}  # Invalid region code
                ]
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=10.0)
            self.log("error_types", "invalid_value_code", {
                "status_code": resp.status_code,
                "response": resp.text[:500]
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
                "response": resp.text[:500]
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
            "response": resp.text[:500]
        })

    def test_timeouts(self):
        """Test 4: Timeout Scenarios"""
        print("\n=== TEST 4: TIMEOUT SCENARIOS ===")

        # Test small request timing
        print("Testing small request (3 regions, 3 time periods)...")
        start = time.time()
        try:
            payload = {
                "table": "FOLK1A",
                "format": "JSON",
                "variables": [
                    {"code": "OMRÅDE", "values": ["000", "101", "147"]},
                    {"code": "TID", "values": ["2020K1", "2021K1", "2022K1"]}
                ]
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=30.0)
            elapsed = time.time() - start

            self.log("timeouts", "small_request", {
                "status_code": resp.status_code,
                "elapsed_seconds": elapsed,
                "response_size_bytes": len(resp.content),
                "rows": len(resp.json()) if resp.status_code == 200 else 0
            })
        except Exception as e:
            elapsed = time.time() - start
            self.log("timeouts", "small_request", {
                "error": str(e),
                "elapsed_seconds": elapsed
            })

        # Test medium request timing
        print("Testing medium request (all regions, 5 years quarterly)...")
        start = time.time()
        try:
            payload = {
                "table": "FOLK1A",
                "format": "BULK",
                "variables": [
                    {"code": "OMRÅDE", "values": ["*"]},
                    {"code": "TID", "values": [
                        f"{year}K{q}"
                        for year in range(2018, 2023)
                        for q in range(1, 5)
                    ]}
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

    def test_encoding(self):
        """Test 5: Character Encoding"""
        print("\n=== TEST 5: CHARACTER ENCODING ===")

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

        # Test special characters in requests
        print("Testing special characters in value filters...")
        try:
            # FOLK1A has region names with Danish characters
            payload = {
                "table": "FOLK1A",
                "format": "JSON",
                "variables": [
                    {"code": "OMRÅDE", "values": ["000"]},  # København (has Ø)
                    {"code": "TID", "values": ["2022K1"]}
                ]
            }
            resp = httpx.post(f"{BASE_URL}/data", json=payload, timeout=10.0)

            self.log("encoding", "special_chars_in_request", {
                "status_code": resp.status_code,
                "success": resp.status_code == 200,
                "sample_data": resp.json()[:2] if resp.status_code == 200 else None
            })
        except Exception as e:
            self.log("encoding", "special_chars_in_request", {"error": str(e)})

    def save_results(self, output_path: str):
        """Save all results to JSON file"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_path}")

def main():
    print("DST API Comprehensive Error & Limits Testing")
    print("=" * 60)

    tester = APITester()

    try:
        tester.test_rate_limiting()
        tester.test_cell_limits()
        tester.test_error_types()
        tester.test_timeouts()
        tester.test_encoding()

        # Save results
        output_path = "/Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/.claude/dev/scratchpads/api_test_results.json"
        tester.save_results(output_path)

        print("\n" + "=" * 60)
        print("TESTING COMPLETE")
        print(f"Results saved to: {output_path}")

    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user")
        output_path = "/Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/.claude/dev/scratchpads/api_test_results_partial.json"
        tester.save_results(output_path)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
