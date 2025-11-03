# DST API /subjects Endpoint - Quick Reference Cheat Sheet

## Endpoint
```
https://api.statbank.dk/v1/subjects
```

## Methods
- **GET**: Returns top-level subjects (Danish)
- **POST**: Supports parameters via JSON body

---

## Parameters (All Optional)

| Parameter | Type | Values | Effect |
|-----------|------|--------|--------|
| `lang` | string | `"da"` (default), `"en"` | Language of descriptions |
| `recursive` | boolean | `true`, `false` (default) | Include nested subjects |
| `includeTables` | boolean | `true`, `false` (default) | Include table listings |
| `format` | string | `"JSON"` (default), `"XML"` | Response format |

---

## Common Requests

### 1. Top-level subjects (Danish)
```bash
curl https://api.statbank.dk/v1/subjects
```

### 2. Top-level subjects (English)
```bash
curl -X POST https://api.statbank.dk/v1/subjects \
  -H 'Content-Type: application/json' \
  -d '{"lang":"en"}'
```

### 3. Full hierarchy (no tables)
```bash
curl -X POST https://api.statbank.dk/v1/subjects \
  -H 'Content-Type: application/json' \
  -d '{"recursive":true}'
```

### 4. Complete catalog (hierarchy + tables)
```bash
curl -X POST https://api.statbank.dk/v1/subjects \
  -H 'Content-Type: application/json' \
  -d '{"recursive":true,"includeTables":true,"lang":"en"}'
```

---

## Response Structure

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
        "subjects": [...],
        "tables": [
          {
            "id": "FOLK1A",
            "text": "Population at the first day of the quarter",
            "unit": "number",
            "updated": "2025-10-15T08:00:00",
            "active": true
          }
        ]
      }
    ]
  }
]
```

---

## Performance

| Configuration | Time | Size |
|--------------|------|------|
| Default (top-level) | 130ms | 897 B |
| Recursive | 180ms | 35 KB |
| Recursive + Tables | 500ms | 1.3 MB |

---

## Error Codes

| Error | Cause | Solution |
|-------|-------|----------|
| 400 `REQUEST-LANGUAGE` | Invalid `lang` value | Use `"da"` or `"en"` |
| 400 | Using `subjects` parameter | Don't use - not supported |

---

## Key Stats

- **10** top-level subjects
- **5,542** total tables across all subjects
- **3** levels of hierarchy depth
- Tables appear only at leaf nodes

---

## Python Example

```python
import requests

def get_subjects(lang='en', recursive=False, include_tables=False):
    url = 'https://api.statbank.dk/v1/subjects'
    params = {
        'lang': lang,
        'recursive': recursive,
        'includeTables': include_tables
    }
    response = requests.post(url, json=params, timeout=30)
    response.raise_for_status()
    return response.json()

# Usage
subjects = get_subjects(recursive=True, include_tables=True)
```

---

## Best Practices

1. **Cache responses** - Data changes infrequently
2. **Start with recursive=false** - Drill down as needed
3. **Use recursive+includeTables once** - Build local index
4. **Prefer English** if building international apps
5. **Check `active` flag** before using tables/subjects

---

## Common Mistakes

❌ Don't use `subjects` parameter (not supported)
❌ Don't expect CSV format to work (returns JSON anyway)
❌ Don't fetch full catalog repeatedly (cache it!)
❌ Don't ignore the hierarchy (tables are nested)

✅ Do cache responses
✅ Do check the `active` field
✅ Do use recursive+includeTables for initial catalog build
✅ Do implement client-side caching (24h recommended)

---

## Related Endpoints

- `/tables` - Search and list tables by subject/keyword
- `/tableinfo` - Get detailed metadata for a specific table
- `/data` - Fetch actual data from a table

---

**Quick Tip:** The full catalog (`recursive=true, includeTables=true`) is perfect for building a searchable local index. Fetch once, cache for 24 hours, and use for fast lookups!
