---
name: DST Subjects
description: Browse Danmarks Statistik subject hierarchy to explore available data topics and categories. Use when user wants to discover what data is available or explore DST's organizational structure.
---

# DST Subjects Skill

## Purpose

Browse DST's subject hierarchy to discover available data topics and understand how Statistics Denmark organizes its data. This is the starting point for exploring what data is available in the DST database.

## When to Use

- User wants to explore available data categories
- User asks "what data is available?"
- User needs to find relevant subjects for their analysis
- User wants to understand DST's organizational structure
- Starting point for data discovery workflow

## How to Use

### Basic Usage

Get all top-level subjects:
```bash
python /home/user/dst-skills/scripts/api/get_subjects.py
```

### Get Complete Hierarchy

Get all subject levels recursively:
```bash
python /home/user/dst-skills/scripts/api/get_subjects.py --recursive
```

### Save to File

Save results to a JSON file:
```bash
python /home/user/dst-skills/scripts/api/get_subjects.py --output subjects.json
```

## Expected Output

The script returns a JSON array of subject objects. Each subject contains:

- **id**: Subject identifier (needed for finding tables)
- **description**: Human-readable topic name
- **active**: Whether subject is currently active
- **hasSubjects**: Indicates if there are sub-subjects

Example output:
```json
[
  {
    "id": "01",
    "description": "Population and elections",
    "active": true,
    "hasSubjects": true
  },
  {
    "id": "02",
    "description": "Labour, income and wealth",
    "active": true,
    "hasSubjects": true
  }
]
```

## Key Information to Extract

When browsing subjects, note:

1. **Subject ID**: You'll need this to find tables in that subject area
2. **Description**: The topic or category name
3. **Hierarchy**: How subjects are organized (when using --recursive)

## Next Steps

After identifying a relevant subject:

1. Note the subject ID (e.g., "02" for Labour)
2. Use the **dst-tables** skill to find tables within that subject
3. Example: `python /home/user/dst-skills/scripts/api/get_tables.py --subject 02`

## Examples

### Example 1: Browse all subjects
```bash
python /home/user/dst-skills/scripts/api/get_subjects.py
```

### Example 2: Get complete hierarchy
```bash
python /home/user/dst-skills/scripts/api/get_subjects.py --recursive
```

### Example 3: Save to file for analysis
```bash
python /home/user/dst-skills/scripts/api/get_subjects.py --output subjects.json
```

## Tips

- **Start simple**: Use non-recursive mode first to see top-level subjects
- **Use recursive**: When you need to understand the complete organizational structure
- **Subject IDs**: Typically 2-digit numbers like "01", "02", etc.
- **Save for reference**: Use `--output` to save the hierarchy for future reference

## Common Subjects (Reference)

Typical DST subject categories include:
- 01: Population and elections
- 02: Labour, income and wealth
- 03: Education and research
- 04: Culture and leisure
- 05: Business
- 06: Trade and services
- 07: Transport and tourism
- 08: Money and credit market
- 09: Housing and construction
- 10: Prices and consumption
- 11: National accounts and balance of payments
- 12: Energy
- 13: Environment and resources
- 14: Justice

Note: Verify actual subjects with the API as this list may change.
