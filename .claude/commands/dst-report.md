---
name: dst-report
description: Generate comprehensive HTML report
---

Generate comprehensive report for: {{topic}}
Using: {{analysis_results}} and {{visualizations}}

Follow this workflow:
1. Invoke dst-report skill for HTML template
2. Create organized folder: reports/{topic}_{timestamp}/
3. Generate report with sections:
   - Executive Summary (key findings)
   - Methodology (data sources, period)
   - Detailed Findings (analysis results)
   - Visualizations (embedded charts)
   - Data Sources (DST tables used)
4. Fill template placeholders:
   - {{REPORT_TITLE}}
   - {{TIMESTAMP}}
   - {{EXECUTIVE_SUMMARY}}
   - {{CONTENT_SECTIONS}}
   - {{DATA_SOURCES}}
5. Save report.html and all assets in subfolder

Return: Absolute path to report.html
