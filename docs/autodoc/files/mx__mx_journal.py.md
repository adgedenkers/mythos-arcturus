# mx/mx_journal.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 138

---

### File: mx/mx_journal.py

#### Purpose
The `mx_journal.py` file manages session intent declaration and session logging. It records various session activities such as commands run, patches deployed, services restarted, and session summaries, and writes these to a journal file and a TODO.md file.

#### Architecture
The file contains a single class `MxJournal` with several methods to record different session activities. The class maintains state for the session and provides methods to update this state and save it to a JSON file and a TODO.md file.

#### Patterns
- **Singleton**: The `MxJournal` class can be considered a singleton in the context of a session, as it is instantiated once per session and maintains state throughout the session.
- **Observer**: The class observes various session activities and records them.

#### Dependencies
- **Imports**: `json`, `re`, `datetime`, `pathlib`
- **External Files**: `TODO_PATH` (`/opt/mythos/docs/TODO.md`), `JOURNAL_DIR` (`~/.mx/journal`)

#### Interfaces
- **Public Methods**:
  - `declare_intent(intent: str)`: Declares the intent for the session.
  - `record_command()`: Records a command run.
  - `record_heal(success: bool)`: Records whether a failure was healed.
  - `record_patch_deploy(patch_id: str)`: Records a patch deployment.
  - `record_service_restart(service: str)`: Records a service restart.
  - `record_snapshot(pre_path: str = None, post_path: str = None)`: Records snapshot paths.
  - `record_delta(summary: str, regressions: list[str])`: Records delta summary and regressions.
  - `write_todo_entry() -> bool`: Writes a session summary to TODO.md.

#### Database
- **PostgreSQL**: No direct database interactions are observed in this file.
- **Neo4j**: No Neo4j interactions are observed in this file.

#### Configuration
- **Environment Variables**: None.
- **Config Files**: None.

#### Key Logic
- **Session State Management**: The `MxJournal` class maintains the state of the session, including the session ID, start time, number of commands run, failures healed, patches deployed, services restarted, and more.
- **Journal File Management**: The `_save` method serializes the session state to a JSON file in the `~/.mx/journal` directory.
- **TODO.md Management**: The `write_todo_entry` method appends a summary of the session to the `TODO.md` file under the "Session Log" section.

#### Integration Points
- **Mythos Subsystems**: This file integrates with other parts of the Mythos system by recording various session activities and summarizing them. It interacts with the filesystem to write to the journal and TODO.md files. It is likely used by other components of the system to log activities and maintain session summaries.

### Detailed Documentation

#### Class: `MxJournal`
- **Attributes**:
  - `session_id`: The unique identifier for the session.
  - `intent`: The declared intent for the session.
  - `start_time`: The start time of the session.
  - `commands_run`: The number of commands run during the session.
  - `failures_healed`: The number of failures that were healed.
  - `failures_unhealed`: The number of failures that were not healed.
  - `patches_deployed`: A list of patch IDs deployed during the session.
  - `services_restarted`: A list of services restarted during the session.
  - `pre_snapshot_path`: The path to the pre-snapshot.
  - `post_snapshot_path`: The path to the post-snapshot.
  - `delta_summary`: A summary of the delta.
  - `regressions`: A list of regressions observed during the session.
  - `journal_file`: The path to the session journal file.

- **Methods**:
  - `__init__(self, session_id: str)`: Initializes the `MxJournal` instance with the session ID and sets up the journal directory and file.
  - `declare_intent(self, intent: str)`: Sets the session intent and saves the state.
  - `record_command(self)`: Increments the command count.
  - `record_heal(self, success: bool)`: Updates the failure count based on the success of the healing.
  - `record_patch_deploy(self, patch_id: str)`: Adds a patch ID to the list of deployed patches.
  - `record_service_restart(self, service: str)`: Adds a service to the list of restarted services.
  - `record_snapshot(self, pre_path: str = None, post_path: str = None)`: Sets the pre-snapshot and post-snapshot paths.
  - `record_delta(self, summary: str, regressions: list[str])`: Sets the delta summary and regressions.
  - `_save(self)`: Serializes the session state to a JSON file.
  - `write_todo_entry(self) -> bool`: Appends a session summary to the TODO.md file and returns a boolean indicating success.

This file plays a crucial role in maintaining and summarizing session activities within the Mythos system, ensuring that all session-related data is logged and accessible for review.
