# iris/introspection/manifest.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 115

---

### Documentation for `iris/introspection/manifest.py`

#### Purpose
This file manages the creation, completion, and storage of introspection runs and their associated file metadata in the Mythos system's PostgreSQL database.

#### Architecture
The file consists of four main functions:
1. `get_connection`: Establishes a connection to the PostgreSQL database.
2. `create_run`: Creates a new record in the `introspection_runs` table and returns the `run_id`.
3. `finish_run`: Updates the `introspection_runs` table with final statistics and status for a completed run.
4. `write_manifest`: Bulk-inserts file metadata into the `system_manifest` table.

Each function is designed to handle specific database operations related to introspection runs and their associated metadata.

#### Patterns
- **Singleton**: The `get_connection` function can be considered a singleton pattern for database connections, although it does not enforce a single instance.
- **DAO (Data Access Object)**: The functions act as a DAO, abstracting database operations and providing a clean interface for other parts of the system to interact with the database.

#### Dependencies
- `json`: For handling JSON serialization and deserialization.
- `logging`: For logging messages.
- `psycopg2`: For PostgreSQL database operations.

#### Interfaces
- `get_connection()`: Returns a PostgreSQL database connection.
- `create_run(conn, mode, target_path)`: Creates a new run record and returns the `run_id`.
- `finish_run(conn, run_id, stats, status, error_message, report)`: Updates the run record with final stats.
- `write_manifest(conn, run_id, file_list)`: Bulk-inserts file metadata into the `system_manifest` table.

#### Database
- **Tables**:
  - `introspection_runs`: Used for creating and updating run records.
  - `system_manifest`: Used for storing file metadata.

#### Configuration
- `DB_NAME`: The name of the PostgreSQL database, set to `"mythos"`.

#### Key Logic
- **`create_run`**: Inserts a new record into the `introspection_runs` table and returns the `run_id`.
- **`finish_run`**: Updates the `introspection_runs` table with final statistics, status, and optional error messages and reports.
- **`write_manifest`**: Bulk-inserts file metadata into the `system_manifest` table using `execute_values` for efficient batch insertion.

#### Integration Points
- **Mythos System**: This module integrates with the Mythos system by providing database operations for introspection runs and their associated file metadata.
- **Logging**: Uses the `logging` module to log important events such as run creation and completion.
- **Database Connection**: Utilizes `psycopg2` to interact with the PostgreSQL database, ensuring that all database operations are performed within the context of a connection.

### Summary
The `manifest.py` file is a critical component of the Mythos system, responsible for managing the lifecycle of introspection runs and storing their metadata in the PostgreSQL database. It provides a clean interface for creating, updating, and storing run data, ensuring that the system can efficiently track and report on introspection activities.
