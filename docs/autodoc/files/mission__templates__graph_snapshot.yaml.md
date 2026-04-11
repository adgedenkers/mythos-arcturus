# mission/templates/graph_snapshot.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 40

---

### File: mission/templates/graph_snapshot.yaml

#### Purpose
This YAML file defines a mission to export a comprehensive JSON snapshot of the Mythos codebase graph directly from Neo4j using the `graph-bridge` tool. The snapshot is intended for use in Claude chat for accurate system knowledge.

#### Architecture
The file is structured as a YAML configuration for a mission in the Mythos system. It includes sections for mission metadata, context, phases, and success criteria. The mission involves running a shell command to generate the snapshot and validating its integrity.

#### Patterns
- **Configuration Pattern**: The file uses a configuration pattern to define mission parameters and steps.
- **Validation Pattern**: The `verify` phase uses validation steps to ensure the snapshot is correctly generated and valid.

#### Dependencies
- **graph-bridge**: A tool used to interact with Neo4j and generate the graph snapshot.
- **Python**: Used for JSON validation and integrity checks.

#### Interfaces
- **Mission Execution**: The mission can be executed using the `mythos-mission run` command.
- **Shell Commands**: The mission uses shell commands to execute `graph-bridge` and perform validation.

#### Database
- **Neo4j**: The graph database from which the snapshot is generated.

#### Configuration
- **Environment Variables**: No explicit environment variables are used.
- **Configuration Files**: The mission configuration is defined entirely within this YAML file.

#### Key Logic
1. **Snapshot Generation**: The `graph-bridge` tool is used to generate a JSON snapshot of the Mythos codebase graph.
2. **Validation**: The snapshot is validated to ensure it exists and contains expected data.
3. **Success Handling**: On successful validation, the snapshot is copied to a log directory and a log entry is created.

#### Integration Points
- **graph-bridge**: The mission integrates with `graph-bridge` to generate the graph snapshot.
- **Mythos Mission System**: The mission is part of the Mythos mission system and can be executed using the `mythos-mission run` command.
- **Logging**: The mission logs the success of the snapshot generation and copies the snapshot to a log directory for future reference.

### Detailed Breakdown

#### Mission Metadata
- **mission**: `graph-snapshot-export`
- **version**: `2`
- **description**: Provides a brief description of the mission's purpose.

#### Context
- **shell**: Defines a shell command to generate the graph snapshot and output it.
  - **command**: `graph-bridge snapshot /tmp/mythos-mission/graph_snapshot.json && cat /tmp/mythos-mission/graph_snapshot.json`
  - **alias**: `snapshot_output`

#### Phases
- **verify**: Ensures the snapshot was generated and is valid JSON.
  - **validate**:
    - **file_exists**: Checks if the snapshot file exists.
    - **shell**: Validates the JSON content using Python to ensure it contains expected keys and values.
  - **on_fail**: Halts the mission if validation fails.

#### Success Criteria
- **description**: Indicates the mission's success.
- **outputs**: Specifies the output file.
- **on_success**:
  - **command**: Copies the snapshot to a log directory.
  - **command**: Logs the success of the mission.

This YAML file is a crucial part of the Mythos system, enabling the export and validation of the Neo4j graph snapshot for use in Claude chat.
