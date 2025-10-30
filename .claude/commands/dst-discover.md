---
name: dst-discover
description: Discover relevant DST tables for a topic
---

Find relevant DST tables for research topic: {{query}}

Follow this workflow:
1. Invoke dst-subjects skill to browse DST subject hierarchy
2. Identify relevant subject areas
3. Invoke dst-tables skill to search for tables in those subjects
4. Invoke dst-tableinfo skill for 3-5 most promising tables
5. Present recommendations to user with:
   - Table ID
   - Full description
   - Time period coverage (firstPeriod - latestPeriod)
   - Number of variables
   - Last updated date
   - Recommendation (fetch or skip) with reasoning

Return a structured list of recommended tables ranked by relevance.
