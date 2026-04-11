# iris/integrity/iris_integrity.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 225

---

### Documentation for `iris/integrity/iris_integrity.py`

#### Purpose
This file contains functions for running integrity scans, reading scan results, and building health summaries for the Mythos system. It provides the core functionality for Iris to monitor and report on the health of the system.

#### Architecture
The file is structured around several top-level functions, each handling a specific aspect of the integrity and health monitoring process:
- `run_integrity_scan`: Runs the integrity scanner and returns parsed results.
- `read_latest_integrity_report`: Reads the latest integrity scan result from disk.
- `read_recent_session_deltas`: Reads recent session journals and extracts delta information.
- `read_recent_snapshots`: Reads the most recent pre/post snapshot pairs.
- `build_health_summary`: Builds a comprehensive health summary for Iris's self-model.
- `format_telegram_report`: Formats a health summary for Telegram.
- `format_iris_context`: Formats a brief health context string for Iris's system prompt.

#### Patterns
- **No explicit design patterns**: The functions are straightforward and do not follow any specific design patterns like factory, singleton, or observer.

#### Dependencies
- **Imports**: `json`, `os`, `subprocess`, `datetime`, `pathlib`
- **Environment Variables**: `MYTHOS_ROOT` (root directory for Mythos)
- **External Commands**: Uses `subprocess` to run the integrity scanner.

#### Interfaces
- **Exposed Functions**:
  - `run_integrity_scan(fast: bool = True) -> dict`
  - `read_latest_integrity_report() -> dict`
  - `read_recent_session_deltas(max_sessions: int = 5) -> list[dict]`
  - `read_recent_snapshots(max_snapshots: int = 2) -> list[dict]`
  - `build_health_summary() -> dict`
  - `format_telegram_report(health: dict) -> str`
  - `format_iris_context(health: dict) -> str`

#### Database
- **PostgreSQL Tables**: `datetime`, `pathlib`, `disk`, `file`, `health`, `Iris`
- **Data Access**: The file does not directly interact with the database but relies on data that is likely stored in these tables.

#### Configuration
- **Environment Variables**: `MYTHOS_ROOT` (used to set the root directory for Mythos)
- **File Paths**: `INTEGRITY_REPORT`, `SNAPSHOT_DIR`, `JOURNAL_DIR`, `PYTHON`

#### Key Logic
- **Integrity Scan Execution**: The `run_integrity_scan` function runs the integrity scanner and captures the output. It handles both fast and full scans.
- **Health Summary Construction**: The `build_health_summary` function aggregates data from the latest integrity report, recent session deltas, and snapshots to build a comprehensive health summary.
- **Formatting Reports**: The `format_telegram_report` and `format_iris_context` functions format the health summary for different contexts (Telegram and Iris's system prompt).

#### Integration Points
- **Integrity Scanner**: The `run_integrity_scan` function integrates with the integrity scanner via `subprocess`.
- **Data Sources**: The functions read data from disk (integrity reports, session journals, snapshots).
- **Health Reporting**: The `build_health_summary` function integrates with other subsystems to gather health data.
- **Reporting Interfaces**: The `format_telegram_report` and `format_iris_context` functions format the health summary for different reporting interfaces (Telegram and Iris's system prompt).

### Detailed Breakdown of Functions

1. **`run_integrity_scan(fast: bool = True) -> dict`**
   - **Purpose**: Runs the integrity scanner and returns parsed results.
   - **Logic**: Uses `subprocess` to run the scanner and captures the output. If `fast` is `True`, it performs a faster scan focusing on services and tables.

2. **`read_latest_integrity_report() -> dict`**
   - **Purpose**: Reads the latest integrity scan result from disk.
   - **Logic**: Reads the JSON file containing the latest scan results and parses it.

3. **`read_recent_session_deltas(max_sessions: int = 5) -> list[dict]`**
   - **Purpose**: Reads recent session journals and extracts delta information.
   - **Logic**: Reads the most recent session journals and extracts relevant delta information.

4. **`read_recent_snapshots(max_snapshots: int = 2) -> list[dict]`**
   - **Purpose**: Reads the most recent pre/post snapshot pairs.
   - **Logic**: Reads the most recent snapshot files and parses them.

5. **`build_health_summary() -> dict`**
   - **Purpose**: Builds a comprehensive health summary for Iris's self-model.
   - **Logic**: Aggregates data from the latest integrity report, recent session deltas, and snapshots to build a health summary.

6. **`format_telegram_report(health: dict) -> str`**
   - **Purpose**: Formats a health summary for Telegram.
   - **Logic**: Formats the health summary into a string suitable for Telegram messages.

7. **`format_iris_context(health: dict) -> str`**
   - **Purpose**: Formats a brief health context string for Iris's system prompt.
   - **Logic**: Formats the health summary into a brief string for Iris's system prompt.

This file is crucial for maintaining the integrity and health awareness of the Mythos system, ensuring that Iris can monitor and report on the system's state effectively.
