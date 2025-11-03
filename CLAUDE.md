# DST Skills - Command Composition Architecture

This project provides composable commands and specialized agents for fetching and analyzing data from Danmarks Statistik (DST).

## Architecture Overview

**Command Composition:** Commands call other commands for complex workflows
**Agent Delegation:** Commands invoke specialized agents via Task tool
**Progressive Disclosure:** Skills provide documentation loaded on-demand

## Quick Start Workflow

### Simple Analysis
```
/dst-discover "electric vehicles"
→ Recommends BIL10, BIL52 tables

/dst-fetch "BIL10,BIL52"
→ Downloads and validates data

/dst-analyze "EV share trends" --tables "BIL10"
→ Calculates trends and metrics
```

### Comprehensive Research
```
/dst-research "Denmark's electric vehicle adoption trends"

This orchestrates:
1. /dst-discover → finds relevant tables
2. /dst-fetch → downloads with validation
3. /dst-analyze → calculates insights
4. /dst-visualize → creates charts
5. /dst-report → generates HTML report

Output: reports/{topic}_{timestamp}/report.html
```

## Available Commands

### Core Workflow Commands
- `/dst-discover {query}` - Find relevant DST tables
- `/dst-fetch {table_ids}` - Download and validate data
- `/dst-analyze {question}` - Query and analyze data
- `/dst-visualize {topic}` - Create Chart.js visualizations
- `/dst-report {topic}` - Generate HTML report

### Orchestration
- `/dst-research {topic}` - Complete workflow (calls all above)

## Specialized Agents

Commands invoke agents via Task tool:

- **dst-fetch-agent** - Data discovery and acquisition
- **dst-analyze-agent** - SQL queries and statistical analysis
- **dst-visualize-agent** - Chart.js visualization creation
- **dst-report-agent** - HTML report generation

## Available Skills

Skills provide documentation and templates:

- `dst-subjects` - Browse DST hierarchy
- `dst-tables` - Search for tables
- `dst-tableinfo` - Get table metadata
- `dst-data` - API quirks (BULK format, suppressed values)
- `dst-query` - SQL patterns for DST data
- `dst-visualization` - Chart.js templates
- `dst-report-template` - HTML report templates
- `dst-list-tables` - List local data
- `dst-check-freshness` - Validate data age

## Key Conventions

- **Table naming:** DST `BIL10` → `dst_bil10` in DuckDB
- **Data location:** `data/dst.db`
- **Reports:** `reports/{topic}_{timestamp}/`
- **BULK format:** Requires ALL variables specified
- **Suppressed values:** `".."` = confidential data

## Example: Complete Analysis

```
User: /dst-research "Share of electric vehicles in Denmark's car fleet"

Phase 1 - Discovery:
  /dst-discover → Finds BIL10 (1993-2025 annual stock data)
  Agent presents: "BIL10 recommended - 33 years, fuel type breakdown"
  User: "Yes, fetch it"

Phase 2 - Acquisition:
  /dst-fetch "BIL10"
  Agent: Fetches 5,940 records, validates, reports: "✓ Ready for analysis"

Phase 3 - Analysis:
  /dst-analyze "Calculate EV share 1993-2025" --tables "BIL10"
  Agent: Queries data, calculates trends, returns metrics

Phase 4 - Visualization:
  /dst-visualize "EV adoption" --data {analysis_results}
  Agent: Creates 3 charts (share %, absolute numbers, BEV vs PHEV)

Phase 5 - Reporting:
  /dst-report "EV adoption" --analysis {results} --viz {charts}
  Agent: Generates comprehensive HTML in reports/ev_adoption_20251030/

Output: reports/ev_adoption_20251030_235658/report.html
```

## Common Tasks

**Browse available data:**
```
/dst-discover "population trends"
```

**Download specific table:**
```
/dst-fetch "FOLK1A"
```

**Quick analysis:**
```
/dst-analyze "Latest population by region" --tables "FOLK1A"
```

**Full research workflow:**
```
/dst-research "Denmark's population aging trends"
```

## Documentation

- `docs/getting-started.md` - Setup and first analysis
- `docs/architecture.md` - Design decisions explained
- `docs/faq.md` - Common questions and solutions
- `.claude/skills/*/SKILL.md` - Detailed skill documentation

## Infrastructure

- **Validation:** Auto-validates fetches (record counts, suppressed values)
- **Caching:** Caches tableinfo (24hr TTL)
- **Error handling:** Helpful messages for BULK format, API errors
- **Organization:** Each research in separate subfolder

## Key Features

✅ Command composition - modular, testable workflows
✅ Agent delegation - specialized capabilities
✅ Organized outputs - subfolders per research topic
✅ Data validation - automatic quality checks
✅ Error recovery - helpful messages and suggestions
✅ Template-based - consistent visualizations and reports
✅ Caching - faster repeated operations
