# Task: DST Tables (Script + Skill)

## Objective
Create the Python script to search and list DST tables from the API and the corresponding skill for the Fetcher Agent to use it.

## Prerequisites
- Infrastructure setup completed (task-infrastructure.md)
- API client and utilities available
- Understanding of DST tables API endpoint

## Tasks

### Create Python Script

#### Script Implementation
- [ ] Create `scripts/api/get_tables.py`
- [ ] Add command-line interface using argparse with arguments:
  - [ ] `--subject` (optional) - Filter by subject ID
  - [ ] `--search` (optional) - Search by keyword
  - [ ] `--output` (optional) - Save to JSON file path
- [ ] Implement `get_tables(subject_id=None, search_term=None)` function:
  - [ ] Use DSTAPIClient to call /tables endpoint
  - [ ] Support filtering by subject if provided
  - [ ] Support keyword search if provided
  - [ ] Support listing all tables if no filters
  - [ ] Parse response to extract: id, text (name), description, updated
  - [ ] Handle pagination if API uses it
  - [ ] Return array of table objects
- [ ] Add error handling:
  - [ ] HTTP errors (404, 500, timeout)
  - [ ] Invalid JSON responses
  - [ ] Empty results
  - [ ] Network errors
- [ ] Add logging:
  - [ ] Log API request with parameters
  - [ ] Log response summary (number of tables)
  - [ ] Log errors with context
- [ ] Add output functionality:
  - [ ] Print to stdout as JSON by default
  - [ ] Save to file if `--output` specified
  - [ ] Format JSON for readability
- [ ] Add usage docstring with examples
- [ ] Set proper exit codes (0=success, 1=error)

#### Script Testing
- [ ] Test: Run without arguments (list all tables)
  - [ ] Verify JSON output to stdout
  - [ ] Verify response contains tables array
  - [ ] Check each table has id, text, updated
- [ ] Test: Run with `--subject <ID>`
  - [ ] Verify only tables for that subject returned
  - [ ] Verify result count makes sense
- [ ] Test: Run with `--search "population"`
  - [ ] Verify results contain search term in name/description
  - [ ] Verify relevant tables returned
- [ ] Test: Run with both `--subject` and `--search`
  - [ ] Verify combination works correctly
- [ ] Test: Run with `--output test_tables.json`
  - [ ] Verify file created
  - [ ] Verify file contains valid JSON
  - [ ] Verify data matches stdout output
- [ ] Test: Error handling
  - [ ] Invalid subject ID
  - [ ] API error
  - [ ] Verify error messages are clear
  - [ ] Verify exit code is 1
- [ ] Verify script logs appropriately to log file
- [ ] Document any API-specific quirks or limitations

### Create Skill

#### Skill Directory and File
- [ ] Create directory: `.claude/skills/dst-tables/`
- [ ] Create file: `.claude/skills/dst-tables/SKILL.md`

#### Skill Frontmatter
- [ ] Add YAML frontmatter:
  ```yaml
  ---
  name: DST Tables
  description: Search and list Danmarks Statistik tables by subject or keyword. Use when user needs to find specific tables or browse tables within a subject area.
  ---
  ```
- [ ] Verify YAML delimiters are correct (`---` at start and end)
- [ ] Verify required fields present (name, description)
- [ ] Verify description is specific and includes trigger keywords

#### Skill Content
- [ ] Add **Purpose** section:
  - [ ] Explain: Find DST tables by subject or search term
  - [ ] Clarify: Bridge between subjects and specific data tables
- [ ] Add **When to Use** section:
  - [ ] User mentions specific topic (population, employment, etc.)
  - [ ] User wants to see all tables in a subject
  - [ ] User searches for tables by keyword
  - [ ] After browsing subjects with dst-subjects skill
- [ ] Add **How to Use** section:
  - [ ] By subject: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_tables.py --subject <subject_id>`
  - [ ] By search: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_tables.py --search "<term>"`
  - [ ] All tables: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_tables.py`
  - [ ] Combined: `--subject <id> --search "<term>"`
  - [ ] Save results: `--output <file>`
- [ ] Add **Expected Output** section:
  - [ ] JSON array of tables
  - [ ] Each table has: id, text (name), description, updated
  - [ ] Example output snippet
- [ ] Add **Key Fields** section:
  - [ ] `id`: Table identifier (use for fetching data)
  - [ ] `text`: Human-readable table name
  - [ ] `description`: What the table contains
  - [ ] `updated`: Last update date from DST
- [ ] Add **Next Steps** section:
  - [ ] After identifying interesting table
  - [ ] Use dst-tableinfo skill to get detailed metadata
  - [ ] Use dst-data skill to fetch actual data
- [ ] Add **Examples** section:
  ```bash
  # List tables in subject 02 (Population)
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_tables.py --subject 02

  # Search for tables about population
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_tables.py --search "population"

  # Combined search
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_tables.py --subject 02 --search "age"

  # Save to file
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_tables.py --subject 02 --output tables.json
  ```
- [ ] Add **Tips** section:
  - [ ] Use subject filter when you know the category
  - [ ] Use search for exploratory discovery
  - [ ] Check updated date to see data currency
  - [ ] Note table IDs for next steps

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
- [ ] Ask agent to find tables about a topic
- [ ] Verify agent references dst-tables skill
- [ ] Verify agent executes correct script with right arguments
- [ ] Verify agent interprets output correctly
- [ ] Verify agent can explain tables to user
- [ ] Verify agent suggests next steps (using dst-tableinfo)

#### Documentation
- [ ] Add entry to `docs/scripts-reference.md` for get_tables.py
- [ ] Add entry to `docs/skills-reference.md` for dst-tables skill
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
- Script lists/searches tables from DST API successfully
- Error handling is comprehensive
- Skill directory and SKILL.md created
- Skill has valid YAML frontmatter
- Skill content follows best practices (progressive disclosure)
- All skill examples are runnable and correct
- Integration with Fetcher Agent verified
- Documentation updated

## Notes
- **KISS**: Keep script focused on one task (find tables)
- **DRY**: Use shared API client and utilities
- **YAGNI**: Only implement essential features
- Use absolute paths in all examples
- Test with actual DST API to verify behavior
- Support both subject-based and keyword-based discovery
