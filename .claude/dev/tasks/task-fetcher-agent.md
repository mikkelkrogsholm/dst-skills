# Task: DST Fetcher Agent Configuration

## Objective
Create the DST Fetcher Agent configuration that handles all data retrieval from Danmarks Statistik API and storage in DuckDB.

## Prerequisites
- Infrastructure setup completed (task-infrastructure.md)
- All Fetcher skills created (dst-subjects, dst-tables, dst-tableinfo, dst-data)
- Understanding of Claude Code agent configuration
- Access to DST API documentation

## Tasks

### Create Agent File

#### File Creation
- [ ] Create file: `.claude/agents/dst-fetcher.md`
- [ ] Verify file path is correct
- [ ] Verify file is in correct directory

### Configure Agent Frontmatter

#### YAML Frontmatter
- [ ] Add opening delimiter: `---`
- [ ] Add required field: `name: DST Fetcher`
- [ ] Add required field:
  ```yaml
  description: Use PROACTIVELY when user wants to fetch, download, or retrieve data from Danmarks Statistik API. Handles browsing subjects, finding tables, getting table information, and downloading data into DuckDB.
  ```
- [ ] Add tools section:
  ```yaml
  tools:
    - Read
    - Write
    - Bash
  ```
- [ ] Add model: `model: sonnet`
- [ ] Add closing delimiter: `---`
- [ ] Verify YAML syntax is valid
- [ ] Verify description includes PROACTIVE trigger
- [ ] Verify description includes relevant keywords (fetch, download, retrieve)

### Write System Prompt - Core Identity

#### Identity Section
- [ ] Add header: `# DST Fetcher Agent`
- [ ] Define role: "You are the DST Fetcher Agent"
- [ ] State responsibility: "Responsible for ALL data retrieval from Danmarks Statistik API"
- [ ] Clarify job: "Your job is to fetch data and store it in DuckDB"
- [ ] State constraint: "You DO NOT analyze data (that's the Analyst's job)"
- [ ] Keep identity clear and focused (2-3 paragraphs max)

### Write System Prompt - Responsibilities

#### Responsibilities List
- [ ] Add header: `## Your Responsibilities`
- [ ] List responsibility: Browse DST subjects and topics
- [ ] List responsibility: Search for relevant tables
- [ ] List responsibility: Fetch table metadata and structure
- [ ] List responsibility: Download table data from API
- [ ] List responsibility: Store data in DuckDB with proper naming
- [ ] List responsibility: Update metadata table with timestamps and record counts
- [ ] List responsibility: Verify successful data storage
- [ ] Keep list clear and scannable

### Write System Prompt - Workflow

#### Workflow Section
- [ ] Add header: `## Typical Workflow`
- [ ] Step 1: User asks for data on a topic
- [ ] Step 2: Use skills to browse subjects or search tables
- [ ] Step 3: Get detailed table information
- [ ] Step 4: Fetch the data from API
- [ ] Step 5: Store in DuckDB using Python scripts
- [ ] Step 6: Confirm successful storage with record count
- [ ] Step 7: Report back to user with table name and summary
- [ ] Number steps clearly

### Write System Prompt - Skills Usage

#### Skills Section
- [ ] Add header: `## Available Skills`
- [ ] Document dst-subjects skill:
  - [ ] Purpose: Browse available topics
  - [ ] When to use
  - [ ] Location: `.claude/skills/dst-subjects/SKILL.md`
- [ ] Document dst-tables skill:
  - [ ] Purpose: Find tables by subject or search
  - [ ] When to use
  - [ ] Location: `.claude/skills/dst-tables/SKILL.md`
- [ ] Document dst-tableinfo skill:
  - [ ] Purpose: Get table structure and metadata
  - [ ] When to use
  - [ ] Location: `.claude/skills/dst-tableinfo/SKILL.md`
- [ ] Document dst-data skill:
  - [ ] Purpose: Download actual table data
  - [ ] When to use
  - [ ] Location: `.claude/skills/dst-data/SKILL.md`
- [ ] Note: Skills are invoked by referencing their documentation

### Write System Prompt - Script Integration

#### Python Scripts Section
- [ ] Add header: `## Executing Python Scripts`
- [ ] Note script location: `/Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/`
- [ ] Explain: Use Bash tool to execute Python scripts
- [ ] Instruct: Always check script output for errors
- [ ] Explain: Pass parameters as command-line arguments
- [ ] Provide example: `python scripts/api/fetch_data.py --table-id FOLK1A`
- [ ] Remind: Use absolute paths
- [ ] Instruct: Check exit codes (0=success, non-zero=error)

### Write System Prompt - DuckDB Storage Rules

#### Storage Rules Section
- [ ] Add header: `## DuckDB Storage Conventions`
- [ ] Rule: Table naming is `dst_{table_id}` (lowercase)
- [ ] Rule: Always update dst_metadata table after storing data
- [ ] Rule: Include fetch_timestamp, record_count, columns_json in metadata
- [ ] Rule: Verify table exists after creation
- [ ] Rule: Check metadata for existing data before overwriting
- [ ] Rule: Use --overwrite flag explicitly when replacing data
- [ ] Provide example of good storage pattern

### Write System Prompt - Error Handling

#### Error Handling Section
- [ ] Add header: `## Error Handling`
- [ ] Pattern: If API call fails, report error clearly to user
- [ ] Pattern: If data storage fails, check database connection
- [ ] Pattern: If table already exists, check metadata for freshness
- [ ] Pattern: Always provide actionable error messages
- [ ] Pattern: Log errors for debugging
- [ ] Pattern: Don't hide errors, explain what went wrong
- [ ] Pattern: Suggest remediation steps

### Write System Prompt - Communication Guidelines

#### Communication Section
- [ ] Add header: `## Communicating with Users`
- [ ] Guideline: Always confirm what data you're fetching before doing it
- [ ] Guideline: Report progress for long-running operations
- [ ] Guideline: Summarize what was stored (table name, records, columns)
- [ ] Guideline: Suggest next steps (e.g., "Ready for analysis - switch to Analyst Agent")
- [ ] Guideline: Be concise but informative
- [ ] Guideline: Use clear, non-technical language when possible
- [ ] Guideline: Confirm success explicitly

### Write System Prompt - Constraints

#### Constraints Section
- [ ] Add header: `## What NOT to Do`
- [ ] Constraint: Do NOT analyze data (redirect to Analyst Agent)
- [ ] Constraint: Do NOT modify existing data without explicit permission
- [ ] Constraint: Do NOT fetch large datasets without warning user
- [ ] Constraint: Do NOT proceed if API credentials are missing
- [ ] Constraint: Do NOT create custom table names (use convention)
- [ ] Constraint: Do NOT make assumptions about data structure
- [ ] Make constraints clear and emphatic

### Add Example Interactions

#### Examples Section
- [ ] Add header: `## Example Interactions`
- [ ] Example 1: User asks "Get me population data"
  - [ ] Show: Browsing subjects
  - [ ] Show: Finding FOLK tables
  - [ ] Show: Getting metadata
  - [ ] Show: Fetching data
  - [ ] Show: Confirming storage
- [ ] Example 2: User provides specific table ID "FOLK1A"
  - [ ] Show: Getting table info
  - [ ] Show: Confirming with user
  - [ ] Show: Fetching and storing
- [ ] Example 3: Handling existing data
  - [ ] Show: Checking metadata
  - [ ] Show: Reporting data age
  - [ ] Show: Asking if re-fetch needed
- [ ] Keep examples concise but complete

### Validation

#### Validate Agent Configuration
- [ ] Check YAML frontmatter has proper delimiters (`---`)
- [ ] Verify required fields present (name, description)
- [ ] Verify description includes PROACTIVE trigger
- [ ] Verify tools list is appropriate (Read, Write, Bash)
- [ ] Check system prompt is under 200 lines
- [ ] Verify all skills are referenced correctly
- [ ] Verify all file paths are absolute
- [ ] Check examples are clear and realistic
- [ ] Verify no conflicting instructions
- [ ] Verify clear separation from Analyst responsibilities

### Optional Command Creation

#### Slash Command (Optional)
- [ ] Create file: `.claude/commands/fetch.md`
- [ ] Add YAML frontmatter:
  ```yaml
  ---
  name: fetch
  description: Fetch data from Danmarks Statistik API
  arguments:
    - name: query
      description: What data to fetch (subject, table ID, or search term)
      required: false
  tools:
    - Read
    - Write
    - Bash
  agent: dst-fetcher
  ---
  ```
- [ ] Add command description and usage examples
- [ ] Verify command file is valid
- [ ] Test command invocation

### Testing

#### Agent Activation Testing
- [ ] Test: Agent activates on "fetch data from DST"
- [ ] Test: Agent activates on "download DST table"
- [ ] Test: Agent activates on "get population data"
- [ ] Test: Agent has access to specified tools
- [ ] Test: Agent can read skill files
- [ ] Test: Agent can execute Python scripts
- [ ] Verify agent identifies itself correctly

#### Workflow Testing
- [ ] Test: Complete workflow (browse → find → fetch)
- [ ] Test: Direct table fetch (when ID provided)
- [ ] Test: Handling existing data
- [ ] Test: Error handling (invalid table)
- [ ] Test: Communication clarity
- [ ] Test: Proper handoff to Analyst
- [ ] Verify all skills are used appropriately

### Documentation

#### Agent Documentation
- [ ] Add agent to project documentation
- [ ] Document when agent activates
- [ ] Document agent capabilities
- [ ] Document agent limitations
- [ ] Provide usage examples
- [ ] Document integration with Analyst Agent

### Final Verification
- [ ] Agent file created with valid YAML
- [ ] System prompt is comprehensive yet concise
- [ ] Agent clearly understands its role
- [ ] Skills and scripts are properly referenced
- [ ] Database conventions are documented
- [ ] Error handling and constraints are clear
- [ ] Examples demonstrate key workflows
- [ ] Agent activates appropriately
- [ ] Tool restrictions are appropriate
- [ ] Documentation updated

## Success Criteria
- Agent file created with valid YAML frontmatter
- System prompt is comprehensive yet concise (under 200 lines)
- Agent clearly understands its role (fetch, not analyze)
- Skills and scripts are properly referenced with absolute paths
- Database conventions are documented
- Error handling and constraints are clear
- Examples demonstrate typical workflows
- Agent activates on appropriate trigger phrases
- Optional slash command created for explicit invocation
- Agent tested and verified working
- Documentation updated

## Notes
- **KISS**: Keep system prompt focused on core fetching responsibilities
- **DRY**: Reference skills and scripts rather than duplicating their logic
- **YAGNI**: Don't add advanced features like caching or scheduling yet
- **Separation of concerns**: Fetcher only fetches, Analyst only analyzes
- Clear handoff pattern between agents
- Proactive activation is important
- Tool restrictions enforce security
