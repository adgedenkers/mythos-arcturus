# services/doc_watcher.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 196

---

### Documentation for `services/doc_watcher.sh`

#### Purpose
This script, `doc_watcher.sh`, monitors specific documentation files and directories within the Mythos system. When changes are detected, it waits for writes to settle, then automatically commits and pushes these changes to a GitHub repository.

#### Architecture
The script is structured as a continuous loop that monitors specified paths using `inotifywait`. It includes several functions for logging, log rotation, path validation, and Git operations. The main loop handles the detection of changes, debouncing, cooldown periods, and committing/pushing changes.

#### Patterns
- **Singleton Pattern**: The script runs as a single instance, handling all monitoring and commit operations.
- **Observer Pattern**: Uses `inotifywait` to observe changes in specified paths.

#### Dependencies
- **External Commands**: `inotifywait`, `git`, `date`, `du`, `mv`, `tee`
- **System Packages**: `inotify-tools` (for `inotifywait`)

#### Interfaces
- **Logging**: Functions `log` and `log_error` for logging messages to `/var/log/mythos/doc-watcher.log`.
- **Git Operations**: Function `git_commit_and_push` for committing and pushing changes to the GitHub repository.
- **Signal Handling**: Handles `SIGTERM`, `SIGINT`, and `SIGHUP` signals to gracefully shut down the script.

#### Database
- **No direct database interaction**: The script does not interact directly with PostgreSQL, Neo4j, or Redis. However, it indirectly affects the state of the Git repository, which could be considered a form of data storage.

#### Configuration
- **Environment Variables**: None.
- **Configuration Variables**:
  - `MYTHOS_ROOT`: Root directory of the Mythos system.
  - `DOCS_DIR`: Directory containing documentation files.
  - `LIVE_DIR`: Directory containing live documentation files.
  - `LOG_FILE`: Path to the log file.
  - `DEBOUNCE_SECONDS`: Time to wait after changes before committing.
  - `COOLDOWN_SECONDS`: Minimum time between commits.
  - `MAX_LOG_SIZE_MB`: Maximum size of the log file before rotation.

#### Key Logic
1. **Monitoring**: Uses `inotifywait` to monitor changes in specified paths.
2. **Debouncing**: Waits for a specified period (`DEBOUNCE_SECONDS`) to ensure all changes have settled before committing.
3. **Cooldown**: Ensures a minimum time (`COOLDOWN_SECONDS`) between commits.
4. **Git Operations**: Stages changes, builds a commit message, and pushes changes to GitHub with retry logic.

#### Integration Points
- **Documentation Files**: Monitors changes in `TODO.md`, `ARCHITECTURE.md`, and the `live/` directory.
- **Git Repository**: Automatically commits and pushes changes to the GitHub repository.
- **Logging**: Logs all activities to `/var/log/mythos/doc-watcher.log`.

### Detailed Breakdown of Functions

1. **Configuration Section**:
   - Sets up environment variables for paths and constants.

2. **Logging Functions**:
   - `log`: Logs messages to the specified log file.
   - `log_error`: Logs error messages to the specified log file and standard error.

3. **Log Rotation**:
   - `rotate_log_if_needed`: Checks if the log file exceeds the maximum size and rotates it if necessary.

4. **Path Validation**:
   - `validate_paths`: Ensures all specified paths exist and logs warnings for non-existent paths.

5. **Git Operations**:
   - `git_commit_and_push`: Stages changes, commits them with a message, and pushes to the GitHub repository with retry logic.

6. **Main Loop**:
   - Continuously monitors specified paths for changes, handles debouncing and cooldown periods, and commits/pushes changes to the repository.

7. **Signal Handling**:
   - Gracefully shuts down the script on receiving `SIGTERM`, `SIGINT`, or `SIGHUP` signals.

This script ensures that documentation changes are automatically synchronized with the GitHub repository, maintaining a live and up-to-date version of the documentation.
