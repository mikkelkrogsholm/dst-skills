# Task: DST Subjects (Script + Skill)

## Objective
Create the Python script to fetch DST subjects from the API and the corresponding skill for the Fetcher Agent to use it.

## Prerequisites
- Infrastructure setup completed (task-infrastructure.md)
- API client and utilities available
- Understanding of DST subjects API endpoint

## Tasks

### Create Python Script

#### Script Implementation
- [ ] Create `scripts/api/get_subjects.py`
- [ ] Add command-line interface using argparse with arguments:
  - [ ] `--recursive` (optional) - Get all subject levels
  - [ ] `--output` (optional) - Save to JSON file path
- [ ] Implement `get_subjects(recursive=False)` function:
  - [ ] Use DSTAPIClient to call /subjects endpoint
  - [ ] Parse response and return structured data
  - [ ] Handle pagination if API uses it
  - [ ] Return subject hierarchy with id, description, and sub-subjects
- [ ] Add error handling:
  - [ ] HTTP errors (404, 500, timeout)
  - [ ] Invalid JSON responses
  - [ ] Network errors
- [ ] Add logging:
  - [ ] Log API request
  - [ ] Log response summary
  - [ ] Log errors with context
- [ ] Add output functionality:
  - [ ] Print to stdout as JSON by default
  - [ ] Save to file if `--output` specified
  - [ ] Format JSON for readability
- [ ] Add usage docstring with examples
- [ ] Set proper exit codes (0=success, 1=error)

#### Script Testing
- [ ] Test: Run script without arguments
  - [ ] Verify JSON output to stdout
  - [ ] Verify response contains subjects array
  - [ ] Check each subject has id and description
- [ ] Test: Run with `--recursive` flag
  - [ ] Verify all subject levels returned
  - [ ] Verify nested structure is correct
- [ ] Test: Run with `--output test_subjects.json`
  - [ ] Verify file created
  - [ ] Verify file contains valid JSON
  - [ ] Verify data matches stdout output
- [ ] Test: Error handling
  - [ ] Simulate API error (invalid URL)
  - [ ] Verify error message is clear
  - [ ] Verify exit code is 1
- [ ] Test: Invalid arguments
  - [ ] Run with invalid argument
  - [ ] Verify help message shown
  - [ ] Verify exit code is non-zero
- [ ] Verify script logs appropriately to log file
- [ ] Document any API-specific quirks or limitations

### Create Skill

#### Skill Directory and File
- [ ] Create directory: `.claude/skills/dst-subjects/`
- [ ] Create file: `.claude/skills/dst-subjects/SKILL.md`

#### Skill Frontmatter
- [ ] Add YAML frontmatter:
  ```yaml
  ---
  name: DST Subjects
  description: Browse Danmarks Statistik subject hierarchy to explore available data topics and categories. Use when user wants to discover what data is available or explore DST's organizational structure.
  ---
  ```
- [ ] Verify YAML delimiters are correct (`---` at start and end)
- [ ] Verify required fields present (name, description)
- [ ] Verify description is specific and includes trigger keywords

#### Skill Content
- [ ] Add **Purpose** section:
  - [ ] Explain: Browse DST's subject hierarchy to discover available topics
  - [ ] Clarify: Helps understand DST data organization
- [ ] Add **When to Use** section:
  - [ ] User wants to explore data categories
  - [ ] User asks "what data is available?"
  - [ ] User needs to find relevant subjects
  - [ ] User wants to understand DST organization
- [ ] Add **How to Use** section:
  - [ ] Basic usage: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_subjects.py`
  - [ ] With recursive flag: `--recursive`
  - [ ] Save to file: `--output <file>`
  - [ ] Note: Use absolute paths
- [ ] Add **Expected Output** section:
  - [ ] JSON array of subjects
  - [ ] Each subject has: id, description, potential sub-subjects
  - [ ] Example output snippet
- [ ] Add **Key Information to Extract** section:
  - [ ] Subject ID (needed for finding tables)
  - [ ] Subject description (topic name)
  - [ ] Hierarchy structure
- [ ] Add **Next Steps** section:
  - [ ] After identifying relevant subject
  - [ ] Use dst-tables skill with subject ID to find tables
- [ ] Add **Examples** section:
  ```bash
  # Get all subjects
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_subjects.py

  # Get complete hierarchy
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_subjects.py --recursive

  # Save to file
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/api/get_subjects.py --output subjects.json
  ```
- [ ] Add **Tips** section:
  - [ ] Start with non-recursive to see top-level subjects
  - [ ] Use recursive for complete understanding
  - [ ] Subject IDs are typically 2-digit numbers

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
- [ ] Ask agent to browse DST subjects
- [ ] Verify agent references dst-subjects skill
- [ ] Verify agent executes correct script with right arguments
- [ ] Verify agent interprets output correctly
- [ ] Verify agent can explain subjects to user
- [ ] Verify agent suggests next steps (using dst-tables)

#### Documentation
- [ ] Add entry to `docs/scripts-reference.md` for get_subjects.py
- [ ] Add entry to `docs/skills-reference.md` for dst-subjects skill
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
- Script fetches subjects from DST API successfully
- Error handling is comprehensive
- Skill directory and SKILL.md created
- Skill has valid YAML frontmatter
- Skill content follows best practices (progressive disclosure)
- All skill examples are runnable and correct
- Integration with Fetcher Agent verified
- Documentation updated

## Notes
- **KISS**: Keep script focused on one task (get subjects)
- **DRY**: Use shared API client and utilities
- **YAGNI**: Only implement essential features
- Use absolute paths in all examples
- Test with actual DST API to verify behavior
- Document any API quirks discovered during testing
