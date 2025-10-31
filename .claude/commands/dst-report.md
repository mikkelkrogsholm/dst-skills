---
name: dst-report
description: Generate comprehensive HTML report
---

Use the Task tool to invoke the DST Reporter agent with this prompt:

"Generate comprehensive HTML report for topic: {{topic}}
Using these inputs:
- Analysis results: {{analysis_results}}
- Visualizations: {{visualizations}}

Your workflow:
1. Invoke dst-report skill for HTML template structure
2. Create organized folder: reports/{topic}_{timestamp}/
3. Generate report with these sections:
   - Executive Summary (key findings and highlights)
   - Methodology (data sources, time period, approach)
   - Detailed Findings (analysis results and metrics)
   - Visualizations (embedded charts from provided paths)
   - Data Sources (DST tables used with metadata)
4. Fill all template placeholders:
   - {{REPORT_TITLE}}
   - {{TIMESTAMP}}
   - {{EXECUTIVE_SUMMARY}}
   - {{CONTENT_SECTIONS}}
   - {{DATA_SOURCES}}
5. Save report.html and all assets in the organized subfolder

Return: Absolute path to the final report.html file"

When the agent completes, present the report path to the user.
