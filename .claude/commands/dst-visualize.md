---
name: dst-visualize
description: Create Chart.js visualizations
---

Use the Task tool to invoke the dst-visualize-agent with this prompt:

"Create visualizations for topic: {{topic}}
Using these analysis results: {{data_summary}}

Your workflow:
1. Invoke dst-visualize skill for Chart.js templates and patterns
2. Select appropriate chart types based on the data:
   - Line charts for time series trends
   - Bar charts for comparisons across categories
   - Stacked charts for composition analysis
3. Apply DST brand color palette consistently:
   - Primary: #1A4D2E (dark green)
   - Secondary: #D4A574 (gold)
   - Series colors: #2E7D54, #E8C9A0, #4A9B7F, #C18A3E
4. Fill Chart.js templates with the provided data
5. Create 2-3 key visualizations that capture the main insights
6. Save to: reports/{topic}_{timestamp}/visualizations.html

Return: Absolute path to the visualization file"

When the agent completes, present the visualization path to the user.
