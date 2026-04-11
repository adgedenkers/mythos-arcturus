# tools/generate_system_state.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 429

---

### File: tools/generate_system_state.py

#### Purpose
This file contains functions to gather various system state information and generate live telemetry files such as `system-state.txt`, `patch-versions.txt`, `patch-install-history.txt`, and `CLAUDE_CONTEXT.md`.

#### Architecture
The file consists of several top-level functions, each responsible for gathering specific types of system state information. The main function `main` orchestrates the generation of these telemetry files by calling the respective generator functions.

- **Functions**: 
  - `run_cmd`: Executes shell commands and handles exceptions.
  - `get_git_tags`: Retrieves version tags from Git.
  - `get_patch_version_map`: Maps patch numbers to versions from Git commit messages.
  - `get_service_health`: Retrieves the health status of Mythos services.
  - `get_postgres_stats`: Retrieves basic PostgreSQL statistics.
  - `get_current_patch_info`: Retrieves current patch and version information.
  - `get_disk_usage`: Retrieves disk usage information.
  - `get_active_work_from_todo`: Extracts the Active Work section from `TODO.md`.
  - `get_known_issues_from_todo`: Extracts Known Issues from `TODO.md`.
  - `get_recent_git_log`: Retrieves recent Git commit logs.
  - `generate_system_state`: Generates `system-state.txt`.
  - `generate_patch_versions`: Generates `patch-versions.txt`.
  - `generate_patch_install_history`: Generates `patch-install-history.txt`.
  - `generate_claude_context`: Generates `CLAUDE_CONTEXT.md`.
  - `main`: Orchestrates the generation of all telemetry files.

#### Patterns
- **No specific design patterns**: The file primarily consists of utility functions and does not implement any specific design patterns like factory, singleton, or observer.

#### Dependencies
- **Imports**: `subprocess`, `os`, `re`, `json`, `argparse`, `datetime`, `pathlib`
- **External Commands**: `git`, `systemctl`, `psql`, `du`, `df`

#### Interfaces
- **Exposed Functions**: All top-level functions are exposed and can be called individually to gather specific system state information.
- **Main Function**: `main` is the primary entry point that orchestrates the generation of telemetry files.

#### Database
- **PostgreSQL Tables**: 
  - `pg_tables`: Used to count the number of tables in the `public` schema.
  - `get_next_patch_info`: Used to retrieve the next patch information.
- **Neo4j**: Not directly used in this file, but mentioned as an optional dependency for node counts.

#### Configuration
- **Environment Variables**: 
  - `MYTHOS_ROOT`: Root directory of the Mythos system.
- **Files**: 
  - `TODO.md`: Used to extract active work and known issues.
  - `get_next_patch_info.sh`: Script to get current patch and version information.

#### Key Logic
- **System State Collection**: Functions like `get_service_health`, `get_postgres_stats`, `get_disk_usage`, `get_current_patch_info`, and `get_git_tags` collect various system state metrics.
- **Text File Generation**: Functions like `generate_system_state`, `generate_patch_versions`, `generate_patch_install_history`, and `generate_claude_context` generate text files with the collected information.

#### Integration Points
- **Git**: Used to retrieve version tags and commit messages.
- **Systemctl**: Used to check the status of Mythos services.
- **PostgreSQL**: Used to retrieve table counts.
- **File System**: Used to read `TODO.md` and write telemetry files.
- **Shell Commands**: Used to gather disk usage and recent Git commit logs.

### Detailed Documentation

#### `run_cmd`
- **Purpose**: Executes a shell command and returns the output or a default value on failure.
- **Dependencies**: `subprocess`
- **Usage**: Used across various functions to execute shell commands.

#### `get_git_tags`
- **Purpose**: Retrieves all version tags from Git sorted by creation date.
- **Dependencies**: `run_cmd`

#### `get_patch_version_map`
- **Purpose**: Builds a mapping of patch numbers to versions from Git commit messages.
- **Dependencies**: `run_cmd`, `re`

#### `get_service_health`
- **Purpose**: Retrieves the health status of all Mythos services.
- **Dependencies**: `run_cmd`

#### `get_postgres_stats`
- **Purpose**: Retrieves basic PostgreSQL statistics, such as the number of tables.
- **Dependencies**: `run_cmd`

#### `get_current_patch_info`
- **Purpose**: Retrieves current patch and version information using a shell script.
- **Dependencies**: `run_cmd`, `json`

#### `get_disk_usage`
- **Purpose**: Retrieves disk usage information for `/opt/mythos` and the root filesystem.
- **Dependencies**: `run_cmd`

#### `get_active_work_from_todo`
- **Purpose**: Extracts the Active Work section from `TODO.md`.
- **Dependencies**: `os`, `re`

#### `get_known_issues_from_todo`
- **Purpose**: Extracts Known Issues from `TODO.md`.
- **Dependencies**: `os`, `re`

#### `get_recent_git_log`
- **Purpose**: Retrieves recent Git commit logs.
- **Dependencies**: `run_cmd`

#### `generate_system_state`
- **Purpose**: Generates `system-state.txt` with a snapshot of the current system state.
- **Dependencies**: `datetime`, `get_current_patch_info`, `get_service_health`, `get_postgres_stats`, `get_disk_usage`

#### `generate_patch_versions`
- **Purpose**: Generates `patch-versions.txt` mapping patch numbers to versions.
- **Dependencies**: `datetime`, `run_cmd`, `re`

#### `generate_patch_install_history`
- **Purpose**: Generates `patch-install-history.txt` from Git log.
- **Dependencies**: `datetime`, `run_cmd`, `re`

#### `generate_claude_context`
- **Purpose**: Generates `CLAUDE_CONTEXT.md` with system context information.
- **Dependencies**: `datetime`, `get_current_patch_info`, `get_service_health`, `get_postgres_stats`, `get_disk_usage`, `get_active_work_from_todo`, `get_known_issues_from_todo`, `get_recent_git_log`

#### `main`
- **Purpose**: Orchestrates the generation of all telemetry files.
- **Dependencies**: All other functions in the file

This file serves as a critical component of the Mythos system, providing comprehensive system state information and generating live telemetry files for monitoring and debugging purposes.
