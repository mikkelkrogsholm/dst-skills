# DST Skills Architecture

## Design Philosophy

The DST Skills system uses three Claude Code primitives:

1. **Commands** - Composable workflow shortcuts
2. **Skills** - Progressive disclosure documentation
3. **Agents** - Specialized task executors

## Why Command Composition?

Commands can invoke other commands, enabling:

- **Modularity:** Each command does one thing well
- **Reusability:** `/dst-fetch` used by both `/dst-research` and standalone
- **Testability:** Test each command independently
- **Maintainability:** Changes to `/dst-analyze` don't break `/dst-fetch`

**Example:**
```
/dst-research {topic}
  ↓ calls
  /dst-discover {topic}
  /dst-fetch {tables}
  /dst-analyze {question}
  /dst-visualize {data}
  /dst-report {results}
```

## Why Specialized Agents?

Each agent has a focused responsibility:

- **dst-fetch-agent** - Discovery and acquisition only
- **dst-analyze-agent** - Querying and analysis only
- **dst-visualize-agent** - Chart creation only
- **dst-report-agent** - Report assembly only

**Benefits:**
- Clear separation of concerns
- Agents can be improved independently
- Easier to understand and maintain

## Why Skills for Documentation?

Skills provide just-in-time knowledge:

- **dst-data** - When fetching, load API quirks
- **dst-query** - When analyzing, load SQL patterns
- **dst-visualization** - When charting, load templates

**NOT executable code** - just reference material.

## How Delegation Works

Commands use the Task tool to invoke agents:

```markdown
# In /dst-fetch command

Invoke the dst-fetch-agent via Task tool to:
1. Check existing data
2. Fetch missing tables
3. Validate results
```

The Task tool:
1. Loads agent prompt
2. Gives agent access to specified tools
3. Agent executes task
4. Returns results to command

## Data Flow

```
User
  ↓
Command (/dst-research)
  ↓ Task tool
Agent (dst-fetch-agent)
  ↓ Bash tool
Python Script (fetch_and_store.py)
  ↓ HTTP
DST API
  ↓
DuckDB (dst.db)
  ↓
Agent (dst-analyze-agent)
  ↓ SQL
Analysis Results
  ↓
Agent (dst-visualize-agent)
  ↓ Write
HTML Charts
  ↓
Agent (dst-report-agent)
  ↓ Write
Final Report (reports/{topic}_{timestamp}/)
```

## File Organization

```
.claude/
├── agents/          # Specialized agents
├── commands/        # Workflow shortcuts
└── skills/          # Documentation

scripts/
├── api/            # DST API clients
├── db/             # DuckDB operations
├── reports/        # Report generation
└── utils/          # Shared utilities

reports/
└── {topic}_{timestamp}/
    ├── report.html
    ├── visualizations.html
    └── data/
```

## Design Decisions

### Why not a single "do everything" agent?
- Too complex to maintain
- Context window limits
- Harder to test individual capabilities

### Why not agents that call other agents?
- Claude Code agents can't directly invoke each other
- Commands provide the orchestration layer
- More explicit and easier to understand

### Why separate visualization and reporting?
- Visualizations useful standalone
- Reports can embed provided charts
- Allows custom chart combinations

### Why subfolders for each research?
- Keeps reports/ organized
- All related files together
- Easy to share complete analysis
- Prevents filename conflicts

## Best Practices

1. **Use commands for workflows** - Don't write custom orchestration
2. **Let agents do their job** - Don't override with direct tool use
3. **Invoke skills for docs** - Don't guess API behavior
4. **Validate early** - Check data after fetching
5. **Organize outputs** - Use provided folder structure

## Evolution

**Phase 1 (Initial):** Multiple agents, unclear delegation
**Phase 2 (Refactor):** Command composition + agent delegation
**Phase 3 (Future):** Additional domain-specific commands and agents

## Key Lessons

- Commands ≠ agent invocation (they expand prompts)
- Skills ≠ executables (they're documentation)
- Agents ≠ independent (they're task executors)
- Delegation requires explicit Task tool usage
