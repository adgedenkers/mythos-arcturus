# mx/mx_logger.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 102

---

### Documentation for `mx_logger.py`

#### Purpose
The `mx_logger.py` file contains the `MxLogger` class, which is responsible for logging various events and commands during a session of the Mythos system. It also handles storing and loading error patterns to improve future command handling.

#### Architecture
The `MxLogger` class is the primary component of this file. It contains several methods for logging different types of events, storing error patterns, and loading previously stored patterns. The class is initialized with a configuration dictionary that specifies the directories for session logs and error patterns.

#### Patterns
- **Singleton Pattern**: Although not explicitly enforced, the `MxLogger` class can be used as a singleton to ensure a single instance handles all logging for a session.
- **Decorator Pattern**: The methods like `log_command`, `log_result`, etc., can be seen as decorators that wrap around the actual logging logic.

#### Dependencies
- **Imports**: The file imports `json`, `datetime`, and `Path` from `pathlib`.
- **External Files**: It relies on configuration files and paths specified in the `config` dictionary passed to the `__init__` method.

#### Interfaces
- **Public Methods**:
  - `log_command`: Logs user commands and their resolutions.
  - `log_result`: Logs the result of executed commands.
  - `log_mx_event`: Logs general events within the Mythos system.
  - `log_fix_attempt`: Logs attempts to fix errors.
  - `log_fix_outcome`: Logs the outcome of fix attempts.
  - `log_session_end`: Logs the end of a session.
  - `load_error_patterns`: Loads previously stored error patterns.
  - `find_known_fix`: Finds a known fix for a given command and error.

#### Database
- **PostgreSQL**: The file references `datetime` and `pathlib` from PostgreSQL, but these are actually Python standard libraries, not database tables.
- **Neo4j**: No direct Neo4j references are found in this file.

#### Configuration
- **Environment Variables/Config Files**: The class relies on a configuration dictionary passed to the `__init__` method, which specifies paths for session logs and error patterns.

#### Key Logic
- **Logging**: The `_write` method appends text to the session log file.
- **Timestamps**: The `_ts` method generates timestamps for log entries.
- **Error Pattern Storage**: The `_store_error_pattern` method appends error patterns to a JSON lines file.
- **Pattern Matching**: The `find_known_fix` method checks known error patterns to find a potential fix for a given command and error.

#### Integration Points
- **Mythos Subsystems**: This logger integrates with the command execution subsystem to log commands and their outcomes. It also interacts with the error handling subsystem to store and retrieve error patterns, which can be used to suggest fixes to users.

### Detailed Breakdown of Methods

1. **`__init__(self, config: dict)`**:
   - Initializes the logger with paths for session logs and error patterns.
   - Creates the necessary directories if they do not exist.
   - Opens a new session log file and logs the start of the session.

2. **`_write(self, text: str)`**:
   - Appends the given text to the session log file.

3. **`_ts(self) -> str`**:
   - Returns the current timestamp in HH:MM:SS format.

4. **`log_command(self, raw_input: str, resolved_command: str = None, intent_matched: str = None)`**:
   - Logs the raw input and resolved command with a timestamp.

5. **`log_result(self, exit_code: int, stdout: str = "", stderr: str = "")`**:
   - Logs the exit code and standard output/error of a command execution.

6. **`log_mx_event(self, event_type: str, message: str)`**:
   - Logs a general event with a type and message.

7. **`log_fix_attempt(self, fix_command: str, attempt_num: int)`**:
   - Logs an attempt to fix an error with a specific command.

8. **`log_fix_outcome(self, success: bool, fix_command: str, original_command: str, original_error: str, reasoning: str)`**:
   - Logs the outcome of a fix attempt, storing the pattern if successful.

9. **`log_session_end(self)`**:
   - Logs the end of the session.

10. **`_store_error_pattern(self, failed_command: str, error: str, fix_command: str, reasoning: str)`**:
    - Stores an error pattern in a JSON lines file.

11. **`load_error_patterns(self) -> list`**:
    - Loads previously stored error patterns from a JSON lines file.

12. **`find_known_fix(self, command: str, error: str)`**:
    - Searches for a known fix for a given command and error by comparing stored patterns.

This documentation provides a comprehensive overview of the `mx_logger.py` file, detailing its purpose, architecture, dependencies, interfaces, and key logic.
