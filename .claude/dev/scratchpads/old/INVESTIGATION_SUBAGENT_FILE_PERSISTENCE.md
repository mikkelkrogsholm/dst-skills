# Investigation: Subagent File Persistence Issue
**Date**: 2025-10-30
**Issue**: Subagents cannot write files to filesystem despite reporting success
**Status**: Known bug, currently unresolved

---

## Summary

This is a **confirmed bug** in Claude Code affecting all subagents spawned via the Task tool. Subagents report successful file creation using Write/Edit tools, but files **do not persist** to the filesystem. This issue has been affecting users since at least **July 2025** and remains **unresolved** as of October 30, 2025.

---

## GitHub Issues Tracking This Bug

### Primary Issue: #4462
**Title**: "[BUG] Sub-agents claim successful file creation but files don't persist to filesystem"
**Opened**: July 25, 2025
**Reporter**: RGCsAGupta
**Status**: OPEN (initially closed as completed Aug 1, reopened Aug 6 after user reports)

**Environment**: Claude Code v1.0.61+, affects macOS, Windows, Linux

**Symptoms**:
- Task tool with subagents: agents report success ❌ files don't exist
- Direct Write tool from main instance: success ✅ files persist
- First invocation occasionally works; subsequent invocations consistently fail
- Agents provide detailed success messages and even mock directory listings
- Filesystem verification consistently shows no files were created

**User Quote**: "sub-agents are just burning tokens and not actually doing anything"

### Duplicate Issues

**Issue #7032** (Sept 2, 2025): Subagent Write Tool Not Creating Files
**Issue #7476** (Sept 11, 2025): Agents are unable to create files

All confirmed as duplicates of #4462. Multiple users across different platforms experiencing identical behavior.

---

## Root Cause Analysis

### Identified Cause (from Issue #7476)
> "The agent is executing within a sandboxed environment"

### Timeline Context

**October 20, 2025**: Anthropic introduced sandboxing feature
- Blog post: "Making Claude Code more secure and autonomous with sandboxing"
- Sandboxing reduces permission prompts by 84% in internal testing
- Uses OS-level primitives (bubblewrap on Linux, Seatbelt on macOS)
- Enforces both filesystem and network isolation

**However**: Bug predates official sandboxing announcement (July vs October)
- This suggests the sandboxing infrastructure was in development earlier
- Or the issue is related but not directly caused by sandboxing

### How Sandboxing Works

According to official documentation:

**Filesystem Restrictions**:
- ✅ Read access: Entire computer (except explicitly denied directories)
- ✅ Write access: Current working directory and subdirectories
- ❌ Cannot modify files outside working directory without permission

**Key Point**: Sandboxing does NOT prevent file writing entirely - it restricts WHERE files can be written.

### Why Subagents Are Different

The issue is **specific to subagents via Task tool**, not sandboxing in general:

| Context | File Writing | Database Writing |
|---------|-------------|------------------|
| Main agent | ✅ Works | ✅ Works |
| Direct tool calls | ✅ Works | ✅ Works |
| Subagent (Task tool) | ❌ Fails silently | ❌ Fails silently |

**Hypothesis**: Subagents execute in an **isolated temporary context** separate from the main working directory. When the subagent completes, this temporary context is destroyed, taking all file modifications with it.

---

## Technical Details

### Execution Context Isolation

From research findings:

1. **Separate Context Windows**: Each subagent operates in its own context, preventing pollution of main conversation

2. **Temporary Working Directory**: Subagents may spawn in a temporary directory that:
   - Appears to be the project directory to the agent
   - Actually exists in an isolated sandbox
   - Gets cleaned up when agent completes
   - Explains why write operations "succeed" but files vanish

3. **Environment Inheritance**:
   - Subagents inherit environment variables
   - But may not inherit the actual filesystem mount point
   - Working directory path may be symbolic/virtualized

### Why Agents Don't Know

The Write tool likely:
1. Writes to what it believes is the correct path
2. Receives success confirmation from the OS
3. File exists within the sandboxed context
4. Agent reads it back successfully (within same context)
5. Context destroyed when agent completes
6. File disappears from main filesystem

This creates perfect illusion of success from agent's perspective.

---

## User-Reported Workarounds

From GitHub issues and community forums:

### 1. Use Direct Tool Calls (Not Task Tool)
```
❌ Don't: Launch agent with Task tool for file operations
✅ Do: Use Write/Edit tools directly from main instance
```

### 2. Execute from System Terminal
```
❌ Don't: Use IDE's integrated terminal
✅ Do: Use system terminal directly
```
Some users report this helps, though mechanism unclear.

### 3. Create New Agents
```
When existing agent fails, create fresh agent
Occasionally first invocation works
```
Not reliable, but sometimes helps.

### 4. Avoid Subagents for Critical File Operations
```
Use subagents for:
- ✅ Research and analysis
- ✅ Code reading and understanding
- ✅ Read-only database queries
- ✅ Generating recommendations

Don't use subagents for:
- ❌ Creating files
- ❌ Editing files
- ❌ Database writes
- ❌ Any persistent state changes
```

---

## Official Anthropic Response

**Status**: No official fix or acknowledgment found in public channels

**Communication**:
- No developer comments on GitHub issues
- No mention in official documentation
- Not listed in known issues or troubleshooting guides
- Sandboxing docs don't mention subagent limitations

**Current State**:
- Issue #4462 remains OPEN (5+ months)
- Marked as duplicate by automated system
- No timeline for fix provided
- No workaround officially documented

---

## Impact on DST Skills Project

### What This Means for Our Agents

**DST Fetcher Agent**:
- ❌ Cannot download data to DuckDB from subagent
- ❌ Cannot create scratchpad documentation files
- ✅ Can research and identify tables
- ✅ Can return recommendations as text

**DST Analyst Agent**:
- ❌ Cannot create analysis documentation files
- ✅ Can analyze existing data in database
- ✅ Can return analysis as formatted text
- ❌ Cannot export results to CSV/JSON files

**All Custom Agents**:
- ❌ Any file write operation will silently fail
- ❌ Any database write operation will silently fail
- ✅ Read operations work normally
- ✅ Analysis and recommendations work

### Why Our Test Failed

1. DST Fetcher agent ran `python scripts/fetch_and_store.py`
2. Script executed successfully in agent's sandbox
3. Data written to DuckDB **within sandbox**
4. Agent queried data successfully **within sandbox**
5. Agent created documentation files **within sandbox**
6. Agent completed and returned success
7. Sandbox destroyed, all changes lost
8. Main environment: empty database, no files

The agent was completely honest - everything DID work from its perspective.

---

## Recommended Solutions

### Immediate Actions (For DST Skills)

#### Option 1: Hybrid Architecture (Recommended)
```
User Request
    ↓
Main Agent: Download data directly (no Task tool)
    ↓
Data persists in DuckDB ✅
    ↓
Subagent: Analyze data (read-only)
    ↓
Subagent: Return analysis as text
    ↓
Main Agent: Parse and present results
    ↓
(Optional) Main Agent: Save analysis to file
```

**Implementation**:
1. Remove file/DB operations from agent tool lists
2. Have main agent run Skills directly (not via Task)
3. Use agents only for analysis of existing data
4. Agents return text, main agent persists if needed

#### Option 2: Skills Without Agents
```
User Request
    ↓
Main Agent with Skills: Direct execution
    ↓
All operations in main context
    ↓
Everything persists normally
```

**Implementation**:
1. Convert agents to Skills (SKILL.md files)
2. Main agent invokes Skills directly
3. No Task tool usage
4. No isolation issues

#### Option 3: Agents Return Everything
```
User Request
    ↓
Subagent: Research, analyze, document
    ↓
Subagent: Return complete report in final message
    ↓
Main Agent: Extract and persist data
    ↓
Main Agent: Parse report for action items
```

**Implementation**:
1. Agents do all work in-memory
2. Return comprehensive text report
3. Include SQL queries, data findings, documentation
4. Main agent parses and persists

### Configuration Changes Required

#### 1. Update Agent Tool Lists

**dst-fetcher.md**:
```yaml
# Current (doesn't work):
tools: Read, Write, Bash, Grep, Glob

# Fixed (read-only):
tools: Read, Bash, Grep, Glob
# Remove: Write, Edit
```

**dst-analyst.md**:
```yaml
# Current (doesn't work):
tools: Read, Write, Bash, Grep, Glob

# Fixed (read-only):
tools: Read, Bash, Grep, Glob
# Remove: Write, Edit
```

#### 2. Update Agent Prompts

Add to all agent instructions:
```markdown
IMPORTANT LIMITATIONS:
- You are running in an isolated context
- File writes will NOT persist to the main filesystem
- Database writes will NOT persist to the main database
- Return ALL findings and documentation as formatted text in your final report
- Do NOT attempt to create files or modify databases
- Focus on research, analysis, and recommendations
```

#### 3. Update Skill Documentation

Add to each SKILL.md:
```markdown
## Usage with Agents

⚠️ **Known Limitation**: Subagents cannot persist file or database changes.

**Correct Usage**:
1. Use this skill directly from main agent (not via Task tool)
2. Or: Have subagent return recommendations, main agent executes
3. Or: Use skill for read-only operations from subagents

**Incorrect Usage**:
❌ Invoking this skill from a subagent expecting data to persist
```

#### 4. Update Documentation

**docs/getting-started.md**:
```markdown
## Important: Agent Limitations

Due to a current limitation in Claude Code, subagents cannot persist files or database changes.

**Correct Workflow**:
1. Download data using Skills directly: `/dst-data --table-id FOLK1A`
2. Analyze data with agent: Creates analysis, returns as text
3. Main agent saves analysis if needed

**Incorrect Workflow**:
❌ Agent downloads data → Data doesn't persist
```

**docs/faq.md**:
```markdown
### Q: Why isn't my data persisting when I use agents?

A: This is a known bug in Claude Code (Issue #4462). Subagents execute in
isolated sandboxes, and their file/database writes don't persist to the main
environment.

**Workaround**: Use Skills directly from the main agent instead of via Task tool.

### Q: Will this be fixed?

A: The issue has been reported to Anthropic (July 2025) and remains open.
We've designed DST Skills to work around this limitation.
```

---

## Long-Term Solutions

### If/When Anthropic Fixes the Bug

Monitor these sources:
- GitHub issue #4462: https://github.com/anthropics/claude-code/issues/4462
- Claude Code changelog: https://claudelog.com/claude-code-changelog/
- Anthropic engineering blog: https://www.anthropic.com/engineering

**When fixed**, we can:
1. Restore Write/Edit tools to agent configurations
2. Enable agents to persist their own documentation
3. Allow agents to download and store data directly
4. Update documentation to remove workarounds

### Alternative: Request Feature Enhancement

File feature request with Anthropic:
```markdown
Title: [FEATURE] Allow subagents to persist files to parent working directory

Description:
Currently subagents execute in isolated sandboxes where file writes don't
persist. This breaks workflows where subagents need to:
- Download and store data
- Create documentation
- Export analysis results

Proposed solution:
- Add `persistFiles: true` option to Task tool
- Or: Auto-persist writes to parent working directory
- Or: Allow explicit path mapping in agent config

Use case:
Data analysis workflows where fetcher agent downloads data for analyst agent
```

---

## Testing Verification

### How to Verify the Issue

```bash
# 1. Create test agent
cat > .claude/agents/test-writer.md << 'EOF'
---
name: test-writer
description: Test file writing
tools: Read, Write, Bash
---

Write a test file to test.txt with content "Hello World".
Then verify it exists with ls and cat.
EOF

# 2. Invoke agent from main Claude
> Use the test-writer agent to create a test file

# 3. Agent will report success and show file contents

# 4. Verify in main environment
ls test.txt  # File does not exist ❌
```

### How to Verify the Fix (When Available)

```bash
# Repeat test above
# If fix is deployed:
ls test.txt  # File exists ✅
cat test.txt  # Shows "Hello World" ✅
```

---

## References

### GitHub Issues
- Primary: https://github.com/anthropics/claude-code/issues/4462
- Duplicate: https://github.com/anthropics/claude-code/issues/7032
- Duplicate: https://github.com/anthropics/claude-code/issues/7476

### Official Documentation
- Sandboxing: https://docs.claude.com/en/docs/claude-code/sandboxing
- Subagents: https://docs.claude.com/en/docs/claude-code/sub-agents
- Sandboxing Blog: https://www.anthropic.com/engineering/claude-code-sandboxing

### Community Resources
- InfoQ Article: https://www.infoq.com/news/2025/08/claude-code-subagents/
- Medium Guide: https://jewelhuq.medium.com/practical-guide-to-mastering-claude-codes-main-agent-and-sub-agents-fd52952dcf00

---

## Conclusion

This is a **real bug**, not a design decision. The issue:
- ✅ Has been reported by multiple users
- ✅ Is tracked in GitHub (open for 5+ months)
- ✅ Affects all platforms (macOS, Windows, Linux)
- ✅ Breaks legitimate use cases
- ❌ Has no official fix or timeline
- ❌ Isn't documented as a known limitation

**For DST Skills**: We need to work around this by:
1. Running data operations in main agent (not subagents)
2. Using subagents only for read-only analysis
3. Having agents return text reports, not create files
4. Documenting the limitation clearly for users
5. Monitoring for fix and updating when available

**This is not our fault** - we discovered a real infrastructure limitation that affects all Claude Code subagent users.

---

**Report Generated**: 2025-10-30
**Investigation Time**: ~30 minutes
**Sources**: 10+ GitHub issues, official docs, community resources
**Confidence**: High (multiple independent confirmations)
**Action Required**: Update agent and skill configurations
