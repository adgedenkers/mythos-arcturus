# doc_manager.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 717

---

### Purpose
The `doc_manager.py` file provides a Textual-based TUI (Text User Interface) for managing versioned downloads and renaming files using an LLM (Language Model) service. It includes functionality to scan directories, group files by their base name, and export the latest versions or LLM-renamed files into a zip file with a manifest.

### Architecture
The file contains two main classes:
1. **LabelInputScreen**: A modal screen to get an export label from the user.
2. **DocManagerApp**: The main TUI application for managing versioned downloads and renaming files.

Additionally, there are several top-level functions for file version detection, directory scanning, and exporting files.

### Patterns
- **Modal Screen**: The `LabelInputScreen` class implements a modal screen pattern to capture user input for the export label.
- **Singleton**: The `DocManagerApp` class can be considered a singleton as it represents the main application instance.

### Dependencies
The file imports the following modules:
- `argparse`, `json`, `os`, `re`, `shutil`, `sys`, `zipfile`, `requests`
- `textual` and its submodules for building the TUI

### Interfaces
- **LabelInputScreen**: Exposes methods for handling button presses and input submissions.
- **DocManagerApp**: Exposes methods for handling button presses, selecting all/none, and performing export actions.

### Database
The file does not directly interact with any database tables or Neo4j labels. However, it references `collections`, `datetime`, `pathlib`, `typing`, and `textual` which are likely used for internal data handling.

### Configuration
The file does not explicitly use any configuration files or environment variables, but it accepts command-line arguments for the scan directory, output directory, LLM model, and Ollama URL.

### Key Logic
1. **File Version Detection**: Functions like `parse_versioned_name` and `get_latest` handle parsing filenames and identifying the latest version.
2. **Directory Scanning**: Functions like `scan_directory` and `scan_all_files` group files by their base name and filter based on version count.
3. **Export Functions**: Functions like `export_latest_versions` and `export_llm_renamed` create zip files with manifests containing the latest versions or LLM-renamed files.
4. **TUI Application**: The `DocManagerApp` class handles user interactions, including selecting files, exporting, and handling modal inputs.

### Integration Points
- **Ollama API**: The `ollama_suggest_name` function integrates with the Ollama API to suggest filenames based on file content.
- **File System**: The application interacts with the file system to read, write, and scan directories.
- **User Interface**: The TUI is built using the `textual` framework, which handles user input and display.

### Detailed Breakdown

#### LabelInputScreen
- **Purpose**: A modal screen to capture the export label from the user.
- **Methods**:
  - `__init__`: Initializes the modal with a default label.
  - `compose`: Composes the layout of the modal.
  - `on_button_pressed`: Handles button press events.
  - `action_cancel`: Dismisses the modal.
  - `on_input_submitted`: Handles input submission.

#### DocManagerApp
- **Purpose**: The main TUI application for managing versioned downloads and renaming files.
- **Methods**:
  - `__init__`: Initializes the application with scan and output directories, LLM model, and Ollama URL.
  - `compose`: Composes the layout of the TUI.
  - `on_button_pressed`: Handles button press events.
  - `_get_selected_version_groups`: Retrieves selected version groups.
  - `_get_selected_rename_groups`: Retrieves selected rename groups.
  - `_do_version_export`: Performs version export.
  - `_do_rename_export`: Performs LLM rename export.
  - `action_select_all`: Selects all files in the current tab.
  - `action_select_none`: Deselects all files in the current tab.

#### Top-Level Functions
- **parse_versioned_name**: Parses a filename into its base name, version, and extension.
- **scan_directory**: Scans a directory and groups files by their base name, filtering for groups with 2+ versions.
- **scan_all_files**: Scans a directory and groups all files by their base name.
- **get_latest**: Retrieves the highest-versioned file from a group.
- **sanitize_id**: Sanitizes a string for use as a Textual widget ID.
- **human_size**: Converts a file size to a human-readable format.
- **ollama_suggest_name**: Sends file content to Ollama and gets a suggested filename.
- **export_latest_versions**: Exports the latest versions of selected groups into a zip file with a manifest.
- **export_llm_renamed**: Exports LLM-renamed files into a zip file with a manifest.

### Main Function
- **main**: The entry point of the application, likely parses command-line arguments and initializes the `DocManagerApp`.

This detailed breakdown provides a comprehensive understanding of the `doc_manager.py` file's structure, functionality, and integration points within the Mythos system.
