# Task: Integration Testing

## Objective
Perform comprehensive end-to-end testing of the complete DST research system including infrastructure, scripts, skills, and agents working together.

## Prerequisites
- All previous tasks completed
- Infrastructure set up
- All scripts created and tested individually
- All skills created and validated
- Both agents configured
- Test data available or ability to fetch from DST API

## Tasks

### Infrastructure Testing

#### Database and Environment
- [ ] Test database initialization
  - [ ] Run `python scripts/db/init_db.py`
  - [ ] Verify database file created
  - [ ] Verify dst_metadata table exists and is queryable
- [ ] Test environment configuration
  - [ ] Verify .env file loads correctly
  - [ ] Verify all environment variables accessible
- [ ] Test logging
  - [ ] Verify log file created
  - [ ] Verify log messages written correctly
- [ ] Test API client
  - [ ] Verify connection to DST API
  - [ ] Test basic API call
  - [ ] Verify error handling

### Script Integration Testing

#### Fetcher Scripts Workflow
- [ ] Test complete fetch workflow
  - [ ] Run `python scripts/api/get_subjects.py`
  - [ ] Verify subjects returned
  - [ ] Save output to file
- [ ] Test table search
  - [ ] Run `python scripts/api/get_tables.py --subject <ID>`
  - [ ] Verify tables returned
  - [ ] Test search functionality
- [ ] Test table info retrieval
  - [ ] Run `python scripts/api/get_tableinfo.py --table-id <ID>`
  - [ ] Verify metadata returned
  - [ ] Verify structure is complete
- [ ] Test data fetch and storage
  - [ ] Run `python scripts/fetch_and_store.py --table-id <ID>`
  - [ ] Verify data fetched from API
  - [ ] Verify data stored in DuckDB
  - [ ] Verify metadata updated
  - [ ] Verify record count matches
- [ ] Test overwrite functionality
  - [ ] Fetch same table again with --overwrite
  - [ ] Verify data replaced
  - [ ] Verify metadata updated

#### Analyst Scripts Workflow
- [ ] Test metadata queries
  - [ ] Run `python scripts/db/query_metadata.py --list-all`
  - [ ] Verify all stored tables listed
  - [ ] Verify metadata complete
- [ ] Test freshness checking
  - [ ] Run `python scripts/db/query_metadata.py --table-id <ID> --check-freshness`
  - [ ] Verify age calculated correctly
  - [ ] Test with different thresholds
- [ ] Test table summary
  - [ ] Run `python scripts/db/table_summary.py --table-id <ID>`
  - [ ] Verify statistics generated
  - [ ] Verify sample rows shown
  - [ ] Verify column info present
- [ ] Test query execution
  - [ ] Run simple SELECT query
  - [ ] Run aggregation query
  - [ ] Run query with joins
  - [ ] Test different output formats (table, JSON, CSV)
  - [ ] Test saving results to file

### Skill Validation Testing

#### Fetcher Skills
- [ ] Test dst-subjects skill
  - [ ] Read skill documentation
  - [ ] Run all examples from skill
  - [ ] Verify all examples work
  - [ ] Verify output matches documentation
- [ ] Test dst-tables skill
  - [ ] Read skill documentation
  - [ ] Run all examples from skill
  - [ ] Verify all examples work
  - [ ] Test both subject and search modes
- [ ] Test dst-tableinfo skill
  - [ ] Read skill documentation
  - [ ] Run all examples from skill
  - [ ] Verify metadata structure documented correctly
- [ ] Test dst-data skill
  - [ ] Read skill documentation
  - [ ] Run all examples from skill
  - [ ] Verify both simple and advanced workflows
  - [ ] Verify verification steps work

#### Analyst Skills
- [ ] Test dst-list-tables skill
  - [ ] Read skill documentation
  - [ ] Run all examples from skill
  - [ ] Verify output interpretation is clear
- [ ] Test dst-check-freshness skill
  - [ ] Read skill documentation
  - [ ] Run all examples from skill
  - [ ] Verify thresholds work as documented
  - [ ] Test decision guide accuracy
- [ ] Test dst-query skill
  - [ ] Read skill documentation
  - [ ] Run all examples from skill
  - [ ] Test query patterns provided
  - [ ] Verify table summary and query execution

### Agent Integration Testing

#### Fetcher Agent Testing
- [ ] Test agent activation
  - [ ] Start Claude Code session
  - [ ] Say "Fetch population data from DST"
  - [ ] Verify Fetcher Agent activates
  - [ ] Verify agent identifies itself
- [ ] Test subject browsing workflow
  - [ ] Ask agent to browse DST subjects
  - [ ] Verify agent uses dst-subjects skill
  - [ ] Verify agent explains subjects to user
- [ ] Test table finding workflow
  - [ ] Ask agent to find tables about specific topic
  - [ ] Verify agent uses dst-tables skill
  - [ ] Verify agent presents relevant tables
- [ ] Test table info retrieval
  - [ ] Ask agent for info about specific table
  - [ ] Verify agent uses dst-tableinfo skill
  - [ ] Verify agent explains table structure
- [ ] Test data fetching
  - [ ] Ask agent to fetch specific table
  - [ ] Verify agent uses dst-data skill
  - [ ] Verify agent executes fetch_and_store script
  - [ ] Verify agent confirms storage success
  - [ ] Verify agent reports record count
- [ ] Test error handling
  - [ ] Request invalid table ID
  - [ ] Verify agent handles error gracefully
  - [ ] Verify agent provides helpful message
- [ ] Test existing data handling
  - [ ] Request table that already exists
  - [ ] Verify agent checks metadata
  - [ ] Verify agent asks about overwriting

#### Analyst Agent Testing
- [ ] Test agent activation
  - [ ] Start Claude Code session
  - [ ] Say "Analyze population trends"
  - [ ] Verify Analyst Agent activates
  - [ ] Verify agent identifies itself
- [ ] Test data availability check
  - [ ] Ask agent to analyze specific data
  - [ ] Verify agent uses dst-list-tables skill
  - [ ] Verify agent checks if data exists
- [ ] Test freshness verification
  - [ ] Ask agent to analyze data
  - [ ] Verify agent uses dst-check-freshness skill
  - [ ] Verify agent reports data age
  - [ ] Verify agent makes freshness recommendation
- [ ] Test table exploration
  - [ ] Ask agent about table structure
  - [ ] Verify agent uses table summary
  - [ ] Verify agent explains structure clearly
- [ ] Test query execution
  - [ ] Ask agent analytical question
  - [ ] Verify agent constructs appropriate SQL
  - [ ] Verify agent uses dst-query skill
  - [ ] Verify agent executes query correctly
  - [ ] Verify agent interprets results
  - [ ] Verify agent presents insights clearly
- [ ] Test complex analysis
  - [ ] Ask for time series analysis
  - [ ] Ask for comparisons between groups
  - [ ] Ask for aggregated statistics
  - [ ] Verify agent handles complexity
- [ ] Test error handling
  - [ ] Ask to analyze non-existent table
  - [ ] Verify agent checks and reports missing data
  - [ ] Verify agent recommends Fetcher Agent

### Cross-Agent Workflow Testing

#### Complete End-to-End Workflows
- [ ] Test Workflow 1: Discover and Fetch
  - [ ] User: "I want data about Danish population"
  - [ ] Verify Fetcher activates
  - [ ] Verify agent browses subjects
  - [ ] Verify agent finds population tables
  - [ ] Verify agent fetches appropriate table
  - [ ] Verify data stored successfully
- [ ] Test Workflow 2: Fetch and Analyze
  - [ ] User: "Get FOLK1A and show me the total population"
  - [ ] Verify Fetcher fetches data
  - [ ] Verify handoff to Analyst (manual or automatic)
  - [ ] Verify Analyst queries data
  - [ ] Verify Analyst presents result
- [ ] Test Workflow 3: Analysis with Missing Data
  - [ ] User: "Analyze employment trends"
  - [ ] Verify Analyst activates
  - [ ] Verify Analyst checks for employment data
  - [ ] Verify Analyst reports data missing
  - [ ] Verify Analyst recommends Fetcher
  - [ ] User switches to Fetcher
  - [ ] Verify Fetcher fetches employment data
  - [ ] User switches back to Analyst
  - [ ] Verify Analyst completes analysis
- [ ] Test Workflow 4: Stale Data Refresh
  - [ ] (Assuming old data exists)
  - [ ] User: "Analyze population with latest data"
  - [ ] Verify Analyst checks freshness
  - [ ] Verify Analyst reports data is stale
  - [ ] Verify Analyst recommends refresh
  - [ ] User switches to Fetcher
  - [ ] Verify Fetcher refreshes data (with --overwrite)
  - [ ] User switches back to Analyst
  - [ ] Verify Analyst analyzes fresh data
- [ ] Test Workflow 5: Complex Multi-Table Analysis
  - [ ] User: "Compare population and employment data"
  - [ ] Verify Analyst checks both tables exist
  - [ ] If missing, verify handoff to Fetcher
  - [ ] Verify Analyst constructs join query
  - [ ] Verify Analyst executes and presents comparison

### Error Recovery Testing

#### API Errors
- [ ] Test API timeout
  - [ ] Simulate slow/timeout response
  - [ ] Verify script handles gracefully
  - [ ] Verify agent communicates error clearly
- [ ] Test invalid table ID
  - [ ] Request non-existent table
  - [ ] Verify 404 error handled
  - [ ] Verify helpful error message
- [ ] Test malformed API response
  - [ ] (If possible to simulate)
  - [ ] Verify error handling
  - [ ] Verify system remains stable

#### Database Errors
- [ ] Test connection failure
  - [ ] (Simulate by corrupting DB path)
  - [ ] Verify error reported
  - [ ] Verify graceful degradation
- [ ] Test table already exists
  - [ ] Attempt to store without --overwrite
  - [ ] Verify error caught
  - [ ] Verify data not corrupted
- [ ] Test query errors
  - [ ] Execute invalid SQL
  - [ ] Verify error reported clearly
  - [ ] Verify helpful suggestion provided

#### User Input Errors
- [ ] Test invalid arguments to scripts
  - [ ] Missing required arguments
  - [ ] Invalid argument values
  - [ ] Verify helpful error messages
- [ ] Test ambiguous user requests
  - [ ] Vague request to agent
  - [ ] Verify agent asks for clarification

### Performance Testing

#### Large Data Handling
- [ ] Test fetching large table
  - [ ] Select table with many records
  - [ ] Verify progress reporting
  - [ ] Verify successful storage
  - [ ] Verify reasonable performance
- [ ] Test querying large table
  - [ ] Query table with many records
  - [ ] Verify query completes
  - [ ] Verify results manageable
  - [ ] Test with and without LIMIT

#### Multiple Tables
- [ ] Test storing multiple tables
  - [ ] Fetch 5-10 different tables
  - [ ] Verify all stored correctly
  - [ ] Verify metadata for each
- [ ] Test querying across tables
  - [ ] Execute join queries
  - [ ] Verify performance acceptable

### Documentation Validation

#### Test Documentation Accuracy
- [ ] Follow getting-started guide
  - [ ] Verify all steps work
  - [ ] Note any unclear instructions
- [ ] Test all code examples in docs
  - [ ] Run each example command
  - [ ] Verify they work as documented
- [ ] Verify all file paths in docs are correct
- [ ] Check cross-references between docs

### Create Test Report

#### Test Results Documentation
- [ ] Create test results file: `tests/integration_test_results.md`
- [ ] Document:
  - [ ] Test date and environment
  - [ ] Each test section with pass/fail
  - [ ] Issues discovered with details
  - [ ] Performance observations
  - [ ] Any deviations from expected behavior
- [ ] Create issues list:
  - [ ] Critical issues (blockers)
  - [ ] Major issues (significant problems)
  - [ ] Minor issues (cosmetic, usability)
  - [ ] Enhancement suggestions
- [ ] Document remediation steps taken
- [ ] Overall system health assessment

### Regression Test Suite

#### Create Automated Tests
- [ ] Create `tests/test_integration.sh` script:
  - [ ] Test database initialization
  - [ ] Test subject fetching
  - [ ] Test table fetching
  - [ ] Test data fetch and store
  - [ ] Test metadata queries
  - [ ] Test data queries
  - [ ] Generate pass/fail report
- [ ] Make script executable: `chmod +x tests/test_integration.sh`
- [ ] Document how to run regression tests
- [ ] Add to testing guide

### Final Verification
- [ ] All infrastructure tests pass
- [ ] All script workflows complete successfully
- [ ] All skills work as documented
- [ ] Both agents activate and function correctly
- [ ] Cross-agent workflows are seamless
- [ ] Error handling is comprehensive and user-friendly
- [ ] Performance is acceptable
- [ ] Documentation is accurate
- [ ] Test report completed
- [ ] Critical issues resolved
- [ ] Regression test suite created

## Success Criteria
- Infrastructure tests pass
- All Python scripts execute without errors in workflows
- All skills validate correctly and examples work
- Both agents activate and execute appropriately
- Agent handoffs work smoothly
- End-to-end workflows complete successfully
- Error handling is graceful and informative
- Performance is acceptable for typical use cases
- Documentation is accurate and complete
- Test results documented
- Regression test suite available

## Notes
- **KISS**: Start with happy path tests, add edge cases
- **DRY**: Use test utilities for common setup
- **YAGNI**: Focus on core functionality testing
- Test with real DST API at least once
- Document any API quirks discovered
- Performance benchmarks for future comparison
- Keep test data small but representative
- Integration testing reveals issues unit tests miss
- Be patient - some tests involve API calls and may be slow
- Document workarounds for known issues
