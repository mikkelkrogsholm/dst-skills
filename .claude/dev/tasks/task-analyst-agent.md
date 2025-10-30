# Task: DST Analyst Agent Configuration

## Objective
Create the DST Analyst Agent configuration that handles all data analysis, querying, and insights from DuckDB-stored DST data.

## Prerequisites
- Infrastructure setup completed (task-infrastructure.md)
- All Analyst skills created (dst-list-tables, dst-check-freshness, dst-query)
- Fetcher agent created (task-fetcher-agent.md)
- Understanding of Claude Code agent configuration

## Tasks

### Create Agent File

#### File Creation
- [ ] Create file: `.claude/agents/dst-analyst.md`
- [ ] Verify file path is correct
- [ ] Verify file is in correct directory

### Configure Agent Frontmatter

#### YAML Frontmatter
- [ ] Add opening delimiter: `---`
- [ ] Add required field: `name: DST Analyst`
- [ ] Add required field:
  ```yaml
  description: Use PROACTIVELY when user wants to analyze, query, explore, or get insights from Danmarks Statistik data already stored in DuckDB. Handles data freshness checks, SQL queries, statistical analysis, and visualization preparation.
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
- [ ] Verify description includes relevant keywords (analyze, query, explore, insights)

### Write System Prompt - Core Identity

#### Identity Section
- [ ] Add header: `# DST Analyst Agent`
- [ ] Define role: "You are the DST Analyst Agent"
- [ ] State responsibility: "Responsible for ALL data analysis from DuckDB"
- [ ] Clarify job: "Your job is to query, analyze, and extract insights from stored data"
- [ ] State constraint: "You DO NOT fetch new data (that's the Fetcher's job)"
- [ ] Keep identity clear and focused (2-3 paragraphs max)

### Write System Prompt - Responsibilities

#### Responsibilities List
- [ ] Add header: `## Your Responsibilities`
- [ ] List responsibility: Check data freshness in DuckDB
- [ ] List responsibility: Run SQL queries against stored DST tables
- [ ] List responsibility: Perform statistical analysis
- [ ] List responsibility: Join multiple DST tables for complex analysis
- [ ] List responsibility: Validate data quality and completeness
- [ ] List responsibility: Prepare data summaries and insights
- [ ] List responsibility: Format results for user consumption
- [ ] List responsibility: Identify when data refresh is needed (delegate to Fetcher)
- [ ] Keep list clear and scannable

### Write System Prompt - Workflow

#### Workflow Section
- [ ] Add header: `## Typical Workflow`
- [ ] Step 1: User asks analytical question about DST data
- [ ] Step 2: Check if required data exists in DuckDB
- [ ] Step 3: Check data freshness
- [ ] Step 4: If data missing/stale, recommend Fetcher Agent
- [ ] Step 5: If data available, construct and run SQL query
- [ ] Step 6: Analyze results and extract insights
- [ ] Step 7: Present findings clearly to user
- [ ] Step 8: Suggest follow-up analyses
- [ ] Number steps clearly

### Write System Prompt - Skills Usage

#### Skills Section
- [ ] Add header: `## Available Skills`
- [ ] Document dst-list-tables skill:
  - [ ] Purpose: See what data is available locally
  - [ ] When to use: Start of analysis, checking availability
  - [ ] Location: `.claude/skills/dst-list-tables/SKILL.md`
- [ ] Document dst-check-freshness skill:
  - [ ] Purpose: Verify data age and currency
  - [ ] When to use: Before analysis, determining refresh needs
  - [ ] Location: `.claude/skills/dst-check-freshness/SKILL.md`
- [ ] Document dst-query skill:
  - [ ] Purpose: Execute SQL queries and get table summaries
  - [ ] When to use: Main analysis work
  - [ ] Location: `.claude/skills/dst-query/SKILL.md`
- [ ] Note: Skills are invoked by referencing their documentation

### Write System Prompt - Script Integration

#### Python Scripts Section
- [ ] Add header: `## Executing Python Scripts`
- [ ] Note script location: `/Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/`
- [ ] Explain: Use Bash tool to execute Python scripts
- [ ] Instruct: Always check script output for errors
- [ ] Explain: Pass SQL queries and parameters as arguments
- [ ] Provide example: `python scripts/db/query_data.py --sql "SELECT * FROM dst_folk1a LIMIT 10"`
- [ ] Remind: Use absolute paths
- [ ] Instruct: Check exit codes (0=success, non-zero=error)

### Write System Prompt - DuckDB Query Guidelines

#### Query Guidelines Section
- [ ] Add header: `## DuckDB Query Best Practices`
- [ ] Guideline: Table naming convention is `dst_{table_id}` (lowercase)
- [ ] Guideline: Always query dst_metadata first to verify table exists
- [ ] Guideline: Check record_count before running expensive queries
- [ ] Guideline: Use LIMIT for exploratory queries
- [ ] Guideline: Use appropriate aggregations for large datasets
- [ ] Guideline: Format dates and numbers appropriately
- [ ] Guideline: Handle NULL values explicitly
- [ ] Guideline: Start with table summary before complex queries
- [ ] Provide example of good query pattern

### Write System Prompt - Data Freshness Management

#### Freshness Section
- [ ] Add header: `## Managing Data Freshness`
- [ ] Rule: Always check fetch_timestamp in dst_metadata
- [ ] Rule: If data older than reasonable threshold, warn user
- [ ] Rule: Suggest re-fetching stale data (redirect to Fetcher)
- [ ] Document thresholds:
  - [ ] Daily tables: refresh if > 1 day old
  - [ ] Monthly tables: refresh if > 30 days old
  - [ ] Annual tables: refresh if > 365 days old
- [ ] Pattern: Check freshness, proceed or recommend refresh
- [ ] Note: Communicate data age in analysis results

### Write System Prompt - Analysis Techniques

#### Analysis Techniques Section
- [ ] Add header: `## Analysis Approaches`
- [ ] Technique: Descriptive statistics (COUNT, SUM, AVG, MIN, MAX)
- [ ] Technique: Time series (GROUP BY date/year, ORDER BY time)
- [ ] Technique: Comparisons (percentage changes, ratios, differences)
- [ ] Technique: Segmentation (GROUP BY categories, PARTITION BY)
- [ ] Technique: Joins (combine related tables using appropriate keys)
- [ ] Technique: Filtering (WHERE clauses for relevant subsets)
- [ ] Provide examples of each technique

### Write System Prompt - Error Handling

#### Error Handling Section
- [ ] Add header: `## Error Handling`
- [ ] Pattern: If table doesn't exist, explain and suggest fetching it
- [ ] Pattern: If query fails, check SQL syntax and table schema
- [ ] Pattern: If no data matches criteria, suggest broadening filters
- [ ] Pattern: If results unexpectedly large, suggest aggregation
- [ ] Pattern: Always provide actionable error messages
- [ ] Pattern: Use table summary to understand structure on errors

### Write System Prompt - Communication Guidelines

#### Communication Section
- [ ] Add header: `## Communicating with Users`
- [ ] Guideline: Confirm what data you'll analyze
- [ ] Guideline: Explain your analytical approach before running queries
- [ ] Guideline: Present results with clear context and units
- [ ] Guideline: Highlight key insights and unexpected findings
- [ ] Guideline: Offer additional analyses or deeper dives
- [ ] Guideline: Format numbers appropriately (e.g., 1,234,567)
- [ ] Guideline: Be concise but thorough
- [ ] Guideline: Include data age in important findings

### Write System Prompt - Constraints

#### Constraints Section
- [ ] Add header: `## What NOT to Do`
- [ ] Constraint: Do NOT fetch new data from API (redirect to Fetcher)
- [ ] Constraint: Do NOT modify data in tables (read-only analysis)
- [ ] Constraint: Do NOT drop or truncate tables
- [ ] Constraint: Do NOT run queries that could overload database
- [ ] Constraint: Do NOT make assumptions about data without checking metadata
- [ ] Constraint: Do NOT proceed with analysis on stale data without warning user
- [ ] Make constraints clear and emphatic

### Add Example Interactions

#### Examples Section
- [ ] Add header: `## Example Interactions`
- [ ] Example 1: User asks "What's the population of Denmark?"
  - [ ] Show: Checking for population table
  - [ ] Show: Verifying freshness
  - [ ] Show: Querying data
  - [ ] Show: Presenting result
- [ ] Example 2: User asks "Compare employment rates over last 5 years"
  - [ ] Show: Checking for employment data
  - [ ] Show: Verifying freshness
  - [ ] Show: Running time series query
  - [ ] Show: Presenting trend analysis
- [ ] Example 3: Handling missing data
  - [ ] Show: Checking dst_metadata
  - [ ] Show: Data doesn't exist
  - [ ] Show: Recommending Fetcher Agent with specific table ID
- [ ] Keep examples concise but complete

### Write System Prompt - Fetcher Collaboration

#### Collaboration Section
- [ ] Add header: `## Working with Fetcher Agent`
- [ ] When to involve Fetcher:
  - [ ] Data doesn't exist in DuckDB
  - [ ] Data is stale and refresh needed
  - [ ] User requests new data source
- [ ] How to hand off:
  - [ ] Clearly state what data is needed
  - [ ] Provide table ID or search terms
  - [ ] Explain why fetch is needed
  - [ ] Wait for Fetcher to complete
- [ ] Resuming after fetch:
  - [ ] Re-check metadata to confirm availability
  - [ ] Verify freshness
  - [ ] Proceed with original analysis
- [ ] Make handoff pattern clear

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
- [ ] Verify clear separation from Fetcher responsibilities
- [ ] Verify read-only philosophy maintained

### Optional Command Creation

#### Slash Command (Optional)
- [ ] Create file: `.claude/commands/analyze.md`
- [ ] Add YAML frontmatter:
  ```yaml
  ---
  name: analyze
  description: Analyze DST data stored in DuckDB
  arguments:
    - name: query
      description: What to analyze (table name, question, or analysis type)
      required: false
  tools:
    - Read
    - Write
    - Bash
  agent: dst-analyst
  ---
  ```
- [ ] Add command description and usage examples
- [ ] Verify command file is valid
- [ ] Test command invocation

### Testing

#### Agent Activation Testing
- [ ] Test: Agent activates on "analyze population trends"
- [ ] Test: Agent activates on "query DST data"
- [ ] Test: Agent activates on "show me statistics"
- [ ] Test: Agent has access to specified tools
- [ ] Test: Agent can read skill files
- [ ] Test: Agent can execute Python scripts
- [ ] Verify agent identifies itself correctly

#### Workflow Testing
- [ ] Test: Complete workflow (check → freshness → query → present)
- [ ] Test: Handling missing data (handoff to Fetcher)
- [ ] Test: Handling stale data (recommend refresh)
- [ ] Test: Complex analysis (multiple tables, aggregations)
- [ ] Test: Error handling (invalid queries, missing tables)
- [ ] Test: Communication clarity
- [ ] Verify all skills are used appropriately

#### Cross-Agent Testing
- [ ] Test: Handoff to Fetcher when data missing
- [ ] Test: Resume after Fetcher completes
- [ ] Test: Complete workflow from fetch to analysis
- [ ] Verify seamless collaboration

### Documentation

#### Agent Documentation
- [ ] Add agent to project documentation
- [ ] Document when agent activates
- [ ] Document agent capabilities
- [ ] Document agent limitations
- [ ] Provide usage examples
- [ ] Document integration with Fetcher Agent
- [ ] Document SQL query patterns

### Final Verification
- [ ] Agent file created with valid YAML
- [ ] System prompt is comprehensive yet concise
- [ ] Agent clearly understands its role
- [ ] Skills and scripts are properly referenced
- [ ] Data freshness management is well-defined
- [ ] Analysis techniques are documented
- [ ] Error handling and constraints are clear
- [ ] Examples demonstrate key workflows
- [ ] Collaboration with Fetcher is explained
- [ ] Agent activates appropriately
- [ ] Tool restrictions are appropriate
- [ ] Read-only philosophy maintained
- [ ] Documentation updated

## Success Criteria
- Agent file created with valid YAML frontmatter
- System prompt is comprehensive yet concise (under 200 lines)
- Agent clearly understands its role (analyze, not fetch)
- Skills and scripts are properly referenced with absolute paths
- Data freshness management is well-defined
- Analysis techniques are documented
- Error handling and constraints are clear
- Collaboration with Fetcher Agent is explained
- Examples demonstrate typical workflows
- Agent activates on appropriate trigger phrases
- Optional slash command created for explicit invocation
- Cross-agent workflow tested and verified
- Agent tested and verified working
- Documentation updated

## Notes
- **KISS**: Keep system prompt focused on core analysis responsibilities
- **DRY**: Reference skills and scripts rather than duplicating logic
- **YAGNI**: Don't add advanced features like ML or complex visualizations yet
- **Separation of concerns**: Analyst only analyzes, Fetcher only fetches
- **Read-only philosophy**: Analyst should never modify source data
- Clear handoff pattern with Fetcher
- Freshness awareness is critical
- Proactive activation is important
