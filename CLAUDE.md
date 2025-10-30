# DST Skills - Danmarks Statistik Data Analysis

This project provides Skills and Agents for fetching and analyzing data from Danmarks Statistik (DST) API, storing it in DuckDB for SQL analysis.

## Quick Start Workflow

### 1. Fetch Data
```
User: "Use dst-data to fetch FOLK1A"
→ Downloads data to DuckDB ✅
```

### 2. Analyze Data
```
User: "Analyze the population trends in dst_folk1a"
→ DST Analyst agent analyzes data and returns insights ✅
```

### 3. Comprehensive Analysis (Optional)
```
User: "Provide multi-table analysis of Denmark's population and economic trends"
→ DST Research Analyst performs deep analysis across multiple datasets ✅
```

## Available Skills

Invoke skills directly for data operations:
- `/dst-subjects` - Browse DST topic hierarchy
- `/dst-tables` - Search for tables by subject/keyword
- `/dst-tableinfo` - Get table metadata and structure
- `/dst-data` - Download and store data
- `/dst-list-tables` - List locally stored tables
- `/dst-check-freshness` - Check data age
- `/dst-query` - Run SQL queries on stored data

## Agents

### DST Fetcher (Data Researcher)
**Trigger**: "Find me X data" or "What data is available about X?"

**Role**: Researches DST API, finds relevant tables, and downloads data
- ✅ Browses subjects and searches for tables
- ✅ Returns table recommendations with exact fetch commands
- ✅ Downloads and stores data in DuckDB

**Example**:
```
User: "Find and fetch electric vehicle data"
Fetcher: [Searches DST] → "Found BIL707. Downloading..." → Data stored in DuckDB
```

### DST Analyst
**Trigger**: "Analyze X" or "What's the trend in X?"

**Role**: Analyzes data stored in DuckDB and generates insights
- ✅ Checks data availability and freshness
- ✅ Runs SQL queries and statistical analysis
- ✅ Returns formatted analysis as text
- ✅ Can create and save analysis reports

**Example**:
```
User: "Analyze population growth in dst_folk1a"
Analyst: [Queries data] → Returns trends, statistics, insights
```

### DST Research Analyst
**Trigger**: "Provide comprehensive analysis of X" or "Compare multiple datasets on X"

**Role**: Performs deep, multi-table analysis across DST datasets
- ✅ Researches and fetches multiple relevant tables
- ✅ Performs cross-table analysis and correlation studies
- ✅ Generates comprehensive statistical reports
- ✅ Creates visualizations and detailed analysis documents
- ✅ Identifies trends and patterns across datasets

**Example**:
```
User: "Analyze Denmark's economic and demographic trends"
Research Analyst: [Fetches population, employment, income data] →
Performs multi-table analysis → Generates comprehensive report with insights
```

## Complete Example

```
User: "I need to analyze Denmark's population by region"

# Step 1: Research what's available
You: "Find population data by region"
Fetcher: "Found FOLK1A (population by region). Use: `/dst-data --table-id FOLK1A`"

# Step 2: Fetch the data
You: "Use dst-data to fetch FOLK1A"
Main Agent: [Downloads] ✅ Stored as dst_folk1a

# Step 3: Analyze
You: "Analyze regional population trends in dst_folk1a"
Analyst: [Returns comprehensive analysis with trends and insights]
```

## Key Points

- ✅ Table naming: DST table "FOLK1A" becomes `dst_folk1a` in DuckDB
- ✅ Data stored in `data/dst.db`
- ✅ Check freshness before re-fetching: `/dst-check-freshness --table-id FOLK1A`
- ✅ Agents work best when you're specific: table IDs > topic names
- ✅ All agents can persist and access data across sessions

## Common Tasks

**Browse available data**:
```
"Use dst-subjects to browse transport data"
```

**Download specific table**:
```
"Use dst-data to fetch BIL707"
```

**Quick analysis**:
```
"Use dst-query on dst_bil707 to show latest electric vehicle registrations"
```

**Complex analysis**:
```
"Analyze the percentage of electric vehicles in Denmark's fleet over time"
→ Analyst will check available tables, run queries, calculate trends
```

## Documentation

- `docs/getting-started.md` - Full setup instructions
- `docs/faq.md` - Common questions and troubleshooting
- `.claude/dev/scratchpads/` - Investigation reports and examples
