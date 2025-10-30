# Task: DST Check Freshness (Uses query_metadata.py Script + Skill)

## Objective
Create the skill for checking data freshness using the existing query_metadata.py script (already created in task-dst-list-tables.md).

## Prerequisites
- Infrastructure setup completed (task-infrastructure.md)
- query_metadata.py script created (task-dst-list-tables.md)
- Understanding of data freshness concepts

## Tasks

### Verify Script Functionality

#### Check Existing Script
- [ ] Verify `scripts/db/query_metadata.py` exists
- [ ] Verify script has `--check-freshness` flag implemented
- [ ] Verify script has `--max-age-days` parameter
- [ ] Test freshness check functionality:
  - [ ] Run: `python scripts/db/query_metadata.py --table-id <ID> --check-freshness`
  - [ ] Verify age reported correctly
  - [ ] Run with threshold: `--max-age-days 30`
  - [ ] Verify fresh/stale determination works
- [ ] If any functionality missing, add it to query_metadata.py

### Create Skill

#### Skill Directory and File
- [ ] Create directory: `.claude/skills/dst-check-freshness/`
- [ ] Create file: `.claude/skills/dst-check-freshness/SKILL.md`

#### Skill Frontmatter
- [ ] Add YAML frontmatter:
  ```yaml
  ---
  name: DST Check Freshness
  description: Check data freshness and age for DST tables in DuckDB. Use when determining if data needs refreshing or validating data currency before analysis.
  ---
  ```
- [ ] Verify YAML delimiters correct
- [ ] Verify required fields present
- [ ] Verify description specific with trigger keywords

#### Skill Content
- [ ] Add **Purpose** section:
  - [ ] Explain: Verify data freshness and determine if refresh needed
  - [ ] Clarify: Essential for ensuring analysis uses current data
- [ ] Add **When to Use** section:
  - [ ] Before starting analysis (ensure data is current)
  - [ ] User asks about data age
  - [ ] Deciding whether to re-fetch data
  - [ ] Validating analysis with recent data
  - [ ] After discovering data with dst-list-tables
- [ ] Add **How to Use** section:
  - [ ] Check specific table: `python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_metadata.py --table-id <TABLE_ID> --check-freshness`
  - [ ] With age threshold: `--max-age-days <N>`
  - [ ] Example: `--max-age-days 30` for 30-day threshold
- [ ] Add **Expected Output** section:
  - [ ] Table name and ID
  - [ ] Last updated by DST (from source)
  - [ ] Fetch timestamp (when we downloaded)
  - [ ] Age of local data (human-readable, e.g., "15 days ago")
  - [ ] Freshness status (fresh/stale based on threshold if provided)
  - [ ] Example output snippet
- [ ] Add **Freshness Thresholds** section (recommended):
  - [ ] Daily updated tables: Refresh if > 1 day old
  - [ ] Weekly updated tables: Refresh if > 7 days old
  - [ ] Monthly updated tables: Refresh if > 30 days old
  - [ ] Quarterly updated tables: Refresh if > 90 days old
  - [ ] Annual updated tables: Refresh if > 365 days old
  - [ ] Note: Thresholds depend on analysis requirements
- [ ] Add **Decision Guide** section:
  - [ ] Fresh: Proceed with analysis confidently
  - [ ] Stale: Recommend refresh to user
  - [ ] Very stale (>threshold): Strongly recommend refresh
  - [ ] Unknown age: Investigate metadata issue
  - [ ] Consider: Does staleness matter for this analysis?
- [ ] Add **Interpreting Results** section:
  - [ ] Age in days: Simple metric for staleness
  - [ ] Last updated vs fetch timestamp: Distinguish source updates from local cache
  - [ ] If last_updated is recent but fetch_timestamp old: Data may have changed at source
- [ ] Add **Next Steps** section:
  - [ ] If fresh: Continue with analysis (use dst-query)
  - [ ] If stale: Inform user and offer to fetch fresh data
  - [ ] If refresh needed: Switch to Fetcher Agent
  - [ ] If acceptable: Proceed with disclaimer about data age
- [ ] Add **Examples** section:
  ```bash
  # Basic freshness check
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_metadata.py --table-id FOLK1A --check-freshness

  # With 30-day threshold
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_metadata.py --table-id FOLK1A --check-freshness --max-age-days 30

  # With 7-day threshold for daily data
  python /Users/mikkelfreltoftkrogsholm/Projekter/dst_skills/scripts/db/query_metadata.py --table-id FOLK1A --check-freshness --max-age-days 7
  ```
- [ ] Add **Tips** section:
  - [ ] Always check freshness before important analysis
  - [ ] Consider update frequency of source data
  - [ ] Communicate data age to user
  - [ ] When in doubt, refresh the data
  - [ ] Document data age in analysis results

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
- [ ] Test with old and new data
- [ ] Test error conditions (table not found)

#### Test with Analyst Agent
- [ ] Start Claude Code with Analyst Agent
- [ ] Ask agent to check if data is fresh
- [ ] Verify agent references dst-check-freshness skill
- [ ] Verify agent executes correct script with right arguments
- [ ] Verify agent interprets freshness correctly
- [ ] Verify agent makes appropriate recommendations:
  - [ ] Proceeds if fresh
  - [ ] Recommends refresh if stale
  - [ ] Suggests Fetcher Agent for refresh
- [ ] Test agent's decision-making with different thresholds

#### Documentation
- [ ] Add entry to `docs/skills-reference.md` for dst-check-freshness skill
- [ ] Update `docs/analyst-skills-guide.md` to include freshness checking in workflow
- [ ] Document recommended thresholds for different data types
- [ ] Add example of freshness-aware analysis workflow

### Final Verification
- [ ] Script functionality verified
- [ ] Skill file has valid YAML
- [ ] Skill content is clear and actionable
- [ ] All examples work correctly
- [ ] Freshness thresholds documented
- [ ] Decision guide is helpful
- [ ] Integration with Analyst Agent successful
- [ ] Agent makes intelligent freshness decisions
- [ ] Documentation updated

## Success Criteria
- query_metadata.py script supports freshness checking
- Skill directory and SKILL.md created
- Skill has valid YAML frontmatter
- Skill content follows best practices
- Freshness thresholds clearly documented
- Decision guide helps users make informed choices
- All skill examples are runnable and correct
- Integration with Analyst Agent verified
- Agent uses freshness info to guide workflow
- Documentation updated

## Notes
- **KISS**: Reuse existing query_metadata.py script
- **DRY**: Don't create separate freshness script
- **YAGNI**: Simple age calculation is sufficient
- Use absolute paths in all examples
- Freshness is context-dependent (analysis needs)
- Always communicate data age to users
- Make refresh easy (suggest Fetcher Agent)
- This skill is critical for data quality
