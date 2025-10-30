# Task: DST Table Info (Script + Skill)

## Objective
Create the Python script to fetch detailed DST table metadata from the API and the corresponding skill for the Fetcher Agent to use it.

## Prerequisites
- Infrastructure setup completed (task-infrastructure.md)
- API client and utilities available
- Understanding of DST tableinfo API endpoint

## Tasks

### Create Python Script

#### Script Implementation
- [ ] Create `scripts/api/get_tableinfo.py`
- [ ] Add command-line interface using argparse with arguments:
  - [ ] `--table-id` (required) - The table identifier
  - [ ] `--output` (optional) - Save to JSON file path
  - [ ] `--verbose` (optional) - Detailed output
- [ ] Implement `get_tableinfo(table_id)` function:
  - [ ] Use DSTAPIClient to call /tableinfo endpoint
  - [ ] Parse response to extract:
    - [ ] Table metadata (id, text, description, unit, updated)
    - [ ] Variables/dimensions structure
    - [ ] Available values for each variable
    - [ ] Time period coverage
    - [ ] Data format information
  - [ ] Return complete metadata object
- [ ] Add error handling:
  - [ ] HTTP errors (404 for invalid table ID, 500, timeout)
  - [ ] Invalid JSON responses
  - [ ] Missing required fields
  - [ ] Network errors
- [ ] Add logging:
  - [ ] Log API request with table ID
  - [ ] Log response summary
  - [ ] Log errors with context
- [ ] Add output functionality:
  - [ ] Print to stdout as JSON by default
  - [ ] Save to file if `--output` specified
  - [ ] Format JSON for readability
  - [ ] In verbose mode, show formatted summary
- [ ] Add usage docstring with examples
- [ ] Set proper exit codes (0=success, 1=error)

#### Script Testing
- [ ] Test: Run with known valid table ID (e.g., FOLK1A)
  - [ ] Verify JSON output to stdout
  - [ ] Verify response contains metadata
  - [ ] Check variables/dimensions present
  - [ ] Verify structure is complete
- [ ] Test: Run with `--verbose` flag
  - [ ] Verify formatted output shown
  - [ ] Verify output is human-readable
- [ ] Test: Run with `--output test_tableinfo.json`
  - [ ] Verify file created
  - [ ] Verify file contains valid JSON
  - [ ] Verify data matches stdout output
- [ ] Test: Error handling
  - [ ] Invalid table ID (non-existent)
  - [ ] Malformed table ID
  - [ ] Verify error messages are clear
  - [ ] Verify exit code is 1
- [ ] Test: Different table types
  - [ ] Test with multiple different tables
  - [ ] Verify script handles varying structures
- [ ] Verify script logs appropriately to log file
- [ ] Document any API-specific quirks or limitations

### Create Skill

#### Skill Directory and File
- [ ] Create directory: `.claude/skills/dst-tableinfo/`
- [ ] Create file: `.claude/skills/dst-tableinfo/SKILL.md`

#### Skill Frontmatter
- [ ] Add YAML frontmatter:
  ```yaml
  ---
  name: DST Table Info
  description: Get detailed metadata for a specific Danmarks Statistik table including variables, dimensions, and structure. Use before fetching data to understand table schema.
  ---
  ```
- [ ] Verify YAML delimiters are correct (`---` at start and end)
- [ ] Verify required fields present (name, description)
- [ ] Verify description is specific and includes trigger keywords

#### Skill Content
- [ ] Add **Purpose** section:
  - [ ] Explain: Get complete metadata and structure for a DST table
  - [ ] Clarify: Essential step before fetching data
- [ ] Add **When to Use** section:
  - [ ] Before fetching data to understand structure
  - [ ] To see available variables and dimensions
  - [ ] To determine appropriate filters for data fetch
  - [ ] To understand table updates and units
  - [ ] User asks "what's in this table?"
- [ ] Add **How to Use** section:
  - [ ] Required: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_tableinfo.py --table-id <TABLE_ID>`
  - [ ] Save to file: `--output <file>`
  - [ ] Detailed view: `--verbose`
- [ ] Add **Expected Output** section:
  - [ ] JSON with table metadata
  - [ ] Variables/dimensions (what can be filtered)
  - [ ] Available values for each variable
  - [ ] Time period coverage
  - [ ] Unit of measurement
  - [ ] Example output snippet
- [ ] Add **Key Information to Extract** section:
  - [ ] Table name and description
  - [ ] What dimensions exist (geography, time, categories)
  - [ ] What filters are available
  - [ ] Date range of data
  - [ ] Unit of measurement
  - [ ] Last update date
- [ ] Add **Next Steps** section:
  - [ ] After understanding table structure
  - [ ] Decide on filters (if needed)
  - [ ] Use dst-data skill to fetch actual data
  - [ ] Know what to expect in the data
- [ ] Add **Examples** section:
  ```bash
  # Get table info for FOLK1A
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_tableinfo.py --table-id FOLK1A

  # Verbose output
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_tableinfo.py --table-id FOLK1A --verbose

  # Save to file
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_tableinfo.py --table-id FOLK1A --output folk1a_info.json
  ```
- [ ] Add **Tips** section:
  - [ ] Always check table info before fetching large datasets
  - [ ] Note available filters to limit data size
  - [ ] Check date range to know data coverage
  - [ ] Understand variables for proper analysis later

### Integration and Verification

#### Validate Skill File
- [ ] Check YAML frontmatter syntax
- [ ] Verify required fields present
- [ ] Confirm description includes when-to-use
- [ ] Verify all file paths are absolute
- [ ] Check examples are concrete and runnable
- [ ] Verify progressive disclosure (simple to advanced)

#### Test Skill with Script
- [ ] Run each example command from skill documentation
- [ ] Verify all examples work as documented
- [ ] Verify output matches expected format described in skill
- [ ] Test error conditions and verify error messages are clear

#### Test with Fetcher Agent
- [ ] Start Claude Code session with Fetcher Agent
- [ ] Ask agent to get info about a specific table
- [ ] Verify agent references dst-tableinfo skill
- [ ] Verify agent executes correct script with right arguments
- [ ] Verify agent interprets metadata correctly
- [ ] Verify agent can explain table structure to user
- [ ] Verify agent suggests appropriate next steps (using dst-data)

#### Documentation
- [ ] Add entry to `docs/scripts-reference.md` for get_tableinfo.py
- [ ] Add entry to `docs/skills-reference.md` for dst-tableinfo skill
- [ ] Update `docs/fetcher-skills-guide.md` to include this skill in workflow

### Final Verification
- [ ] Script runs without errors
- [ ] Script handles all argument combinations
- [ ] Script has proper error handling
- [ ] Script logs appropriately
- [ ] Skill file has valid YAML
- [ ] Skill content is clear and actionable
- [ ] All examples in skill work correctly
- [ ] Integration with Fetcher Agent successful
- [ ] Documentation updated

## Success Criteria
- Python script created and executable
- Script has proper CLI with argparse
- Script fetches table metadata from DST API successfully
- Error handling is comprehensive
- Skill directory and SKILL.md created
- Skill has valid YAML frontmatter
- Skill content follows best practices (progressive disclosure)
- All skill examples are runnable and correct
- Integration with Fetcher Agent verified
- Documentation updated

## Notes
- **KISS**: Keep script focused on one task (get table metadata)
- **DRY**: Use shared API client and utilities
- **YAGNI**: Only implement essential features
- Use absolute paths in all examples
- Test with multiple different table types
- Document the structure of metadata response
