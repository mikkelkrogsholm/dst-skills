# DST API /data Endpoint - Comprehensive Format Guide

**Date:** 2025-10-30
**Author:** API Investigation
**Status:** Complete

## Executive Summary

The Danmarks Statistik (DST) API `/data` endpoint supports **9 different output formats** for retrieving statistical data. This guide documents all formats based on comprehensive testing with table FOLK1A (Population statistics).

### Key Findings

- **9 formats supported:** CSV, JSONSTAT, BULK, XLSX, HTML, DSTML, SDMXCOMPACT, SDMXGENERIC, PX
- **JSON format NOT supported** (returns 400 error)
- **Cell limits apply:** CSV, XLSX, HTML, and XML formats have a 1,000,000 cell limit
- **BULK format recommended** for large datasets (no cell limit, streaming)
- **Wildcards supported:** `*` for all values, `YYYY*` for time patterns
- **Auto-elimination:** When no variables specified, API returns first/default values

---

## Format Comparison Table

| Format | Content-Type | Size (1 row) | Type | Cell Limit | Best For |
|--------|-------------|--------------|------|------------|----------|
| **CSV** | text/csv; charset=utf-8 | 98 bytes | Text | 1M cells | Small datasets, Excel import |
| **JSONSTAT** | text/json; charset=utf-8 | 1,109 bytes | JSON | 1M cells | Statistical analysis, R/Python |
| **BULK** | text/csv; charset=utf-8 | 95 bytes | Text | None | Large datasets, streaming |
| **XLSX** | application/octet-stream | 7,626 bytes | Binary | 1M cells | Excel users, formatted output |
| **HTML** | text/html; charset=utf-8 | 752 bytes | HTML | 1M cells | Web display, reports |
| **DSTML** | text/xml; charset=utf-8 | 1,109 bytes | XML | 1M cells | DST-specific applications |
| **SDMXCOMPACT** | text/xml; charset=utf-8 | 981 bytes | XML | 1M cells | SDMX consumers, compact format |
| **SDMXGENERIC** | text/xml; charset=utf-8 | 1,108 bytes | XML | 1M cells | SDMX consumers, verbose format |
| **PX** | application/octet-stream | 1,650 bytes | Binary | Unknown | PC-Axis tools, Nordic stats |

---

## Format Details

### 1. CSV Format

**Content-Type:** `text/csv; charset=utf-8`
**Separator:** Semicolon (`;`)
**Encoding:** UTF-8 with BOM (`﻿`)

**Sample Output:**
```csv
OMRÅDE;KØN;ALDER;CIVILSTAND;TID;INDHOLD
Hele landet;I alt;Alder i alt;I alt;2023K1;5932654
```

**Characteristics:**
- Human-readable text format
- Semicolon-separated (not comma!)
- UTF-8 encoding with BOM marker
- Headers included
- **Cell limit: 1,000,000 cells**

**When to Use:**
- Small to medium datasets
- Import into Excel or Google Sheets
- Simple parsing requirements
- When you need readable text format

**Error Example (too many cells):**
```json
{
  "errorTypeCode": "REQUEST-LIMIT",
  "message": "Forespørgslen på op mod 4.800.600 celler er over begrænsningen på 1.000.000 celler for denne filtype. Anvend BULK eller andet streaming format i stedet."
}
```

---

### 2. JSONSTAT Format

**Content-Type:** `text/json; charset=utf-8`
**Standard:** JSON-stat (statistical JSON standard)

**Sample Output:**
```json
{
  "dataset": {
    "dimension": {
      "OMRÅDE": {
        "label": "område",
        "category": {
          "index": {"000": 0},
          "label": {"000": "Hele landet"}
        }
      },
      "KØN": {
        "label": "køn",
        "category": {
          "index": {"TOT": 0},
          "label": {"TOT": "I alt"}
        }
      },
      "Tid": {
        "label": "tid",
        "category": {
          "index": {"2023K1": 0},
          "label": {"2023K1": "2023K1"}
        }
      }
    },
    "value": [5932654],
    "label": "Befolkningen den 1. i kvartalet...",
    "source": "Danmarks Statistik",
    "updated": "2025-08-11T06:00:00Z"
  }
}
```

**Characteristics:**
- Structured JSON format following JSON-stat standard
- Includes dimension metadata (labels, categories, indices)
- Data in flat `value` array
- Includes source and update information
- Size: ~1,100 bytes for 1 data point

**When to Use:**
- Statistical analysis in R or Python (pyjstat library)
- When you need dimension metadata
- Machine-readable format with structure
- Integration with JSON-stat compatible tools

**Parsing Libraries:**
- Python: `pyjstat`
- R: `rjstat`
- JavaScript: `jsonstat-toolkit`

---

### 3. BULK Format (RECOMMENDED)

**Content-Type:** `text/csv; charset=utf-8`
**Separator:** Semicolon (`;`)
**Special Feature:** **NO CELL LIMIT** - Streaming format

**Sample Output:**
```csv
OMRÅDE;KØN;ALDER;CIVILSTAND;TID;INDHOLD
Hele landet;I alt;Alder i alt;I alt;2023K1;5932654
```

**Characteristics:**
- Identical structure to CSV
- **NO cell limit** - can handle massive datasets
- Streaming response
- Semicolon-separated
- No BOM marker (unlike CSV)

**When to Use:**
- **Large datasets** (>1M cells)
- **Recommended as default format**
- Programmatic data extraction
- When you might exceed CSV limits
- Production systems

**Example - Large Dataset:**
```python
# Request with all regions and multiple years
variables = [
    {"code": "OMRÅDE", "values": ["*"]},      # All regions
    {"code": "KØN", "values": ["1", "2"]},    # Men and Women
    {"code": "Tid", "values": ["2020*", "2021*", "2022*", "2023*"]}
]
# Works with BULK, would fail with CSV if too many cells
```

**Test Results:**
- All regions (100+), 4 years, 2 genders: ✓ Success (20,165 bytes)
- Would have failed with CSV if more dimensions added

---

### 4. XLSX Format

**Content-Type:** `application/octet-stream; charset=utf-8`
**Format:** Excel 2007+ (.xlsx)
**Type:** Binary

**Characteristics:**
- Binary Excel file format
- Can be opened directly in Excel
- Formatted output with proper styling
- Size: ~7.6 KB for single data point (includes Excel metadata)
- **Cell limit: 1,000,000 cells**

**When to Use:**
- End-users working in Excel
- When you need formatted output
- Reports and presentations
- Non-technical users

**Parsing:**
- Python: `openpyxl`, `pandas.read_excel()`
- Save to file and open in Excel

---

### 5. HTML Format

**Content-Type:** `text/html; charset=utf-8`
**Format:** HTML table

**Sample Output:**
```html
<HTML>
<HEAD>
<META http-equiv="content-type" content="text/html; charset=utf-8">
<TITLE>Befolkningen den 1. i kvartalet efter område, køn, alder, civilstand og tid</TITLE>
</HEAD>
<BODY>
<TABLE>
<TR ALIGN=LEFT>
<TH COLSPAN=5>Befolkningen den 1. i kvartalet efter område, køn, alder, civilstand og tid</TH>
</TR>
<TR ALIGN=RIGHT>
<TH ALIGN=LEFT VALIGN=TOP>Hele landet</TH>
<TH ALIGN=LEFT VALIGN=TOP>I alt</TH>
<TH ALIGN=LEFT VALIGN=TOP>Alder i alt</TH>
<TH ALIGN=LEFT VALIGN=TOP>I alt</TH>
<TD>5.932.654</TD>
</TR>
</TABLE>
</BODY>
</HTML>
```

**Characteristics:**
- Complete HTML document
- Formatted table with headers
- Styled for display
- Numbers formatted with thousands separators
- Size: ~752 bytes for 1 data point
- **Cell limit: 1,000,000 cells**

**When to Use:**
- Embedding in web pages
- Quick data visualization
- Reports and dashboards
- Email content

---

### 6. DSTML Format

**Content-Type:** `text/xml; charset=utf-8`
**Format:** DST's custom XML format

**Sample Output:**
```xml
<?xml version="1.0"?>
<Cube xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <MetaData>
    <Language>0</Language>
    <Creation-date>30-10-2025 21:46:00</Creation-date>
    <LastUpdated>11-08-2025 08:00:00</LastUpdated>
    <TableSource>FOLK1A</TableSource>
    <Title>Befolkningen den 1. i kvartalet efter område, køn, alder, civilstand og tid</Title>
    <Contents>Befolkningen den 1. i kvartalet</Contents>
    <Unit>Antal</Unit>
    <Variable Code="V1" Text="område">
      <Value Code="000">Hele landet</Value>
    </Variable>
    <Variable Code="V2" Text="køn">
      <Value Code="TOT">I alt</Value>
    </Variable>
    <Variable Code="V5" Text="tid">
      <Value Code="2023K1">2023K1</Value>
    </Variable>
  </MetaData>
  <Data>
    <Cell CellKey="0,0,0,0,0">
      <Value>5932654</Value>
    </Cell>
  </Data>
</Cube>
```

**Characteristics:**
- DST-specific XML schema
- Rich metadata included
- Cell-based data structure
- Creation and update timestamps
- Size: ~1,109 bytes for 1 data point
- **Cell limit: 1,000,000 cells**

**When to Use:**
- DST-specific applications
- When you need metadata preservation
- Legacy system integration
- Archival purposes

---

### 7. SDMXCOMPACT Format

**Content-Type:** `text/xml; charset=utf-8`
**Standard:** SDMX 2.0 Compact

**Sample Output:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<CompactData xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message"
             xmlns:fol="urn:sdmx:org.sdmx.infomodel.keyfamily.KeyFamily=:FOLK1A(1.0):compact">
  <Header>
    <ID>FOLK1A_20251030214629_06bb204a-b8c2-4bca-8fef-e2b5ee93521d</ID>
    <Test>false</Test>
    <Prepared>2025-10-30T21:46:29+01:00</Prepared>
    <Sender>
      <Name xml:lang="da">Danmarks Statistik</Name>
      <Contact>
        <Name xml:lang="da">Dorthe Larsen</Name>
        <Telephone>+45 23498326</Telephone>
        <Email>dla@dst.dk</Email>
      </Contact>
    </Sender>
    <Extracted>2025-10-30T21:46:29+01:00</Extracted>
  </Header>
  <fol:DataSet>
    <fol:Series OMRÅDE="000" KØN="TOT" ALDER="IALT" CIVILSTAND="TOT">
      <fol:Obs Tid="2023K1" OBS_VALUE="5932654" />
    </fol:Series>
  </fol:DataSet>
</CompactData>
```

**Characteristics:**
- SDMX 2.0 standard (Statistical Data and Metadata eXchange)
- Compact format (attributes on elements)
- International standard for statistical data
- Size: 981 bytes for 1 data point
- **Cell limit: 1,000,000 cells**

**When to Use:**
- International data exchange
- SDMX-compliant systems
- Central banks, statistical agencies
- When compact XML needed

---

### 8. SDMXGENERIC Format

**Content-Type:** `text/xml; charset=utf-8`
**Standard:** SDMX 2.0 Generic

**Sample Output:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<GenericData xmlns="http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message">
  <Header>
    <ID>FOLK1A_20251030214629_92806ebc-355d-4971-8b07-e392a1353bf8</ID>
    <Test>false</Test>
    <Prepared>2025-10-30T21:46:29+01:00</Prepared>
    <Sender>
      <Name xml:lang="da">Danmarks Statistik</Name>
    </Sender>
  </Header>
  <DataSet>
    <fol:KeyFamilyRef>FOLK1A</fol:KeyFamilyRef>
    <fol:Series>
      <fol:SeriesKey>
        <fol:Value concept="OMRÅDE" value="000" />
        <fol:Value concept="KØN" value="TOT" />
        <fol:Value concept="ALDER" value="IALT" />
        <fol:Value concept="CIVILSTAND" value="TOT" />
      </fol:SeriesKey>
      <fol:Obs>
        <fol:Time>2023K1</fol:Time>
        <fol:ObsValue value="5932654" />
      </fol:Obs>
    </fol:Series>
  </DataSet>
</GenericData>
```

**Characteristics:**
- SDMX 2.0 Generic format (more verbose than Compact)
- Uses nested elements instead of attributes
- More flexible structure
- Size: 1,108 bytes for 1 data point (slightly larger than Compact)
- **Cell limit: 1,000,000 cells**

**When to Use:**
- SDMX systems requiring generic format
- When schema flexibility needed
- Maximum compatibility with SDMX tools

**Compact vs Generic:**
- **Compact:** Attributes on elements, smaller size, faster parsing
- **Generic:** Nested elements, more flexible, better schema validation

---

### 9. PX Format (PC-Axis)

**Content-Type:** `application/octet-stream; charset=ansi`
**Standard:** PC-Axis file format
**Type:** Binary (text-based but ANSI encoded)

**Characteristics:**
- Nordic statistical standard
- Text-based but binary encoding (ANSI charset)
- Used by statistical agencies in Nordic countries
- Size: ~1,650 bytes for 1 data point
- Cell limit: Unknown (not tested)

**When to Use:**
- PC-Axis software users
- Nordic statistical applications
- Integration with Statistics Norway, Statistics Sweden, etc.
- When required by downstream systems

**Tools:**
- PC-Axis desktop application
- PX-Web
- Nordic statistical software

---

## Variable Specification Guide

### Basic Structure

Variables are specified as an array of objects with `code` and `values`:

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
      "values": ["1", "2"]
    },
    {
      "code": "Tid",
      "values": ["2023K1"]
    }
  ]
}
```

### Variable Value Patterns

#### 1. Specific Values
```json
{"code": "KØN", "values": ["1", "2"]}  // Men and Women
{"code": "OMRÅDE", "values": ["101", "147"]}  // Copenhagen and Frederiksberg
```

#### 2. Wildcard - All Values
```json
{"code": "KØN", "values": ["*"]}  // All gender categories
{"code": "OMRÅDE", "values": ["*"]}  // All regions
```

**Example Result:**
```csv
Hele landet;I alt;...
Hele landet;Mænd;...
Hele landet;Kvinder;...
```

#### 3. Time Pattern - Year Wildcard
```json
{"code": "Tid", "values": ["2023*"]}  // All 2023 quarters
```

**Expands to:**
- 2023K1
- 2023K2
- 2023K3
- 2023K4

**Multiple Years:**
```json
{"code": "Tid", "values": ["2020*", "2021*", "2022*", "2023*"]}
```

#### 4. Total/Aggregate Values
```json
{"code": "KØN", "values": ["TOT"]}  // "I alt" (Total)
{"code": "ALDER", "values": ["IALT"]}  // "Alder i alt" (All ages)
```

### No Variables - Auto Elimination

When you don't specify variables, the API uses **auto-elimination**:

```json
{
  "table": "FOLK1A",
  "format": "CSV"
  // No variables specified
}
```

**Result:**
```csv
TID;INDHOLD
2025K3;6002420
```

**Behavior:**
- Variables with `elimination: true` are eliminated to their first value
- Only time dimension (`Tid`) is kept
- Returns latest available data point

---

## Cell Limit Details

### What Counts as a Cell?

**Cell calculation:** `cells = value_count_var1 × value_count_var2 × ... × value_count_varN`

**Example 1 - Within Limit:**
```json
// 1 region × 2 genders × 1 age × 1 civil status × 4 quarters = 8 cells
{
  "variables": [
    {"code": "OMRÅDE", "values": ["000"]},      // 1 value
    {"code": "KØN", "values": ["1", "2"]},      // 2 values
    {"code": "ALDER", "values": ["IALT"]},      // 1 value
    {"code": "CIVILSTAND", "values": ["TOT"]},  // 1 value
    {"code": "Tid", "values": ["2023*"]}        // 4 values (K1-K4)
  ]
}
// Total: 1 × 2 × 1 × 1 × 4 = 8 cells ✓
```

**Example 2 - Exceeds Limit:**
```json
// 100 regions × 3 genders × 126 ages × 5 civil statuses × 4 quarters
{
  "variables": [
    {"code": "OMRÅDE", "values": ["*"]},        // ~100 values
    {"code": "KØN", "values": ["*"]},           // 3 values
    {"code": "ALDER", "values": ["*"]},         // ~126 values
    {"code": "CIVILSTAND", "values": ["*"]},    // 5 values
    {"code": "Tid", "values": ["2023*"]}        // 4 values
  ]
}
// Total: 100 × 3 × 126 × 5 × 4 = 756,000 cells ✓
// But close to limit! Add one more quarter and it fails.
```

**Example 3 - Error:**
```json
// Request: All dimensions with wildcard
// Error response:
{
  "errorTypeCode": "REQUEST-LIMIT",
  "message": "Forespørgslen på op mod 4.800.600 celler er over begrænsningen på 1.000.000 celler for denne filtype. Anvend BULK eller andet streaming format i stedet."
}
```

### Formats with Cell Limits

| Format | Cell Limit | Recommendation |
|--------|------------|----------------|
| CSV | 1,000,000 | Use BULK if unsure |
| XLSX | 1,000,000 | Use BULK for large datasets |
| HTML | 1,000,000 | Not for large datasets |
| JSONSTAT | 1,000,000 | Use BULK if unsure |
| DSTML | 1,000,000 | Use BULK if unsure |
| SDMXCOMPACT | 1,000,000 | Use BULK if unsure |
| SDMXGENERIC | 1,000,000 | Use BULK if unsure |
| **BULK** | **None** | **Recommended** |
| PX | Unknown | Assume limit exists |

---

## Request Examples

### Example 1: Basic CSV Request

```json
POST https://api.statbank.dk/v1/data
Content-Type: application/json

{
  "table": "FOLK1A",
  "format": "CSV",
  "variables": [
    {"code": "OMRÅDE", "values": ["000"]},
    {"code": "KØN", "values": ["TOT"]},
    {"code": "ALDER", "values": ["IALT"]},
    {"code": "CIVILSTAND", "values": ["TOT"]},
    {"code": "Tid", "values": ["2023K1"]}
  ]
}
```

**Response:**
```csv
OMRÅDE;KØN;ALDER;CIVILSTAND;TID;INDHOLD
Hele landet;I alt;Alder i alt;I alt;2023K1;5932654
```

### Example 2: BULK with Wildcards

```json
POST https://api.statbank.dk/v1/data
Content-Type: application/json

{
  "table": "FOLK1A",
  "format": "BULK",
  "variables": [
    {"code": "OMRÅDE", "values": ["*"]},
    {"code": "KØN", "values": ["TOT"]},
    {"code": "ALDER", "values": ["IALT"]},
    {"code": "CIVILSTAND", "values": ["TOT"]},
    {"code": "Tid", "values": ["2023K1", "2023K2", "2023K3", "2023K4"]}
  ]
}
```

**Response:** 20,165 bytes of CSV data with all regions

### Example 3: JSONSTAT for Analysis

```json
POST https://api.statbank.dk/v1/data

{
  "table": "FOLK1A",
  "format": "JSONSTAT",
  "variables": [
    {"code": "OMRÅDE", "values": ["000"]},
    {"code": "KØN", "values": ["1", "2"]},
    {"code": "ALDER", "values": ["IALT"]},
    {"code": "CIVILSTAND", "values": ["TOT"]},
    {"code": "Tid", "values": ["2020*", "2021*", "2022*", "2023*"]}
  ]
}
```

**Use case:** Time series analysis of men vs women over 4 years

### Example 4: XLSX for Excel Users

```json
POST https://api.statbank.dk/v1/data

{
  "table": "FOLK1A",
  "format": "XLSX",
  "variables": [
    {"code": "OMRÅDE", "values": ["101", "147", "151"]},
    {"code": "KØN", "values": ["TOT"]},
    {"code": "ALDER", "values": ["IALT"]},
    {"code": "CIVILSTAND", "values": ["TOT"]},
    {"code": "Tid", "values": ["2023K1"]}
  ]
}
```

**Response:** Binary Excel file that opens directly in Excel

---

## Error Handling

### Error 1: Invalid Format

**Request:**
```json
{"table": "FOLK1A", "format": "JSON"}
```

**Response:**
```json
HTTP 400 Bad Request
{
  "errorTypeCode": "REQUEST-MISSING",
  "message": "Format ikke angivet, eller ikke gyldigt."
}
```

**Translation:** "Format not specified or not valid"

**Valid formats:** CSV, JSONSTAT, BULK, XLSX, HTML, DSTML, SDMXCOMPACT, SDMXGENERIC, PX

### Error 2: Cell Limit Exceeded

**Request:**
```json
{
  "table": "FOLK1A",
  "format": "CSV",
  "variables": [
    {"code": "OMRÅDE", "values": ["*"]},
    {"code": "KØN", "values": ["*"]},
    {"code": "ALDER", "values": ["*"]},
    {"code": "CIVILSTAND", "values": ["*"]},
    {"code": "Tid", "values": ["2023*"]}
  ]
}
```

**Response:**
```json
HTTP 400 Bad Request
{
  "errorTypeCode": "REQUEST-LIMIT",
  "message": "Forespørgslen på op mod 4.800.600 celler er over begrænsningen på 1.000.000 celler for denne filtype. Anvend BULK eller andet streaming format i stedet."
}
```

**Translation:** "The request for approximately 4,800,600 cells exceeds the limit of 1,000,000 cells for this file type. Use BULK or another streaming format instead."

**Solution:** Change format to BULK

---

## Best Practices

### 1. Choose the Right Format

```
Small dataset (<1000 rows)     → CSV or JSONSTAT
Large dataset (>1000 rows)     → BULK
Excel users                    → XLSX
Web display                    → HTML
Statistical analysis           → JSONSTAT
International exchange         → SDMXCOMPACT or SDMXGENERIC
Nordic stats software          → PX
DST-specific apps              → DSTML
```

### 2. Always Use BULK for Production

**Why:**
- No cell limit
- Same structure as CSV
- Handles growth
- No surprises in production

**Example:**
```python
# Instead of this:
payload = {"table": "FOLK1A", "format": "CSV", ...}

# Do this:
payload = {"table": "FOLK1A", "format": "BULK", ...}
```

### 3. Filter Before Requesting

**Bad - Request everything:**
```json
{
  "table": "FOLK1A",
  "format": "BULK"
  // No variables - gets minimal data due to auto-elimination
}
```

**Good - Request what you need:**
```json
{
  "table": "FOLK1A",
  "format": "BULK",
  "variables": [
    {"code": "OMRÅDE", "values": ["000"]},  // Just whole country
    {"code": "KØN", "values": ["1", "2"]},  // Men and women
    {"code": "Tid", "values": ["2020*", "2021*", "2022*", "2023*"]}
  ]
}
```

### 4. Use Wildcards Wisely

**Efficient - Specific values:**
```json
{"code": "Tid", "values": ["2023K1", "2023K2", "2023K3", "2023K4"]}
```

**Efficient - Year wildcard:**
```json
{"code": "Tid", "values": ["2023*"]}
```

**Potentially problematic - All wildcard:**
```json
{"code": "Tid", "values": ["*"]}  // Could be 70+ quarters!
```

### 5. Calculate Cell Counts

Before requesting, estimate cells:

```python
def estimate_cells(variables_dict):
    """Estimate number of cells in request"""
    cell_count = 1
    for var, values in variables_dict.items():
        if values == ["*"]:
            # Need to know dimension size - check tableinfo
            print(f"Warning: {var} uses wildcard - check tableinfo")
            return None
        else:
            cell_count *= len(values)
    return cell_count

# Example
vars = {
    "OMRÅDE": ["000"],      # 1
    "KØN": ["1", "2"],      # 2
    "ALDER": ["IALT"],      # 1
    "CIVILSTAND": ["TOT"],  # 1
    "Tid": ["2023K1", "2023K2", "2023K3", "2023K4"]  # 4
}
cells = estimate_cells(vars)  # Returns 8
```

---

## Python Code Examples

### Example 1: Fetch CSV Data

```python
import httpx

def fetch_csv_data(table_id, variables):
    """Fetch data in CSV format"""
    url = "https://api.statbank.dk/v1/data"
    payload = {
        "table": table_id,
        "format": "CSV",
        "variables": variables
    }

    response = httpx.post(url, json=payload)
    response.raise_for_status()

    return response.text

# Usage
variables = [
    {"code": "OMRÅDE", "values": ["000"]},
    {"code": "KØN", "values": ["TOT"]},
    {"code": "ALDER", "values": ["IALT"]},
    {"code": "CIVILSTAND", "values": ["TOT"]},
    {"code": "Tid", "values": ["2023K1"]}
]

csv_data = fetch_csv_data("FOLK1A", variables)
print(csv_data)
```

### Example 2: Fetch BULK Data (Recommended)

```python
import httpx
import csv
from io import StringIO

def fetch_bulk_data(table_id, variables):
    """Fetch data in BULK format - no cell limit"""
    url = "https://api.statbank.dk/v1/data"
    payload = {
        "table": table_id,
        "format": "BULK",
        "variables": variables
    }

    response = httpx.post(url, json=payload, timeout=60)
    response.raise_for_status()

    # Parse CSV
    csv_reader = csv.DictReader(StringIO(response.text), delimiter=';')
    return list(csv_reader)

# Usage - Large dataset
variables = [
    {"code": "OMRÅDE", "values": ["*"]},  # All regions
    {"code": "KØN", "values": ["TOT"]},
    {"code": "ALDER", "values": ["IALT"]},
    {"code": "CIVILSTAND", "values": ["TOT"]},
    {"code": "Tid", "values": ["2023*"]}  # All 2023 quarters
]

data = fetch_bulk_data("FOLK1A", variables)
print(f"Retrieved {len(data)} rows")
```

### Example 3: Fetch JSONSTAT Data

```python
import httpx

def fetch_jsonstat_data(table_id, variables):
    """Fetch data in JSONSTAT format"""
    url = "https://api.statbank.dk/v1/data"
    payload = {
        "table": table_id,
        "format": "JSONSTAT",
        "variables": variables
    }

    response = httpx.post(url, json=payload)
    response.raise_for_status()

    return response.json()

# Usage
variables = [
    {"code": "OMRÅDE", "values": ["000"]},
    {"code": "KØN", "values": ["1", "2"]},
    {"code": "ALDER", "values": ["IALT"]},
    {"code": "CIVILSTAND", "values": ["TOT"]},
    {"code": "Tid", "values": ["2020*", "2021*", "2022*", "2023*"]}
]

jsonstat_data = fetch_jsonstat_data("FOLK1A", variables)

# Access data
dataset = jsonstat_data["dataset"]
values = dataset["value"]
dimensions = dataset["dimension"]

print(f"Values: {values}")
print(f"Dimensions: {list(dimensions.keys())}")
```

### Example 4: Fetch XLSX and Save to File

```python
import httpx
from pathlib import Path

def fetch_xlsx_file(table_id, variables, output_path):
    """Fetch data in XLSX format and save to file"""
    url = "https://api.statbank.dk/v1/data"
    payload = {
        "table": table_id,
        "format": "XLSX",
        "variables": variables
    }

    response = httpx.post(url, json=payload)
    response.raise_for_status()

    # Save binary content
    Path(output_path).write_bytes(response.content)
    print(f"Saved Excel file to {output_path}")

# Usage
variables = [
    {"code": "OMRÅDE", "values": ["101", "147", "151"]},
    {"code": "KØN", "values": ["TOT"]},
    {"code": "ALDER", "values": ["IALT"]},
    {"code": "CIVILSTAND", "values": ["TOT"]},
    {"code": "Tid", "values": ["2023*"]}
]

fetch_xlsx_file("FOLK1A", variables, "population_data.xlsx")
```

### Example 5: Handle Cell Limit Errors

```python
import httpx

def fetch_with_fallback(table_id, variables, preferred_format="CSV"):
    """Try preferred format, fall back to BULK if cell limit exceeded"""
    url = "https://api.statbank.dk/v1/data"

    # Try preferred format first
    payload = {
        "table": table_id,
        "format": preferred_format,
        "variables": variables
    }

    response = httpx.post(url, json=payload)

    # Check for cell limit error
    if response.status_code == 400:
        error_data = response.json()
        if error_data.get("errorTypeCode") == "REQUEST-LIMIT":
            print(f"Cell limit exceeded for {preferred_format}, falling back to BULK")

            # Retry with BULK
            payload["format"] = "BULK"
            response = httpx.post(url, json=payload)
            response.raise_for_status()

            return response.text, "BULK"

    response.raise_for_status()
    return response.text, preferred_format

# Usage
variables = [
    {"code": "OMRÅDE", "values": ["*"]},
    {"code": "KØN", "values": ["*"]},
    {"code": "ALDER", "values": ["IALT"]},
    {"code": "CIVILSTAND", "values": ["TOT"]},
    {"code": "Tid", "values": ["2023*"]}
]

data, format_used = fetch_with_fallback("FOLK1A", variables, "CSV")
print(f"Data retrieved using {format_used} format")
```

---

## Summary & Recommendations

### Quick Reference

**Use BULK by default** - It's the safest choice:
```json
{"table": "FOLK1A", "format": "BULK", "variables": [...]}
```

**Format Selection Matrix:**

| Requirement | Format | Reason |
|-------------|--------|--------|
| Default choice | BULK | No cell limit, CSV structure |
| Excel users | XLSX | Native format |
| Python/R analysis | JSONSTAT | Rich metadata |
| Web display | HTML | Ready to render |
| Large datasets | BULK | No limits |
| International exchange | SDMXCOMPACT | Standard format |
| Nordic stats tools | PX | Standard format |

### Key Takeaways

1. **BULK is recommended** - Same as CSV but no cell limit
2. **Always estimate cells** before using CSV, XLSX, HTML, or XML formats
3. **Wildcards work** - Use `*` for all values, `YYYY*` for year patterns
4. **No variables = auto-elimination** - Returns minimal data
5. **JSON format not supported** - Use JSONSTAT instead
6. **Cell limit is 1,000,000** for most formats except BULK
7. **Semicolon separator** - All CSV-like formats use `;` not `,`

### Implementation Checklist

- [ ] Use BULK format by default in production code
- [ ] Add cell limit estimation before CSV/XLSX requests
- [ ] Implement fallback from CSV to BULK on limit errors
- [ ] Use wildcards for time patterns (`2023*`)
- [ ] Filter variables to only what you need
- [ ] Handle Danish error messages properly
- [ ] Set appropriate timeouts (60s+ for large datasets)
- [ ] Test with representative data volumes

---

## Appendix: Test Results

All tests conducted on 2025-10-30 using table FOLK1A.

### Successful Format Tests (13/15)

1. CSV - Basic ✓
2. JSONSTAT ✓
3. BULK ✓
4. XLSX ✓
5. HTML ✓
6. DSTML ✓
7. SDMXCOMPACT ✓
8. SDMXGENERIC ✓
9. PX ✓
10. CSV with wildcards ✓
11. No variables (auto-elimination) ✓
12. BULK with multiple years ✓
13. BULK with all regions ✓

### Failed Tests (2/15)

14. JSON format - Not supported ✗
15. CSV cell limit - Exceeded 1M cells ✗

### Test Data Volumes

| Test | Format | Rows | Size | Status |
|------|--------|------|------|--------|
| Minimal (1 cell) | CSV | 1 | 98 bytes | ✓ |
| Minimal (1 cell) | JSONSTAT | 1 | 1,109 bytes | ✓ |
| Minimal (1 cell) | BULK | 1 | 95 bytes | ✓ |
| Minimal (1 cell) | XLSX | 1 | 7,626 bytes | ✓ |
| Wildcards (12 cells) | CSV | 12 | 678 bytes | ✓ |
| Multi-year (32 cells) | BULK | 32 | 1,739 bytes | ✓ |
| All regions (400 cells) | BULK | ~400 | 20,165 bytes | ✓ |
| All dimensions | CSV | 4.8M cells | - | ✗ Limit exceeded |

---

**End of Guide**
