# Task: DST Query (Scripts + Skill)

## Objective
Create Python scripts for querying DST data and generating table summaries, plus the corresponding skill for the Analyst Agent to use them.

## Prerequisites
- Infrastructure setup completed (task-infrastructure.md)
- Database utilities available
- Data stored in DuckDB (from Fetcher)
- Understanding of SQL and DuckDB

## Tasks

### Create Query Execution Script

#### Query Script Implementation
- [ ] Create `scripts/db/query_data.py`
- [ ] Add command-line interface using argparse with arguments:
  - [ ] `--sql` (required) - SQL query string
  - [ ] `--output` (optional) - Save to file (CSV/JSON)
  - [ ] `--format` (optional) - Output format (table/json/csv), default table
  - [ ] `--limit` (optional) - Limit results (safety feature)
- [ ] Implement `execute_query(sql, format='table')` function:
  - [ ] Connect to DuckDB (read-only if possible)
  - [ ] Validate SQL is SELECT only (safety check)
  - [ ] Execute query safely
  - [ ] Fetch results
  - [ ] Handle large result sets gracefully
  - [ ] Return formatted results
- [ ] Add result formatting:
  - [ ] Table format: Pretty ASCII table for console
  - [ ] JSON format: Array of objects
  - [ ] CSV format: Standard CSV with headers
- [ ] Add error handling:
  - [ ] Database connection errors
  - [ ] SQL syntax errors
  - [ ] Table not found errors
  - [ ] Query timeout (if applicable)
  - [ ] Provide clear, actionable error messages
- [ ] Add logging:
  - [ ] Log queries executed
  - [ ] Log row counts returned
  - [ ] Log errors with context
- [ ] Add safety features:
  - [ ] Detect and warn about queries without LIMIT
  - [ ] Optional automatic LIMIT application
  - [ ] Read-only mode (no INSERT/UPDATE/DELETE)
- [ ] Add usage docstring with examples
- [ ] Set proper exit codes (0=success, 1=error)

#### Query Script Testing
- [ ] Test: Simple SELECT query
  - [ ] Verify results returned
  - [ ] Verify table format readable
- [ ] Test: Query with aggregation
  - [ ] GROUP BY, SUM, AVG, etc.
  - [ ] Verify results correct
- [ ] Test: Query with LIMIT
  - [ ] Verify limit respected
- [ ] Test: Large result set
  - [ ] Verify handling is graceful
  - [ ] Verify output manageable
- [ ] Test: JSON output format
  - [ ] Verify valid JSON
  - [ ] Verify complete data
- [ ] Test: CSV output format
  - [ ] Verify valid CSV
  - [ ] Verify headers present
- [ ] Test: Save to file
  - [ ] Verify file created
  - [ ] Verify correct format
- [ ] Test: Error handling
  - [ ] Invalid SQL syntax
  - [ ] Table doesn't exist
  - [ ] Non-SELECT query (should reject)
  - [ ] Verify error messages clear
- [ ] Verify script logs appropriately

### Create Table Summary Script

#### Summary Script Implementation
- [ ] Create `scripts/db/table_summary.py`
- [ ] Add command-line interface using argparse with arguments:
  - [ ] `--table-id` (required) - The table identifier
  - [ ] `--format` (optional) - Output format (text/json), default text
- [ ] Implement `get_table_summary(table_id)` function:
  - [ ] Connect to DuckDB
  - [ ] Build table name: `dst_{table_id}` (lowercase)
  - [ ] Check table exists
  - [ ] Generate summary statistics:
    - [ ] Record count: `SELECT COUNT(*) FROM table`
    - [ ] Column info: Get column names and types
    - [ ] Sample rows: First 5 rows
    - [ ] For numeric columns: MIN, MAX, AVG, MEDIAN
    - [ ] NULL counts per column
    - [ ] Distinct value counts for categorical columns
  - [ ] Return formatted summary
- [ ] Add error handling:
  - [ ] Table doesn't exist
  - [ ] Database connection errors
  - [ ] Query execution errors
- [ ] Add logging:
  - [ ] Log table being summarized
  - [ ] Log errors
- [ ] Add output formatting:
  - [ ] Text: Human-readable summary
  - [ ] JSON: Structured summary data
- [ ] Add usage docstring with examples
- [ ] Set proper exit codes (0=success, 1=error)

#### Summary Script Testing
- [ ] Test: Generate summary for valid table
  - [ ] Verify all sections present
  - [ ] Verify statistics calculated correctly
  - [ ] Verify sample rows shown
- [ ] Test: Table with various column types
  - [ ] Numeric, text, date columns
  - [ ] Verify appropriate statistics for each
- [ ] Test: JSON output format
  - [ ] Verify valid JSON
  - [ ] Verify complete data
- [ ] Test: Error handling
  - [ ] Table doesn't exist
  - [ ] Invalid table ID
  - [ ] Verify error messages clear
- [ ] Verify script logs appropriately

### Create Skill

#### Skill Directory and File
- [ ] Create directory: `.claude/skills/dst-query/`
- [ ] Create file: `.claude/skills/dst-query/SKILL.md`

#### Skill Frontmatter
- [ ] Add YAML frontmatter:
  ```yaml
  ---
  name: DST Query
  description: Execute SQL queries on Danmarks Statistik data stored in DuckDB. Use when user needs specific data analysis, filtering, aggregation, or joins. Also includes table summary functionality.
  ---
  ```
- [ ] Verify YAML delimiters correct
- [ ] Verify required fields present
- [ ] Verify description specific with trigger keywords

#### Skill Content
- [ ] Add **Purpose** section:
  - [ ] Explain: Run SQL queries to analyze DST data
  - [ ] Clarify: Core skill for data analysis
  - [ ] Mention table summary functionality
- [ ] Add **When to Use** section:
  - [ ] User asks analytical questions
  - [ ] Need to filter or aggregate data
  - [ ] Joining multiple tables
  - [ ] Extracting specific insights
  - [ ] Computing statistics
  - [ ] Exploring table structure (use summary)
- [ ] Add **Table Summary** section:
  - [ ] Purpose: Quick overview of table structure and statistics
  - [ ] Usage: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/table_summary.py --table-id <TABLE_ID>`
  - [ ] When to use: Before detailed querying, understanding structure
  - [ ] Output includes: Record count, columns, sample rows, statistics
- [ ] Add **Running Queries** section:
  - [ ] Basic: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_data.py --sql "SELECT * FROM dst_<table_id> LIMIT 10"`
  - [ ] Save results: `--output <file> --format json`
  - [ ] Format options: `--format table` (console), `--format json`, `--format csv`
- [ ] Add **Table Naming Convention** section:
  - [ ] All DST tables: `dst_{table_id}` (lowercase)
  - [ ] Example: Table FOLK1A → `dst_folk1a`
  - [ ] Metadata table: `dst_metadata`
- [ ] Add **Common Query Patterns** section:
  - [ ] Explore data: `SELECT * FROM dst_<id> LIMIT 10`
  - [ ] Count records: `SELECT COUNT(*) FROM dst_<id>`
  - [ ] Aggregation: `SELECT category, SUM(value) FROM dst_<id> GROUP BY category`
  - [ ] Time series: `SELECT year, value FROM dst_<id> ORDER BY year`
  - [ ] Filtering: `SELECT * FROM dst_<id> WHERE year >= 2020`
  - [ ] Join tables: `SELECT a.*, b.value FROM dst_<id1> a JOIN dst_<id2> b ON a.key = b.key`
- [ ] Add **Best Practices** section:
  - [ ] Always use LIMIT for exploratory queries
  - [ ] Use table summary before complex queries
  - [ ] Check record counts before expensive operations
  - [ ] Handle NULL values explicitly
  - [ ] Format dates and numbers appropriately
  - [ ] Test queries on small samples first
- [ ] Add **Query Safety** section:
  - [ ] Queries are READ-ONLY
  - [ ] Cannot modify data
  - [ ] Cannot drop tables
  - [ ] Cannot alter schema
  - [ ] Script validates SELECT-only queries
- [ ] Add **Troubleshooting** section:
  - [ ] "Table not found": Check table exists with dst-list-tables
  - [ ] "Column not found": Check schema with table summary
  - [ ] Large result sets: Add LIMIT or aggregation
  - [ ] Slow queries: Check indexes, simplify query
- [ ] Add **Examples** section:
  ```bash
  # Get table summary first
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/table_summary.py --table-id FOLK1A

  # Simple exploration
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_data.py --sql "SELECT * FROM dst_folk1a LIMIT 5"

  # Aggregation
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_data.py --sql "SELECT year, SUM(population) as total FROM dst_folk1a GROUP BY year ORDER BY year"

  # Save to file
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_data.py --sql "SELECT * FROM dst_folk1a" --output results.json --format json

  # Complex analysis
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_data.py --sql "SELECT region, AVG(value) as avg_val FROM dst_folk1a WHERE year >= 2020 GROUP BY region"
  ```
- [ ] Add **Tips** section:
  - [ ] Start with table summary to understand structure
  - [ ] Use LIMIT liberally during exploration
  - [ ] Build complex queries incrementally
  - [ ] Test aggregations on subsets first
  - [ ] Use meaningful aliases in SELECT
  - [ ] Comment complex queries for clarity

### Integration and Verification

#### Validate Skill File
- [ ] Check YAML frontmatter syntax
- [ ] Verify required fields present
- [ ] Confirm description includes when-to-use
- [ ] Verify all file paths are absolute
- [ ] Check examples are concrete and runnable
- [ ] Verify progressive disclosure

#### Test Skill with Scripts
- [ ] Run each example command from skill documentation
- [ ] Verify all examples work as documented
- [ ] Verify output matches expected format
- [ ] Test error conditions
- [ ] Verify table summary works
- [ ] Verify query execution works

#### Test with Analyst Agent
- [ ] Start Claude Code with Analyst Agent
- [ ] Ask agent analytical questions
- [ ] Verify agent references dst-query skill
- [ ] Verify agent uses table summary appropriately
- [ ] Verify agent constructs correct SQL queries
- [ ] Verify agent executes queries correctly
- [ ] Verify agent interprets results correctly
- [ ] Verify agent presents insights clearly
- [ ] Test with various query types:
  - [ ] Simple SELECT
  - [ ] Aggregations
  - [ ] Time series
  - [ ] Joins
  - [ ] Complex filters

#### Documentation
- [ ] Add entries to `docs/scripts-reference.md` for both scripts
- [ ] Add entry to `docs/skills-reference.md` for dst-query skill
- [ ] Create `docs/sql-recipes.md` with common query patterns
- [ ] Update `docs/analyst-skills-guide.md` to include query workflow

### Final Verification
- [ ] Both scripts run without errors
- [ ] Scripts handle all argument combinations
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] Skill file has valid YAML
- [ ] Skill content is clear and actionable
- [ ] All examples work correctly
- [ ] Integration with Analyst Agent successful
- [ ] Agent constructs valid SQL
- [ ] Documentation updated

## Success Criteria
- Two Python scripts created (query, summary)
- Scripts have proper CLIs with argparse
- Query script executes SQL safely
- Summary script generates comprehensive statistics
- Error handling is comprehensive
- Skill directory and SKILL.md created
- Skill has valid YAML frontmatter
- Skill documents both query and summary usage
- Common query patterns documented
- All skill examples are runnable and correct
- Integration with Analyst Agent verified
- Agent can construct and execute effective queries
- Documentation updated with SQL recipes

## Notes
- **KISS**: Keep scripts focused on their tasks
- **DRY**: Use shared database utilities
- **YAGNI**: Essential features only
- Use absolute paths in all examples
- Read-only queries for safety
- Table summary before complex queries
- SQL recipes are valuable for agents
- Test with various data types and structures
