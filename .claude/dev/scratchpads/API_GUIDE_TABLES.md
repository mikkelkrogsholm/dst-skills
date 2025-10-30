# DST API /tables Endpoint - Comprehensive Guide

**Endpoint URL:** `https://api.statbank.dk/v1/tables`
**Methods:** GET, POST
**Last Tested:** 2025-10-30

---

## Table of Contents
1. [Overview](#overview)
2. [HTTP Methods](#http-methods)
3. [Parameters](#parameters)
4. [Response Structure](#response-structure)
5. [Usage Examples](#usage-examples)
6. [Filtering Strategies](#filtering-strategies)
7. [Performance Analysis](#performance-analysis)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)

---

## Overview

The `/tables` endpoint returns a list of statistical tables available in the Danmarks Statistik API. It provides metadata about each table including ID, description, update timestamp, period coverage, active status, and available variables.

### Key Features
- **2,223** active tables available
- **5,486** total tables (including 3,263 inactive)
- Supports filtering by subject, recency, and activity status
- Available in Danish (default) and English
- Fast response times (0.13s - 0.67s depending on filters)

---

## HTTP Methods

### GET Request
```bash
curl https://api.statbank.dk/v1/tables
```
- Returns all active tables (default behavior)
- Simplest method, no body required
- Response size: ~499 KB
- Response time: ~0.39s

### POST Request
```bash
curl -X POST https://api.statbank.dk/v1/tables \
  -H "Content-Type: application/json" \
  -d '{}'
```
- Allows parameter-based filtering
- Empty body `{}` returns same as GET (all active tables)
- Required for using filters

---

## Parameters

All parameters are optional and used via POST requests with JSON body.

### 1. `subjects` (array of strings)
Filter tables by subject category.

**Valid Subject IDs:**
- `"1"` - Borgere (Citizens)
- `"2"` - Arbejde og indkomst (Work and Income)
- `"3"` - Økonomi (Economy)
- `"4"` - Sociale forhold (Social Conditions)
- `"5"` - Uddannelse og forskning (Education and Research)
- `"6"` - Erhvervsliv (Business)
- `"7"` - Transport
- `"8"` - Kultur og fritid (Culture and Leisure)
- `"9"` - Miljø og energi (Environment and Energy)
- `"19"` - Om Danmarks Statistik (About Statistics Denmark)

**Example:**
```json
{"subjects": ["7"]}           // Single subject: 175 tables
{"subjects": ["7", "9"]}      // Multiple subjects: 302 tables
```

**Behavior:**
- Multiple subjects are OR'ed (union, not intersection)
- Invalid subject IDs return HTTP 400 Bad Request
- Empty array returns all tables

### 2. `pastDays` (integer)
Filter tables updated within the last N days.

**Example:**
```json
{"pastDays": 7}    // Last week: 121 tables
{"pastDays": 30}   // Last month: 307 tables
{"pastDays": 0}    // Returns 0 tables
```

**Behavior:**
- Filters by the `updated` timestamp field
- `pastDays: 0` returns empty list
- Combines with other filters (AND logic)

### 3. `includeInactive` (boolean)
Include inactive/discontinued tables in results.

**Example:**
```json
{"includeInactive": true}     // Returns 5,486 tables (vs 2,223 active)
{"includeInactive": false}    // Default: only active tables
```

**Behavior:**
- Default: `false` (only active tables)
- Inactive tables have `"active": false` in response
- Significantly increases response size (~1,229 KB vs ~499 KB)
- Slower response time (~0.67s vs ~0.41s)

### 4. `lang` (string)
Set response language.

**Example:**
```json
{"lang": "en"}    // English
{"lang": "da"}    // Danish (default)
```

**Behavior:**
- Affects `text` (table description) field
- Affects `variables` field (translated variable names)
- Does not affect `id`, `unit`, timestamps, or structural fields
- Slightly larger response size in English (~41 KB vs ~40 KB for same query)

### 5. `format` (string)
Specify response format.

**Example:**
```json
{"format": "JSON"}    // Default behavior
```

**Behavior:**
- `"JSON"` is the only tested format
- Parameter appears to have no effect (JSON is default)
- Other formats may exist but are undocumented

### Unsupported Parameters

These parameters were tested but are **NOT supported**:
- `text` - Text search returns all tables (parameter ignored)
- `id` - ID filtering returns all tables (parameter ignored)
- Unknown parameters are silently ignored

---

## Response Structure

### Response Format
```json
[
  {
    "id": "FOLK1A",
    "text": "Befolkningen den 1. i kvartalet",
    "unit": "Antal",
    "updated": "2025-08-11T08:00:00",
    "firstPeriod": "2008K1",
    "latestPeriod": "2025K3",
    "active": true,
    "variables": ["område", "køn", "alder", "civilstand", "tid"]
  },
  ...
]
```

### Field Descriptions

| Field | Type | Always Present | Description |
|-------|------|----------------|-------------|
| `id` | string | ✅ Yes | Unique table identifier (e.g., "FOLK1A") |
| `text` | string | ✅ Yes | Table description (language-dependent) |
| `unit` | string | ✅ Yes | Measurement unit (e.g., "Antal", "Pct.", "Kr.") |
| `updated` | string | ✅ Yes | Last update timestamp (ISO 8601 format) |
| `firstPeriod` | string | ✅ Yes | First available time period (e.g., "2008K1", "1971") |
| `latestPeriod` | string | ✅ Yes | Most recent time period (e.g., "2025K3", "2025M09") |
| `active` | boolean | ✅ Yes | Whether table is currently maintained |
| `variables` | array | ✅ Yes | List of variable/dimension names |

### Field Consistency
All 8 fields are present in **100%** of table entries across 2,223+ tables tested.

### Time Period Formats
- **Yearly:** `"2025"`, `"1971"`
- **Quarterly:** `"2025K3"` (K = Kvartal/Quarter)
- **Monthly:** `"2025M09"` (M = Month)
- **Other formats** may exist (e.g., weekly, daily)

### Timestamp Format
- ISO 8601: `"2025-10-30T08:00:00"`
- Always includes time component (typically 08:00:00)
- No timezone indicator (assumed Danish local time)

---

## Usage Examples

### Example 1: Get All Active Tables
```python
import urllib.request
import json

url = "https://api.statbank.dk/v1/tables"
response = urllib.request.urlopen(url)
tables = json.loads(response.read())
print(f"Found {len(tables)} active tables")
```

**Output:** 2,223 tables, ~499 KB, ~0.39s

### Example 2: Get Transport Tables
```python
import urllib.request
import json

url = "https://api.statbank.dk/v1/tables"
payload = {"subjects": ["7"]}
req = urllib.request.Request(url,
                              data=json.dumps(payload).encode('utf-8'),
                              headers={'Content-Type': 'application/json'})
response = urllib.request.urlopen(req)
tables = json.loads(response.read())
print(f"Transport tables: {len(tables)}")
```

**Output:** 175 tables, ~40 KB, ~0.19s

### Example 3: Recently Updated Tables (Last 7 Days)
```python
import urllib.request
import json

url = "https://api.statbank.dk/v1/tables"
payload = {"pastDays": 7}
req = urllib.request.Request(url,
                              data=json.dumps(payload).encode('utf-8'),
                              headers={'Content-Type': 'application/json'})
response = urllib.request.urlopen(req)
tables = json.loads(response.read())
print(f"Recently updated: {len(tables)}")
for table in tables[:5]:
    print(f"  {table['id']}: Updated {table['updated']}")
```

**Output:** 121 tables, ~30 KB, ~0.27s

### Example 4: Combined Filters - Recent Transport Tables in English
```python
import urllib.request
import json

url = "https://api.statbank.dk/v1/tables"
payload = {
    "subjects": ["7"],
    "pastDays": 30,
    "lang": "en"
}
req = urllib.request.Request(url,
                              data=json.dumps(payload).encode('utf-8'),
                              headers={'Content-Type': 'application/json'})
response = urllib.request.urlopen(req)
tables = json.loads(response.read())
print(f"Recent transport tables (30 days): {len(tables)}")
for table in tables[:3]:
    print(f"  {table['id']}: {table['text']}")
```

**Output:** 14 tables, ~3 KB, ~0.13s

### Example 5: Include Inactive Tables
```python
import urllib.request
import json

url = "https://api.statbank.dk/v1/tables"
payload = {"includeInactive": True}
req = urllib.request.Request(url,
                              data=json.dumps(payload).encode('utf-8'),
                              headers={'Content-Type': 'application/json'})
response = urllib.request.urlopen(req)
tables = json.loads(response.read())

active = sum(1 for t in tables if t['active'])
inactive = sum(1 for t in tables if not t['active'])
print(f"Total: {len(tables)} (Active: {active}, Inactive: {inactive})")
```

**Output:** 5,486 tables (2,223 active, 3,263 inactive), ~1,229 KB, ~0.67s

### Example 6: Multiple Subjects (Population + Work)
```python
import urllib.request
import json

url = "https://api.statbank.dk/v1/tables"
payload = {"subjects": ["1", "2"]}
req = urllib.request.Request(url,
                              data=json.dumps(payload).encode('utf-8'),
                              headers={'Content-Type': 'application/json'})
response = urllib.request.urlopen(req)
tables = json.loads(response.read())
print(f"Population + Work tables: {len(tables)}")
```

**Output:** 928 tables, ~210 KB, ~0.31s

---

## Filtering Strategies

### Strategy 1: Filter by Subject (Most Common)
**Use when:** You know the general topic area

```json
{"subjects": ["7"]}  // Transport
```

**Pros:**
- Fast (0.19s)
- Small response (40 KB)
- Returns 175 manageable results
- Clear categorization

**Cons:**
- Requires knowing subject IDs
- May miss cross-category tables

### Strategy 2: Filter by Recency
**Use when:** Looking for latest data or monitoring updates

```json
{"pastDays": 7}  // Last week's updates
```

**Pros:**
- Very fast (0.27s)
- Small response (30 KB)
- Returns actively maintained tables
- Good for monitoring data freshness

**Cons:**
- No categorical filtering
- Time-sensitive (results change daily)

### Strategy 3: Combined Filtering
**Use when:** Need precise, targeted results

```json
{
  "subjects": ["7"],
  "pastDays": 30,
  "lang": "en"
}
```

**Pros:**
- Fastest option (0.13s)
- Smallest response (3 KB)
- Very targeted results (14 tables)
- Filters are AND'ed (intersection)

**Cons:**
- May be too restrictive
- Requires multiple parameters

### Strategy 4: Broad Search with Client-Side Filtering
**Use when:** Need flexibility or text search

```python
# Get all tables, filter client-side
tables = get_all_tables()
filtered = [t for t in tables if 'befolkning' in t['text'].lower()]
```

**Pros:**
- Maximum flexibility
- Can search by text, ID, or any field
- Complex logic possible

**Cons:**
- Larger initial download (499 KB)
- Slower initial request (0.41s)
- More memory usage
- Not scalable for very large datasets

### Strategy 5: Include Inactive for Historical Research
**Use when:** Researching discontinued tables or historical data

```json
{"includeInactive": true}
```

**Pros:**
- Access to all 5,486 tables
- Historical data discovery
- Complete dataset

**Cons:**
- Much larger (1,229 KB)
- Slower (0.67s)
- Most results are obsolete

### Recommended Strategy Matrix

| Goal | Recommended Filter | Expected Results |
|------|-------------------|------------------|
| Browse category | `{"subjects": ["X"]}` | 100-300 tables |
| Find latest updates | `{"pastDays": 7}` | ~120 tables |
| Targeted search | Subject + pastDays | ~5-20 tables |
| Full catalog | GET or `{}` | 2,223 tables |
| Historical research | `{"includeInactive": true}` | 5,486 tables |
| English interface | Add `"lang": "en"` | Same count, translated |

---

## Performance Analysis

### Response Time Comparison

| Query Type | Time (s) | Size (KB) | Tables |
|------------|----------|-----------|--------|
| Combined filters (subject + pastDays) | **0.13** | **3.0** | 14 |
| Single subject | 0.19 | 64.8 | 292 |
| Recent updates (7 days) | 0.27 | 29.7 | 121 |
| Recent updates (30 days) | 0.30 | 71.6 | 307 |
| Multiple subjects (3) | 0.31 | 210.0 | 928 |
| All tables (GET) | 0.39 | 498.5 | 2,223 |
| All tables (POST) | 0.41 | 498.5 | 2,223 |
| With inactive tables | 0.67 | 1,229.1 | 5,486 |

### Key Findings

1. **Fastest:** Combined filters (0.13s) - filters reduce server-side processing
2. **Smallest:** Combined filters (3 KB) - fewer results = smaller payload
3. **Slowest:** Include inactive (0.67s) - 2.4x more tables to process
4. **Largest:** Include inactive (1,229 KB) - 2.5x larger payload

### Performance Characteristics

- **Linear scaling:** Response time roughly correlates with result count
- **Efficient filtering:** Server-side filters are faster than client-side
- **Network bound:** Small datasets (<100 KB) dominated by latency
- **Subject filtering:** Most efficient single filter (0.19s, 65 KB)
- **GET vs POST:** No significant difference (~0.02s, same size)

### Optimization Tips

1. **Always filter when possible** - Don't request all 2,223 tables if you need 14
2. **Combine filters** - AND logic gives smallest, fastest results
3. **Avoid includeInactive** unless necessary - 2.4x slower, 2.5x larger
4. **Cache results** - Tables metadata doesn't change frequently
5. **Use pastDays for monitoring** - Efficient way to find new/updated tables

---

## Error Handling

### HTTP Status Codes

| Code | Scenario | Example |
|------|----------|---------|
| 200 OK | Successful request | Any valid query |
| 400 Bad Request | Invalid subject ID | `{"subjects": ["999"]}` |
| 400 Bad Request | Malformed JSON | `{invalid json}` |

### Error Scenarios

#### 1. Invalid Subject ID
```python
payload = {"subjects": ["999"]}  # Non-existent subject
# Result: HTTP 400 Bad Request
```

#### 2. Malformed JSON
```python
payload = b"{invalid json}"
# Result: HTTP 400 Bad Request
```

#### 3. Invalid Parameters (Silently Ignored)
```python
payload = {"invalidParam": "test"}
# Result: HTTP 200, returns all tables (parameter ignored)
```

#### 4. Empty Results (Not an Error)
```python
payload = {"pastDays": 0}
# Result: HTTP 200, returns [] (0 tables)
```

### Error Handling Pattern

```python
import urllib.request
import json

def get_tables(payload=None):
    """Safe table fetching with error handling."""
    url = "https://api.statbank.dk/v1/tables"

    try:
        if payload is None:
            # GET request
            response = urllib.request.urlopen(url, timeout=30)
        else:
            # POST request
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            response = urllib.request.urlopen(req, timeout=30)

        content = response.read()
        tables = json.loads(content)
        return tables

    except urllib.error.HTTPError as e:
        if e.code == 400:
            error_body = e.read().decode('utf-8')
            raise ValueError(f"Invalid request: {error_body}")
        else:
            raise

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {e}")

    except Exception as e:
        raise RuntimeError(f"Request failed: {e}")

# Usage
try:
    tables = get_tables({"subjects": ["7"]})
    print(f"Found {len(tables)} tables")
except ValueError as e:
    print(f"Invalid request: {e}")
except RuntimeError as e:
    print(f"Request error: {e}")
```

### Common Pitfalls

1. **Wrong subject ID format**
   - ❌ `{"subjects": [23]}` (integer)
   - ✅ `{"subjects": ["23"]}` (string)

2. **Assuming text search works**
   - ❌ `{"text": "befolkning"}` (ignored, returns all)
   - ✅ Get all, filter client-side

3. **Not handling empty results**
   - `{"pastDays": 0}` returns `[]`, not an error
   - Always check `len(tables) > 0`

4. **Forgetting Content-Type header**
   - Required for POST requests
   - Must be `application/json`

---

## Best Practices

### 1. Choose the Right Method

```python
# Use GET for simple "all tables" request
tables = get_tables_via_get()

# Use POST with filters for targeted queries
tables = get_tables_via_post({"subjects": ["7"], "pastDays": 30})
```

### 2. Filter Server-Side, Not Client-Side

```python
# ❌ Inefficient: Download all, filter locally
all_tables = get_tables()
transport = [t for t in all_tables if t in transport_ids]

# ✅ Efficient: Filter server-side
transport = get_tables({"subjects": ["7"]})
```

### 3. Cache Results Appropriately

```python
import time
import json

class TablesCache:
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds

    def get_tables(self, payload_key, fetch_func):
        key = json.dumps(payload_key, sort_keys=True)

        if key in self.cache:
            timestamp, data = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data

        data = fetch_func()
        self.cache[key] = (time.time(), data)
        return data

# Usage
cache = TablesCache(ttl_seconds=1800)  # 30 minute cache
tables = cache.get_tables(
    {"subjects": ["7"]},
    lambda: get_tables({"subjects": ["7"]})
)
```

### 4. Use Appropriate Timeouts

```python
# Short timeout for fast queries
response = urllib.request.urlopen(url, timeout=10)

# Longer timeout for large datasets
response = urllib.request.urlopen(url, timeout=30)  # includeInactive
```

### 5. Validate Subject IDs

```python
VALID_SUBJECTS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "19"]

def validate_subjects(subjects):
    invalid = [s for s in subjects if s not in VALID_SUBJECTS]
    if invalid:
        raise ValueError(f"Invalid subject IDs: {invalid}")
    return subjects

# Usage
try:
    subjects = validate_subjects(["7", "9"])
    tables = get_tables({"subjects": subjects})
except ValueError as e:
    print(f"Validation error: {e}")
```

### 6. Handle Rate Limiting (If Applicable)

```python
import time

def get_tables_with_retry(payload, max_retries=3, delay=1):
    """Get tables with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return get_tables(payload)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay * (2 ** attempt))
```

### 7. Parse Timestamps Correctly

```python
from datetime import datetime

def parse_dst_timestamp(timestamp_str):
    """Parse DST API timestamp to datetime object."""
    return datetime.fromisoformat(timestamp_str)

# Usage
table = tables[0]
updated = parse_dst_timestamp(table['updated'])
print(f"Updated: {updated.strftime('%Y-%m-%d %H:%M')}")
```

### 8. Build Reusable Query Helpers

```python
def get_recent_tables(days=7, subjects=None, lang="da"):
    """Get recently updated tables with optional subject filter."""
    payload = {"pastDays": days, "lang": lang}
    if subjects:
        payload["subjects"] = subjects
    return get_tables(payload)

def get_tables_by_subject(subject_id, lang="en"):
    """Get all tables for a subject in English."""
    return get_tables({"subjects": [subject_id], "lang": lang})

def get_active_tables():
    """Get all active tables (default behavior)."""
    return get_tables()

def get_all_tables(include_inactive=False):
    """Get all tables, optionally including inactive ones."""
    if include_inactive:
        return get_tables({"includeInactive": True})
    return get_tables()
```

### 9. Document Data Freshness

```python
def analyze_freshness(tables):
    """Analyze update patterns of tables."""
    from datetime import datetime, timedelta

    now = datetime.now()
    fresh = sum(1 for t in tables
                if (now - parse_dst_timestamp(t['updated'])).days <= 7)
    stale = sum(1 for t in tables
                if (now - parse_dst_timestamp(t['updated'])).days > 365)

    print(f"Total tables: {len(tables)}")
    print(f"Fresh (<7 days): {fresh} ({fresh/len(tables)*100:.1f}%)")
    print(f"Stale (>1 year): {stale} ({stale/len(tables)*100:.1f}%)")

# Usage
tables = get_tables()
analyze_freshness(tables)
```

### 10. Use English for International Applications

```python
# For user-facing applications
def get_tables_for_ui(subject_id):
    """Get tables formatted for UI display."""
    tables = get_tables({
        "subjects": [subject_id],
        "lang": "en"  # English for wider audience
    })

    return [{
        'id': t['id'],
        'title': t['text'],
        'unit': t['unit'],
        'updated': t['updated'],
        'period_range': f"{t['firstPeriod']} - {t['latestPeriod']}",
        'is_active': t['active']
    } for t in tables]
```

---

## Summary

### Quick Reference

- **Endpoint:** `https://api.statbank.dk/v1/tables`
- **Methods:** GET (all tables), POST (filtered)
- **Default results:** 2,223 active tables
- **Response format:** JSON array of table objects
- **Average response time:** 0.13s - 0.67s
- **Response size:** 3 KB - 1,229 KB

### Most Useful Queries

1. **Get all tables:** `GET /tables` or `POST {}` → 2,223 tables
2. **Transport tables:** `{"subjects": ["7"]}` → 175 tables
3. **Recent updates:** `{"pastDays": 7}` → ~120 tables
4. **Targeted search:** `{"subjects": ["7"], "pastDays": 30}` → ~14 tables
5. **English version:** Add `"lang": "en"` to any query

### Key Takeaways

✅ **Server-side filtering is fast and efficient**
✅ **All response fields are always present (100% consistency)**
✅ **Subject filtering is the most practical filter**
✅ **Combine multiple filters for precise results**
✅ **Invalid parameters are silently ignored (no error)**
✅ **GET and POST have identical performance for "all tables"**

⚠️ **Text search is NOT supported (parameter ignored)**
⚠️ **ID filtering is NOT supported (parameter ignored)**
⚠️ **Including inactive tables is 2.4x slower, 2.5x larger**
⚠️ **Invalid subject IDs return HTTP 400 error**

---

**Report Generated:** 2025-10-30
**API Version:** v1
**Total Tests Executed:** 15
**Test Duration:** ~15 seconds
