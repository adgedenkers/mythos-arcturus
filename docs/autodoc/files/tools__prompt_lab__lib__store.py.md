# tools/prompt_lab/lib/store.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 124

---

### File: tools/prompt_lab/lib/store.py

#### Purpose
This file provides utility functions for saving, loading, listing, and comparing test run results in JSON format. It ensures the results directory exists, saves run data to timestamped JSON files, loads saved runs, lists recent runs, and generates a human-readable diff between two runs.

#### Architecture
The file consists of several top-level functions:
- `ensure_results_dir`: Ensures the results directory exists.
- `save_run`: Saves a test run to a timestamped JSON file.
- `load_run`: Loads a saved run from a JSON file.
- `list_runs`: Lists recent saved runs.
- `diff_runs`: Compares two runs and produces a human-readable diff.

#### Patterns
- **Utility Functions**: Each function serves a specific utility purpose, such as file operations, data serialization, and data comparison.
- **Single Responsibility Principle**: Each function has a single, well-defined responsibility.

#### Dependencies
- `json`: For JSON serialization and deserialization.
- `os`: For interacting with the file system.
- `datetime`: For generating timestamps.
- `pathlib`: For path operations.
- `typing`: For type hints.

#### Interfaces
- `ensure_results_dir()`: Ensures the results directory exists.
- `save_run(run_data: Dict[str, Any], tag: str = "") -> Path`: Saves a test run to a timestamped JSON file and returns the file path.
- `load_run(path: str) -> Dict[str, Any]`: Loads a saved run from a JSON file.
- `list_runs(limit: int = 20) -> List[Dict[str, str]]`: Lists recent saved runs.
- `diff_runs(path_a: str, path_b: str) -> str`: Compares two runs and produces a human-readable diff.

#### Database
- No direct database interactions are present in this file. The file operations are purely file-based and do not interact with PostgreSQL or Neo4j.

#### Configuration
- No configuration files or environment variables are used directly in this file. The results directory path is derived from the file's location.

#### Key Logic
- **Saving and Loading Runs**: The `save_run` function serializes the run data into a JSON file with a timestamped filename. The `load_run` function deserializes the JSON file back into a dictionary.
- **Listing Runs**: The `list_runs` function lists recent runs by sorting files in the results directory and extracting metadata from each file.
- **Diffing Runs**: The `diff_runs` function compares two runs by loading their JSON data, extracting relevant fields, and generating a human-readable diff including score differences, penalties, and average scores.

#### Integration Points
- **File System**: The functions interact with the file system to save and load JSON files.
- **Other Modules**: This file can be imported and used by other parts of the Mythos system to manage test run results. For example, it can be used by testing modules to save and compare test results.

### Detailed Function Descriptions

1. **ensure_results_dir**
   - **Purpose**: Ensures the results directory exists.
   - **Logic**: Creates the results directory if it does not exist.

2. **save_run**
   - **Purpose**: Saves a test run to a timestamped JSON file.
   - **Logic**: Ensures the results directory exists, generates a timestamped filename, and writes the run data to a JSON file.

3. **load_run**
   - **Purpose**: Loads a saved run from a JSON file.
   - **Logic**: Reads the JSON file and returns the deserialized data.

4. **list_runs**
   - **Purpose**: Lists recent saved runs.
   - **Logic**: Ensures the results directory exists, sorts files by timestamp, and extracts metadata from each file.

5. **diff_runs**
   - **Purpose**: Compares two runs and produces a human-readable diff.
   - **Logic**: Loads the JSON data for both runs, compares the data, and generates a detailed diff including score differences, penalties, and average scores.

This file serves as a critical utility for managing and comparing test run results within the Mythos system.
