# mission/templates/system_archaeology.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 370

---

### Purpose
The `system_archaeology.yaml` file defines a mission template for the Mythos system to perform a comprehensive analysis of the entire system's codebase, live services, and database state. This mission aims to identify dead code, orphaned tables, architectural stress points, and other critical insights to improve system health and resilience.

### Architecture
The file is structured as a YAML configuration file, defining a mission with multiple phases. Each phase includes:
- **Context**: Data collection queries and commands to gather information from Neo4j, PostgreSQL, and the filesystem.
- **Prompt**: Instructions for the AI model to analyze the collected data and generate reports.
- **Output**: JSON-formatted reports for dead code analysis, stress analysis, and a final synthesis report.

### Patterns
- **Composite Pattern**: The mission is composed of multiple phases, each with its own context and prompt.
- **Template Method Pattern**: The mission template defines a standard structure for data collection and analysis, which can be reused for different missions.

### Dependencies
- **Neo4j**: For graph queries to gather information about files, functions, and services.
- **PostgreSQL**: For queries to gather live data statistics about tables.
- **Shell Commands**: For gathering live system state information.

### Interfaces
- **Mission Execution**: The mission is executed via the `mythos-mission run` command.
- **Output**: JSON-formatted reports are generated for each phase and the final synthesis.

### Database
- **Neo4j**: Queries to retrieve information from `IntegrityFile`, `IntegrityFunction`, `IntegrityTable`, `IntegrityColumn`, `IntegrityService`, and `IntegrityDirectory` nodes.
- **PostgreSQL**: Queries to retrieve row counts and disk sizes of tables in the `public` schema.

### Configuration
- **Environment Variables**: No explicit environment variables are used, but the mission relies on the Mythos system's configuration for database and Neo4j connections.
- **Mission Parameters**: The mission uses predefined parameters such as `mission`, `version`, `description`, `model`, and `temperature`.

### Key Logic
- **Data Collection**: Collects data from Neo4j, PostgreSQL, and shell commands to gather a comprehensive view of the system's state.
- **Analysis**: Uses AI prompts to analyze the collected data and generate reports on dead code, architectural stress, and system health.
- **Report Generation**: Generates JSON-formatted reports for each phase and a final synthesis report.

### Integration Points
- **Neo4j Integration**: Uses Cypher queries to gather graph data.
- **PostgreSQL Integration**: Uses SQL queries to gather live data statistics.
- **Shell Integration**: Uses shell commands to gather live system state information.
- **AI Model Integration**: Uses the `qwen2.5:32b` model to analyze data and generate reports.

### Detailed Breakdown of Phases

#### Phase 1: Dead Code Detection
- **Context**: Collects data on never-imported Python files, empty tables, registered services, running services, and empty directories.
- **Prompt**: Analyzes the collected data to identify dead code, orphaned tables, and services that are registered but not running.
- **Output**: JSON report detailing dead code, orphaned tables, service ghosts, and empty directories.

#### Phase 2: Architectural Stress Analysis
- **Context**: Collects data on the largest files, god files, most depended-on files, files with the most dependencies, widest tables, largest tables on disk, key file line counts, and stream counters.
- **Prompt**: Analyzes the collected data to identify architectural stress points, including god files, dependency bottlenecks, coupling hotspots, and database concerns.
- **Output**: JSON report detailing architectural risks and resilience scores.

#### Phase 3: Synthesis — Final Archaeology Report
- **Context**: Combines the outputs from the previous phases and adds additional context from directory sizes, files modified since the last architecture document update, and stream status.
- **Prompt**: Synthesizes the data to produce a final report with findings, recommendations, and a system health score.
- **Output**: JSON report summarizing the findings, recommendations, and system health score.

### Example Queries and Commands
- **Neo4j Queries**: 
  - `MATCH (f:IntegrityFile)-[:CONTAINS]->(fn:IntegrityFunction) WITH f.path as path, f.size_bytes as size, count(fn) as functions, f.directory as dir, f.extension as ext RETURN path, size, functions, dir, ext ORDER BY size DESC LIMIT 30`
  - `MATCH (t:IntegrityTable)-[:HAS_COLUMN]->(c:IntegrityColumn) WITH t.name as table_name, count(c) as col_count RETURN table_name, col_count ORDER BY col_count DESC LIMIT 20`
- **PostgreSQL Queries**:
  - `SELECT relname as table_name, n_live_tup as row_count FROM pg_stat_user_tables WHERE schemaname = 'public' ORDER BY n_live_tup DESC`
  - `SELECT relname as table_name, pg_size_pretty(pg_total_relation_size(relid)) as total_size FROM pg_stat_user_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(relid) DESC LIMIT 20`
- **Shell Commands**:
  - `systemctl list-units --type=service --state=running | grep mythos | awk '{print $1}'`
  - `du -sh /opt/mythos/*/ 2>/dev/null | sort -rh | head -20`

This comprehensive mission template ensures a thorough analysis of the Mythos system, providing actionable insights to improve system health and resilience.
