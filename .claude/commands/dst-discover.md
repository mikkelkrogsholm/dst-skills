---
name: dst-discover
description: Discover relevant DST tables for a topic
---

Use the Task tool to invoke the DST Fetcher agent with this prompt:

"Find relevant DST tables for research topic: {{query}}

Your workflow:
1. Invoke dst-subjects skill to browse DST subject hierarchy
2. Identify relevant subject areas for this topic
3. Invoke dst-tables skill to search for tables in those subjects
4. Invoke dst-tableinfo skill for the 3-5 most promising tables
5. Assess each table's suitability

Return a structured list of recommended tables ranked by relevance, with:
- Table ID
- Full description
- Time period coverage (firstPeriod - latestPeriod)
- Number of variables
- Last updated date
- Recommendation (fetch or skip) with clear reasoning"

When the agent completes, present the table recommendations to the user.
