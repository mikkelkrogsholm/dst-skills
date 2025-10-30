# DST API Documentation Index

This directory contains comprehensive testing and documentation for the Danmarks Statistik (DST) API.

## Latest: /subjects Endpoint Testing (2025-10-30)

### Documentation Files

| File | Size | Type | Purpose |
|------|------|------|---------|
| **API_GUIDE_SUBJECTS.md** | 24KB | Complete Guide | Full reference documentation with examples, best practices, and integration patterns |
| **API_GUIDE_SUBJECTS_CHEATSHEET.md** | 3.9KB | Quick Reference | One-page cheat sheet for common operations |
| **API_TEST_LOG_SUBJECTS.json** | 7KB | Test Results | Machine-readable test results (16 tests) |
| **TESTING_SUMMARY.md** | 9.5KB | Executive Summary | Overview of testing process, findings, and recommendations |

---

## Quick Links

### For Developers
- **Getting Started:** Read `API_GUIDE_SUBJECTS_CHEATSHEET.md`
- **Complete Reference:** See `API_GUIDE_SUBJECTS.md`
- **Code Examples:** Both guides include Python examples

### For QA/Testing
- **Test Results:** `API_TEST_LOG_SUBJECTS.json`
- **Test Summary:** `TESTING_SUMMARY.md`

### For Project Managers
- **Executive Summary:** `TESTING_SUMMARY.md`
- **Key Findings:** Section in summary

---

## Testing Coverage

### /subjects Endpoint ✅ Complete

**Tests Run:** 16
**Status:** Production Ready

**What was tested:**
- ✅ HTTP methods (GET, POST)
- ✅ All parameters (lang, recursive, includeTables, format)
- ✅ Error cases (invalid language, unsupported parameters)
- ✅ Performance (response times and sizes)
- ✅ Response structure and headers

**Key Findings:**
- 10 top-level subjects
- 5,542 total tables in hierarchy
- Response times: 100-540ms
- Both Danish and English supported
- XML format supported (CSV/JSONP not functional)

---

## Endpoint Status

| Endpoint | Status | Documentation |
|----------|--------|---------------|
| `/subjects` | ✅ Complete | API_GUIDE_SUBJECTS.md |
| `/tables` | ⏳ Partial | API_GUIDE_TABLES.md |
| `/tableinfo` | ⏳ Partial | API_GUIDE_TABLEINFO.md |
| `/data` | ⏳ Partial | API_GUIDE_DATA_FORMATS.md |

---

## Quick Start

### Get all subjects (English)
```bash
curl -X POST https://api.statbank.dk/v1/subjects \
  -H 'Content-Type: application/json' \
  -d '{"lang":"en"}'
```

### Get complete catalog
```bash
curl -X POST https://api.statbank.dk/v1/subjects \
  -H 'Content-Type: application/json' \
  -d '{"recursive":true,"includeTables":true,"lang":"en"}'
```

### Python Example
```python
import requests

def get_subjects(lang='en', recursive=False, include_tables=False):
    url = 'https://api.statbank.dk/v1/subjects'
    params = {'lang': lang, 'recursive': recursive, 'includeTables': include_tables}
    response = requests.post(url, json=params, timeout=30)
    response.raise_for_status()
    return response.json()

subjects = get_subjects(recursive=True, include_tables=True)
```

---

## Other Documentation in This Directory

- `API_GUIDE_TABLES.md` - Tables endpoint documentation
- `API_GUIDE_TABLEINFO.md` - Table info endpoint documentation
- `API_GUIDE_DATA_FORMATS.md` - Data formats guide
- `API_GUIDE_ERRORS_LIMITS.md` - Error handling and limits
- `EV_ANALYSIS_COMPLETE_LOG.md` - Electric vehicle analysis example

---

## Contributing

When adding new documentation:
1. Follow the naming convention: `API_GUIDE_<ENDPOINT>.md`
2. Create both full guide and cheat sheet
3. Include test results as JSON
4. Update this index file

---

**Last Updated:** 2025-10-30
**Test Framework:** Python 3 + urllib
**Documentation Standard:** Markdown with code examples
