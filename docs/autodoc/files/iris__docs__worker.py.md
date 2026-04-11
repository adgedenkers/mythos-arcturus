# iris/docs/worker.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 140

---

### File: `iris/docs/worker.py`

#### Purpose
This file contains the core logic for a documentation worker that polls Redis queues, dispatches tasks to appropriate handlers, and tracks the progress and status of these tasks in a PostgreSQL database.

#### Architecture
The file consists of several top-level functions:
- `_signal_handler`: Handles shutdown signals.
- `task_hash`: Generates a hash for a given task.
- `run_worker`: The main entry point for the worker, which processes tasks from Redis queues.
- `_create_worker_run`: Creates a new worker run record in the PostgreSQL database.
- `_finish_worker_run`: Updates the worker run record with the final status and statistics.

The worker uses Redis for task queuing and PostgreSQL for tracking the worker's progress and status.

#### Patterns
- **Singleton**: The worker uses a global `_shutdown` flag to manage the shutdown state.
- **Observer**: The worker observes Redis queues for new tasks.

#### Dependencies
- `os`, `json`, `time`, `hashlib`, `logging`, `signal`: Standard Python libraries for various utilities.
- `psycopg2`: PostgreSQL database adapter.
- `redis_lib`: Redis client library.
- `iris.docs.handlers`: Handlers for different types of documentation tasks.

#### Interfaces
- `run_worker(mode, queue_filter, dry_run)`: The main entry point for the worker, which starts the task processing loop.
- `_create_worker_run(conn, mode, queue_filter)`: Creates a new worker run record in the PostgreSQL database.
- `_finish_worker_run(conn, run_id, processed, failed, docs, status, error)`: Updates the worker run record with the final status and statistics.

#### Database
- **Tables/Lables**:
  - `doc_worker_runs`: Tracks the progress and status of worker runs.
  - `worker`: (Not explicitly used in the provided code but referenced in the DB references list).

#### Configuration
- Environment variables or configuration files are not explicitly used in the provided code. However, the PostgreSQL and Redis connections rely on default settings or environment configurations.

#### Key Logic
- **Task Processing Loop**: The `run_worker` function continuously polls Redis queues for tasks and processes them using the appropriate handler.
- **Task Deduplication**: Uses Redis sets to track processing and completed tasks to avoid duplicates.
- **Worker Run Tracking**: Uses PostgreSQL to log the start and end of worker runs, including statistics on processed and failed tasks.

#### Integration Points
- **Redis Queues**: The worker polls Redis queues to get tasks. The queues are named based on the type of documentation task (e.g., `iris:docs:queue:component`).
- **PostgreSQL**: The worker logs the start and end of runs in the `doc_worker_runs` table, including statistics on processed and failed tasks.
- **Task Handlers**: The worker dispatches tasks to handlers defined in `iris/docs/handlers` based on the queue from which the task was retrieved.

### Detailed Analysis

#### `_signal_handler(signum, frame)`
- **Purpose**: Handles shutdown signals (SIGTERM, SIGINT) by setting a global `_shutdown` flag to `True`.
- **Dependencies**: `logging` for logging the shutdown signal.

#### `task_hash(task)`
- **Purpose**: Generates a hash for a given task using SHA-256.
- **Dependencies**: `hashlib` for hashing and `json` for serializing the task.

#### `run_worker(mode, queue_filter, dry_run)`
- **Purpose**: Main entry point for the worker, which processes tasks from Redis queues.
- **Dependencies**: `redis_lib` for Redis operations, `psycopg2` for PostgreSQL operations, and `iris/docs/handlers` for task handlers.
- **Key Logic**:
  - Sets up signal handlers for graceful shutdown.
  - Connects to Redis and PostgreSQL.
  - Creates a new worker run record in PostgreSQL.
  - Continuously polls Redis queues for tasks.
  - Dispatches tasks to appropriate handlers based on the queue.
  - Tracks task progress and updates Redis and PostgreSQL accordingly.
  - Logs task processing and completion.

#### `_create_worker_run(conn, mode, queue_filter)`
- **Purpose**: Creates a new worker run record in the PostgreSQL database.
- **Dependencies**: `psycopg2` for database operations.
- **Key Logic**:
  - Inserts a new record into the `doc_worker_runs` table with the mode and queue filter.
  - Returns the `run_id` of the new record.

#### `_finish_worker_run(conn, run_id, processed, failed, docs, status, error)`
- **Purpose**: Updates the worker run record with the final status and statistics.
- **Dependencies**: `psycopg2` for database operations.
- **Key Logic**:
  - Updates the `doc_worker_runs` table with the final status, number of processed and failed tasks, and any error message.
  - Logs any exceptions that occur during the update.

### Summary
The `worker.py` file is a critical component of the Mythos system, responsible for processing documentation tasks from Redis queues and tracking the progress and status of these tasks in a PostgreSQL database. It integrates with Redis for task queuing and PostgreSQL for task tracking, and it uses task-specific handlers to process different types of documentation tasks.
