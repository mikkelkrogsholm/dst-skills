# Frequently Asked Questions (FAQ)

## General Questions

### What is DST Skills?
DST Skills is an AI-powered system for fetching and analyzing data from Statistics Denmark (Danmarks Statistik). It uses two intelligent agents to help you discover, download, and analyze Danish statistical data.

### Who should use this?
- Data analysts working with Danish statistics
- Researchers studying Danish demographics, economy, or society
- Anyone needing programmatic access to DST data
- Users who prefer conversational interfaces over web forms

### What are the system requirements?
- Python 3.8 or higher
- At least 100 MB disk space (more for large datasets)
- Internet connection for fetching from DST API
- Works on Linux, macOS, and Windows

### How is this different from the DST website?
- **Conversational**: Ask questions in natural language
- **Local Storage**: Data stored locally for offline analysis
- **SQL Access**: Query data with SQL for complex analyses
- **Automation**: Scriptable workflows for repeated tasks
- **AI-Powered**: Agents guide you through the data discovery process

### Can I use it offline?
Partially. Once data is fetched, you can analyze it offline. However, fetching new data requires internet connectivity to access the DST API.

### Is my data private?
Yes. All data is stored locally on your machine in the DuckDB database file (`./data/dst_data.duckdb`). Nothing is sent to external servers except API calls to DST for fetching public statistical data.

## Usage Questions

### How do I get started?
Follow the [Getting Started Guide](getting-started.md). In brief:
1. Install dependencies: `pip install -r requirements.txt`
2. Initialize database: `python scripts/db/init_db.py`
3. Start using agents or scripts

### Which agent should I use?
- **Fetcher Agent**: When you need to download data from DST
- **Analyst Agent**: When you want to analyze data you already have

Trigger words:
- Fetcher: "fetch", "download", "retrieve", "get"
- Analyst: "analyze", "query", "show", "compare"

### How do I switch between agents?
Agents activate based on your request. Simply phrase your question to match what you want:
- "Fetch population data" → Activates Fetcher
- "Analyze population trends" → Activates Analyst

Or explicitly say: "Switch to dst-fetch-agent" or "Switch to dst-analyze-agent"

### Can I use natural language?
Yes! The agents understand natural language requests like:
- "Get me the latest population data"
- "What's the unemployment rate in Copenhagen?"
- "Compare housing prices over the last 5 years"

### How do I export results?
Use the `--output` and `--format` flags:
```bash
# Export to CSV
python scripts/db/query_data.py --sql "SELECT * FROM dst_folk1a" --format csv --output results.csv

# Export to JSON
python scripts/db/query_data.py --sql "SELECT * FROM dst_folk1a" --format json --output results.json
```

### How often should I refresh data?
Depends on the update frequency of the source:
- **Daily data**: Refresh every 1-2 days
- **Monthly data**: Refresh every 30 days
- **Quarterly data**: Refresh every 90 days

Check freshness with:
```bash
python scripts/db/query_metadata.py --table-id <ID> --check-freshness
```

### Can I work with multiple tables?
Yes! You can:
- Fetch multiple tables
- Query multiple tables simultaneously
- Join tables in SQL queries

Example join:
```sql
SELECT a.region, a.population, b.employment
FROM dst_folk1a a
JOIN dst_aup01 b ON a.region = b.region
```

### How do I save my analysis?
Several options:
1. **Export results**: Use `--output` flag to save query results
2. **Save SQL queries**: Create `.sql` files with your queries
3. **Document workflow**: Create markdown files documenting your analysis
4. **Backup database**: Copy `data/dst_data.duckdb` to preserve all fetched data

### Can agents create files and persist data?

**Yes!** The previous limitation (bug #4462) has been fixed. Agents can now:
- Create files (reports, analysis outputs)
- Persist data to DuckDB
- Write directly to the reports/ directory

The dst-analyze-agent and dst-report-agent can generate and save report files.

### When should I use /dst-research vs individual commands?

**/dst-research command**: Use for comprehensive research workflows:
- Orchestrates discovery, fetch, analysis, visualization, and reporting
- Analyzing relationships between multiple datasets
- Comparative analysis across time/regions
- Generates complete HTML reports with interactive visualizations
- Automatically coordinates dst-fetch-agent, dst-analyze-agent, dst-visualize-agent, and dst-report-agent

**Individual commands** (/dst-discover, /dst-analyze, etc.): Use for focused tasks:
- Working with specific tables you already know
- Quick insights and queries on fetched data
- Step-by-step control over the workflow
- When you only need part of the workflow (e.g., just fetch or just analyze)

Think: /dst-research = complete workflow, individual commands = targeted steps.

## Technical Questions

### What database does it use?
DuckDB - an in-process analytical database. It's fast, lightweight, and perfect for analytical queries. No separate server required.

### Can I use SQL directly?
Yes! Use the query_data.py script:
```bash
python scripts/db/query_data.py --sql "YOUR SQL QUERY HERE"
```

Or connect directly to the DuckDB file using any DuckDB client.

### How do I backup my data?
Simple file copy:
```bash
# Backup
cp data/dst_data.duckdb data/dst_data.duckdb.backup

# Restore
cp data/dst_data.duckdb.backup data/dst_data.duckdb
```

### What DST API does it use?
Danmarks Statistik API v1: `https://api.statbank.dk/v1`

Official documentation: https://www.dst.dk/en/Statistik/brug-statistikken/muligheder-i-statistikbanken/api

### Can I extend the system?
Yes! The system is designed to be extensible:
- Add new scripts in `scripts/` directory
- Create new skills in `.claude/skills/` directory
- Modify agent configurations in `.claude/agents/`

### How do I update the system?
```bash
# Pull latest changes (if using git)
git pull

# Update dependencies
pip install --upgrade -r requirements.txt

# Run any new migrations or setup scripts as needed
```

### Where are logs stored?
`logs/dst_system.log` - Check this file for debugging and error information.

### How do I report bugs?
1. Check logs: `logs/dst_system.log`
2. Check existing issues in project repository
3. Create new issue with:
   - What you were trying to do
   - What happened
   - Relevant log entries
   - Your environment (Python version, OS)

## Data Questions

### What DST data is available?
All public data from Statistics Denmark's API. Use the Fetcher Agent to browse subjects or check DST's website: https://www.dst.dk/en

Common categories:
- Population (subject 01-02)
- Labour and income (subject 02)
- Education (subject 03)
- Business (subject 05)
- Housing (subject 09)
- Prices (subject 10)

### How current is the data?
Data freshness depends on DST's update schedule:
- Some tables update daily
- Most update monthly or quarterly
- Some update annually

Always check `fetch_timestamp` in metadata to see when you last downloaded it.

### What's the data format?
DST data is stored in structured tables with columns representing:
- **Dimensions**: Time, geography, categories
- **Values**: The actual statistics (counts, percentages, amounts)

Each table has different variables depending on the dataset.

### Can I filter data when fetching?
Yes, using the `--filters` parameter:
```bash
python scripts/fetch_and_store.py --table-id FOLK1A --filters '{"OMRÅDE":["000"]}'
```

Check table info first to see available filters:
```bash
python scripts/api/get_tableinfo.py --table-id FOLK1A
```

### How much data can I store?
Limited only by your disk space. DuckDB is efficient:
- 1 million rows ≈ 10-50 MB (depends on columns)
- Monitor disk usage with `du -sh data/`

### What if the data seems wrong?
1. Check data freshness - may be outdated
2. Verify query logic - ensure SQL is correct
3. Check DST's official website for comparison
4. Review table metadata for units and definitions
5. If truly incorrect, report to DST (it's their source data)

### How do I clean up old data?
```bash
# List all tables
python scripts/db/query_metadata.py --list-all

# Remove specific table (manual SQL)
# Connect to database and:
# DROP TABLE dst_tablename;
# DELETE FROM dst_metadata WHERE table_id = 'TABLEID';

# Or reinitialize entire database (deletes everything)
rm data/dst_data.duckdb
python scripts/db/init_db.py
```

## Troubleshooting

### Agent doesn't activate
- Use clearer trigger words ("fetch", "analyze")
- Check agent configurations in `.claude/agents/`
- Ensure Claude Code is running properly

### Command not found
- Check you're in the project directory
- Use absolute paths: `./scripts/...`
- Verify Python is in your PATH

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "Table not found" in query
- Table may not be fetched yet - use Fetcher Agent first
- Check available tables: `python scripts/db/query_metadata.py --list-all`
- Remember: table names are lowercase with `dst_` prefix

### API timeout/connection errors
- Check internet connection
- DST API may be temporarily down
- Retry after a few minutes
- Check DST status page

## Still Have Questions?

- **Documentation**: Explore the `docs/` directory
- **Workflows**: See `docs/workflows.md` for examples
- **Troubleshooting**: Check `docs/troubleshooting.md`
- **Quick Reference**: See `docs/quick-reference.md`
- **Logs**: Always check `logs/dst_system.log` for details
