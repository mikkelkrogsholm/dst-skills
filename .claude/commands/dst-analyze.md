---
name: dst-analyze
description: Analyze DST data with SQL queries
---

Use the Task tool to invoke the DST Analyst agent with this prompt:

"Analyze the following research question: {{research_question}}
Using these DST tables: {{table_ids}}

Your workflow:
1. Invoke dst-query skill for SQL patterns and helper functions
2. Understand what metrics and insights are needed
3. Handle DST data quirks properly:
   - Filter suppressed values: WHERE column != '..'
   - Safe numeric casting: CASE WHEN != '..' THEN CAST(...)
   - Recognize aggregate codes (TOT, I alt, Drivmidler i alt, etc.)
4. Execute SQL queries against data/dst.db:
   - Use CTEs/WITH clauses for complex analysis
   - Calculate trends, aggregations, and comparisons
   - Extract key insights from the data
5. Assess data quality and note any limitations

Return structured analysis results with:
- Key metrics and statistics
- Trends over time (with percentages/rates where applicable)
- Patterns, anomalies, or interesting findings
- Data quality notes and caveats
- Results formatted for visualization and reporting"

When the agent completes, present the analysis findings to the user.
