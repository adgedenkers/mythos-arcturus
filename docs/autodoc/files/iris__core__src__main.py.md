# iris/core/src/main.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 107

---

### Documentation for `iris/core/src/main.py`

#### Purpose
This file serves as the main entry point for the IRIS Core system. It initializes the system, sets up logging, handles signals for graceful shutdown, and manages the primary `ConsciousnessLoop` and a health check server.

#### Architecture
- **Main Function**: `main` is the primary function that orchestrates the initialization and running of the system.
- **Signal Handler**: `signal_handler` is a function that sets a shutdown event when a SIGINT or SIGTERM signal is received.
- **Logging Configuration**: Structured logging is configured at the beginning of the file.
- **Classes and Functions**:
  - `main`: Asynchronous function that initializes and runs the system.
  - `signal_handler`: Synchronous function that handles shutdown signals.

#### Patterns
- **Singleton**: The `log` object is a singleton instance of `structlog.stdlib.BoundLogger`.
- **Observer**: The `signal_handler` function acts as an observer for shutdown signals.

#### Dependencies
- **Imports**:
  - `asyncio`: For asynchronous operations.
  - `signal`: For handling system signals.
  - `sys`: For system-related operations.
  - `structlog`: For structured logging.
  - `uvicorn`: For running the health check server.
  - `datetime`: For timestamp operations.
- **Internal Modules**:
  - `ConsciousnessLoop`: From `iris.core.src.loop`.
  - `Config`: From `iris.core.src.config`.
  - `create_health_app`: From `iris.core.src.health`.

#### Interfaces
- **Exposed Functions**:
  - `main`: The entry point for the system, which is run when the module is executed.
  - `signal_handler`: Handles SIGINT and SIGTERM signals.

#### Database
- **References**:
  - `datetime`: Uses PostgreSQL to store timestamps.

#### Configuration
- **Configuration**:
  - `Config.from_environment()`: Loads configuration from environment variables.

#### Key Logic
- **Initialization**:
  - Configures structured logging.
  - Loads configuration from environment variables.
  - Initializes the `ConsciousnessLoop` and a health check server.
- **Running**:
  - Starts the health check server and the `ConsciousnessLoop` in background tasks.
  - Waits for a shutdown signal.
- **Shutdown**:
  - Sets a shutdown event.
  - Requests graceful shutdown of the `ConsciousnessLoop`.
  - Waits for all tasks to complete.

#### Integration Points
- **ConsciousnessLoop**: Integrates with the `ConsciousnessLoop` class to manage the core logic of the system.
- **Health Check Server**: Integrates with `uvicorn` to run a health check server.
- **Logging**: Uses `structlog` for logging, which is configured at the beginning of the file.
- **Configuration**: Uses `Config` to load system configuration from environment variables.

### Summary
This file is the entry point for the IRIS Core system, responsible for setting up logging, initializing the `ConsciousnessLoop`, and managing the health check server. It handles graceful shutdowns and ensures that all system components are properly started and stopped.
