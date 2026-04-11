# graph_logging/src/event_logger.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 275

---

### Documentation for `event_logger.py`

#### Purpose
The `event_logger.py` file provides a logging mechanism for system events, metrics, and states to a Neo4j graph database. It includes a factory to manage the creation and lifecycle of `EventLogger` instances using a singleton pattern.

#### Architecture
- **Classes**:
  - `EventLogger`: Manages the connection to Neo4j and provides methods to log events, metrics, and system states.
  - `EventLoggerFactory`: A factory class that uses the singleton pattern to manage the lifecycle of `EventLogger` instances.
- **Methods**:
  - `EventLogger`:
    - `__init__`: Initializes the Neo4j connection.
    - `_connect`: Establishes the Neo4j connection.
    - `close`: Closes the Neo4j connection.
    - `log_event`: Logs an event to the Neo4j graph.
    - `_create_event_tx`: Creates an event node and links causality.
    - `_link_causality`: Links the event to recent events that may have caused it.
    - `log_metric`: Logs a simple metric.
    - `_create_metric_tx`: Creates a metric snapshot.
    - `log_process_state`: Logs the current state of a process.
    - `_update_process_tx`: Updates or creates a process node.
    - `log_service_state`: Logs the state of a systemd service.
    - `_update_service_tx`: Updates or creates a service node.
    - `get_recent_events`: Retrieves recent events from the graph.
    - `trace_causality`: Traces the causal chain for an event.
  - `EventLoggerFactory`:
    - `get_logger`: Gets or creates an `EventLogger` instance.
    - `close_logger`: Closes the logger connection.

#### Patterns
- **Singleton Pattern**: The `EventLoggerFactory` class uses the singleton pattern to ensure that only one instance of `EventLogger` is created and reused.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `json`: For JSON operations.
  - `uuid`: For generating unique identifiers.
  - `datetime`: For handling timestamps.
  - `typing`: For type hints.
  - `neo4j`: For Neo4j database operations.
  - `neo4j.exceptions`: For handling Neo4j exceptions.

#### Interfaces
- **Public Methods**:
  - `EventLogger`:
    - `log_event(event_type: str, data: Dict[str, Any]) -> str`: Logs an event and returns the event ID.
    - `log_metric(metric_type: str, value: float, unit: str = "")`: Logs a metric.
    - `log_process_state(pid: int, name: str, memory_mb: float, cpu_percent: float)`: Logs the state of a process.
    - `log_service_state(service_name: str, status: str, substate: str = "")`: Logs the state of a service.
    - `get_recent_events(minutes: int = 5, event_type: Optional[str] = None) -> List[Dict]`: Retrieves recent events.
    - `trace_causality(event_id: str) -> List[Dict]`: Traces the causal chain for an event.
  - `EventLoggerFactory`:
    - `get_logger(uri: str = None, user: str = None, password: str = None) -> EventLogger`: Gets or creates an `EventLogger` instance.
    - `close_logger()`: Closes the logger connection.

#### Database
- **Neo4j Labels and Relationships**:
  - **Labels**:
    - `Event`: Represents system events.
    - `Metric`: Represents system metrics.
    - `Process`: Represents system processes.
    - `Service`: Represents systemd services.
    - `System`: Represents the system (e.g., localhost).
  - **Relationships**:
    - `LOGGED`: Links a system to an event.
    - `MAY_HAVE_CAUSED`: Links events based on causality.
    - `HAS_METRIC`: Links a system to a metric.
    - `RUNS`: Links a system to a process.
    - `RUNS_SERVICE`: Links a system to a service.

#### Configuration
- **Environment Variables**:
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for the Neo4j database.
  - `NEO4J_PASSWORD`: Password for the Neo4j database.

#### Key Logic
- **Event Logging**:
  - The `log_event` method logs an event to the Neo4j graph and automatically links it to recent events that may have caused it.
  - The `_link_causality` method determines potential causes based on predefined causal relationships and links them to the event.
- **Metric Logging**:
  - The `log_metric` method logs a simple metric and associates it with the system.
- **State Logging**:
  - The `log_process_state` and `log_service_state` methods log the current state of processes and services, respectively.
- **Causal Chain Tracing**:
  - The `trace_causality` method traces the causal chain for a given event, returning a list of events in the causal chain.

#### Integration Points
- **Mythos Subsystems**:
  - This module integrates with the Mythos system by logging events, metrics, and states to the Neo4j graph database. It can be used by other subsystems to log system activities and retrieve historical data for analysis.
