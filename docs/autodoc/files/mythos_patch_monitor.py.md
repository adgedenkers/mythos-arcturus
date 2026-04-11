# mythos_patch_monitor.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 785

---

### Documentation for `mythos_patch_monitor.py`

#### Purpose
This file monitors the `~/Downloads` directory for specific artifact files (patches, sales/shoe DB ingestion, bank CSVs) and handles their processing. It integrates with Git for versioning and snapshot management, and supports Telegram notifications for finance imports.

#### Architecture
The file consists of two main classes:
1. **GitManager**: Manages Git operations for patch versioning.
2. **DownloadsHandler**: Handles file system events, specifically file creation, and processes different types of artifacts.

Additionally, there are several top-level functions for utility operations like sending Telegram notifications and the main entry point.

#### Patterns
- **Observer Pattern**: The `DownloadsHandler` class extends `FileSystemEventHandler` to observe file system events.
- **Singleton Pattern**: The `GitManager` instance is created globally and reused.

#### Dependencies
- **Standard Libraries**: `os`, `re`, `shutil`, `sys`, `zipfile`, `time`, `logging`, `subprocess`, `json`, `pathlib`, `datetime`
- **External Libraries**: `watchdog`, `dotenv`, `psycopg2`, `file_analyzer`

#### Interfaces
- **GitManager**: Exposes methods for Git operations such as `is_repo`, `has_remote`, `get_current_version`, `increment_version`, `get_manifest_version`, `update_version_file`, `has_changes`, `create_snapshot`, `commit_patch`, `tag_version`, `push`, `rollback_to_tag`, `list_tags`.
- **DownloadsHandler**: Handles file creation events and processes artifacts based on their type.
- **Top-level Functions**: `send_telegram_notification`, `main`.

#### Database
The file interacts with PostgreSQL tables for various operations:
- `banks`
- `manifest`
- `catalog_record`
- `file`
- `parsers`
- `transactions`
- `DB`
- `Downloads`
- `install_script`

#### Configuration
- **Environment Variables**: Loaded via `dotenv.load_dotenv("/opt/mythos/.env")`.
- **Configuration Constants**: Defined at the top of the file, such as `WATCH_DIR`, `MYTHOS_ROOT`, `PATCH_DIR`, `PATCH_ARCHIVE_DIR`, `PATCH_LOG_DIR`, `SALES_DIR`, `SALES_ARCHIVE_DIR`, `SHOE_DIR`, `SHOE_ARCHIVE_DIR`, `FINANCE_DIR`, `FINANCE_ARCHIVE_DIR`, `BANK_ACCOUNTS`, `INGESTOR`, `VENV_PY`, `ARTIFACT_PATTERNS`, `GIT_ENABLED`, `GITHUB_PUSH_ENABLED`, `AUTO_EXECUTE_INSTALL`, `TELEGRAM_NOTIFY_FINANCE`.

#### Key Logic
1. **GitManager**:
   - Manages Git operations for patch versioning, including creating snapshots, committing changes, tagging versions, and pushing to GitHub.
   - Handles rollback operations to specific tags.
2. **DownloadsHandler**:
   - Monitors the `~/Downloads` directory for new files.
   - Processes different types of artifacts (patches, sales/shoe DB ingestion, bank CSVs) based on predefined patterns.
   - Sends notifications via Telegram for finance imports.
   - Logs important events and errors.

#### Integration Points
- **Git Integration**: Uses `GitManager` to manage Git operations for patch versioning.
- **Telegram Notifications**: Uses `send_telegram_notification` to send notifications for finance imports.
- **File System Events**: Uses `DownloadsHandler` to handle file creation events in the `~/Downloads` directory.
- **Database Operations**: Interacts with PostgreSQL for various operations related to artifact processing and finance imports.

### Detailed Breakdown

#### GitManager Class
- **Purpose**: Manages Git operations for patch versioning.
- **Methods**:
  - `__init__`: Initializes the GitManager with the repository path.
  - `_run_git`: Runs a Git command in the repository directory.
  - `is_repo`: Checks if the directory is a Git repository.
  - `has_remote`: Checks if a remote origin is configured.
  - `get_current_version`: Retrieves the latest version tag or returns `v0.0.0`.
  - `increment_version`: Increments the patch version number.
  - `get_manifest_version`: Reads the version from `manifest.json` if present.
  - `update_version_file`: Updates the `.version` file with the current version.
  - `has_changes`: Checks for uncommitted changes.
  - `create_snapshot`: Creates a tagged snapshot of the repository.
  - `commit_patch`: Commits the patch changes.
  - `tag_version`: Creates a version tag.
  - `push`: Pushes commits and tags to the origin.
  - `rollback_to_tag`: Rolls back to a specific tag.
  - `list_tags`: Lists recent tags.

#### DownloadsHandler Class
- **Purpose**: Handles file system events and processes different types of artifacts.
- **Methods**:
  - `__init__`: Initializes the DownloadsHandler and sets up the file analyzer.
  - `on_created`: Handles file creation events.
  - `_detect_artifact_type`: Detects the type of artifact based on the filename.
  - `process_artifact`: Processes the artifact based on its type.
  - `process_bank_csv`: Processes bank CSV files for auto-import with smart analysis.
  - `_get_latest_balance`: Retrieves the latest balance from the database for an account.
  - `_notify_finance_import_simple`: Sends a notification for finance import results.
  - `_notify_finance_error`: Sends a notification for finance import errors.
  - `process_patch`: Processes patch files.
  - `_write_patch_log`: Writes patch application to a log file.
  - `process_sales_ingestion`: Processes sales DB ingestion files.
  - `process_shoe_ingestion`: Processes shoe DB ingestion files.
  - `_process_ingestion_zip`: Processes ingestion ZIP files.
  - `_is_valid_zip`: Checks if a file is a valid ZIP.

#### Top-level Functions
- **send_telegram_notification**: Sends a notification via Telegram bot if configured.
- **main**: The main entry point for the script.

### Conclusion
The `mythos_patch_monitor.py` file is a critical component of the Mythos system, responsible for monitoring and processing various artifact files, managing Git operations for versioning, and sending notifications for finance imports. It integrates with the file system, Git, and PostgreSQL databases to ensure robust artifact management and version control.
