# Task: DST List Tables (Script + Skill)

## Objective
Create the Python script to list DST tables stored in DuckDB and the corresponding skill for the Analyst Agent to use it.

## Prerequisites
- Infrastructure setup completed (task-infrastructure.md)
- Database utilities available
- Understanding of metadata table structure

## Tasks

### Create Python Script

#### Script Implementation
- [ ] Create `scripts/db/query_metadata.py`
- [ ] Add command-line interface using argparse with arguments:
  - [ ] `--list-all` (optional) - List all stored tables
  - [ ] `--table-id` (optional) - Get metadata for specific table
  - [ ] `--check-freshness` (optional) - Check data age
  - [ ] `--max-age-days` (optional) - Freshness threshold in days
  - [ ] `--format` (optional) - Output format (table/json), default table
- [ ] Implement `list_all_tables()` function:
  - [ ] Connect to DuckDB
  - [ ] Query dst_metadata for all records
  - [ ] Calculate age for each table (days since fetch_timestamp)
  - [ ] Return formatted list with: table_id, table_name, record_count, last_updated, fetch_timestamp, age
  - [ ] Sort by table_id
- [ ] Implement `get_metadata(table_id)` function:
  - [ ] Query dst_metadata for specific table
  - [ ] Return complete metadata record
  - [ ] Handle table not found
- [ ] Implement `check_freshness(table_id, max_age_days=None)` function:
  - [ ] Get metadata for table
  - [ ] Calculate age in days
  - [ ] Compare to threshold if provided
  - [ ] Return freshness status (fresh/stale) and age info
  - [ ] Include human-readable age (e.g., "5 days ago")
- [ ] Add error handling:
  - [ ] Database connection errors
  - [ ] Table not found
  - [ ] Missing metadata
  - [ ] Invalid arguments
- [ ] Add logging:
  - [ ] Log queries executed
  - [ ] Log errors with context
- [ ] Add output functionality:
  - [ ] Format as table for console (default)
  - [ ] Format as JSON if requested
  - [ ] Human-readable formatting
- [ ] Add usage docstring with examples
- [ ] Set proper exit codes (0=success, 1=error)

#### Script Testing
- [ ] Test: List all tables (after storing some test data)
  - [ ] Verify all tables shown
  - [ ] Verify metadata fields present
  - [ ] Verify age calculation correct
  - [ ] Verify sorted by table_id
- [ ] Test: Get specific table metadata
  - [ ] Verify correct metadata returned
  - [ ] Test with valid table ID
  - [ ] Test with invalid table ID (error)
- [ ] Test: Check freshness without threshold
  - [ ] Verify age reported
  - [ ] Verify human-readable format
- [ ] Test: Check freshness with threshold
  - [ ] Verify fresh/stale determination
  - [ ] Test with old and new data
- [ ] Test: JSON output format
  - [ ] Verify valid JSON
  - [ ] Verify complete data
- [ ] Test: Error handling
  - [ ] Empty database
  - [ ] Invalid table ID
  - [ ] Verify error messages clear
- [ ] Verify script logs appropriately

### Create Skill

#### Skill Directory and File
- [ ] Create directory: `.claude/skills/dst-list-tables/`
- [ ] Create file: `.claude/skills/dst-list-tables/SKILL.md`

#### Skill Frontmatter
- [ ] Add YAML frontmatter:
  ```yaml
  ---
  name: DST List Tables
  description: List all Danmarks Statistik tables currently stored in DuckDB with metadata. Use when user wants to know what data is available locally or explore stored tables.
  ---
  ```
- [ ] Verify YAML delimiters correct
- [ ] Verify required fields present
- [ ] Verify description specific with trigger keywords

#### Skill Content
- [ ] Add **Purpose** section:
  - [ ] Explain: Discover what DST data is stored locally
  - [ ] Clarify: First step in analysis workflow
- [ ] Add **When to Use** section:
  - [ ] User asks "what data do we have?"
  - [ ] Starting an analysis session
  - [ ] Checking if specific data exists locally
  - [ ] Exploring available tables
  - [ ] Before deciding what to analyze
- [ ] Add **How to Use** section:
  - [ ] List all: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_metadata.py --list-all`
  - [ ] Check specific: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_metadata.py --table-id <TABLE_ID>`
  - [ ] JSON output: `--format json`
- [ ] Add **Expected Output** section:
  - [ ] Table with columns:
    - [ ] table_id
    - [ ] table_name
    - [ ] record_count
    - [ ] last_updated (from DST)
    - [ ] fetch_timestamp (when downloaded)
    - [ ] age (calculated, human-readable)
  - [ ] Example output snippet
- [ ] Add **Interpreting Results** section:
  - [ ] table_id: Use for queries (format: dst_{table_id})
  - [ ] record_count: Size of dataset
  - [ ] fetch_timestamp: Freshness of local copy
  - [ ] age: How old the local data is
- [ ] Add **Next Steps** section:
  - [ ] If data exists: Use dst-table-summary or dst-query
  - [ ] If data missing: Switch to Fetcher Agent
  - [ ] If data stale: Use dst-check-freshness to decide if refresh needed
- [ ] Add **Examples** section:
  ```bash
  # List all stored tables
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_metadata.py --list-all

  # Get specific table metadata
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_metadata.py --table-id FOLK1A

  # JSON output for programmatic use
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_metadata.py --list-all --format json
  ```
- [ ] Add **Tips** section:
  - [ ] Run at start of analysis session
  - [ ] Check data age before analyzing
  - [ ] Note table IDs for query building
  - [ ] Use to verify data was stored successfully

### Integration and Verification

#### Validate Skill File
- [ ] Check YAML frontmatter syntax
- [ ] Verify required fields present
- [ ] Confirm description includes when-to-use
- [ ] Verify all file paths are absolute
- [ ] Check examples are concrete and runnable
- [ ] Verify progressive disclosure

#### Test Skill with Script
- [ ] Run each example command from skill documentation
- [ ] Verify all examples work as documented
- [ ] Verify output matches expected format
- [ ] Test error conditions

#### Test with Analyst Agent
- [ ] Start Claude Code with Analyst Agent
- [ ] Ask agent what data is available
- [ ] Verify agent references dst-list-tables skill
- [ ] Verify agent executes correct script
- [ ] Verify agent interprets output correctly
- [ ] Verify agent explains available data to user
- [ ] Verify agent suggests next steps

#### Documentation
- [ ] Add entry to `docs/scripts-reference.md` for query_metadata.py
- [ ] Add entry to `docs/skills-reference.md` for dst-list-tables skill
- [ ] Update `docs/analyst-skills-guide.md` to include in workflow

### Final Verification
- [ ] Script runs without errors
- [ ] Script handles all argument combinations
- [ ] Script has proper error handling
- [ ] Script logs appropriately
- [ ] Skill file has valid YAML
- [ ] Skill content is clear and actionable
- [ ] All examples work correctly
- [ ] Integration with Analyst Agent successful
- [ ] Documentation updated

## Success Criteria
- Python script created and executable
- Script has proper CLI with argparse
- Script lists tables from DuckDB metadata successfully
- Script calculates data age correctly
- Error handling is comprehensive
- Skill directory and SKILL.md created
- Skill has valid YAML frontmatter
- Skill content follows best practices
- All skill examples are runnable and correct
- Integration with Analyst Agent verified
- Documentation updated

## Notes
- **KISS**: Keep script focused on metadata queries
- **DRY**: Use shared database utilities
- **YAGNI**: Essential features only
- Use absolute paths in all examples
- Human-readable age formatting is important
- This is typically the first skill Analyst uses
