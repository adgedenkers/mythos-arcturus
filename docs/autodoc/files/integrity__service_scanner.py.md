# integrity/service_scanner.py

**Language:** python
**Stream:** SYS
**Module:** Integrity Scanner
**Lines:** 228

---

### Documentation for `integrity/service_scanner.py`

#### Purpose
This file contains the logic to scan all `mythos-*` systemd services, check their health status, and merge the service information into a Neo4j graph database. It also attempts to link each service to its entry point file.

#### Architecture
The file consists of several functions that work together to achieve the scanning and merging process:
- `run_cmd`: Executes a shell command and returns the output.
- `scan_services`: The main function that orchestrates the scanning process, including finding unit files, parsing them, checking service status, and merging the information into Neo4j.
- `_find_unit_files`: Locates all `mythos-*` service unit files.
- `_parse_unit_file`: Parses a systemd unit file to extract key fields.
- `_merge_service`: Merges service information into Neo4j as `IntegrityService` nodes.
- `_link_to_entry_point`: Links a service to its entry point `IntegrityFile` node.

#### Patterns
- **Helper Functions**: The use of helper functions like `_find_unit_files`, `_parse_unit_file`, `_merge_service`, and `_link_to_entry_point` to modularize the code.
- **Singleton**: The `driver` parameter in `scan_services` is designed to be reused, implying a singleton pattern for the Neo4j driver.

#### Dependencies
- **Standard Libraries**: `os`, `re`, `logging`, `subprocess`, `datetime`
- **Custom Modules**: `integrity.graph` (for `get_driver`, `run_write`, `run_query`)

#### Interfaces
- **Public Functions**:
  - `run_cmd(cmd, default)`: Executes a shell command and returns the output.
  - `scan_services(driver=None)`: Scans all `mythos-*` services and merges them into Neo4j, returning a dictionary with statistics.
- **Private Functions**:
  - `_find_unit_files()`: Finds all `mythos-*` service unit files.
  - `_parse_unit_file(unit_name, unit_path)`: Parses a systemd unit file.
  - `_merge_service(driver, info)`: Merges service information into Neo4j.
  - `_link_to_entry_point(driver, unit_name, exec_path)`: Links a service to its entry point file.

#### Database
- **Neo4j Labels**:
  - `IntegrityService`: Represents a service node.
  - `IntegrityFile`: Represents a file node.
  - `ENTRY_POINT`: Represents the relationship between a service and its entry point file.

#### Configuration
- **Environment Variables**:
  - `MYTHOS_ROOT`: Specifies the root directory for Mythos services (default is `/opt/mythos`).

#### Key Logic
- **Service Discovery and Parsing**: The `_find_unit_files` function locates all `mythos-*` service unit files, and `_parse_unit_file` extracts relevant information from these files.
- **Health Check**: The `scan_services` function checks the active status of each service using `systemctl` commands.
- **Neo4j Integration**: The `_merge_service` function merges the parsed service information into Neo4j, and `_link_to_entry_point` links the service to its entry point file if it exists in the graph.

#### Integration Points
- **Neo4j Driver**: The `get_driver`, `run_write`, and `run_query` functions from `integrity.graph` are used to interact with the Neo4j database.
- **Systemd Integration**: The `systemctl` commands are used to check the status of the services.
- **File System**: The file system is accessed to read the content of systemd unit files.

This file is a crucial component of the Mythos system, ensuring that the integrity of the services is monitored and recorded in the Neo4j graph database.
