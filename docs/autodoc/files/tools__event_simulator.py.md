# tools/event_simulator.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 596

---

### File: tools/event_simulator.py

#### Purpose
This file contains the `EventSimulator` class, which simulates various system events (CPU spike, memory pressure, disk fill, service restart, and process spawn) and tracks the test results historically per machine using Neo4j.

#### Architecture
The `EventSimulator` class is designed to manage the simulation of system events and the tracking of test results. It includes methods for initializing the simulator, connecting to Neo4j, running tests, saving results, and displaying summaries. The class has a main entry point function `main` to orchestrate the execution of tests.

#### Patterns
- **Singleton**: The `EventSimulator` class can be considered as a singleton since it manages a single instance of the Neo4j driver and test run.
- **Factory**: The `run_all_tests` method acts as a factory, orchestrating the execution of various test methods.

#### Dependencies
- **Standard Libraries**: `os`, `sys`, `json`, `uuid`, `psutil`, `socket`, `subprocess`, `time`, `argparse`
- **External Libraries**: `neo4j` (for Neo4j database operations)
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

#### Interfaces
- **Public Methods**: `run_all_tests`, `show_history`, `show_common_failures`, `cleanup`
- **Internal Methods**: `_connect_neo4j`, `_save_results`, `_create_test_run_node`, `_display_summary`

#### Database
- **Neo4j Labels**: `TestRun`, `TestMachine`, `System`
- **Neo4j Relationships**: `HAD_TEST_RUN`, `TESTED_BY`

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- **Configuration Files**: None

#### Key Logic
- **Test Execution**: The `run_all_tests` method orchestrates the execution of various tests (`test_cpu_spike`, `test_memory_pressure`, `test_disk_fill`, `test_service_restart`, `test_process_spawn`).
- **Result Saving**: The `_save_results` method saves the test results to Neo4j.
- **Summary Display**: The `_display_summary` method displays a summary of the test results.

#### Integration Points
- **Neo4j**: The `EventSimulator` class connects to Neo4j to save test results and retrieve historical data.
- **System Monitoring**: The class interacts with the system to simulate events (CPU spike, memory pressure, disk fill, service restart, process spawn) and monitor the system's response.

### Detailed Analysis

#### Classes
- **EventSimulator**
  - **Purpose**: Manages the simulation of system events and tracks test results.
  - **Methods**:
    - `__init__`: Initializes the simulator with a unique test run ID and connects to Neo4j.
    - `_connect_neo4j`: Connects to the Neo4j database using environment variables.
    - `run_all_tests`: Runs all event simulation tests and saves results.
    - `test_cpu_spike`: Simulates high CPU usage.
    - `test_memory_pressure`: Simulates memory pressure.
    - `test_disk_fill`: Simulates disk fill using temporary files.
    - `test_service_restart`: Tests service restart by restarting a safe service.
    - `test_process_spawn`: Spawns multiple processes to trigger monitoring.
    - `_save_results`: Saves test results to Neo4j.
    - `_create_test_run_node`: Creates a test run node in Neo4j.
    - `_display_summary`: Displays a summary of the test results.
    - `show_history`: Shows test history for the machine.
    - `show_common_failures`: Shows common test failures across all runs.
    - `cleanup`: Cleans up connections and resources.

#### Top-level Functions
- **main**: Main entry point to run the event simulator.
- **__init__**: Placeholder for the class initializer.
- **_connect_neo4j**: Connects to Neo4j.
- **run_all_tests**: Runs all event simulation tests.
- **test_cpu_spike**: Simulates high CPU usage.
- **test_memory_pressure**: Simulates memory pressure.
- **test_disk_fill**: Simulates disk fill using temporary files.
- **test_service_restart**: Tests service restart by restarting a safe service.
- **test_process_spawn**: Spawns multiple processes to trigger monitoring.
- **_save_results**: Saves test results to Neo4j.
- **_create_test_run_node**: Creates a test run node in Neo4j.
- **_display_summary**: Displays a summary of the test results.
- **show_history**: Shows test history for the machine.
- **show_common_failures**: Shows common test failures across all runs.
- **cleanup**: Cleans up connections and resources.

#### Key Logic
- **Test Execution**: The `run_all_tests` method orchestrates the execution of various tests by calling methods like `test_cpu_spike`, `test_memory_pressure`, etc.
- **Result Saving**: The `_save_results` method saves the test results to Neo4j by creating nodes and relationships.
- **Summary Display**: The `_display_summary` method prints a summary of the test results, including success status, events triggered, and any errors.

#### Integration Points
- **Neo4j**: The `EventSimulator` class connects to Neo4j to save test results and retrieve historical data.
- **System Monitoring**: The class interacts with the system to simulate events and monitor the system's response, using libraries like `psutil` and `subprocess`.

This file is crucial for testing and validating the Mythos system's monitoring capabilities by simulating various system events and tracking their outcomes.
