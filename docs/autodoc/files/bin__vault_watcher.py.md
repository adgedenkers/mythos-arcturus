# bin/vault_watcher.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 547

---

### File: bin/vault_watcher.py

#### Purpose
The `vault_watcher.py` script monitors a specified directory (vault root) for new or modified files, classifies them using a local language model (LLM), and moves them to appropriate subfolders based on the classification. It also maintains a persistent log of all file moves for reversibility.

#### Architecture
The script consists of two main classes and several top-level functions:
- **MoveLog**: Manages a persistent log of file moves.
- **VaultHandler**: Handles file events (created, moved) within the vault root.

Top-level functions include:
- `call_ollama`: Sends a prompt to the Ollama LLM and parses the JSON response.
- `classify_file`: Classifies a file based on its content and returns the target folder and metadata.
- `inject_frontmatter`: Updates the file's frontmatter with classification metadata.
- `process_file`: Classifies and moves a single file.
- `sweep_root`: Processes all files in the root that do not belong there.
- `main`: The entry point for the script.

#### Patterns
- **Singleton**: The `MoveLog` class can be considered a singleton as it maintains a single log file for all operations.
- **Observer**: The `VaultHandler` class extends `FileSystemEventHandler` to observe file system events.

#### Dependencies
The script imports various modules:
- `argparse`, `hashlib`, `json`, `os`, `re`, `shutil`, `sys`, `time`, `unicodedata`, `requests` for general file handling and HTTP requests.
- `datetime`, `Path`, `typing` for date handling and type annotations.
- `watchdog.observers.Observer`, `watchdog.events.FileSystemEventHandler` for file system event monitoring.

#### Interfaces
- **MoveLog**: Exposes methods for recording, undoing, and listing recent moves.
- **VaultHandler**: Handles file events (`on_created`, `on_moved`) and processes pending files (`process_pending`).
- **Top-level functions**: Provide functionality for classification, frontmatter injection, and file processing.

#### Database
- **PostgreSQL**: No direct database operations are performed in this script. However, the `datetime` and `pathlib` modules are imported, which might be used in conjunction with PostgreSQL elsewhere in the system.
- **Neo4j**: No direct Neo4j operations are performed in this script.

#### Configuration
- **Environment Variables**: No environment variables are used directly in this script.
- **Config Files**: No configuration files are explicitly loaded, but constants like `OLLAMA_URL`, `DEFAULT_MODEL`, and `FOLDER_MAP` are defined.

#### Key Logic
- **Classification**: Uses a combination of keyword matching and LLM-based classification to determine the target folder for a file.
- **Move Logging**: Every file move is logged in a JSON file (`_move_log.json`), and the log supports undo operations.
- **Frontmatter Injection**: Updates the file's frontmatter with classification metadata to ensure consistency.

#### Integration Points
- **Ollama**: The script integrates with the Ollama LLM to classify files.
- **File System**: Monitors and interacts with the file system using `watchdog` and `shutil`.
- **Mythos System**: The script is part of the larger Mythos system, which includes other subsystems like the database and frontmatter management.

### Detailed Documentation

#### Classes

1. **MoveLog**
   - **Purpose**: Manages a persistent log of file moves.
   - **Methods**:
     - `__init__`: Initializes the log file path and loads existing entries.
     - `_load`: Loads entries from the log file.
     - `_save`: Saves entries to the log file.
     - `record`: Records a new move entry.
     - `undo`: Undoes a specific move by ID.
     - `undo_last`: Undoes the most recent non-undone move.
     - `recent`: Returns the most recent entries.

2. **VaultHandler**
   - **Purpose**: Handles file events in the vault root.
   - **Methods**:
     - `__init__`: Initializes the handler with the vault root, model, move log, and dry run flag.
     - `on_created`: Handles file creation events.
     - `on_moved`: Handles file move events.
     - `process_pending`: Processes files that have settled (no changes for `SETTLE_SECONDS`).

#### Top-level Functions

1. **call_ollama**
   - **Purpose**: Sends a prompt to the Ollama LLM and parses the JSON response.
   - **Arguments**: `prompt`, `model`
   - **Returns**: A dictionary containing the LLM response.

2. **classify_file**
   - **Purpose**: Classifies a file and returns the target folder and metadata.
   - **Arguments**: `filepath`, `model`
   - **Returns**: A dictionary with the target folder, summary, confidence, and reasoning.

3. **inject_frontmatter**
   - **Purpose**: Adds or updates frontmatter with classification metadata.
   - **Arguments**: `filepath`, `classification`

4. **process_file**
   - **Purpose**: Classifies and moves a single file.
   - **Arguments**: `filepath`, `vault_root`, `model`, `move_log`, `dry_run`

5. **sweep_root**
   - **Purpose**: Processes all files in the root that do not belong there.
   - **Arguments**: `vault_root`, `model`, `move_log`, `dry_run`

6. **main**
   - **Purpose**: The entry point for the script, parses command-line arguments and starts the file watcher.

#### Configuration and Constants

- **OLLAMA_URL**: The URL for the Ollama LLM API.
- **DEFAULT_MODEL**: The default LLM model to use.
- **MAX_CONTENT_CHARS**: The maximum number of characters to read from a file for classification.
- **ROOT_PERMANENT**: Files that should remain in the root directory.
- **SKIP_DIRS**: Directories to ignore during file processing.
- **WATCH_EXTENSIONS**: File extensions to watch.
- **MIN_AGE_SECONDS**: Minimum file age before processing.
- **SETTLE_SECONDS**: Time to wait after the last modification before classifying a file.
- **FOLDER_MAP**: A dictionary mapping folder paths to keywords for classification.

#### Example Usage

```bash
python3 vault_watcher.py /path/to/vault --model qwen2.5:32b --dry-run
```

This command starts the vault watcher in dry-run mode, using the specified model to classify files but not actually moving them.
