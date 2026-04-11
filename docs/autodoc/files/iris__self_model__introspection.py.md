# iris/self_model/introspection.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 418

---

### File: iris/self_model/introspection.py

#### Purpose
This file contains functions for introspection and self-awareness within the Mythos system, specifically for the Iris subsystem. It loads the capabilities configuration, gathers system vitals, checks the health of capabilities, and generates self-reflections using the 9-layer Arcturian Grid.

#### Architecture
The file consists of several top-level functions that perform specific introspection tasks:
- `load_capabilities`: Loads the capabilities configuration from a YAML file.
- `get_system_vitals`: Gathers core metrics from the Neo4j graph database.
- `get_disk_vitals`: Retrieves disk and system resource information using shell commands.
- `get_capability_health`: Checks the health of each capability by verifying its dependencies.
- `generate_reflection`: Generates a comprehensive self-reflection based on the 9-layer Arcturian Grid.
- `generate_brief_status`: Generates a brief self-status report.
- `run_cmd`: Executes shell commands and captures their output.

#### Patterns
- **Singleton Pattern**: The `get_driver` function from `integrity.graph` is used to obtain a Neo4j driver, which is a singleton pattern to ensure a single instance of the driver.
- **Factory Pattern**: The `load_capabilities` function can be seen as a factory method that produces a dictionary of capabilities.

#### Dependencies
- **Imports**: `os`, `yaml`, `logging`, `subprocess`, `datetime`, `pathlib`, `integrity.graph`
- **External Services**: Neo4j graph database, PostgreSQL database, shell commands for system information

#### Interfaces
- **Exposed Functions**:
  - `load_capabilities()`: Loads the capabilities configuration.
  - `get_system_vitals(driver=None)`: Gathers system vitals.
  - `get_disk_vitals()`: Retrieves disk and system resource information.
  - `get_capability_health(driver=None)`: Checks the health of each capability.
  - `generate_reflection(driver=None)`: Generates a comprehensive self-reflection.
  - `generate_brief_status(driver=None)`: Generates a brief self-status report.
  - `run_cmd(cmd)`: Executes shell commands.

#### Database
- **Neo4j Labels**:
  - `IntegrityFile`
  - `IntegrityFunction`
  - `IntegrityService`
  - `IntegrityTable`
  - `IntegrityColumn`
  - `IntegrityDirectory`
  - `IMPORTS`
- **PostgreSQL Tables**:
  - `datetime`
  - `pathlib`
  - `integrity`
  - `the`
  - `expected`
  - `but`

#### Configuration
- **Environment Variables**:
  - `MYTHOS_ROOT`: Path to the root directory of the Mythos system.
- **Files**:
  - `capabilities.yaml`: Configuration file for capabilities.

#### Key Logic
- **`load_capabilities`**: Loads the `capabilities.yaml` file and returns its contents as a dictionary.
- **`get_system_vitals`**: Executes multiple Neo4j queries to gather various metrics such as file counts, function counts, service statuses, and more.
- **`get_disk_vitals`**: Uses shell commands to retrieve disk usage, memory usage, GPU status, and system uptime.
- **`get_capability_health`**: Loads capabilities and checks the health of each capability by verifying its dependencies against the Neo4j graph.
- **`generate_reflection`**: Combines the results from `get_system_vitals`, `get_disk_vitals`, and `get_capability_health` to generate a comprehensive self-reflection based on the 9-layer Arcturian Grid.

#### Integration Points
- **Neo4j**: The file interacts with the Neo4j graph database to gather system vitals and capability health information.
- **PostgreSQL**: The file indirectly references PostgreSQL tables, though the specific interactions are not detailed in the provided code.
- **Shell Commands**: The file uses shell commands to gather system resource information.
- **Capabilities Configuration**: The file loads and processes the `capabilities.yaml` file to understand the system's capabilities and their dependencies.

### Summary
The `introspection.py` file is a critical component of the Mythos system, enabling self-awareness and introspection through various metrics and reflections. It integrates with Neo4j and PostgreSQL databases, processes configuration files, and executes shell commands to gather comprehensive system information.
