---
name: DST Tables
description: Search and list Danmarks Statistik tables by subject or keyword. Use when user needs to find specific tables or browse tables within a subject area.
---

# DST Tables Skill

## Purpose

Find DST tables by subject or search term. This skill bridges the gap between browsing subjects and accessing specific data tables. Use it to discover which tables contain the data you need.

## When to Use

- User mentions a specific topic (population, employment, housing, etc.)
- User wants to see all tables in a subject area
- User searches for tables by keyword
- After browsing subjects with the dst-subjects skill
- Need to identify the table ID for data fetching

## How to Use

### List All Tables

Get all available tables (warning: large list):
```bash
python /home/user/dst-skills/scripts/api/get_tables.py
```

### Filter by Subject

Get tables for a specific subject:
```bash
python /home/user/dst-skills/scripts/api/get_tables.py --subject <subject_id>
```

### Search by Keyword

Find tables matching a search term:
```bash
python /home/user/dst-skills/scripts/api/get_tables.py --search "<term>"
```

### Combined Filtering

Use both subject and keyword filters:
```bash
python /home/user/dst-skills/scripts/api/get_tables.py --subject <id> --search "<term>"
```

### Save Results

Save to a file for later reference:
```bash
python /home/user/dst-skills/scripts/api/get_tables.py --subject 02 --output tables.json
```

## Expected Output

The script returns a JSON array of table objects. Each table contains:

- **id**: Table identifier (e.g., "FOLK1A")
- **text**: Human-readable table name
- **description**: What the table contains
- **updated**: Last update date from DST
- **active**: Whether table is currently active
- **variables**: Available dimensions/filters

Example output:
```json
[
  {
    "id": "FOLK1A",
    "text": "Population at the first day of the quarter",
    "description": "Population by region, age, and sex",
    "updated": "2025-10-15T10:30:00",
    "active": true,
    "variables": ["region", "age", "sex", "time"]
  }
]
```

## Key Fields

- **id**: Use this for fetching table info or data
- **text**: Short description of the table
- **description**: Detailed explanation of table contents
- **updated**: Shows data currency - recent updates mean fresh data
- **variables**: The dimensions you can filter/query by

## Next Steps

After identifying an interesting table:

1. Note the table ID (e.g., "FOLK1A")
2. Use **dst-tableinfo** skill to get detailed metadata:
   ```bash
   python /home/user/dst-skills/scripts/api/get_tableinfo.py --table-id FOLK1A
   ```
3. Or use **dst-data** skill to fetch the actual data:
   ```bash
   python /home/user/dst-skills/scripts/fetch_and_store.py --table-id FOLK1A
   ```

## Examples

### Example 1: Tables in Population subject
```bash
python /home/user/dst-skills/scripts/api/get_tables.py --subject 02
```

### Example 2: Search for population tables
```bash
python /home/user/dst-skills/scripts/api/get_tables.py --search "population"
```

### Example 3: Combined search
Find age-related tables in the labour subject:
```bash
python /home/user/dst-skills/scripts/api/get_tables.py --subject 02 --search "age"
```

### Example 4: Save to file
```bash
python /home/user/dst-skills/scripts/api/get_tables.py --subject 02 --output labour_tables.json
```

## Tips

- **Use subject filter** when you know the category (more focused results)
- **Use keyword search** for exploratory discovery across all subjects
- **Check updated date** to see data currency - recently updated tables have fresh data
- **Note table IDs** for the next steps in your workflow
- **Combine filters** to narrow down large result sets

## Common Search Terms

- Population: "population", "folk", "befolkning"
- Employment: "employment", "arbejde", "labour"
- Income: "income", "indkomst", "salary"
- Housing: "housing", "bolig", "dwelling"
- Education: "education", "uddannelse", "school"
- Health: "health", "sundhed"
- Business: "business", "virksomhed", "company"

## Troubleshooting

- **Too many results**: Add `--subject` filter or more specific `--search` term
- **No results**: Try broader search terms or different keywords
- **Need Danish terms**: DST data often uses Danish labels
- **Table not found**: Verify subject ID is correct, try without filters first
