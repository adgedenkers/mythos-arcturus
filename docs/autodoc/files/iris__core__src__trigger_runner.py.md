# iris/core/src/trigger_runner.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 100

---

### Documentation for `trigger_runner.py`

#### Purpose
This file runs the Iris Trigger Engine as a standalone service. It loads environment variables from a `.env` file, configures logging, builds a database configuration, and initializes the trigger engine to run tasks based on schedules.

#### Architecture
The file consists of several functions and a main asynchronous function:
1. **`load_env`**: Loads environment variables from a `.env` file.
2. **`build_db_config`**: Constructs the database configuration dictionary using environment variables.
3. **`try_load_task_registry`**: Attempts to load the task registry for idle task support.
4. **`main`**: The main asynchronous function that initializes the trigger engine and handles shutdown signals.
5. **`signal_handler`**: Handles shutdown signals to gracefully stop the trigger engine.

#### Patterns
- **Singleton Pattern**: The `load_env` function ensures that environment variables are loaded only once.
- **Observer Pattern**: The `signal_handler` function observes and reacts to shutdown signals (`SIGTERM`, `SIGINT`).

#### Dependencies
- **Imports**: `asyncio`, `logging`, `os`, `signal`, `sys`
- **Internal Modules**: `src.trigger_engine`, `src.task_registry`

#### Interfaces
- **Exposed Functions**: None (all functions are internal).
- **Main Entry Point**: `main` function is the entry point for the trigger engine.

#### Database
- **PostgreSQL**: The file references the `src` table in PostgreSQL for database operations.

#### Configuration
- **Environment Variables**: The file reads several environment variables:
  - `POSTGRES_HOST`
  - `POSTGRES_PORT`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
- **.env File**: Environment variables are loaded from `/opt/mythos/.env`.

#### Key Logic
- **Loading Environment Variables**: The `load_env` function reads and sets environment variables from a `.env` file.
- **Database Configuration**: The `build_db_config` function constructs the database configuration using environment variables.
- **Task Registry Initialization**: The `try_load_task_registry` function attempts to initialize the task registry for idle task support.
- **Trigger Engine Execution**: The `main` function initializes the `TriggerEngine` and runs it until a shutdown signal is received.

#### Integration Points
- **Trigger Engine**: The `main` function initializes and runs the `TriggerEngine` from the `src.trigger_engine` module.
- **Task Registry**: The `try_load_task_registry` function integrates with the `TaskRegistry` from the `src.task_registry` module to support idle tasks.
- **Shutdown Handling**: The `signal_handler` function integrates with the operating system to handle shutdown signals (`SIGTERM`, `SIGINT`).

### Summary
The `trigger_runner.py` file is responsible for running the Iris Trigger Engine as a standalone service. It handles environment variable loading, database configuration, task registry initialization, and graceful shutdown handling. The file integrates with the `TriggerEngine` and `TaskRegistry` modules to provide a robust and configurable trigger engine service.
