# Task: DST Data Fetch and Store (Scripts + Skill)

## Objective
Create Python scripts to fetch data from DST API and store it in DuckDB, plus the corresponding skill for the Fetcher Agent to use them.

## Prerequisites
- Infrastructure setup completed (task-infrastructure.md)
- API client, database utilities available
- Understanding of DST data API endpoint and DuckDB operations

## Tasks

### Create Data Fetch Script

#### Fetch Script Implementation
- [ ] Create `scripts/api/fetch_data.py`
- [ ] Add command-line interface using argparse with arguments:
  - [ ] `--table-id` (required) - The table identifier
  - [ ] `--filters` (optional) - JSON string with filter parameters
  - [ ] `--format` (optional) - Output format (json/csv), default json
  - [ ] `--output` (optional) - Save to file path
- [ ] Implement `fetch_data(table_id, filters=None, format='json')` function:
  - [ ] Use DSTAPIClient to call /data endpoint
  - [ ] Build proper request payload with table ID
  - [ ] Apply filters if provided
  - [ ] Handle large responses (streaming if needed)
  - [ ] Parse and validate response
  - [ ] Return data in requested format
- [ ] Add progress indicator for large downloads
- [ ] Add error handling:
  - [ ] HTTP errors (404, 500, timeout)
  - [ ] Invalid JSON responses
  - [ ] Invalid filters
  - [ ] Network errors
- [ ] Add logging:
  - [ ] Log API request with parameters
  - [ ] Log download progress
  - [ ] Log response size
  - [ ] Log errors with context
- [ ] Add output functionality:
  - [ ] Print to stdout by default
  - [ ] Save to file if `--output` specified
  - [ ] Format appropriately (JSON or CSV)
- [ ] Add usage docstring with examples
- [ ] Set proper exit codes (0=success, 1=error)

#### Fetch Script Testing
- [ ] Test: Fetch small table without filters
  - [ ] Verify data downloaded
  - [ ] Verify JSON format correct
  - [ ] Check reasonable record count
- [ ] Test: Fetch with filters
  - [ ] Verify filters applied correctly
  - [ ] Verify filtered data returned
- [ ] Test: Save to file with `--output`
  - [ ] Verify file created
  - [ ] Verify file contains valid data
- [ ] Test: CSV format with `--format csv`
  - [ ] Verify CSV output
  - [ ] Verify proper formatting
- [ ] Test: Error handling
  - [ ] Invalid table ID
  - [ ] Invalid filter JSON
  - [ ] Verify error messages clear
  - [ ] Verify exit code is 1
- [ ] Verify script logs appropriately

### Create Data Storage Script

#### Storage Script Implementation
- [ ] Create `scripts/db/store_data.py`
- [ ] Add command-line interface using argparse with arguments:
  - [ ] `--table-id` (required) - The table identifier
  - [ ] `--data-file` (required) - Path to JSON/CSV data file
  - [ ] `--overwrite` (optional) - Overwrite if table exists
  - [ ] `--update-metadata` (optional) - Update metadata (default true)
- [ ] Implement `store_data(table_id, data, overwrite=False)` function:
  - [ ] Connect to DuckDB
  - [ ] Check if table `dst_{table_id}` exists
  - [ ] Handle existing table (error or overwrite based on flag)
  - [ ] Infer schema from data
  - [ ] Create table with proper naming: `dst_{table_id}` (lowercase)
  - [ ] Insert records using transaction
  - [ ] Verify record count
  - [ ] Update dst_metadata table:
    - [ ] table_id, table_name
    - [ ] fetch_timestamp (now)
    - [ ] record_count
    - [ ] columns_json (schema info)
  - [ ] Commit transaction
  - [ ] Return success with statistics
- [ ] Add error handling:
  - [ ] Database connection errors
  - [ ] Table exists errors (when not overwrite)
  - [ ] Schema inference errors
  - [ ] Insert errors
  - [ ] Rollback on any error
  - [ ] Close connection in finally block
- [ ] Add logging:
  - [ ] Log database operations
  - [ ] Log record counts
  - [ ] Log errors with context
- [ ] Add usage docstring with examples
- [ ] Set proper exit codes (0=success, 1=error)

#### Storage Script Testing
- [ ] Test: Store data from file
  - [ ] Verify table created in DuckDB
  - [ ] Verify table name follows convention
  - [ ] Verify record count matches
- [ ] Test: Metadata update
  - [ ] Verify dst_metadata entry created
  - [ ] Verify all metadata fields populated
  - [ ] Verify timestamps correct
- [ ] Test: Overwrite existing table
  - [ ] Create table first
  - [ ] Run with `--overwrite`
  - [ ] Verify table replaced
  - [ ] Verify metadata updated
- [ ] Test: Error when table exists (no overwrite flag)
  - [ ] Verify error message clear
  - [ ] Verify original table untouched
  - [ ] Verify exit code is 1
- [ ] Test: Transaction rollback on error
  - [ ] Simulate error during insert
  - [ ] Verify no partial data
  - [ ] Verify database consistent
- [ ] Verify script logs appropriately

### Create Combined Fetch-and-Store Script

#### Combined Script Implementation
- [ ] Create `scripts/fetch_and_store.py`
- [ ] Add command-line interface using argparse with arguments:
  - [ ] `--table-id` (required) - The table identifier
  - [ ] `--filters` (optional) - JSON string with filters
  - [ ] `--overwrite` (optional) - Overwrite if exists
  - [ ] `--skip-if-fresh` (optional) - Skip if data is fresh
  - [ ] `--max-age-days` (optional) - Freshness threshold (default 30)
- [ ] Implement `fetch_and_store(table_id, filters=None, overwrite=False, skip_if_fresh=False)` function:
  - [ ] Step 1: Check if data exists and freshness
  - [ ] Step 2: Skip if fresh and skip_if_fresh=True
  - [ ] Step 3: Get table info from API (for metadata)
  - [ ] Step 4: Fetch data from API
  - [ ] Step 5: Store in DuckDB
  - [ ] Step 6: Update metadata with table info
  - [ ] Step 7: Report success with statistics
- [ ] Add comprehensive error handling
- [ ] Add progress reporting for each step
- [ ] Add logging for complete workflow
- [ ] Add usage docstring with examples
- [ ] Set proper exit codes (0=success, 1=error, 2=skipped)

#### Combined Script Testing
- [ ] Test: Complete workflow (fetch and store)
  - [ ] Verify end-to-end success
  - [ ] Verify data in DuckDB
  - [ ] Verify metadata complete
- [ ] Test: Skip if fresh
  - [ ] Store data first
  - [ ] Run with `--skip-if-fresh`
  - [ ] Verify skipped (exit code 2)
- [ ] Test: Overwrite stale data
  - [ ] Store old data
  - [ ] Run with `--overwrite`
  - [ ] Verify data replaced
- [ ] Test: With filters
  - [ ] Run with filter JSON
  - [ ] Verify filtered data stored
- [ ] Verify complete workflow logging

### Create Skill

#### Skill Directory and File
- [ ] Create directory: `.claude/skills/dst-data/`
- [ ] Create file: `.claude/skills/dst-data/SKILL.md`

#### Skill Frontmatter
- [ ] Add YAML frontmatter:
  ```yaml
  ---
  name: DST Data
  description: Fetch actual data from Danmarks Statistik API and store in DuckDB. Use when user wants to download and store specific DST table data for analysis.
  ---
  ```
- [ ] Verify YAML delimiters correct
- [ ] Verify required fields present
- [ ] Verify description specific with trigger keywords

#### Skill Content
- [ ] Add **Purpose** section:
  - [ ] Explain: Fetch data from DST API and store in DuckDB
  - [ ] Clarify: Final step in data acquisition workflow
- [ ] Add **When to Use** section:
  - [ ] User requests specific table data
  - [ ] Ready to download after reviewing tableinfo
  - [ ] Need to refresh existing data
  - [ ] Want to store data for analysis
- [ ] Add **How to Use - Recommended (Fetch and Store)** section:
  - [ ] Basic: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/fetch_and_store.py --table-id <TABLE_ID>`
  - [ ] With filters: `--filters '<JSON>'`
  - [ ] Overwrite existing: `--overwrite`
  - [ ] Skip if fresh: `--skip-if-fresh --max-age-days 30`
- [ ] Add **How to Use - Advanced (Separate Steps)** section:
  - [ ] Fetch only: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/fetch_data.py --table-id <TABLE_ID> --output data.json`
  - [ ] Store separately: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/store_data.py --table-id <TABLE_ID> --data-file data.json`
- [ ] Add **Expected Output** section:
  - [ ] Data stored in table named `dst_{table_id}` (lowercase)
  - [ ] Metadata updated in dst_metadata table
  - [ ] Success message with record count
  - [ ] Table ready for querying
- [ ] Add **Important Considerations** section:
  - [ ] Large tables may take time to download
  - [ ] Check tableinfo first to understand data size
  - [ ] Use filters to limit data if needed
  - [ ] Default behavior: fail if table already exists
  - [ ] Use --overwrite to replace existing data
- [ ] Add **Verification Steps** section:
  - [ ] Check script output for success message
  - [ ] Verify record count is reasonable
  - [ ] Query metadata: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_metadata.py --table-id <id>`
  - [ ] Spot check data: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_data.py --sql "SELECT * FROM dst_<id> LIMIT 5"`
- [ ] Add **Next Steps** section:
  - [ ] Data is ready for analysis
  - [ ] Switch to DST Analyst Agent for querying
  - [ ] Can now run SQL queries on stored data
- [ ] Add **Examples** section with real commands
- [ ] Add **Tips** section:
  - [ ] Always check tableinfo before large downloads
  - [ ] Use filters for large tables
  - [ ] Monitor disk space for large datasets
  - [ ] Verify data after storage

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

#### Test with Fetcher Agent
- [ ] Start Claude Code with Fetcher Agent
- [ ] Ask agent to fetch specific table
- [ ] Verify agent references dst-data skill
- [ ] Verify agent executes correct scripts
- [ ] Verify agent verifies storage success
- [ ] Verify agent reports results clearly
- [ ] Verify agent suggests handoff to Analyst

#### Documentation
- [ ] Add entries to `docs/scripts-reference.md` for all three scripts
- [ ] Add entry to `docs/skills-reference.md` for dst-data skill
- [ ] Update `docs/fetcher-skills-guide.md` workflow

### Final Verification
- [ ] All three scripts run without errors
- [ ] Scripts handle all argument combinations
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] Skill file has valid YAML
- [ ] Skill content is clear and actionable
- [ ] All examples work correctly
- [ ] Integration with Fetcher Agent successful
- [ ] Documentation updated
- [ ] End-to-end workflow verified

## Success Criteria
- Three Python scripts created (fetch, store, combined)
- All scripts have proper CLIs with argparse
- Fetch script downloads data from DST API
- Store script saves data to DuckDB correctly
- Combined script completes full workflow
- Error handling is comprehensive
- Skill directory and SKILL.md created
- Skill has valid YAML frontmatter
- Skill documents both simple and advanced usage
- All skill examples are runnable and correct
- Integration with Fetcher Agent verified
- Documentation updated

## Notes
- **KISS**: Keep each script focused on its task
- **DRY**: Share code via utilities where possible
- **YAGNI**: Essential features only
- Combined script is what agents will use most
- Test with various table sizes
- Handle large downloads gracefully
- Always verify storage success
