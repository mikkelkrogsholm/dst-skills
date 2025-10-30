---
name: creating-skills
description: Expert knowledge on creating Agent Skills for Claude Code. Use when designing or creating SKILL.md files, understanding Skill structure, or implementing progressive disclosure patterns.
allowed-tools: Read, Grep, Glob
---

# Creating Agent Skills

This Skill provides comprehensive knowledge about creating effective Agent Skills in Claude Code.

## What Are Agent Skills?

Agent Skills are modular capabilities that extend Claude's functionality through organized folders containing instructions, scripts, and resources. Skills are **model-invoked** - Claude autonomously decides when to use them based on context and the Skill's description.

## File Structure

### Basic Skill (Instruction-Based)
```
.claude/skills/skill-name/
└── SKILL.md
```

### Advanced Skill (Code-Based with Resources)
```
.claude/skills/skill-name/
├── SKILL.md              # Main instructions
├── reference.md          # Detailed documentation
├── examples.md           # Usage examples
├── scripts/
│   └── helper.py        # Utility scripts
└── templates/
    └── template.txt     # Code templates
```

## SKILL.md Format

### Required Structure
```yaml
---
name: skill-name
description: What this Skill does and when to use it. Include trigger keywords.
---

# Skill Name

## Instructions
Step-by-step guidance for Claude.

## Examples
Concrete usage examples.
```

### YAML Frontmatter Fields

**Required**:
- `name` - Lowercase letters, numbers, hyphens only (max 64 characters)
- `description` - What it does + when to use it (max 1024 characters)

**Optional**:
- `allowed-tools` - Comma-separated list of tools (e.g., `Read, Grep, Glob`)
  - If omitted, inherits all tools from conversation
  - Use to restrict capabilities (e.g., read-only Skills)

## Writing Effective Descriptions

The `description` field is **critical** for Claude to discover when to use your Skill.

### Good Descriptions (Specific + Triggers)
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

```yaml
description: FastAPI endpoint patterns, dependency injection, error handling. Use when creating or modifying API routes, implementing authentication, or handling HTTP requests.
```

```yaml
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when working with Excel files, spreadsheets, or analyzing tabular data in .xlsx format.
```

### Bad Descriptions (Too Vague)
```yaml
description: Helps with documents  # ❌ What documents? When to use?
description: For data              # ❌ What kind of data? What operations?
description: Coding assistance     # ❌ What language? What tasks?
```

### Key Elements
1. **What it does** - List main capabilities
2. **When to use** - Specific triggers and keywords
3. **Context clues** - Technology names, file types, operations

## Instruction-Based vs Code-Based Skills

### Instruction-Based (Most Common)
**Use when**: Providing guidance, patterns, best practices, analysis

**Example**: Code review checklist, testing guidelines, style guide
```yaml
---
name: code-review-checklist
description: Code review best practices and security checks. Use when reviewing code, checking PRs, or analyzing code quality.
---

# Code Review Checklist

## Security
- Check for exposed secrets or API keys
- Verify input validation
- Review authentication/authorization

## Quality
- Functions are well-named and focused
- No code duplication
- Proper error handling
```

### Code-Based (For Generation/Automation)
**Use when**: Generating code, running scripts, automating tasks

**Example**: Endpoint scaffolding, test generation, migration creation
```
.claude/skills/scaffold-endpoint/
├── SKILL.md           # When/how to use the generator
├── scaffold.py        # Python script that generates code
└── templates/         # Jinja2 templates
    ├── model.py.jinja2
    └── endpoint.py.jinja2
```

**SKILL.md for code-based**:
```yaml
---
name: scaffold-endpoint
description: Generates complete REST endpoint with model, schema, and tests. Use when creating new API resources or adding CRUD operations.
allowed-tools: Read, Write, Bash
---

# Endpoint Scaffolding

## Usage
Run the scaffold script: `python scripts/scaffold.py [resource-name]`

## What It Generates
- SQLAlchemy model
- Pydantic schemas
- CRUD operations
- API endpoints
- Test fixtures

## Requirements
- Project uses FastAPI + SQLAlchemy
- Database connection configured
```

## Progressive Disclosure

For complex Skills, use multiple files to avoid overwhelming Claude with information.

**SKILL.md** - Overview and common usage:
```markdown
# PDF Processing

## Quick Start
Basic text extraction pattern.

## Advanced Usage
See [reference.md](reference.md) for:
- Form filling
- Table extraction
- Merging documents
```

**reference.md** - Detailed documentation (loaded only when needed):
```markdown
# PDF Processing Reference

## Form Filling
Detailed instructions for PDF form filling...

## Table Extraction
Advanced table extraction patterns...
```

Claude reads additional files only when it needs them, keeping context efficient.

## Tool Restrictions with allowed-tools

Use `allowed-tools` to limit capabilities for security or focus.

### Read-Only Skill
```yaml
---
name: safe-file-reader
description: Read and analyze files without modifications. Use when you need read-only access.
allowed-tools: Read, Grep, Glob
---
```

### Limited Scope Skill
```yaml
---
name: data-analyzer
description: Analyze data files and generate reports. Use for data analysis tasks.
allowed-tools: Read, Bash(python:*), Write
---
```

### No Restrictions (Inherits All)
```yaml
---
name: full-access-skill
description: Complete access to all tools.
# allowed-tools field omitted - inherits all tools
---
```

## Validation Rules

### Name Rules
- ✅ `creating-skills`, `code-reviewer`, `test-generator`
- ❌ `Creating Skills` (no spaces or capitals)
- ❌ `create_skills` (use hyphens, not underscores)
- ❌ `this-is-a-very-long-skill-name-that-exceeds-sixty-four-characters` (too long)

### Description Rules
- ✅ Include what + when + triggers
- ✅ Specific technologies/file types mentioned
- ✅ Under 1024 characters
- ❌ Vague "helps with X"
- ❌ Missing when-to-use guidance
- ❌ Too long/verbose

### YAML Rules
- ✅ Opening `---` on line 1
- ✅ Closing `---` before Markdown
- ✅ Valid YAML syntax (no tabs)
- ❌ Missing delimiters
- ❌ Invalid field names
- ❌ Tabs instead of spaces

## Best Practices

### 1. Keep Skills Focused
**Good** - One capability:
- "PDF form filling"
- "Excel data analysis"
- "Git commit messages"

**Bad** - Too broad:
- "Document processing" (split into PDF, Word, Excel Skills)
- "Data tools" (split by data type)
- "All coding tasks" (way too broad)

### 2. Use Clear Triggers
Include keywords users would naturally mention:
```yaml
# Good - Multiple triggers
description: Analyze Excel spreadsheets (.xlsx, .xls), create pivot tables, generate charts. Use when working with spreadsheets, tabular data, or Excel files.

# Bad - No triggers
description: Data analysis tool
```

### 3. Start Simple, Add Complexity
Begin with basic SKILL.md, add reference files only if needed:
1. Start: Single SKILL.md (~100 lines)
2. If too long: Split to SKILL.md + reference.md
3. If needs automation: Add scripts/ directory
4. If needs templates: Add templates/ directory

### 4. Provide Examples
Include concrete examples in SKILL.md:
```markdown
## Examples

### Basic Usage
```python
import pdfplumber
with pdfplumber.open("doc.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

### Advanced Usage
See [examples.md](examples.md) for table extraction and form filling.
```

### 5. Document Dependencies
If Skill requires packages, list them:
```markdown
## Requirements

Packages must be installed:
```bash
pip install pypdf pdfplumber pandas
```
```

## Common Patterns

### Analysis/Review Skills
```yaml
---
name: security-reviewer
description: Security vulnerability analysis for code. Use when reviewing security, checking authentication, or analyzing API endpoints.
allowed-tools: Read, Grep, Glob
---

# Security Review Checklist
- Authentication checks
- Input validation
- SQL injection risks
...
```

### Generation/Scaffolding Skills
```yaml
---
name: test-generator
description: Generate pytest test fixtures and test cases. Use when creating tests or adding test coverage.
allowed-tools: Read, Write, Bash
---

# Test Generation

Run: `python scripts/generate_test.py [module-name]`

Generates:
- Test fixtures
- Unit tests
- Integration tests
```

### Pattern/Convention Skills
```yaml
---
name: api-patterns
description: REST API design patterns and conventions. Use when creating API endpoints or designing REST interfaces.
allowed-tools: Read, Grep
---

# API Design Patterns

## Endpoint Structure
Standard CRUD pattern:
- GET /resources - List
- GET /resources/{id} - Retrieve
- POST /resources - Create
- PUT /resources/{id} - Update
- DELETE /resources/{id} - Delete
```

## Testing Skills

Test your Skills by asking questions that match the description:

**If description mentions "PDF files"**:
> "Can you help me extract text from this PDF?"

**If description mentions "API endpoints"**:
> "Create a new REST endpoint for products"

Claude should autonomously invoke your Skill based on the context.

## Troubleshooting

### Skill Not Invoked
**Problem**: Claude doesn't use the Skill

**Check**:
1. Is description specific enough? (Not "helps with data")
2. Does description include trigger keywords? (file types, operations)
3. Is YAML valid? (Check `---` delimiters)
4. Does file exist at correct path? (`.claude/skills/{name}/SKILL.md`)

### Skill Loaded But Not Helpful
**Problem**: Skill is used but doesn't provide useful guidance

**Check**:
1. Are instructions clear and actionable?
2. Are examples concrete? (Not "do X", but "use this code...")
3. Is Skill too broad? (Split into focused Skills)
4. Should it reference additional files? (Use progressive disclosure)

## Summary

**Essential Elements**:
1. Clear, focused purpose (one capability)
2. Specific description with triggers
3. Actionable instructions with examples
4. Valid YAML frontmatter
5. Appropriate tool restrictions

**Success Criteria**:
- Claude invokes Skill at the right time
- Instructions are clear and followable
- Examples are helpful and concrete
- Skill integrates well with others
