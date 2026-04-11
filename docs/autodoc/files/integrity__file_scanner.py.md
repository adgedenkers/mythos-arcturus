# integrity/file_scanner.py

**Language:** python
**Stream:** SYS
**Module:** Integrity Scanner
**Lines:** 286

---

### File: `integrity/file_scanner.py`

#### Purpose
The `file_scanner.py` module is responsible for walking the Mythos directory tree, computing SHA-256 hashes for files, and merging `File` and `Directory` nodes into Neo4j. It also detects orphan files (files on disk but not in the graph) and ghost nodes (nodes in the graph but not on disk).

#### Architecture
The module consists of several top-level functions:
- `compute_sha256`: Computes the SHA-256 hash of a file.
- `should_skip_dir`: Determines if a directory should be skipped during the scan.
- `should_skip_file`: Determines if a file should be skipped based on its name or extension.
- `scan_files`: Walks the directory tree, merges nodes into Neo4j, and returns scan statistics.
- `_merge_directory`: Merges a directory node into Neo4j.
- `_link_directory_parent`: Creates a `CHILD_OF` relationship between directories.
- `_merge_file`: Merges a file node into Neo4j and returns its status.
- `_link_file_to_directory`: Creates an `IN_DIRECTORY` relationship.
- `_mark_missing_files`: Marks files that are in the graph but not on disk as "missing".

#### Patterns
- **Singleton Pattern**: The `get_driver` function likely returns a singleton Neo4j driver instance.
- **Factory Method**: The `compute_sha256` function can be seen as a factory method for generating SHA-256 hashes.

#### Dependencies
- `os`: For directory and file operations.
- `hashlib`: For computing SHA-256 hashes.
- `logging`: For logging messages.
- `datetime`: For timestamp operations.
- `pathlib`: For path operations.
- `integrity.graph`: For Neo4j driver and query functions (`get_driver`, `run_write`, `run_query`).

#### Interfaces
- `compute_sha256(filepath: str) -> str`: Computes the SHA-256 hash of a file.
- `should_skip_dir(dirname: str) -> bool`: Determines if a directory should be skipped.
- `should_skip_file(filename: str) -> bool`: Determines if a file should be skipped.
- `scan_files(root: str = None, driver=None) -> dict`: Walks the directory tree, merges nodes into Neo4j, and returns scan statistics.

#### Database
- **Neo4j Labels**:
  - `IntegrityDirectory`: Represents directories.
  - `IntegrityFile`: Represents files.
- **Neo4j Relationships**:
  - `CHILD_OF`: Represents the parent-child relationship between directories.
  - `IN_DIRECTORY`: Represents the relationship between a file and its directory.

#### Configuration
- `MYTHOS_ROOT`: The root directory for the Mythos system, defaulting to `/opt/mythos` if not set in the environment.

#### Key Logic
- **Directory and File Scanning**: The `scan_files` function walks the directory tree, skipping certain directories and files based on predefined rules.
- **SHA-256 Hashing**: The `compute_sha256` function computes the SHA-256 hash of a file.
- **Node Merging**: The `_merge_directory` and `_merge_file` functions merge directory and file nodes into Neo4j, respectively.
- **Relationship Creation**: The `_link_directory_parent` and `_link_file_to_directory` functions create relationships between nodes.
- **Missing File Detection**: The `_mark_missing_files` function marks files that are in the graph but not on disk as "missing".

#### Integration Points
- **Neo4j Driver**: The module integrates with the Neo4j driver to perform database operations.
- **Logging**: The module uses the `logging` module to log messages.
- **Environment Variables**: The module reads the `MYTHOS_ROOT` environment variable to determine the root directory for scanning.

This module is a crucial part of the Mythos system's integrity subsystem, ensuring that the file system is accurately represented in the Neo4j graph database.
