# DST API /subjects Endpoint - Complete Guide

**Test Date:** 2025-10-30
**Base URL:** `https://api.statbank.dk/v1/subjects`
**API Version:** v1

---

## Table of Contents

1. [Overview](#overview)
2. [HTTP Methods](#http-methods)
3. [Parameters](#parameters)
4. [Response Structure](#response-structure)
5. [Request Examples](#request-examples)
6. [Response Examples](#response-examples)
7. [Error Responses](#error-responses)
8. [Performance Metrics](#performance-metrics)
9. [Best Practices](#best-practices)

---

## Overview

The `/subjects` endpoint returns the hierarchical structure of Danmarks Statistik's subject taxonomy. This taxonomy organizes all statistical tables into a multi-level hierarchy of topics and subtopics.

**Key Features:**
- Returns top-level subjects by default
- Supports full recursive hierarchy expansion
- Can include table listings at any level
- Supports both Danish and English
- Available in JSON (default) and XML formats
- Total of 5,542 tables across all subjects (as of test date)

---

## HTTP Methods

### GET Request

**Support:** ✅ Fully supported
**Use Case:** Quick retrieval of top-level subjects in Danish

```bash
GET https://api.statbank.dk/v1/subjects
```

**Behavior:**
- Returns 10 top-level subjects
- Danish language by default
- No nested subjects included
- No tables included
- Fast response (~130ms)

### POST Request

**Support:** ✅ Fully supported
**Use Case:** Advanced queries with parameters

```bash
POST https://api.statbank.dk/v1/subjects
Content-Type: application/json

{
  "recursive": true,
  "lang": "en",
  "includeTables": true
}
```

**Behavior:**
- Allows parameter customization
- Same default behavior as GET when body is empty
- Supports all query parameters

---

## Parameters

All parameters are optional and passed in the POST request body as JSON.

### `lang` - Language Selection

| Value | Description | Status |
|-------|-------------|--------|
| `"da"` | Danish (default) | ✅ Supported |
| `"en"` | English | ✅ Supported |
| Other | Invalid | ❌ Returns 400 error |

**Example:**
```json
{
  "lang": "en"
}
```

**Effect:**
- Changes `description` field to specified language
- English: "Population" vs Danish: "Befolkning"
- Affects all levels of the hierarchy

**Performance:** ~120-140ms (no significant difference between languages)

---

### `recursive` - Expand Full Hierarchy

| Value | Description | Status |
|-------|-------------|--------|
| `true` | Include all nested subjects | ✅ Supported |
| `false` | Only top-level subjects (default) | ✅ Supported |
| String | Treated as false | ⚠️ No error, converts to boolean |

**Example:**
```json
{
  "recursive": true
}
```

**Effect:**
- `false`: Returns only top-level subjects (10 items), empty `subjects` arrays
- `true`: Returns complete hierarchy (all levels nested), populated `subjects` arrays

**Performance:**
- `false`: ~130ms, ~900 bytes
- `true`: ~180ms, ~35KB (without tables)

**Hierarchy Depth:**
- Level 0: 10 top-level subjects
- Level 1: Subject areas (e.g., "Population", "Labour market")
- Level 2: Specific topics (e.g., "Population figures", "Immigrants")
- Tables appear at level 2 and sometimes level 3

---

### `includeTables` - Include Table Listings

| Value | Description | Status |
|-------|-------------|--------|
| `true` | Include tables in each subject | ✅ Supported |
| `false` | No tables (default) | ✅ Supported |

**Example:**
```json
{
  "includeTables": true
}
```

**Effect:**
- Adds `tables` array to subject objects that have tables
- Tables appear at the leaf nodes of the subject hierarchy
- Each table includes: `id`, `text`, `unit`, `updated`, `active`

**Performance:**
- Without tables: ~130ms, ~1KB
- With tables (non-recursive): ~110ms, ~1KB
- With tables (recursive): ~500ms, ~1.3MB

**Table Distribution:**
- Total tables in database: 5,542
- Tables only appear at terminal subject nodes (deepest level)
- Example: "Population figures" subject has 45 tables
- Top-level subjects never have tables directly

---

### `format` - Response Format

| Value | Description | Content-Type | Status |
|-------|-------------|--------------|--------|
| `"JSON"` | JSON format (default) | `text/json; charset=utf-8` | ✅ Supported |
| `"JSONP"` | JSON (no callback support) | `text/json; charset=utf-8` | ⚠️ Same as JSON |
| `"CSV"` | Returns JSON anyway | `text/json; charset=utf-8` | ❌ Not implemented |
| `"XML"` | XML format | `text/xml; charset=utf-8` | ✅ Supported |

**Example:**
```json
{
  "format": "XML"
}
```

**XML Response Structure:**
```xml
<ArrayOfsubject xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
  <subject>
    <id>1</id>
    <description>Borgere</description>
    <active>true</active>
    <hasSubjects>true</hasSubjects>
    <subjects />
  </subject>
  ...
</ArrayOfsubject>
```

**Note:** CSV and JSONP formats are not actually implemented despite being accepted.

---

### `subjects` - Filter by Subject IDs

**Status:** ❌ Not supported

**Tested:**
```json
{
  "subjects": ["02"]
}
```

**Result:** HTTP 400 Bad Request

**Note:** This parameter appears in some documentation but is not functional on the `/subjects` endpoint. Use the `/tables` endpoint with `subjects` filter instead.

---

### `omitInactiveSubjects` - Filter Inactive Subjects

**Status:** ⚠️ Unknown effect / Not verified

**Tested:**
```json
{
  "omitInactiveSubjects": true
}
```

**Result:** Returns 200, but no observable difference in response. Most subjects are already marked as `active: true`. This parameter may be for internal use or legacy compatibility.

---

## Response Structure

### JSON Schema

```typescript
interface Subject {
  id: string;                    // Unique subject ID (e.g., "1", "3401", "20021")
  description: string;           // Subject name (language-dependent)
  active: boolean;              // Whether subject is currently active
  hasSubjects: boolean;         // Whether subject has child subjects
  subjects: Subject[];          // Nested child subjects (empty if recursive=false)
  tables?: Table[];             // Tables in this subject (only if includeTables=true)
}

interface Table {
  id: string;                   // Table ID (e.g., "FOLK1A")
  text: string;                 // Table description
  unit?: string;                // Measurement unit
  updated: string;              // ISO date string (e.g., "2025-10-15T08:00:00")
  active: boolean;              // Whether table is currently active
  variables?: string[];         // List of variable names in the table
}

type SubjectsResponse = Subject[];
```

### Response Headers

```
Cache-Control: no-cache
Pragma: no-cache
Content-Type: text/json; charset=utf-8
Expires: -1
Server: Microsoft-IIS/10.0
StatbankAPI-Request-Id: <uuid>
Access-Control-Expose-Headers: StatbankAPI-Request-Id
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
Strict-Transport-Security: max-age=31536000
Date: <http-date>
Connection: close
Content-Length: <bytes>
```

**Important Headers:**
- `StatbankAPI-Request-Id`: Unique request identifier for debugging
- `Content-Type`: Always `text/json` for JSON, `text/xml` for XML
- `Cache-Control: no-cache`: Responses are not cached

---

## Request Examples

### 1. Basic GET Request (Top-Level Subjects, Danish)

```bash
curl -X GET 'https://api.statbank.dk/v1/subjects'
```

**Use Case:** Quick overview of main subject categories

---

### 2. Top-Level Subjects in English

```bash
curl -X POST 'https://api.statbank.dk/v1/subjects' \
  -H 'Content-Type: application/json' \
  -d '{"lang":"en"}'
```

**Use Case:** English-language applications

---

### 3. Full Hierarchy Without Tables

```bash
curl -X POST 'https://api.statbank.dk/v1/subjects' \
  -H 'Content-Type: application/json' \
  -d '{"recursive":true}'
```

**Use Case:** Understanding complete taxonomy structure

---

### 4. Top-Level with Table Counts

```bash
curl -X POST 'https://api.statbank.dk/v1/subjects' \
  -H 'Content-Type: application/json' \
  -d '{"includeTables":true}'
```

**Use Case:** Seeing which subjects have tables available

---

### 5. Complete Dataset (Full Hierarchy + All Tables)

```bash
curl -X POST 'https://api.statbank.dk/v1/subjects' \
  -H 'Content-Type: application/json' \
  -d '{
    "recursive": true,
    "includeTables": true,
    "lang": "en"
  }'
```

**Use Case:** Building a complete local catalog of all DST data

**Warning:** Large response (~1.3MB, 5,542 tables)

---

### 6. XML Format

```bash
curl -X POST 'https://api.statbank.dk/v1/subjects' \
  -H 'Content-Type: application/json' \
  -d '{"format":"XML"}'
```

**Use Case:** Integration with XML-based systems

---

## Response Examples

### Example 1: Default GET Response (Top-Level, Danish)

**Request:**
```bash
curl -X GET 'https://api.statbank.dk/v1/subjects'
```

**Response:**
```json
[
  {
    "id": "1",
    "description": "Borgere",
    "active": true,
    "hasSubjects": true,
    "subjects": []
  },
  {
    "id": "2",
    "description": "Arbejde og indkomst",
    "active": true,
    "hasSubjects": true,
    "subjects": []
  },
  {
    "id": "3",
    "description": "Erhverv",
    "active": true,
    "hasSubjects": true,
    "subjects": []
  },
  {
    "id": "4",
    "description": "Produktion, teknologi og innovation",
    "active": true,
    "hasSubjects": true,
    "subjects": []
  },
  {
    "id": "5",
    "description": "Priser og forbrug",
    "active": true,
    "hasSubjects": true,
    "subjects": []
  },
  {
    "id": "6",
    "description": "Offentlig sektor",
    "active": true,
    "hasSubjects": true,
    "subjects": []
  },
  {
    "id": "7",
    "description": "Boliger og bygninger",
    "active": true,
    "hasSubjects": true,
    "subjects": []
  },
  {
    "id": "8",
    "description": "Uddannelse og viden",
    "active": true,
    "hasSubjects": true,
    "subjects": []
  },
  {
    "id": "9",
    "description": "Kultur og fritid",
    "active": true,
    "hasSubjects": true,
    "subjects": []
  },
  {
    "id": "10",
    "description": "Miljø og energi",
    "active": true,
    "hasSubjects": true,
    "subjects": []
  }
]
```

**Stats:**
- Response time: ~130ms
- Response size: 897 bytes
- Items: 10 subjects

---

### Example 2: Recursive Hierarchy (Excerpt)

**Request:**
```bash
curl -X POST 'https://api.statbank.dk/v1/subjects' \
  -H 'Content-Type: application/json' \
  -d '{"recursive":true,"lang":"en"}'
```

**Response (partial):**
```json
[
  {
    "id": "1",
    "description": "People",
    "active": true,
    "hasSubjects": true,
    "subjects": [
      {
        "id": "3401",
        "description": "Population",
        "active": true,
        "hasSubjects": true,
        "subjects": [
          {
            "id": "20021",
            "description": "Population figures",
            "active": true,
            "hasSubjects": false,
            "subjects": []
          },
          {
            "id": "20024",
            "description": "Immigrants and their descendants",
            "active": true,
            "hasSubjects": false,
            "subjects": []
          },
          {
            "id": "20022",
            "description": "Population projection",
            "active": true,
            "hasSubjects": false,
            "subjects": []
          }
        ]
      },
      {
        "id": "3407",
        "description": "Households and family matters",
        "active": true,
        "hasSubjects": true,
        "subjects": [
          {
            "id": "20010",
            "description": "Households and families",
            "active": true,
            "hasSubjects": false,
            "subjects": []
          }
        ]
      }
    ]
  }
]
```

**Stats:**
- Response time: ~180ms
- Response size: ~35KB
- Hierarchy depth: 3 levels

---

### Example 3: With Tables Included (Excerpt)

**Request:**
```bash
curl -X POST 'https://api.statbank.dk/v1/subjects' \
  -H 'Content-Type: application/json' \
  -d '{
    "recursive": true,
    "includeTables": true,
    "lang": "en"
  }'
```

**Response (partial showing tables):**
```json
[
  {
    "id": "1",
    "description": "People",
    "active": true,
    "hasSubjects": true,
    "subjects": [
      {
        "id": "3401",
        "description": "Population",
        "active": true,
        "hasSubjects": true,
        "subjects": [
          {
            "id": "20021",
            "description": "Population figures",
            "active": true,
            "hasSubjects": false,
            "subjects": [],
            "tables": [
              {
                "id": "FOLK1A",
                "text": "Population at the first day of the quarter",
                "unit": "number",
                "updated": "2025-10-15T08:00:00",
                "active": true,
                "variables": ["area", "sex", "age", "time"]
              },
              {
                "id": "FOLK1AM",
                "text": "Population at the first day of the month",
                "unit": "number",
                "updated": "2025-10-20T08:00:00",
                "active": true,
                "variables": ["area", "sex", "age", "time"]
              }
            ]
          }
        ]
      }
    ]
  }
]
```

**Stats:**
- Response time: ~500ms
- Response size: ~1.3MB
- Total tables: 5,542

**Notes:**
- `tables` array only appears in leaf subjects (those with `hasSubjects: false`)
- Tables include metadata: ID, description, unit, last update date, active status
- Variable names show what dimensions are available in each table

---

## Error Responses

### 1. Invalid Language Code

**Request:**
```json
{
  "lang": "invalid"
}
```

**Response:**
```
HTTP/1.1 400 Bad Request
Content-Type: text/json; charset=utf-8

{
  "errorTypeCode": "REQUEST-LANGUAGE",
  "message": "Det angivne sprog er ugyldigt. / The specified language is not valid."
}
```

**Valid languages:** `"da"`, `"en"`

---

### 2. Using `subjects` Filter Parameter

**Request:**
```json
{
  "subjects": ["02"]
}
```

**Response:**
```
HTTP/1.1 400 Bad Request
```

**Reason:** The `subjects` parameter is not supported on the `/subjects` endpoint. Use the `/tables` endpoint instead to filter by subject.

---

### 3. Malformed JSON

**Request:**
```
{invalid json}
```

**Response:**
```
HTTP/1.1 200 OK
```

**Note:** Surprisingly, malformed JSON returns 200 OK with default response (likely treats as empty body). This is lenient error handling but not recommended to rely on.

---

## Performance Metrics

### Response Times (Average)

| Configuration | Time | Size | Use Case |
|--------------|------|------|----------|
| GET (default) | 130ms | 897 B | Quick lookup |
| POST empty body | 112ms | 897 B | Same as GET |
| POST lang=en | 142ms | 897 B | Translation |
| POST lang=da | 120ms | 897 B | Default |
| POST recursive=true | 187ms | 35 KB | Full hierarchy |
| POST recursive=false | 127ms | 897 B | Top-level only |
| POST includeTables=true | 112ms | 1 KB | Tables metadata |
| POST recursive + includeTables | 500ms | 1.3 MB | Complete catalog |
| POST all params combined | 540ms | 1.3 MB | Maximum data |

**Test Environment:**
- Network: Standard internet connection
- Location: Denmark region
- Date: 2025-10-30

**Observations:**
- Language selection has minimal impact (~10-20ms variation)
- Recursive expansion adds ~50ms but 40x more data
- Including tables with recursion significantly increases time (3-4x) and data (40x)
- Response times are consistent and predictable

---

## Best Practices

### 1. Choose the Right Parameters for Your Use Case

**For browsing/exploration:**
```json
{
  "lang": "en",
  "recursive": false
}
```
Start with top-level, drill down as needed.

**For building a subject tree UI:**
```json
{
  "recursive": true,
  "lang": "en"
}
```
Get full hierarchy without tables to keep response small.

**For creating a complete catalog:**
```json
{
  "recursive": true,
  "includeTables": true,
  "lang": "en"
}
```
Cache this response locally, as it's large.

**For table discovery in a specific area:**
Use the `/tables` endpoint with subject filter instead of this endpoint.

---

### 2. Caching Strategy

**Response Headers:**
- `Cache-Control: no-cache` means responses are not cached by the server
- However, the subject taxonomy changes infrequently

**Recommended:**
- Cache responses client-side for 24 hours
- The complete catalog (recursive + tables) is ideal for local caching
- Use `StatbankAPI-Request-Id` header for debugging cache issues

**Example caching logic:**
```python
import time
import json

CACHE_DURATION = 86400  # 24 hours

def get_subjects_cached(params):
    cache_key = json.dumps(params, sort_keys=True)

    if cache_key in cache and time.time() - cache[cache_key]['time'] < CACHE_DURATION:
        return cache[cache_key]['data']

    data = fetch_subjects(params)
    cache[cache_key] = {'data': data, 'time': time.time()}
    return data
```

---

### 3. Error Handling

**Always handle HTTP errors:**
```python
try:
    response = requests.post('https://api.statbank.dk/v1/subjects', json=params)
    response.raise_for_status()  # Raises HTTPError for 4xx/5xx
    data = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        error_data = e.response.json()
        if error_data.get('errorTypeCode') == 'REQUEST-LANGUAGE':
            # Handle invalid language
            print("Invalid language specified")
except requests.exceptions.RequestException as e:
    # Handle network errors
    print(f"Network error: {e}")
```

---

### 4. Working with the Hierarchy

**Traversing the tree:**
```python
def find_subject_by_id(subjects, target_id):
    """Recursively find a subject by ID"""
    for subject in subjects:
        if subject['id'] == target_id:
            return subject
        if subject.get('subjects'):
            found = find_subject_by_id(subject['subjects'], target_id)
            if found:
                return found
    return None

def get_all_tables(subjects):
    """Extract all tables from hierarchy"""
    tables = []
    for subject in subjects:
        if 'tables' in subject:
            tables.extend(subject['tables'])
        if subject.get('subjects'):
            tables.extend(get_all_tables(subject['subjects']))
    return tables

def count_subjects(subjects, active_only=False):
    """Count total subjects in hierarchy"""
    count = 0
    for subject in subjects:
        if not active_only or subject.get('active', True):
            count += 1
        if subject.get('subjects'):
            count += count_subjects(subject['subjects'], active_only)
    return count
```

**Building a path to a subject:**
```python
def get_subject_path(subjects, target_id, path=None):
    """Get the full path to a subject"""
    if path is None:
        path = []

    for subject in subjects:
        current_path = path + [subject['description']]
        if subject['id'] == target_id:
            return current_path
        if subject.get('subjects'):
            result = get_subject_path(subject['subjects'], target_id, current_path)
            if result:
                return result
    return None

# Example: path = get_subject_path(data, "20021")
# Result: ["People", "Population", "Population figures"]
```

---

### 5. Language Considerations

**Support both languages:**
```python
def get_subjects_multilingual():
    """Fetch subjects in both languages for bilingual support"""
    subjects_da = fetch_subjects({'recursive': True, 'lang': 'da'})
    subjects_en = fetch_subjects({'recursive': True, 'lang': 'en'})

    # Build mapping
    translations = {}

    def map_translations(da_list, en_list):
        for da_subj, en_subj in zip(da_list, en_list):
            translations[da_subj['id']] = {
                'da': da_subj['description'],
                'en': en_subj['description']
            }
            if da_subj.get('subjects') and en_subj.get('subjects'):
                map_translations(da_subj['subjects'], en_subj['subjects'])

    map_translations(subjects_da, subjects_en)
    return translations
```

---

### 6. Performance Optimization

**Avoid repeated large requests:**
```python
# Bad: Fetching full catalog on every request
def get_table_info(table_id):
    all_subjects = fetch_subjects({
        'recursive': True,
        'includeTables': True
    })  # 1.3 MB every time!
    return find_table(all_subjects, table_id)

# Good: Fetch once, cache, and reuse
class SubjectCache:
    def __init__(self):
        self._cache = None
        self._timestamp = 0

    def get_subjects(self, refresh_hours=24):
        now = time.time()
        if self._cache is None or (now - self._timestamp) > refresh_hours * 3600:
            self._cache = fetch_subjects({
                'recursive': True,
                'includeTables': True
            })
            self._timestamp = now
        return self._cache
```

**Lazy loading for UI:**
```python
# Instead of loading full hierarchy, load on-demand
def get_subject_children(subject_id):
    """Load only one level at a time"""
    # Implementation depends on whether you want to:
    # A) Fetch full hierarchy once and traverse (better for offline)
    # B) Make multiple requests (better for reducing initial load)
    pass
```

---

### 7. Integration Patterns

**Pattern A: Pre-fetch and index (Recommended for applications)**
```python
# On application startup or scheduled task
def build_subject_index():
    data = fetch_subjects({
        'recursive': True,
        'includeTables': True,
        'lang': 'en'
    })

    # Build indexes for fast lookup
    index = {
        'subjects_by_id': {},
        'tables_by_id': {},
        'subjects_by_name': {},
        'hierarchy': data
    }

    def index_subjects(subjects):
        for s in subjects:
            index['subjects_by_id'][s['id']] = s
            index['subjects_by_name'][s['description'].lower()] = s

            if 'tables' in s:
                for table in s['tables']:
                    index['tables_by_id'][table['id']] = {
                        'table': table,
                        'subject': s
                    }

            if s.get('subjects'):
                index_subjects(s['subjects'])

    index_subjects(data)
    return index

# Use the index
index = build_subject_index()
subject = index['subjects_by_id']['20021']
table_info = index['tables_by_id']['FOLK1A']
```

**Pattern B: On-demand loading (For exploratory tools)**
```python
# Load only what's needed when needed
def explore_subjects(subject_id=None):
    if subject_id is None:
        # Top level
        return fetch_subjects({})
    else:
        # Get full tree and navigate to subject
        data = fetch_subjects({'recursive': True})
        return find_subject_by_id(data, subject_id)
```

---

### 8. API Request Etiquette

**Rate limiting:**
- No official rate limits documented
- Be respectful: cache responses and avoid hammering the API
- Use request IDs from headers for debugging

**Request headers to include:**
```python
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'YourApp/1.0 (contact@example.com)'  # Good practice
}
```

**Timeout configuration:**
```python
# Different timeouts for different request types
TIMEOUTS = {
    'top_level': 5,      # Fast requests
    'recursive': 10,     # Medium requests
    'with_tables': 30    # Large requests
}

response = requests.post(url, json=params, timeout=TIMEOUTS['with_tables'])
```

---

## Summary

### Key Findings

1. **Both GET and POST work identically** with default parameters
2. **Three main parameters:** `lang`, `recursive`, `includeTables`
3. **Format support:** JSON (default) and XML only; CSV/JSONP don't work
4. **Response size varies dramatically:** 900 bytes to 1.3 MB
5. **Performance is good:** 100-500ms depending on parameters
6. **No caching by default:** Implement client-side caching
7. **5,542 total tables** across 10 main subject areas
8. **Subject filter doesn't work:** Use `/tables` endpoint instead

### Quick Reference

| Goal | Parameters |
|------|------------|
| Browse subjects | `{}` or `{"lang": "en"}` |
| Full hierarchy | `{"recursive": true}` |
| See all tables | `{"recursive": true, "includeTables": true}` |
| Complete catalog | `{"recursive": true, "includeTables": true, "lang": "en"}` |

### Common Pitfalls

1. Don't try to use `subjects` parameter - it doesn't work
2. Don't request CSV format - you'll get JSON anyway
3. Don't forget to cache - the API returns `no-cache` but data is stable
4. Don't ignore the hierarchy - tables are nested deep in the structure

### Next Steps

- See `API_GUIDE_TABLES.md` for the `/tables` endpoint documentation
- See `API_GUIDE_TABLEINFO.md` for the `/tableinfo` endpoint documentation
- See `API_GUIDE_DATA.md` for the `/data` endpoint documentation

---

**Document Version:** 1.0
**Last Updated:** 2025-10-30
**Tested By:** Claude Code (Automated Testing)
