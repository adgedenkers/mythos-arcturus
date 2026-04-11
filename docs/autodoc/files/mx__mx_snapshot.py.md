# mx/mx_snapshot.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 154

---

### Documentation for `mx/mx_snapshot.py`

#### Purpose
This file captures a point-in-time snapshot of the Mythos system state, including service statuses, PostgreSQL table counts and row counts, Git state, integrity scan results, and the active Ollama model. The snapshot is serialized to a JSON file.

#### Architecture
The file consists of several top-level functions that each capture a specific aspect of the system state. These functions are:
- `_run`: Executes shell commands and returns their output.
- `capture_services`: Captures the status of all `mythos-*` services.
- `capture_git`: Captures the current Git state of `/opt/mythos`.
- `capture_postgres`: Captures PostgreSQL table counts and row counts for key tables.
- `capture_ollama_model`: Captures the currently active Ollama model.
- `capture_integrity`: Captures the latest integrity scan results.
- `take_snapshot`: Combines all the captured data into a single snapshot and writes it to a JSON file.
- `load_snapshot`: Loads a previously captured snapshot from a JSON file.
- `pg`: A helper function to execute PostgreSQL queries.

#### Patterns
- **Helper Function**: `_run` is a helper function used by other functions to execute shell commands.
- **Data Aggregation**: `take_snapshot` aggregates data from multiple sources into a single snapshot.

#### Dependencies
- `json`: For JSON serialization and deserialization.
- `os`: For interacting with the operating system.
- `subprocess`: For executing shell commands.
- `datetime`: For timestamp generation.
- `pathlib`: For path manipulation.

#### Interfaces
- `capture_services()`: Returns a dictionary of service statuses.
- `capture_git()`: Returns a dictionary of Git state.
- `capture_postgres()`: Returns a dictionary of PostgreSQL table counts and row counts.
- `capture_ollama_model()`: Returns the currently active Ollama model.
- `capture_integrity()`: Returns a dictionary of integrity scan results.
- `take_snapshot(trigger: str, label: str)`: Captures a full system state snapshot and returns the path to the JSON file.
- `load_snapshot(path: str)`: Loads a snapshot from a JSON file and returns it as a dictionary.

#### Database
- **PostgreSQL**:
  - `information_schema.tables`: Used to get the count of tables in the `public` schema.
  - Key tables: `transactions`, `recurring_bills`, `accounts`, `people`, `chat_messages`, `life_events`, `routines`, `calendar_events`: Used to get row counts for these tables.

#### Configuration
- `SNAPSHOT_DIR`: Path to the directory where snapshots are stored (`~/.mx/snapshots`).
- `INTEGRITY_REPORT`: Path to the latest integrity scan report (`/opt/mythos/docs/live/integrity-scan-latest.json`).
- `MYTHOS_ROOT`: Root directory of the Mythos system (`/opt/mythos`).

#### Key Logic
- **Service Status Capture**: Uses `systemctl` to list all `mythos-*` services and determine their active/inactive status.
- **Git State Capture**: Uses `git` commands to capture the current Git state, including hash, message, clean/dirty status, and branch.
- **PostgreSQL Table Counts and Row Counts**: Executes PostgreSQL queries to get the count of tables and row counts for key tables.
- **Ollama Model Capture**: Reads an override file to get the active Ollama model, falling back to a default model if no override is found.
- **Integrity Scan Results**: Reads the latest integrity scan report and extracts summary statistics.

#### Integration Points
- **mx_hooks.py**: Invokes the integrity scanner pre/post operation, which generates the report read by `capture_integrity`.
- **System Services**: Captures the status of all `mythos-*` services.
- **PostgreSQL**: Captures table counts and row counts for key tables.
- **Git**: Captures the current state of the Git repository.
- **Ollama**: Captures the currently active model.
- **Integrity Scanner**: Reads the latest scan report to capture system integrity status.
