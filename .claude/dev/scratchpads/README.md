# DST API Investigation - Scratchpad Documentation

This directory contains comprehensive documentation and test results from investigating the Danmarks Statistik (DST) API.

## Investigation Date
**2025-10-30**

## Documentation Files

### Core API Guides

1. **API_GUIDE_SUBJECTS.md** (24 KB)
   - Complete subject hierarchy documentation
   - 86 subjects organized in tree structure
   - Navigation patterns and examples
   - Search strategies

2. **API_GUIDE_SUBJECTS_CHEATSHEET.md** (3.9 KB)
   - Quick reference for common subjects
   - Subject ID lookup table
   - Most frequently used subjects

3. **API_GUIDE_TABLES.md** (21 KB)
   - Tables endpoint documentation
   - Filtering by subject
   - Table metadata structure
   - Search examples

4. **API_GUIDE_TABLEINFO.md** (16 KB)
   - Detailed table metadata documentation
   - Variable structure and types
   - Elimination flags
   - Time dimensions

5. **API_GUIDE_DATA_FORMATS.md** (28 KB) ⭐
   - **COMPREHENSIVE FORMAT GUIDE**
   - All 9 supported formats documented
   - Cell limits and constraints
   - Variable specification patterns
   - Python code examples
   - **BULK format recommended**

6. **API_GUIDE_DATA_FILTERING.md** (22 KB)
   - Advanced filtering techniques
   - Variable specification examples
   - Error handling
   - Best practices

7. **API_GUIDE_ERRORS_LIMITS.md** (23 KB)
   - Error codes and messages
   - Cell limit calculations
   - Rate limiting
   - Troubleshooting guide

### Test Reports

8. **FORMAT_TEST_SUMMARY.md** (8.4 KB)
   - Executive summary of format testing
   - 15 tests conducted
   - 13/15 success rate
   - Quick reference guide

9. **TESTING_SUMMARY.md** (9.5 KB)
   - Overall testing summary
   - Coverage matrix
   - Key findings

### Other Files

10. **EV_ANALYSIS_COMPLETE_LOG.md** (13 KB)
    - Electric vehicle analysis example
    - Real-world usage demonstration

## Test Result Data

- `test_results_formats_corrected.json` - Detailed format test results
- `api_test_results.json` - General API test results
- `api_test_results_v2.json` - Updated test results
- `test_results.txt` - Raw test output

## Test Scripts

- `test_api_errors.py` - Error handling tests
- `test_api_errors_v2.py` - Updated error tests
- `test_filtering.py` - Filtering tests
- `test_filtering_v2.py` - Updated filtering tests

## Key Findings Summary

### 1. Format Testing (API_GUIDE_DATA_FORMATS.md)
- ✅ 9 formats supported: CSV, JSONSTAT, BULK, XLSX, HTML, DSTML, SDMXCOMPACT, SDMXGENERIC, PX
- ✅ **BULK format recommended** - no cell limits, streaming
- ❌ JSON format not supported (use JSONSTAT instead)
- ⚠️ Most formats have 1,000,000 cell limit

### 2. Variable Specification
- Use exact IDs from tableinfo endpoint
- Wildcards supported: `*` for all, `YYYY*` for time patterns
- Variables are array of `{"code": "VAR", "values": [...]}`
- Auto-elimination when no variables specified

### 3. Cell Limits
- Formula: `cells = var1_count × var2_count × ... × varN_count`
- Limit: 1,000,000 cells for CSV, XLSX, HTML, XML formats
- BULK format: **NO LIMIT** (streaming)
- Error code: `REQUEST-LIMIT`

### 4. Data Separator
- **All text formats use semicolon (`;`)**
- Not comma (`,`) as typical in CSV
- Important for parsing

### 5. Subject Hierarchy
- 86 total subjects
- 3-level tree structure
- IDs from "01" to "99"
- Main categories: Demographics, Economy, Labor, etc.

## Quick Start

### Find Data
1. Browse subjects → `API_GUIDE_SUBJECTS.md`
2. Search tables → `API_GUIDE_TABLES.md`
3. Get table metadata → `API_GUIDE_TABLEINFO.md`

### Fetch Data
1. Read format guide → `API_GUIDE_DATA_FORMATS.md`
2. Use BULK format (recommended)
3. Specify variables correctly
4. Handle errors → `API_GUIDE_ERRORS_LIMITS.md`

## Recommended Reading Order

For **new users**:
1. `FORMAT_TEST_SUMMARY.md` - Quick overview
2. `API_GUIDE_DATA_FORMATS.md` - Essential reading
3. `API_GUIDE_SUBJECTS_CHEATSHEET.md` - Find your data
4. `API_GUIDE_TABLEINFO.md` - Understand table structure

For **developers**:
1. `API_GUIDE_DATA_FORMATS.md` - Format details and code
2. `API_GUIDE_ERRORS_LIMITS.md` - Error handling
3. `API_GUIDE_DATA_FILTERING.md` - Advanced techniques
4. Test scripts for examples

For **researchers**:
1. `API_GUIDE_SUBJECTS.md` - Explore available data
2. `API_GUIDE_TABLES.md` - Find specific tables
3. `API_GUIDE_DATA_FORMATS.md` - Choose format (JSONSTAT for analysis)
4. `EV_ANALYSIS_COMPLETE_LOG.md` - Real example

## Code Examples

All guides include Python code examples using `httpx` library.

### Recommended Pattern
```python
import httpx

def fetch_dst_data(table_id, variables):
    """Fetch DST data using BULK format (recommended)"""
    response = httpx.post(
        "https://api.statbank.dk/v1/data",
        json={
            "table": table_id,
            "format": "BULK",
            "variables": variables
        },
        timeout=60
    )
    response.raise_for_status()
    return response.text

# Example usage
data = fetch_dst_data("FOLK1A", [
    {"code": "OMRÅDE", "values": ["000"]},
    {"code": "KØN", "values": ["*"]},
    {"code": "Tid", "values": ["2023*"]}
])
```

## API Endpoints Documented

| Endpoint | Guide | Status |
|----------|-------|--------|
| `/subjects` | API_GUIDE_SUBJECTS.md | ✅ Complete |
| `/tables` | API_GUIDE_TABLES.md | ✅ Complete |
| `/tableinfo` | API_GUIDE_TABLEINFO.md | ✅ Complete |
| `/data` | API_GUIDE_DATA_FORMATS.md | ✅ Complete |

## Coverage Matrix

| Feature | Documented | Tested | Examples |
|---------|------------|--------|----------|
| Subjects browsing | ✅ | ✅ | ✅ |
| Table search | ✅ | ✅ | ✅ |
| Table metadata | ✅ | ✅ | ✅ |
| Data formats (9) | ✅ | ✅ | ✅ |
| Variable specification | ✅ | ✅ | ✅ |
| Wildcards | ✅ | ✅ | ✅ |
| Cell limits | ✅ | ✅ | ✅ |
| Error handling | ✅ | ✅ | ✅ |
| Best practices | ✅ | ⚠️ | ✅ |

## Statistics

- **Total documentation:** ~160 KB
- **Total guides:** 10 markdown files
- **Test scripts:** 6 Python files
- **Test data:** 4 JSON/text files
- **Code examples:** 50+ Python snippets
- **Formats tested:** 9/9 (100%)
- **Success rate:** 13/15 tests (86.7%)

## Key Recommendations

1. **Always use BULK format** by default
2. **Check tableinfo** before requesting data
3. **Use wildcards** for time patterns (`2023*`)
4. **Estimate cells** before using CSV/XLSX
5. **Handle Danish errors** properly
6. **Set appropriate timeouts** (60s+)

## Contact

This documentation was created through systematic API testing and investigation.

For official DST API documentation: https://www.dst.dk/en/Statistik/brug-statistikken/muligheder-i-statistikbanken/api

---

**Last Updated:** 2025-10-30
**Status:** Complete
**Next:** Implement recommendations in production code
