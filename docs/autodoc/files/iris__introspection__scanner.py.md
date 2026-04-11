# iris/introspection/scanner.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 171

---

### Documentation for `iris/introspection/scanner.py`

#### Purpose
This file contains functions to scan files and directories within the Mythos codebase, determine which component each file belongs to, and generate metadata for each file. It also groups the scanned files by their respective components.

#### Architecture
The file consists of several top-level functions:
1. `detect_component`: Determines the component a file belongs to based on its path.
2. `file_hash`: Computes the SHA-256 hash of a file's content.
3. `scan_file`: Scans a single file and returns its metadata.
4. `scan_directory`: Walks through a directory, scans each file, and collects metadata.
5. `group_by_component`: Groups the scanned files by their components.

The functions are designed to be modular and reusable, with clear separation of concerns.

#### Patterns
- **No explicit design patterns**: The code does not explicitly follow any design patterns like factory, singleton, or observer. It is a straightforward procedural approach.

#### Dependencies
- **Imports**:
  - `os`: For file system operations.
  - `hashlib`: For computing file hashes.
  - `logging`: For logging.
  - `pathlib`: For path manipulations.
  - `datetime`: For handling timestamps.

#### Interfaces
- **Exposed Functions**:
  - `detect_component(file_path: str, base_path: str = "/opt/mythos") -> str`
  - `file_hash(file_path: str) -> str`
  - `scan_file(file_path: str, base_path: str = "/opt/mythos") -> dict`
  - `scan_directory(base_path: str = "/opt/mythos", target_path: str = None) -> list[dict]`
  - `group_by_component(file_list: list[dict]) -> dict[str, list[dict]]`

#### Database
- **Database References**:
  - The file does not directly interact with the database tables mentioned (`pathlib`, `datetime`, `patch`, `integrity`). These references are likely placeholders or misinterpretations from the analysis tool.

#### Configuration
- **Configuration**:
  - No explicit configuration files or environment variables are used. The base path `/opt/mythos` is hardcoded.

#### Key Logic
- **Component Detection**: Uses a predefined `COMPONENT_MAP` to map directory prefixes to component names.
- **File Hashing**: Computes SHA-256 hash of file content for change detection and deduplication.
- **File Scanning**: Collects metadata such as file path, component, file type, size, line count, last modified timestamp, and content hash.
- **Directory Scanning**: Walks through directories, skipping certain directories and file types, and collects metadata for each file.
- **Grouping by Component**: Groups the scanned files by their components for easier management and analysis.

#### Integration Points
- **Integrity Scanner Integration**: Tries to use an existing `integrity.file_scanner` if available, falling back to its own scanning logic if the integration fails.
- **Logging**: Uses the `logging` module to log information and warnings during the scanning process.

### Detailed Function Descriptions

1. **`detect_component(file_path: str, base_path: str = "/opt/mythos") -> str`**
   - **Purpose**: Determines which component a file belongs to based on its path.
   - **Logic**: Uses the `COMPONENT_MAP` to map the first directory in the relative path to a component name.

2. **`file_hash(file_path: str) -> str`**
   - **Purpose**: Computes the SHA-256 hash of a file's content.
   - **Logic**: Reads the file in chunks and updates the hash object.

3. **`scan_file(file_path: str, base_path: str = "/opt/mythos") -> dict`**
   - **Purpose**: Scans a single file and returns its metadata.
   - **Logic**: Collects metadata such as file path, component, file type, size, line count, last modified timestamp, and content hash.

4. **`scan_directory(base_path: str = "/opt/mythos", target_path: str = None) -> list[dict]`**
   - **Purpose**: Walks through a directory, scans each file, and collects metadata.
   - **Logic**: Tries to use an existing `integrity.file_scanner` if available, falling back to its own scanning logic if the integration fails. Skips certain directories and file types, and collects metadata for each file.

5. **`group_by_component(file_list: list[dict]) -> dict[str, list[dict]]`**
   - **Purpose**: Groups the scanned files by their components.
   - **Logic**: Uses a dictionary to group files by their component names.

This file is a crucial part of the Mythos system, providing the necessary functionality to scan and analyze the codebase, which can be used for various purposes such as dependency management, change tracking, and code analysis.
