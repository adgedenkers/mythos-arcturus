# mission/missions/system_archaeology/prompts/synthesis.md

**Language:** markdown
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 94

---

### Purpose
This markdown file (`synthesis.md`) serves as a template for generating a final archaeology report for the Mythos system on Arcturus. It combines prior analysis reports on dead code and stress into a prioritized report with actionable recommendations.

### Architecture
The file is structured as a markdown document with sections for prior analyses, additional context, report instructions, and the expected JSON output structure. It uses placeholders for dynamic content such as `{phases.dead_code}`, `{context.graph.system_stats}`, etc.

### Patterns
No specific design patterns are used since this is a markdown file and not a code file.

### Dependencies
This markdown file does not directly import or rely on any code dependencies. It is intended to be used as a template by a script or a service that processes the content and fills in the placeholders.

### Interfaces
The file exposes a template structure that is meant to be filled by a script or service. It does not have direct interfaces but serves as a template for generating JSON output.

### Database
The file references data from the system, including system stats, directory sizes, and stream status, which are likely derived from the PostgreSQL, Neo4j, or Redis databases used in the Mythos system.

### Configuration
The file does not use any configuration files or environment variables directly. However, the placeholders suggest that the script or service using this template will need to configure the data sources for the placeholders.

### Key Logic
The key logic involves combining prior analyses (dead code and stress) into a unified report and categorizing findings into categories like `dead_code`, `fragility`, `complexity`, `data`, and `documentation`. Each finding is assigned a severity and effort level, and the report includes sections for quick wins, strategic recommendations, and buried treasures.

### Integration Points
This markdown file integrates with the Mythos system through the script or service that processes it. The placeholders suggest integration with subsystems that provide dead code analysis, stress analysis, system stats, directory sizes, and stream status. The final JSON output is likely used by another subsystem for further processing or reporting.

### Detailed Analysis
- **Prior Analyses**: The file combines two prior analyses: dead code and stress.
- **Additional Context**: Provides additional context such as system stats, directory sizes, and stream status.
- **Report Instructions**: Specifies how to combine the analyses into a unified report, categorize findings, and assign severity and effort levels.
- **Output Structure**: The JSON structure is defined with specific fields for the report title, executive summary, system health score, findings, quick wins, strategic recommendations, buried treasures, and stats.

This markdown file is a crucial template for generating comprehensive and actionable reports on the Mythos system's health and areas for improvement.
