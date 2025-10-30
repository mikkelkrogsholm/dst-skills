---
name: dst-analyze
description: Analyze DST data with SQL queries
---

Analyze: {{research_question}}
Using tables: {{table_ids}}

Follow this workflow:
1. Invoke dst-query skill for SQL patterns and helpers
2. Understand the research question and required metrics
3. Handle DST data quirks:
   - Filter suppressed values: WHERE column != '..'
   - Safe numeric casting: CASE WHEN != '..' THEN CAST(...)
   - Aggregate codes (TOT, I alt, etc.)
4. Execute SQL queries:
   - Use CTEs/WITH clauses for complex analysis
   - Calculate trends, aggregations, comparisons
   - Extract key insights
5. Present findings:
   - Key metrics and statistics
   - Trends over time
   - Patterns and anomalies
   - Data quality notes

Return structured analysis results suitable for visualization and reporting.
