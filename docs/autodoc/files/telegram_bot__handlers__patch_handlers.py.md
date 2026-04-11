# telegram_bot/handlers/patch_handlers.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 440

---

### File: `telegram_bot/handlers/patch_handlers.py`

#### Purpose
This file contains handlers for Telegram bot commands related to patch management in the Mythos system. These handlers manage operations such as listing available patches, applying patches, and rolling back to previous states.

#### Architecture
The file is structured around several utility functions and command handlers. Utility functions handle tasks like loading authorized user IDs, checking authorization, running Git commands, and fetching patch-related information. Command handlers are asynchronous functions that process specific Telegram bot commands.

#### Patterns
- **Singleton**: The `AUTHORIZED_IDS` set is initialized once and reused across multiple function calls.
- **Helper Methods**: Utility functions like `_load_authorized_ids`, `_is_authorized`, `_run_git`, etc., encapsulate specific functionalities and are reused by the command handlers.

#### Dependencies
- **Standard Libraries**: `os`, `subprocess`, `json`, `logging`, `re`
- **Third-party Libraries**: `pathlib`, `datetime`, `telegram`, `telegram.ext`

#### Interfaces
The file exposes several asynchronous functions that handle specific Telegram bot commands:
- `patch_command`
- `patch_status_command`
- `patch_list_command`
- `patch_apply_command`
- `patch_rollback_command`
- `patch_rollback_confirm_command`

These functions are designed to be called by the Telegram bot framework and process user commands.

#### Database
The file does not directly interact with any database tables or Neo4j labels. However, it references `pathlib` and `datetime`, which are used to manage file paths and timestamps.

#### Configuration
The file reads environment variables for authorized Telegram user IDs:
- `TELEGRAM_ID_KA`
- `TELEGRAM_ID_SERAPHE`

These IDs are used to authorize users for patch operations.

#### Key Logic
1. **Authorization**: Checks if the user is authorized to perform patch operations.
2. **Git Operations**: Uses `subprocess` to run Git commands for fetching tags, applying patches, and rolling back.
3. **Patch Management**: Lists available patches, applies patches, and rolls back to previous states.
4. **Logging**: Uses the `logging` module to log important events and errors.

#### Integration Points
The file integrates with:
- **Telegram Bot Framework**: Handles commands sent via the Telegram bot.
- **File System**: Reads and writes files in the `/opt/mythos/patches` directory.
- **Environment Variables**: Loads authorized user IDs from environment variables.
- **Subprocess**: Runs Git commands to manage the repository state.

### Detailed Breakdown

#### Utility Functions
- `_load_authorized_ids`: Loads authorized Telegram user IDs from environment variables.
- `_is_authorized`: Checks if a given user ID is authorized for patch operations.
- `_run_git`: Runs a Git command and returns the success status and output.
- `_get_current_version`: Fetches the current Git version tag.
- `_get_recent_tags`: Retrieves recent Git tags with dates.
- `_get_pending_patches`: Lists patches that haven't been applied.
- `_get_recent_logs`: Fetches recent patch application logs.
- `_get_highest_patch_number`: Finds the highest real patch number from logs.

#### Command Handlers
- `patch_command`: Shows patch system status and help.
- `patch_status_command`: Displays the current version and recent patches.
- `patch_list_command`: Lists available patches.
- `patch_apply_command`: Applies a specific patch.
- `patch_rollback_command`: Shows rollback options or initiates a rollback.
- `patch_rollback_confirm_command`: Confirms and performs the rollback operation.

Each command handler processes user input, checks authorization, performs the required operations, and sends appropriate responses back to the user via the Telegram bot.
