# DST API /tableinfo Endpoint - Complete Guide

**Date:** 2025-10-30
**Status:** Comprehensive testing completed
**Tested Tables:** FOLK1A, BIL707, FOLK1C

---

## Endpoint Overview

**URL:** `https://api.statbank.dk/v1/tableinfo`
**Method:** POST
**Content-Type:** application/json
**Purpose:** Retrieve complete metadata and structure for a DST table

---

## Request Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `table` | string | Table ID (case-insensitive) | `"FOLK1A"` or `"folk1a"` |

### Optional Parameters

| Parameter | Type | Description | Default | Example |
|-----------|------|-------------|---------|---------|
| `lang` | string | Language code | `"da"` | `"en"` for English |
| `format` | string | Response format | `"JSON"` | `"JSON"` |

### Parameter Testing Results

**Case Sensitivity:**
- Table IDs are case-insensitive
- `{"table": "FOLK1A"}` and `{"table": "folk1a"}` both work
- Response always returns uppercase table ID

**Alternative Parameters:**
- `{"id": "FOLK1A"}` does NOT work
- Must use `"table"` parameter name

**Language Support:**
- `{"table": "FOLK1A", "lang": "en"}` returns English labels
- Available: `"da"` (Danish), `"en"` (English)
- Affects: `text`, `description`, `unit` fields and all variable labels

---

## Response Structure

### Top-Level Metadata

```json
{
  "id": "FOLK1A",
  "text": "Befolkningen den 1. i kvartalet",
  "description": "Befolkningen den 1. i kvartalet efter område, køn, alder, civilstand og tid",
  "unit": "Antal",
  "suppressedDataValue": "0",
  "updated": "2025-08-11T08:00:00",
  "active": true,
  "contacts": [...],
  "documentation": {...},
  "footnote": null,
  "variables": [...]
}
```

### Metadata Fields Explained

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique table identifier | `"FOLK1A"` |
| `text` | string | Short table title | `"Befolkningen den 1. i kvartalet"` |
| `description` | string | Full table description with dimensions | `"Befolkningen...efter område, køn..."` |
| `unit` | string | Measurement unit | `"Antal"` (count) |
| `suppressedDataValue` | string | Value used for suppressed data | `"0"` |
| `updated` | string | Last update timestamp (ISO 8601) | `"2025-08-11T08:00:00"` |
| `active` | boolean | Whether table is actively maintained | `true` |
| `contacts` | array | Contact persons for the table | See below |
| `documentation` | object | Link to documentation | See below |
| `footnote` | string/null | Table-level footnote | Usually `null` |
| `variables` | array | List of table dimensions/variables | See below |

### Contact Structure

```json
{
  "name": "Dorthe Larsen",
  "phone": "+4523498326",
  "mail": "dla@dst.dk"
}
```

### Documentation Structure

```json
{
  "id": "4a12721d-a8b0-4bde-82d7-1d1c6f319de3",
  "url": "https://www.dst.dk/statistikdokumentation/4a12721d-a8b0-4bde-82d7-1d1c6f319de3"
}
```

---

## Variables Structure

Each variable represents a dimension of the table (e.g., region, time, age).

### Variable Object Schema

```json
{
  "id": "OMRÅDE",
  "text": "område",
  "elimination": true,
  "time": false,
  "map": "Denmark_municipality_07",
  "values": [...]
}
```

### Variable Fields

| Field | Type | Description | Notes |
|-------|------|-------------|-------|
| `id` | string | Variable identifier (uppercase) | Used in data requests |
| `text` | string | Variable label | Lowercase in Danish, varies in English |
| `elimination` | boolean | Can be eliminated from result | `true` = can aggregate across this dimension |
| `time` | boolean | Is this the time variable? | Only one variable has `time: true` |
| `map` | string/null | Geographic map identifier | Only for geographic variables |
| `values` | array | List of possible values | Each value has `id` and `text` |

### Value Object Schema

```json
{
  "id": "000",
  "text": "Hele landet"
}
```

Each value in the `values` array contains:
- `id`: The code to use in data requests
- `text`: Human-readable label

---

## Understanding Variables

### 1. Time Variables

**Characteristics:**
- `time: true`
- `elimination: false`
- Usually named `"Tid"` (Danish) or `"time"` (English)
- Values represent time periods

**Example (FOLK1A - Quarterly data):**
```json
{
  "id": "Tid",
  "text": "tid",
  "elimination": false,
  "time": true,
  "values": [
    {"id": "2008K1", "text": "2008K1"},
    {"id": "2008K2", "text": "2008K2"},
    ...
    {"id": "2025K3", "text": "2025K3"}
  ]
}
```

**Example (BIL707 - Annual data):**
```json
{
  "id": "Tid",
  "text": "tid",
  "elimination": false,
  "time": true,
  "values": [
    {"id": "2007", "text": "2007"},
    {"id": "2008", "text": "2008"},
    ...
    {"id": "2025", "text": "2025"}
  ]
}
```

**Time Format Patterns:**
- `"2025"` - Year
- `"2025K1"` - Quarter (K = Kvartal)
- `"2025M01"` - Month
- `"2025U01"` - Week (U = Uge)

### 2. Geographic Variables

**Characteristics:**
- Often named `"OMRÅDE"` (area/region)
- May include `map` field with map identifier
- `elimination: true` (can aggregate regions)

**Example:**
```json
{
  "id": "OMRÅDE",
  "text": "område",
  "elimination": true,
  "time": false,
  "map": "Denmark_municipality_07",
  "values": [
    {"id": "000", "text": "Hele landet"},
    {"id": "084", "text": "Region Hovedstaden"},
    {"id": "101", "text": "København"},
    ...
  ]
}
```

**Geographic Hierarchies:**
- `"000"` typically means "Whole country"
- Region codes: `"081"-"085"`
- Municipality codes: three digits (e.g., `"101"` for Copenhagen)

### 3. Category Variables

**Characteristics:**
- Demographic or classification dimensions
- `elimination: true` (can aggregate)
- `time: false`
- No `map` field

**Example - Gender (KØN):**
```json
{
  "id": "KØN",
  "text": "køn",
  "elimination": true,
  "time": false,
  "values": [
    {"id": "TOT", "text": "I alt"},
    {"id": "1", "text": "Mænd"},
    {"id": "2", "text": "Kvinder"}
  ]
}
```

**Example - Age (ALDER):**
```json
{
  "id": "ALDER",
  "text": "alder",
  "elimination": true,
  "time": false,
  "values": [
    {"id": "IALT", "text": "Alder i alt"},
    {"id": "0", "text": "0 år"},
    {"id": "1", "text": "1 år"},
    ...
    {"id": "125", "text": "125 år"}
  ]
}
```

### 4. Hierarchical Classification Variables

Some variables use hierarchical codes (e.g., vehicle types).

**Example - Vehicle Type (BILTYPE):**
```json
{
  "id": "BILTYPE",
  "text": "køretøjstype",
  "elimination": false,
  "time": false,
  "values": [
    {"id": "4000101002", "text": "Personbiler i alt"},
    {"id": "4000101011", "text": "Personbiler til hyrevognskørsel"},
    {"id": "4000101012", "text": "Personbiler til udlejning"},
    ...
  ]
}
```

**Code Structure:**
- Longer numeric codes indicate hierarchical classification
- Leading digits indicate category level
- Cannot be eliminated (aggregation managed by classification itself)

---

## Elimination Rules

The `elimination` field determines how variables can be aggregated:

### `elimination: true`
- Variable can be eliminated from queries
- Data can be aggregated across this dimension
- Requesting aggregate values (e.g., "I alt", "TOT") returns sum of sub-categories
- Examples: Gender, Age, Region

**Use Case:**
```json
// Request only total population, eliminating gender breakdown
{
  "table": "FOLK1A",
  "variables": [
    {"code": "KØN", "values": ["TOT"]},  // Only total
    {"code": "Tid", "values": ["*"]}      // All time periods
  ]
}
```

### `elimination: false`
- Variable cannot be eliminated
- Must explicitly select values when querying
- Often applies to: time variables, hierarchical classifications
- Examples: Time (Tid), hierarchical vehicle types

**Use Case:**
```json
// Must specify time periods, cannot eliminate
{
  "table": "BIL707",
  "variables": [
    {"code": "Tid", "values": ["2023", "2024", "2025"]}  // Must specify
  ]
}
```

---

## Using Variable Codes for Data Requests

### Step 1: Get Table Structure
```bash
curl -X POST https://api.statbank.dk/v1/tableinfo \
  -H "Content-Type: application/json" \
  -d '{"table":"FOLK1A"}'
```

### Step 2: Identify Variables
From the response, you get:
- Variable IDs (e.g., `"OMRÅDE"`, `"KØN"`, `"Tid"`)
- Value codes for each variable (e.g., `"000"`, `"TOT"`, `"2025K1"`)

### Step 3: Construct Data Request
```json
{
  "table": "FOLK1A",
  "format": "BULK",
  "variables": [
    {
      "code": "OMRÅDE",
      "values": ["000"]
    },
    {
      "code": "KØN",
      "values": ["TOT"]
    },
    {
      "code": "ALDER",
      "values": ["IALT"]
    },
    {
      "code": "CIVILSTAND",
      "values": ["TOT"]
    },
    {
      "code": "Tid",
      "values": ["*"]
    }
  ]
}
```

### Wildcards
- `"*"` - Select all values
- `["2020K1", "2020K2", "2020K3", "2020K4"]` - Select specific values

### Aggregation Values
Common aggregate codes:
- `"TOT"` - Total (common in demographic variables)
- `"IALT"` - Total (Danish: "I alt", used for age, etc.)
- `"000"` - Whole country (for geographic variables)

---

## Error Responses

### 1. Invalid Table ID
**Request:**
```json
{"table": "INVALID123"}
```

**Response:**
```json
{
  "errorTypeCode": "EXTRACT-NOTFOUND",
  "message": "Tabel findes ikke: INVALID123"
}
```
**HTTP Status:** 400

### 2. Missing Table Parameter
**Request:**
```json
{}
```

**Response:**
```json
{
  "errorTypeCode": "REQUEST-MISSING",
  "message": "Der er ikke angivet nogen tabel-id."
}
```
**HTTP Status:** 400

### 3. Empty Table Parameter
**Request:**
```json
{"table": ""}
```

**Response:**
```json
{
  "errorTypeCode": "EXTRACT-NOTFOUND",
  "message": "Tabel findes ikke: "
}
```
**HTTP Status:** 400

---

## Real Examples from Different Tables

### Example 1: FOLK1A (Population by Quarter)

**Request:**
```bash
curl -X POST https://api.statbank.dk/v1/tableinfo \
  -H "Content-Type: application/json" \
  -d '{"table":"FOLK1A","lang":"en"}'
```

**Key Characteristics:**
- **ID:** FOLK1A
- **Type:** Quarterly population statistics
- **Updated:** 2025-08-11
- **Variables:** 5 (Region, Gender, Age, Marital Status, Time)
- **Time Format:** Quarterly (e.g., "2025K1", "2025K2")
- **Geographic:** 105 regions/municipalities
- **Age:** 127 values (0-125 years)

**Variable Summary:**
```
OMRÅDE (region)      - 105 values, elimination: true, map: Denmark_municipality_07
KØN (gender)         - 3 values, elimination: true
ALDER (age)          - 127 values, elimination: true
CIVILSTAND (marital) - 5 values, elimination: true
Tid (time)           - 71 values (2008K1 - 2025K3), elimination: false, time: true
```

### Example 2: BIL707 (Vehicle Fleet)

**Request:**
```bash
curl -X POST https://api.statbank.dk/v1/tableinfo \
  -H "Content-Type: application/json" \
  -d '{"table":"BIL707"}'
```

**Key Characteristics:**
- **ID:** BIL707
- **Type:** Vehicle fleet as of January 1st
- **Updated:** 2025-03-25
- **Variables:** 3 (Region, Vehicle Type, Time)
- **Time Format:** Annual (e.g., "2007", "2008", "2025")
- **Geographic:** 117 regions (includes some special territories)
- **Vehicle Types:** 54 hierarchical classifications

**Variable Summary:**
```
OMRÅDE (region)       - 117 values, elimination: true
BILTYPE (vehicle type)- 54 values, elimination: false (hierarchical codes)
Tid (time)            - 19 values (2007 - 2025), elimination: false, time: true
```

**Vehicle Type Example:**
```json
{
  "id": "4000101002",
  "text": "Personbiler i alt"
}
```
Note: Long numeric codes indicate hierarchical classification.

### Example 3: FOLK1C (Population by Origin)

**Request:**
```bash
curl -X POST https://api.statbank.dk/v1/tableinfo \
  -H "Content-Type: application/json" \
  -d '{"table":"FOLK1C"}'
```

**Key Characteristics:**
- **ID:** FOLK1C
- **Type:** Quarterly population by origin/country
- **Updated:** 2025-08-11
- **Variables:** 6 (Region, Gender, Age, Origin, Country, Time)
- **Time Format:** Quarterly (e.g., "2008K1")
- **Age Groups:** 22 grouped values (not individual years)
- **Countries:** 242 countries/territories

**Variable Summary:**
```
OMRÅDE (region)          - 105 values, elimination: true
KØN (gender)             - 3 values, elimination: true
ALDER (age)              - 22 values (grouped), elimination: true
HERKOMST (origin)        - 4 values, elimination: true
IELAND (country)         - 242 values, elimination: true
Tid (time)               - 71 values (2008K1 - 2025K3), elimination: false, time: true
```

---

## Best Practices

### 1. Always Check tableinfo First
Before requesting data, use `/tableinfo` to:
- Verify table ID is correct
- Understand available variables and their codes
- Check time range available
- Identify which variables can be eliminated

### 2. Use English for International Applications
```json
{"table": "FOLK1A", "lang": "en"}
```
This returns all labels in English, making it easier for non-Danish speakers.

### 3. Identify the Time Variable
Look for `"time": true` to find the time dimension:
```python
time_var = next(v for v in variables if v['time'] == True)
```

### 4. Understand Elimination Rules
- Variables with `elimination: true` can be aggregated
- Variables with `elimination: false` must be explicitly specified

### 5. Check Update Timestamp
Use the `updated` field to:
- Determine data freshness
- Decide if you need to refresh cached data
- Display data currency to users

### 6. Use Geographic Maps
The `map` field indicates available geographic visualizations:
```json
"map": "Denmark_municipality_07"
```

### 7. Handle Hierarchical Codes
Long numeric codes (e.g., "4000101002") indicate hierarchical classifications:
- Leading digits define hierarchy level
- These typically have `elimination: false`
- Must be handled specially in aggregations

### 8. Cache tableinfo Responses
Table structures change infrequently:
- Cache responses locally
- Check `updated` timestamp periodically
- Refresh if data is outdated

---

## Implementation Notes

### Python Example: Parse tableinfo Response
```python
import httpx

def get_table_structure(table_id: str, lang: str = "da") -> dict:
    """Fetch table structure from DST API."""
    response = httpx.post(
        "https://api.statbank.dk/v1/tableinfo",
        json={"table": table_id, "lang": lang},
        timeout=30.0
    )
    response.raise_for_status()
    return response.json()

def extract_time_variable(table_info: dict) -> dict:
    """Extract the time variable from table info."""
    for var in table_info['variables']:
        if var['time']:
            return var
    return None

def extract_variable_codes(table_info: dict) -> dict:
    """Extract all variable codes and their values."""
    return {
        var['id']: [v['id'] for v in var['values']]
        for var in table_info['variables']
    }
```

### SQL Schema for Storing Metadata
```sql
CREATE TABLE table_metadata (
    table_id TEXT PRIMARY KEY,
    text TEXT,
    description TEXT,
    unit TEXT,
    updated TIMESTAMP,
    active BOOLEAN,
    raw_response TEXT  -- Store full JSON
);

CREATE TABLE table_variables (
    table_id TEXT,
    variable_id TEXT,
    text TEXT,
    elimination BOOLEAN,
    time BOOLEAN,
    map TEXT,
    value_count INTEGER,
    PRIMARY KEY (table_id, variable_id)
);
```

---

## Comparison with Other Endpoints

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `/tableinfo` | Get table structure | Variables, codes, metadata |
| `/tables` | Search/list tables | Table IDs and descriptions |
| `/subjects` | Browse topics | Subject hierarchy |
| `/data` | Fetch actual data | Statistical values |

**Workflow:**
1. `/subjects` or `/tables` - Find table IDs
2. `/tableinfo` - Understand table structure
3. `/data` - Request actual data using codes from tableinfo

---

## Testing Summary

**Tables Tested:** FOLK1A, BIL707, FOLK1C
**Parameter Combinations Tested:** 8
**Error Cases Tested:** 3
**Response Fields Documented:** 11 top-level + 6 variable fields

**Test Results:**
- Case-insensitive table IDs: Confirmed
- Language parameter support: Confirmed (da, en)
- Alternative parameter names: Not supported (must use "table")
- Error messages: Clear, with error codes
- Response structure: Consistent across all tested tables

---

## Additional Resources

- **Official Documentation:** https://www.dst.dk/en/Statistik/brug-statistikken/muligheder-i-statistikbanken/api
- **Interactive API Console:** https://api.statbank.dk/console
- **Metadata Standards:** Check individual table documentation URLs

---

**Document Version:** 1.0
**Last Updated:** 2025-10-30
**Author:** Claude Code DST Skills Project
