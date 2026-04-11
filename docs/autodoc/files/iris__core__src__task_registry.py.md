# iris/core/src/task_registry.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 793

---

### File: `iris/core/src/task_registry.py`

#### Purpose
This file manages background tasks for the Mythos system, providing a registry to initialize, schedule, and execute tasks based on their priority and cooldown periods. It includes a base class `BackgroundTask` and several specific task implementations.

#### Architecture
The file is structured around a registry (`TaskRegistry`) and a base class (`BackgroundTask`). The `TaskRegistry` manages task initialization, scheduling, and execution. The `BackgroundTask` class defines the interface for all tasks, with specific tasks inheriting from it and implementing the required methods.

#### Patterns
- **Abstract Base Class (ABC)**: Used for `BackgroundTask` to enforce method implementations in subclasses.
- **Factory Method**: `TaskRegistry` uses factory-like methods to register and initialize tasks.

#### Dependencies
- **Standard Libraries**: `asyncio`, `logging`, `os`, `json`, `time`, `subprocess`, `sys`
- **External Libraries**: `psycopg2`, `redis`, `neo4j`
- **Internal Modules**: `iris/core/src/task_registry.py` (self-referential for internal classes)

#### Interfaces
- **TaskRegistry**:
  - `initialize()`: Initializes the task registry by loading history and registering built-in tasks.
  - `register(task)`: Registers a new task at runtime.
  - `next_task(current_mode)`: Returns the next task to be executed based on the current mode.
  - `record_result(task, result)`: Records the result of a task execution.
- **BackgroundTask**:
  - `should_run()`: Determines if the task should run based on cooldown and other conditions.
  - `execute()`: Executes the task and returns a `TaskResult`.

#### Database
- **PostgreSQL**:
  - `iris_task_log`: Used to log task execution history and status.
- **Neo4j**:
  - `Person`: Used in `Neo4jHygieneTask` to check for orphan nodes and broken relationships.

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` for Neo4j connection.
- **Database Configuration**: Passed via `db_config` dictionary.

#### Key Logic
- **Task Prioritization**: Tasks are prioritized based on their `priority` and `cooldown` attributes.
- **Task Execution**: Tasks are executed based on their `should_run()` and `execute()` methods.
- **Result Logging**: Task results are logged to `iris_task_log` for tracking and auditing.

#### Integration Points
- **Consciousness Loop**: Tasks are picked and executed by the consciousness loop, which interacts with the `TaskRegistry`.
- **Redis**: Used in `RedisQueueHealthTask` to check the health of Redis streams.
- **Neo4j**: Used in `Neo4jHygieneTask` to perform graph hygiene tasks.

### Detailed Breakdown of Classes and Functions

#### `TaskPriority`
- **Purpose**: Enum for task priority levels.
- **Methods**: None.
- **Usage**: Used to set the priority level of tasks.

#### `TaskResult`
- **Purpose**: Data class to store the result of a task execution.
- **Attributes**: `success`, `summary`, `items_processed`, `error`, `metadata`.

#### `BackgroundTask`
- **Purpose**: Abstract base class for all background tasks.
- **Methods**:
  - `__init__(db_config)`: Initializes the task with database configuration.
  - `get_db()`: Returns a PostgreSQL connection.
  - `set_last_run(when, status)`: Sets the last run time and status.
  - `cooldown_elapsed()`: Checks if the cooldown period has elapsed.
  - `should_run()`: Abstract method to determine if the task should run.
  - `execute()`: Abstract method to execute the task and return a `TaskResult`.

#### `PatchAuditTask`
- **Purpose**: Verifies that patch counters in `STREAMS.json` match reality.
- **Methods**:
  - `should_run()`: Checks if the cooldown period has elapsed.
  - `execute()`: Verifies patch counters and returns a `TaskResult`.

#### `Neo4jHygieneTask`
- **Purpose**: Finds orphan nodes and broken relationships in Neo4j.
- **Methods**:
  - `should_run()`: Checks if the cooldown period has elapsed.
  - `execute()`: Executes graph hygiene tasks and returns a `TaskResult`.

#### `DocStalenessTask`
- **Purpose**: Checks if documentation files are stale relative to recent code changes.
- **Methods**:
  - `should_run()`: Checks if the cooldown period has elapsed.
  - `execute()`: Checks the staleness of documentation files and returns a `TaskResult`.

#### `RedisQueueHealthTask`
- **Purpose**: Checks the health of Redis streams.
- **Methods**:
  - `should_run()`: Checks if the cooldown period has elapsed.
  - `execute()`: Executes Redis health checks and returns a `TaskResult`.

#### `TaskRegistry`
- **Purpose**: Manages all background tasks and picks the next one to run.
- **Methods**:
  - `__init__(db_config)`: Initializes the task registry with database configuration.
  - `initialize()`: Registers built-in tasks and loads run history.
  - `register(task)`: Registers a new task at runtime.
  - `_load_history()`: Loads last run times from `iris_task_log`.
  - `next_task(current_mode)`: Picks the next task to run based on the current mode.
  - `record_result(task, result)`: Records the result of a task execution.

#### `run_idle_task`
- **Purpose**: Convenience function to pick and run one idle task.
- **Arguments**: `db_config`, `mode`.
- **Returns**: The result of the task execution or `None` if no task is available.

This file serves as the core task management system for the Mythos infrastructure, ensuring that background tasks are executed efficiently and according to their defined priorities and cooldown periods.
