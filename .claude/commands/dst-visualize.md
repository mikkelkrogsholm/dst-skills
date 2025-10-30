---
name: dst-visualize
description: Create Chart.js visualizations
---

Create visualizations for: {{topic}}
Using analysis results: {{data_summary}}

Follow this workflow:
1. Invoke dst-visualize skill for Chart.js templates
2. Select appropriate chart types:
   - Line charts for time series trends
   - Bar charts for comparisons
   - Stacked charts for composition
3. Use DST color palette:
   - Primary: #1A4D2E (dark green)
   - Secondary: #D4A574 (gold)
   - Series: #2E7D54, #E8C9A0, #4A9B7F, #C18A3E
4. Fill templates with data
5. Create 2-3 key visualizations
6. Save to: reports/{topic}_{timestamp}/visualizations.html

Return: Path to visualization file
