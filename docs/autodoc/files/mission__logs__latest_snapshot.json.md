# mission/logs/latest_snapshot.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 131

---

### File: mission/logs/latest_snapshot.json

#### Purpose
This JSON file serves as a snapshot of the current state of the Mythos system, capturing essential information about directories, files, services, and recent changes. It provides a comprehensive overview of the system's structure and recent modifications.

#### Architecture
The file is structured as a JSON object with several key-value pairs, each representing different aspects of the system:
- `snapshot_date`: The date of the snapshot.
- `summary`: A brief summary of the system's operational status.
- `directories`: An array of objects detailing directories, their files, and functions.
- `tables`: An array of objects detailing database tables and their column counts.
- `services`: An array of objects detailing services and their associated files.
- `key_files`: An array of objects detailing key files and their functions.
- `recent_changes`: An array of objects detailing recently modified files and their modification times.
- `hub_files`: An array of objects detailing hub files and their import counts.
- `stream_status`: An object detailing the status of various streams and their next patch numbers.

#### Patterns
No specific design patterns are used in this JSON file, as it is a data structure rather than code.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone data file.

#### Interfaces
This file does not expose any interfaces directly. It is intended to be read and processed by other parts of the system, such as monitoring or reporting tools.

#### Database
The file references database tables but does not perform any database operations. The tables mentioned are:
- `users` (6 columns)
- `transactions` (21 columns)
- `recurring_bills` (12 columns)

#### Configuration
This file does not use any configuration files or environment variables. It is a static data file.

#### Key Logic
The key logic in this file is the representation of the system's state at a specific point in time. It captures the structure of directories, the status of key files and services, and recent changes, providing a snapshot of the system's health and activity.

#### Integration Points
This file integrates with other parts of the Mythos system by providing data that can be used for monitoring, reporting, and system diagnostics. It can be read by tools that need to understand the current state of the system, such as:
- Monitoring tools that track recent changes and system status.
- Reporting tools that generate summaries of the system's operational status.
- Diagnostic tools that analyze the structure and health of the system.

### Detailed Breakdown

#### Directories
- `/opt/mythos/api/`: Contains no files or functions.
- `/opt/mythos/telegram_bot/handlers/`: Contains files like `sell_mode.py`, `weather_handler.py`, and `route_handler.py`.
- `/opt/mythos/integrity/`: Contains files like `__main__.py`, `file_scanner.py`, `function_extractor.py`, `table_scanner.py`, and `service_scanner.py`.

#### Key Files
- `/opt/mythos/assistants/chat_assistant.py`: Contains functions like `set_user`, `dispatch_to_grid`, `build_context_package`, `research_route`, `track_subject`, `get_context_stats`, `clear_context`, `get_last_prompt`, and `query`.
- `/opt/mythos/core/action_executor.py`: Contains functions like `_execute_balance_update`, `_execute_life_event`, `_execute_routine_done`, `_execute_task_added`, `_execute_task_completed`, `_execute_calendar_delete`, `_execute_calendar_update`, `_execute_calendar_create`, `_execute_bill_paid`, and `execute_actions`.
- `/opt/mythos/core/life_context.py`: Contains functions like `get_system_health_context`, `build_life_context`, and `_get_conn`.

#### Recent Changes
- `/opt/mythos/docs/PATCH_HISTORY.md`: Modified on `2026-03-07T16:53:01.369610`.
- `/opt/mythos/core/life_context.py`: Modified on `2026-03-07T16:39:52.607228`.

#### Hub Files
- `/opt/mythos/api/main.py`: Has 55 imports.
- `/opt/mythos/telegram_bot/mythos_bot.py`: Has 16 imports.

#### Stream Status
- `NEU`: Next patch is 6.
- `LOG`: Next patch is 13.
- `MNE`: Next patch is 5.
- `SEN`: Next patch is 1.
- `SYS`: Next patch is 27.

This file serves as a critical component for understanding the current state and recent activity within the Mythos system, enabling effective monitoring and maintenance.
