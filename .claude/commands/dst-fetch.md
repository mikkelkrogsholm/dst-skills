---
name: dst-fetch
description: Fetch DST data and validate
---

Fetch Danmarks Statistik data for tables: {{table_ids}}

Follow this workflow:
1. Check existing data:
   - Invoke dst-list-tables skill to see what's stored
   - Invoke dst-check-freshness skill for specified tables
2. Fetch missing or stale tables:
   - Invoke dst-data skill for API quirks reference
   - Execute: python scripts/fetch_and_store.py --table-id <ID> --filters '{"VAR":["*"],...}'
   - Handle BULK format requirements (all variables must be specified)
3. Validate fetched data:
   - Execute: python scripts/db/validate.py --table-id <ID>
   - Check record counts match expected
   - Identify suppressed values (..)
   - Report any issues

Present validation report with:
- Tables fetched successfully
- Record counts
- Any warnings or issues
- Ready for analysis: Yes/No
