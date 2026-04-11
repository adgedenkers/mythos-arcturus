# graph_logging/src/system_monitor.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 352

---

### File: `graph_logging/src/system_monitor.py`

#### Purpose
This file contains the `SystemMonitor` class, which is responsible for continuously monitoring system metrics (CPU, memory, disk, processes, and services) and logging events to a Neo4j graph database.

#### Architecture
The `SystemMonitor` class is the main component of this file. It contains several methods to handle initialization, configuration loading, logging setup, signal handling, and monitoring cycles. The class is designed to run in a loop, checking various system metrics at regular intervals and logging any significant events.

#### Patterns
- **Singleton**: The `SystemMonitor` class can be considered a singleton as it is intended to have a single instance running the monitoring loop.
- **Observer**: The class observes system metrics and logs changes to the Neo4j graph database.

#### Dependencies
- **Imports**: `os`, `sys`, `time`, `signal`, `logging`, `yaml`, `psutil`, `subprocess`, `re`, `pathlib`, `typing`, `datetime`, `event_logger`
- **External Libraries**: `psutil` for system monitoring, `subprocess` for running shell commands, `yaml` for configuration file parsing.

#### Interfaces
- **Public Methods**:
  - `__init__(self, config_path: str)`: Initializes the monitor with a configuration file path.
  - `start(self)`: Starts the monitoring loop.
  - `main()`: The main entry point for the script.

#### Database
- **Neo4j**: The `SystemMonitor` class interacts with Neo4j to log events and system states.
  - **Tables/Labels**: The specific Neo4j labels and relationships used are not explicitly defined in the code but are inferred from the `event_logger` interactions.

#### Configuration
- **Config File**: The configuration is loaded from a YAML file specified by `config_path`.
- **Environment Variables**: Environment variables are expanded in the configuration using `_expand_env_vars`.

#### Key Logic
- **Monitoring Loop**: The `_monitor_cycle` method checks CPU, memory, disk, processes, and services, logging any significant events.
- **Event Logging**: Significant events (e.g., high CPU usage, service failures) are logged to Neo4j using the `event_logger`.
- **Graceful Shutdown**: Signal handlers (`_signal_handler`) ensure the monitoring loop can be stopped gracefully.

#### Integration Points
- **Event Logger**: The `SystemMonitor` class uses `EventLoggerFactory` to connect to Neo4j and log events.
- **System Metrics**: The class uses `psutil` to gather system metrics and `subprocess` to check systemd services.

### Detailed Breakdown of Methods

1. **`__init__(self, config_path: str)`**:
   - Initializes the monitor with a configuration file path.
   - Loads the configuration and expands environment variables.
   - Sets up logging and signal handlers for graceful shutdown.

2. **`_load_config(self) -> Dict`**:
   - Loads the configuration from a YAML file and returns it as a dictionary.
   - Expands environment variables within the configuration.

3. **`_expand_env_vars(self, obj)`**:
   - Recursively expands environment variables in the configuration.

4. **`_setup_logging(self) -> logging.Logger`**:
   - Sets up logging to a file and console based on the configuration.

5. **`_signal_handler(self, signum, frame)`**:
   - Handles shutdown signals (SIGTERM, SIGINT) to stop the monitoring loop gracefully.

6. **`start(self)`**:
   - Starts the monitoring loop.
   - Connects to Neo4j and runs the monitoring loop at a specified interval.
   - Calls `_monitor_cycle` in a loop until interrupted.

7. **`_monitor_cycle(self)`**:
   - Executes a single monitoring cycle, calling methods to check CPU, memory, disk, processes, and services.

8. **`_check_cpu(self)`**:
   - Checks CPU usage and logs a warning if it exceeds the threshold.

9. **`_check_memory(self)`**:
   - Checks memory usage and logs a warning if it exceeds the threshold.

10. **`_check_disk(self)`**:
    - Checks disk usage and logs a warning if it exceeds the threshold.

11. **`_check_processes(self)`**:
    - Checks running processes for high resource usage and logs significant events.

12. **`_check_services(self)`**:
    - Checks systemd services and handles wildcard patterns.

13. **`_check_single_service(self, service_name: str)`**:
    - Checks the status of a single systemd service and logs state changes.

14. **`_check_service_pattern(self, pattern: str)`**:
    - Checks services matching a wildcard pattern.

15. **`_cleanup(self)`**:
    - Cleans up resources on shutdown.

16. **`main()`**:
    - The main entry point for the script, typically used to start the `SystemMonitor`.

This file is a critical component of the Mythos system, ensuring continuous monitoring and logging of system health and performance.
