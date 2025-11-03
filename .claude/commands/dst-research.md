---
name: dst-research
description: Comprehensive DST research workflow (orchestrates other commands)
args:
  - name: topic
    description: Research topic or question (e.g., "electric vehicles", "population aging")
    required: true
---

Perform comprehensive research on: {{topic}}

This command orchestrates a complete research workflow by calling other commands.

## Workflow

**Phase 1: Discovery**
Execute: /dst-discover {{topic}}
- Review recommended tables
- Get user confirmation on which tables to fetch

**Phase 2: Data Acquisition**
Execute: /dst-fetch {{approved_table_ids}}
- Review validation report
- Confirm data is ready for analysis

**Phase 3: Analysis**
Execute: /dst-analyze "{{research_question}}" --tables {{table_ids}}
- Review findings and metrics
- Identify key insights

**Phase 4: Visualization**
Execute: /dst-visualize {{topic}} --data {{analysis_summary}}
- Preview generated charts
- Confirm visualizations capture key insights

**Phase 5: Reporting**
Execute: /dst-report {{topic}} --analysis {{results}} --viz {{charts}}
- Review final report
- Return path to HTML report

## Important
- Present results at end of each phase
- Get user confirmation before proceeding to next phase
- Each phase uses specialized capabilities via command composition
- Final output: Comprehensive HTML report in organized subfolder

Begin the research on: {{topic}}
