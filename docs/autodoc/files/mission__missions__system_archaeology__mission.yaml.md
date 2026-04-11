# mission/missions/system_archaeology/mission.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 213

---

### File: mission/missions/system_archaeology/mission.yaml

#### Purpose
This YAML file defines a modular mission named "System Archaeology v2" for the Mythos system. It outlines various phases, queries, and commands to analyze the system's codebase, database, and live state to identify dead code, architectural stress points, and other system patterns.

#### Architecture
The file is structured into several sections:
- **Mission Metadata**: Contains basic information like mission name, version, and description.
- **Context**: Defines queries and commands to gather data from Neo4j, PostgreSQL, and shell commands.
- **Phases**: Specifies different phases of the mission, each with its own prompt file, output format, and paths.
- **Success and Failure**: Defines actions to be taken upon mission success or failure.

#### Patterns
- **Configuration Pattern**: The file uses a configuration pattern to define mission parameters and actions.
- **Modular Design**: The mission is divided into modular phases, each with specific tasks and outputs.

#### Dependencies
- **Neo4j**: For executing Cypher queries.
- **PostgreSQL**: For executing SQL queries.
- **Shell Commands**: For executing system commands to gather live system state data.
- **Ollama**: Likely used for processing prompts and generating outputs.

#### Interfaces
- **Prompts**: The mission uses prompts defined in `prompts/*.md` files.
- **Outputs**: The mission generates JSON outputs for each phase and a final report.

#### Database
- **Neo4j**: Queries are executed against labels such as `IntegrityFile`, `IntegrityFunction`, `IntegrityTable`, `IntegrityColumn`, `IntegrityService`, and `IntegrityDirectory`.
- **PostgreSQL**: Queries are executed against the `public` schema to gather live row counts, empty tables, and disk sizes.

#### Configuration
- **Environment Variables**: No explicit environment variables are used, but the mission relies on the system environment for executing shell commands.
- **Mission Configuration**: The mission configuration is defined entirely within this YAML file.

#### Key Logic
- **Data Gathering**: The mission gathers data from Neo4j, PostgreSQL, and shell commands to analyze the system.
- **Phase Execution**: Each phase executes a specific prompt file and processes the output.
- **Output Handling**: The mission handles outputs by writing them to specific paths and performing actions upon success or failure.

#### Integration Points
- **Prompts**: The mission integrates with prompt files located in `prompts/*.md`.
- **Database Queries**: The mission integrates with Neo4j and PostgreSQL to execute queries.
- **Shell Commands**: The mission integrates with the system to execute shell commands.
- **Output Processing**: The mission integrates with Ollama to process prompts and generate outputs.

### Detailed Breakdown

#### Mission Metadata
- **mission**: `system-archaeology-v2`
- **version**: `2`
- **description**: A deep multi-phase investigation of the Mythos system to find dead code, architectural stress, and buried patterns.
- **model**: `qwen2.5:32b`
- **temperature**: `0.15`

#### Context
- **Neo4j Queries**:
  - `files_by_function_count`: Finds the largest Python files by function count.
  - `never_imported_py`: Finds Python files that are not imported by any other file.
  - `files_with_main`: Finds Python files containing a `main` function.
  - `import_bottlenecks`: Identifies files that are imported by many other files.
  - `high_dependency_files`: Identifies files that import many other files.
  - `table_column_counts`: Finds tables with the most columns.
  - `graph_services`: Lists all services in the graph.
  - `system_stats`: Provides overall system statistics.

- **PostgreSQL Queries**:
  - `live_row_counts`: Counts rows in all tables.
  - `truly_empty_tables`: Identifies truly empty tables.
  - `table_disk_sizes`: Lists the top 15 tables by disk size.

- **Shell Commands**:
  - `refresh_stats`: Refreshes PostgreSQL statistics.
  - `running_services`: Lists running services.
  - `dir_sizes`: Lists directory sizes.
  - `key_file_lines`: Counts lines in key files.
  - `streams`: Lists stream counters.
  - `files_newer_than_docs`: Counts files changed since the architecture document.

#### Phases
- **dead_code**: Finds dead code, orphaned tables, and ghost services.
- **stress**: Identifies god files, bottlenecks, coupling hotspots, and wide tables.
- **synthesis**: Combines analyses into a final report with recommendations.

#### Success and Failure
- **Success**: On success, the mission logs the completion and copies the final report to a log file.
- **Failure**: On failure, the mission logs the failure and performs diagnostic actions.

This YAML file serves as the central configuration for the "System Archaeology v2" mission, orchestrating data gathering, phase execution, and output handling to provide a comprehensive analysis of the Mythos system.
