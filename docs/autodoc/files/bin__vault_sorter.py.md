# bin/vault_sorter.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 754

---

### Purpose
The `vault_sorter.py` script provides an interactive terminal user interface (TUI) for reviewing and routing unsorted files from the `UNSORTED` directory within a vault system. It leverages an LLM (Language Model) to classify files and allows manual overrides before moving them to their respective destinations.

### Architecture
The script is structured around two main classes:
1. **FileEntry**: Represents an individual file entry with methods for classification and status management.
2. **VaultSorterTUI**: Manages the TUI, including file loading, classification, and user interactions.

Additionally, there are several top-level functions that handle specific tasks such as calling the LLM, classifying files, building and saving an index, logging moves, and the main entry point.

### Patterns
- **Factory Method**: The `call_ollama` function acts as a factory method to generate classification results based on the provided prompt.
- **Singleton**: The `VaultSorterTUI` class can be considered a singleton as it manages the entire TUI session and is not intended to have multiple instances.

### Dependencies
- **argparse**: For parsing command-line arguments.
- **curses**: For creating the TUI.
- **hashlib**: For hashing file contents.
- **json**: For handling JSON data.
- **os**: For file system operations.
- **re**: For regular expression operations.
- **shutil**: For file operations.
- **sys**: For system-specific parameters and functions.
- **textwrap**: For text formatting.
- **time**: For time-related functions.
- **requests**: For making HTTP requests to the LLM.

### Interfaces
- **FileEntry**: Exposes methods for classification (`classify`), size conversion (`size_str`), and status conversion (`status_str`).
- **VaultSorterTUI**: Provides methods for initializing the TUI (`__init__`), loading files (`load_files`), setting status messages (`set_status`), running the TUI (`run`), drawing the interface (`draw`), handling key inputs (`handle_*_key`), and processing selected files (`classify_selected`, `process_selected`).

### Database
The script interacts with PostgreSQL tables:
- **UNSORTED**: Manages unsorted files.
- **datetime**: Stores timestamps.
- **pathlib**: Manages file paths.
- **disk**: Manages disk operations.
- **preview**: Manages file previews.
- **the**: Placeholder for other database operations.

### Configuration
- **VAULT_ROOT**: Root directory of the vault.
- **UNSORTED_DIR**: Directory containing unsorted files.
- **INDEX_PATH**: Path to the vault index file.
- **MOVE_LOG_PATH**: Path to the move log file.
- **OLLAMA_URL**: URL for the LLM API.
- **DEFAULT_MODEL**: Default LLM model to use.
- **MAX_CONTENT_CHARS**: Maximum number of characters to read from a file for classification.
- **VAULT_FOLDERS**: List of valid vault folders.

### Key Logic
- **Classification**: Uses the `call_ollama` function to send a file's content to an LLM for classification.
- **TUI Management**: Manages the TUI using `curses` for drawing the interface and handling user inputs.
- **File Operations**: Handles file reading, writing, moving, and logging.

### Integration Points
- **LLM Integration**: Uses the `call_ollama` function to interact with the LLM via HTTP requests.
- **File System Integration**: Reads and writes files from the `UNSORTED` directory and moves them to their respective destinations.
- **Logging**: Logs file moves to `_move_log.json`.
- **Indexing**: Builds and saves an index of files in `_vault_index.json`.

### Detailed Breakdown

#### `call_ollama(prompt, model=DEFAULT_MODEL)`
- **Purpose**: Sends a classification prompt to the LLM and returns the result.
- **Logic**: Uses `requests.post` to send a JSON payload to the LLM API and processes the response.

#### `classify_file(filepath)`
- **Purpose**: Classifies a file by reading its content and sending it to the LLM for classification.
- **Logic**: Reads the file content, formats the prompt, and calls `call_ollama` to get the classification result.

#### `build_index()`
- **Purpose**: Builds an index of files in the vault.
- **Logic**: Reads files from the vault and constructs an index.

#### `save_index(index)`
- **Purpose**: Saves the file index to a JSON file.
- **Logic**: Writes the index to `_vault_index.json`.

#### `log_move(source, dest, classification)`
- **Purpose**: Logs a file move operation.
- **Logic**: Appends the move details to `_move_log.json`.

#### `main()`
- **Purpose**: Entry point of the script, parses command-line arguments and runs the TUI.
- **Logic**: Parses arguments using `argparse`, initializes the TUI, and runs the main loop.

#### `FileEntry` Class
- **Purpose**: Represents a file entry with methods for classification and status management.
- **Methods**:
  - `__init__`: Initializes the file entry.
  - `classify`: Classifies the file using the LLM.
  - `size_str`: Returns the file size as a string.
  - `status_str`: Returns the file status as a string.

#### `VaultSorterTUI` Class
- **Purpose**: Manages the TUI for file sorting.
- **Methods**:
  - `__init__`: Initializes the TUI.
  - `safe_print`: Safely prints text to the screen.
  - `load_files`: Loads files from the `UNSORTED` directory.
  - `set_status`: Sets the status message.
  - `run`: Runs the TUI main loop.
  - `draw`: Draws the TUI interface.
  - `draw_list`: Draws the file list.
  - `draw_preview`: Draws the file preview.
  - `draw_dest_picker`: Draws the destination picker.
  - `draw_index`: Draws the vault index.
  - `draw_help`: Draws the help screen.
  - `handle_list_key`: Handles key inputs in the list view.
  - `handle_preview_key`: Handles key inputs in the preview view.
  - `handle_dest_picker_key`: Handles key inputs in the destination picker.
  - `handle_index_key`: Handles key inputs in the index view.
  - `handle_help_key`: Handles key inputs in the help view.
  - `classify_selected`: Classifies selected files.
  - `process_selected`: Processes selected files by moving them to their destinations.

This script is a comprehensive tool for managing and classifying files within a vault system, leveraging both automated and manual processes to ensure accurate organization.
