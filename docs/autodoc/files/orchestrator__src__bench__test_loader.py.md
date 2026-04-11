# orchestrator/src/bench/test_loader.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 302

---

### Documentation for `orchestrator/src/bench/test_loader.py`

#### Purpose
The `TestLoader` class in `test_loader.py` is responsible for loading and saving test suites from JSON files and a PostgreSQL database. It provides methods to handle both file-based and database-based storage of test suites.

#### Architecture
The `TestLoader` class contains several methods to manage test suite data:
- `__init__`: Initializes the `TestLoader` instance, setting up the directory for JSON files.
- `load_from_json`: Loads a test suite from a JSON file.
- `save_to_json`: Saves a test suite to a JSON file.
- `load_from_database`: Loads a test suite from the PostgreSQL database.
- `save_to_database`: Saves a test suite to the PostgreSQL database.
- `list_suites`: Lists available test suites from the database.
- `list_json_files`: Lists available JSON test suite files.

#### Patterns
- **Singleton Pattern**: The `TestLoader` class can be used as a singleton to manage test suite operations across the system.
- **Factory Pattern**: The `TestLoader` class acts as a factory for creating `TestSuite` instances from different sources.

#### Dependencies
- `json`: For JSON serialization and deserialization.
- `logging`: For logging operations.
- `sys`: For manipulating the system path.
- `os`: For file system operations.
- `Path` from `pathlib`: For handling file paths.
- `settings` from `config`: For configuration settings.
- `db` from `database`: For database operations.
- `generate_id`, `safe_json_dumps`, `safe_json_loads` from `utils`: For utility functions.
- `TestQuestion` from `bench.test_question`: For handling individual test questions.
- `TestSuite` from `bench.test_suite`: For handling test suites.

#### Interfaces
- `load_from_json(filepath: str) -> TestSuite`: Loads a test suite from a JSON file.
- `save_to_json(suite: TestSuite, filepath: Optional[str] = None) -> Path`: Saves a test suite to a JSON file.
- `load_from_database(suite_id: str) -> TestSuite`: Loads a test suite from the database.
- `save_to_database(suite: TestSuite) -> str`: Saves a test suite to the database.
- `list_suites(category: Optional[str] = None, public_only: bool = True) -> List[Dict[str, Any]]`: Lists available test suites from the database.
- `list_json_files(category: Optional[str] = None) -> List[Path]`: Lists available JSON test suite files.

#### Database
- **Tables**: `orch_test_suites`, `orch_test_questions`
- **Operations**:
  - `orch_test_suites`: Insert, Update, Select
  - `orch_test_questions`: Insert, Select, Delete

#### Configuration
- `settings.TEST_SUITES_DIR`: Directory for storing JSON test suite files.

#### Key Logic
- **Validation**: Before saving or loading, the `TestSuite` instance is validated to ensure it meets the required criteria.
- **Database Operations**: Uses asynchronous database operations to load and save test suites, ensuring non-blocking I/O operations.
- **File Operations**: Handles file paths and ensures the directory structure is maintained.

#### Integration Points
- **Database**: Integrates with the PostgreSQL database to store and retrieve test suite metadata and questions.
- **File System**: Integrates with the file system to store and retrieve JSON files.
- **Configuration**: Uses configuration settings to determine the directory for JSON files.
- **Test Suite and Question Models**: Integrates with `TestSuite` and `TestQuestion` models to handle test suite data.

### Summary
The `TestLoader` class in `test_loader.py` is a critical component of the Mythos system, providing a robust interface for managing test suites through both JSON files and a PostgreSQL database. It ensures data integrity through validation and leverages asynchronous operations for efficient database interactions.
