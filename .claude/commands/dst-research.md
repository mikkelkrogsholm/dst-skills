---
name: dst-research
description: |
  Launch comprehensive research workflow across multiple DST tables.
  Discovers relevant tables, guides data fetching, performs multi-dimensional
  analysis, and generates HTML reports with visualizations.
args:
  - name: topic
    description: Research topic or question (e.g., "electric vehicles", "population aging")
    required: true
---

Research Danmarks Statistik data comprehensively on: {{topic}}

You are now acting as the DST Research Analyst. Follow this workflow:

1. **Discovery Phase**
   - Use dst-subjects and dst-tables to find relevant tables
   - Present findings and get user confirmation on which tables to analyze

2. **Data Availability Check**
   - Use dst-list-tables to see what's already stored
   - Use dst-check-freshness for existing tables

3. **Data Fetching Instructions**
   - **CRITICAL**: You cannot fetch data directly due to Claude Code bug #4462
   - Provide explicit commands for user to run in main agent:
     - "Use dst-data to fetch [TABLE_ID]"
   - Wait for user confirmation that data is fetched

4. **Analysis Phase**
   - Use dst-join-analysis if multiple tables need combining
   - Use dst-query for data extraction and calculations

5. **Visualization Phase**
   - Use dst-visualize to create line/bar charts
   - Focus on trend analysis and comparisons

6. **Reporting Phase**
   - Use dst-report to generate HTML output
   - Decide: single comprehensive report OR multiple focused reports
   - Save to reports/ directory with timestamp

Begin the research on: {{topic}}
