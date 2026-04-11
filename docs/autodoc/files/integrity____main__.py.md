# integrity/__main__.py

**Language:** python
**Stream:** SYS
**Module:** Integrity Scanner
**Lines:** 202

---

### File: `integrity/__main__.py`

#### Purpose
This file serves as the entry point for the Mythos Integrity Scanner, providing command-line interfaces for running integrity scans and displaying graph statistics.

#### Architecture
The file consists of three main functions:
1. `cmd_scan(args)`: Executes integrity scans for files, functions, tables, and services.
2. `cmd_stats(args)`: Displays current graph statistics.
3. `main()`: Parses command-line arguments and delegates to `cmd_scan` or `cmd_stats` based on the provided command.

The file imports necessary modules and uses functions from other modules (`integrity.graph`, `integrity.file_scanner`, `integrity.function_extractor`, `integrity.table_scanner`, `integrity.service_scanner`) to perform specific tasks.

#### Patterns
- **Command Pattern**: The `main` function acts as a dispatcher, invoking specific commands (`cmd_scan` or `cmd_stats`) based on user input.
- **Dependency Injection**: The `get_driver` function is used to obtain a Neo4j driver, which is passed to various scanning functions.

#### Dependencies
- Standard libraries: `argparse`, `json`, `sys`, `time`, `logging`, `os`
- Custom modules: `integrity.graph`, `integrity.file_scanner`, `integrity.function_extractor`, `integrity.table_scanner`, `integrity.service_scanner`

#### Interfaces
- Exposes command-line interfaces for:
  - `scan`: Runs integrity scans for files, functions, tables, and services.
  - `stats`: Displays current graph statistics.

#### Database
- **PostgreSQL**:
  - `datetime` table
  - `integrity` table
  - `rels` table
- **Neo4j**:
  - Nodes: `IntegrityFile`, `IntegrityDirectory`, `IntegrityFunction`, `IntegrityTable`, `IntegrityColumn`, `IntegrityDatabase`, `IntegrityService`
  - Relationships: `CONTAINS`, `IMPORTS`, `HAS_TABLE`, `HAS_COLUMN`

#### Configuration
- Environment variable: `MYTHOS_ROOT` (used to determine the root directory for writing reports)
- Logging level set to `WARNING`

#### Key Logic
- **Integrity Scan (`cmd_scan`)**:
  - Ensures Neo4j constraints.
  - Scans files, extracts functions, scans PostgreSQL tables, and scans systemd services based on user-specified options.
  - Logs detailed statistics for each scan.
  - Writes scan results to a JSON report in the `docs/live` directory.

- **Graph Statistics (`cmd_stats`)**:
  - Queries Neo4j to retrieve counts of various nodes and relationships.
  - Displays top directories by file count.
  - Calculates the percentage of functions with docstrings.

#### Integration Points
- **Neo4j Integration**: Uses `get_driver` and `run_query` from `integrity.graph` to interact with the Neo4j graph database.
- **File Scanner**: Uses `scan_files` from `integrity.file_scanner` to scan files and directories.
- **Function Extractor**: Uses `extract_functions` from `integrity.function_extractor` to extract functions from files.
- **Table Scanner**: Uses `scan_tables` from `integrity.table_scanner` to scan PostgreSQL tables.
- **Service Scanner**: Uses `scan_services` from `integrity.service_scanner` to scan systemd services.

### Summary
This file serves as the main entry point for the Mythos Integrity Scanner, providing command-line interfaces for running integrity scans and displaying graph statistics. It integrates with various subsystems to perform detailed scans and queries on the Neo4j graph database, ensuring the integrity of the Mythos system.
