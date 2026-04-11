# core/segment_manager.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 76

---

### Documentation for `core/segment_manager.py`

#### Purpose
The `segment_manager.py` script is a background service that periodically checks and manages the lifecycle of segments in the Mythos system. It performs tasks such as soft-closing stale open segments, hard-closing old soft-closed segments, and archiving very old closed segments.

#### Architecture
The script is designed as a lightweight loop that can be run as a systemd timer or as a persistent service. It consists of the following components:
- **Global Variables**: `_running` to control the main loop.
- **Functions**:
  - `_signal_handler(signum, frame)`: Handles termination signals.
  - `run_lifecycle_check()`: Executes one lifecycle check cycle.
  - `main()`: The main loop that runs the lifecycle checks periodically.

#### Patterns
- **Singleton Pattern**: The script uses a global variable `_running` to control the main loop, acting as a singleton for the running state.
- **Signal Handling**: Uses the `signal` module to handle termination signals (`SIGTERM` and `SIGINT`).

#### Dependencies
- **Standard Libraries**: `os`, `sys`, `time`, `logging`, `signal`
- **External Libraries**: `dotenv` for loading environment variables
- **Internal Modules**: `subject_tracker` for segment lifecycle management

#### Interfaces
- **Functions Exposed**:
  - `_signal_handler(signum, frame)`: Handles termination signals.
  - `run_lifecycle_check()`: Executes one lifecycle check cycle.
  - `main()`: The main loop that runs the lifecycle checks periodically.

#### Database
- **PostgreSQL Tables**:
  - `a`
  - `dotenv`
  - `subject_tracker`

#### Configuration
- **Environment Variables**: Loaded from `/opt/mythos/.env` using `dotenv`.
- **Logging Configuration**: Configured to log messages with a specific format and level.

#### Key Logic
- **Lifecycle Check**:
  - The `run_lifecycle_check()` function calls `close_stale_segments()` from the `subject_tracker` module to close stale segments.
  - The function logs the number of segments closed and handles any exceptions that occur during the process.

- **Main Loop**:
  - The `main()` function runs the `run_lifecycle_check()` function every 5 minutes.
  - It uses a while loop controlled by the `_running` flag to ensure graceful shutdown when receiving termination signals.

#### Integration Points
- **Signal Handling**: The script integrates with the operating system's signal handling mechanism to ensure it can be gracefully shut down.
- **Segment Lifecycle Management**: Integrates with the `subject_tracker` module to perform segment lifecycle operations.
- **Logging**: Uses the Python `logging` module to log messages, which can be integrated with system-wide logging mechanisms.

### Summary
The `segment_manager.py` script is a critical component of the Mythos system, responsible for managing the lifecycle of segments. It runs periodically to ensure that segments are properly closed and archived based on their activity and age. The script is designed to be robust and responsive to termination signals, ensuring it can be integrated into a larger system with minimal disruption.
