# graph_logging/scripts/cleanup_old_events.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 125

---

### File: `graph_logging/scripts/cleanup_old_events.py`

#### Purpose
This script is designed to remove old events, metric snapshots, and orphaned process nodes from a Neo4j database based on a specified retention period.

#### Architecture
The script consists of two main functions:
1. `cleanup_old_events(retention_days)`: This function handles the core logic of identifying and deleting old events, metric snapshots, and orphaned process nodes.
2. `main()`: This function serves as the entry point of the script, setting up the retention period and calling `cleanup_old_events`.

#### Patterns
- **Singleton**: The script uses a single instance of the Neo4j driver, which is a common pattern for database connections.
- **Dependency Injection**: The retention period is passed as an argument to `cleanup_old_events`, allowing for flexibility in how it is determined (e.g., from environment variables).

#### Dependencies
- `os`: Used to access environment variables.
- `sys`: Used to exit the script with a status code.
- `logging`: Used for logging information and errors.
- `datetime`: Used to calculate the retention period.
- `pathlib`: Used to ensure the log file directory exists.
- `neo4j`: Used to connect to and interact with the Neo4j database.

#### Interfaces
- `cleanup_old_events(retention_days: int)`: Exposes a function to delete old events, metric snapshots, and orphaned process nodes based on the retention period.
- `main()`: Serves as the main entry point for the script, setting up the retention period and calling `cleanup_old_events`.

#### Database
- **Neo4j**:
  - **Labels**:
    - `Event`: Nodes representing events.
    - `Metric`: Nodes representing metric snapshots.
    - `Process`: Nodes representing processes.
  - **Properties**:
    - `timestamp`: Used to determine the age of the event or metric snapshot.
    - `last_seen`: Used to determine the age of a process node.

#### Configuration
- Environment Variables:
  - `NEO4J_URI`: The URI for connecting to the Neo4J database.
  - `NEO4J_USER`: The username for the Neo4J database.
  - `NEO4J_PASSWORD`: The password for the Neo4J database.
  - `EVENT_RETENTION_DAYS`: The number of days to retain events (default is 10).

#### Key Logic
1. **Connection Setup**: Establishes a connection to the Neo4j database using environment variables.
2. **Event Cleanup**:
   - Queries the database to count and delete events older than the retention period.
   - Logs the number of events deleted.
3. **Metric Cleanup**:
   - Queries the database to count and delete metric snapshots older than the retention period.
   - Logs the number of metric snapshots deleted.
4. **Process Cleanup**:
   - Queries the database to count and delete process nodes that have not been seen in 7 days.
   - Logs the number of process nodes deleted.
5. **Logging**: Uses the `logging` module to log information and errors to both a file and the console.

#### Integration Points
- **Environment Variables**: The script integrates with the environment to retrieve configuration details such as database connection information and retention period.
- **Neo4j Database**: The script interacts with the Neo4j database to perform cleanup operations on events, metric snapshots, and process nodes.
- **Logging**: The script logs its operations to a file and the console, which can be integrated with other logging systems or monitoring tools.

### Summary
The `cleanup_old_events.py` script is a critical component of the Mythos system, ensuring that the Neo4j database does not accumulate unnecessary data by removing old events, metric snapshots, and orphaned process nodes based on a configurable retention period. It uses environment variables for configuration, logs its operations, and interacts with the Neo4j database to perform the cleanup.
