# event_simulator/mythos_event_simulator.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 596

---

### Documentation for `event_simulator/mythos_event_simulator.py`

#### Purpose
The `EventSimulator` class simulates various system events (CPU spike, memory pressure, disk fill, service restart, process spawn) and tracks the results historically using Neo4j. The `main` function serves as the entry point for running these simulations.

#### Architecture
The `EventSimulator` class is the primary component, containing methods for initializing the simulator, connecting to Neo4j, running tests, saving results, and displaying summaries. Each test method simulates a specific system event and returns a dictionary of results. The class maintains state such as the hostname, test run ID, and results list.

#### Patterns
- **Singleton**: The `EventSimulator` class can be considered a singleton as it manages a single instance of the Neo4j connection.
- **Factory**: The `run_all_tests` method acts as a factory, orchestrating the execution of multiple test methods.

#### Dependencies
- **Standard Libraries**: `os`, `sys`, `json`, `uuid`, `psutil`, `socket`, `subprocess`, `time`, `argparse`
- **External Libraries**: `neo4j` (for Neo4j database operations)

#### Interfaces
- **Public Methods**: `run_all_tests`, `show_history`, `show_common_failures`, `cleanup`
- **Private Methods**: `_connect_neo4j`, `_save_results`, `_create_test_run_node`, `_display_summary`

#### Database
- **Neo4j Labels**: `TestRun`, `TestMachine`, `System`
- **Neo4j Relationships**: `HAD_TEST_RUN`, `TESTED_BY`

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- **Configuration Files**: None

#### Key Logic
- **Initialization**: The `__init__` method initializes the simulator with the hostname, a unique test run ID, and connects to Neo4j.
- **Test Execution**: Methods like `test_cpu_spike`, `test_memory_pressure`, `test_disk_fill`, `test_service_restart`, and `test_process_spawn` simulate specific system events and return detailed results.
- **Result Handling**: The `_save_results` method saves the test results to Neo4j, and `_display_summary` prints a summary of the test results.
- **History Management**: Methods `show_history` and `show_common_failures` retrieve and display historical test data from Neo4j.

#### Integration Points
- **Neo4j**: The simulator connects to Neo4j to save and retrieve test results.
- **System Monitoring**: The simulator interacts with the system to simulate events (CPU, memory, disk, service restart, process spawn) and uses `psutil` for system monitoring.
- **Command Line Interface**: The `main` function provides a command-line interface for running the simulator.

### Detailed Analysis

#### `EventSimulator` Class
- **Initialization (`__init__`)**: Initializes the simulator with the hostname, a unique test run ID, and connects to Neo4j.
- **Connection to Neo4j (`_connect_neo4j`)**: Establishes a connection to the Neo4j database using environment variables for URI, user, and password.
- **Running Tests (`run_all_tests`)**: Executes a series of predefined tests (CPU spike, memory pressure, disk fill, service restart, process spawn) and collects their results.
- **Saving Results (`_save_results`)**: Saves the test results to Neo4j, creating nodes and relationships for the test run and machine.
- **Displaying Summary (`_display_summary`)**: Prints a summary of the test results, including pass/fail status and events triggered.
- **Showing History (`show_history`)**: Retrieves and displays historical test data for the machine.
- **Showing Common Failures (`show_common_failures`)**: Retrieves and displays common test failures across all runs.
- **Cleanup (`cleanup`)**: Cleans up any open connections and resources.

#### Test Methods
- **CPU Spike (`test_cpu_spike`)**: Simulates high CPU usage by spawning multiple processes that consume CPU.
- **Memory Pressure (`test_memory_pressure`)**: Simulates memory pressure by allocating a significant portion of available memory.
- **Disk Fill (`test_disk_fill`)**: Simulates disk fill by creating a large temporary file.
- **Service Restart (`test_service_restart`)**: Simulates a service restart by stopping and starting a predefined service.
- **Process Spawn (`test_process_spawn`)**: Simulates multiple processes being spawned to trigger monitoring.

#### Main Function
- **Entry Point (`main`)**: Provides a command-line interface for running the `EventSimulator` and handling user input.

This documentation provides a comprehensive overview of the `EventSimulator` class and its integration with the Mythos system, detailing its purpose, architecture, dependencies, and key logic.
