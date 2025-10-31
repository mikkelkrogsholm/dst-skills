---
name: dst-fetch
description: Fetch DST data and validate
---

Use the Task tool to invoke the DST Fetcher agent with this prompt:

"Fetch Danmarks Statistik data for tables: {{table_ids}}

Your workflow:
1. Check existing data:
   - Invoke dst-list-tables skill to see what's already stored
   - Invoke dst-check-freshness skill for the specified tables
2. For missing or stale tables:
   - Invoke dst-data skill for API quirks reference
   - Execute: python scripts/fetch_and_store.py --table-id <ID> --filters '{"VAR":["*"],...}'
   - Handle BULK format requirements (all variables must be specified)
3. Validate all fetched data:
   - Execute: python scripts/db/validate.py --table-id <ID>
   - Check record counts match expected
   - Identify suppressed values (..)
   - Note any issues

Return a validation report with:
- Tables fetched successfully
- Record counts for each table
- Any warnings or issues encountered
- Ready for analysis: Yes/No"

When the agent completes, present the validation report to the user.
