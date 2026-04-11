# orchestrator/src/bench/test_runner.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 361

---

### File: orchestrator/src/bench/test_runner.py

#### Purpose
This file contains the `TestRunner` class, which is responsible for executing test suites against AI models, grading the responses, and storing the results in a PostgreSQL database.

#### Architecture
The `TestRunner` class is the main component of this file. It includes methods for initializing the runner, running test suites, saving and updating runs and results in the database, and retrieving runs from the database. The class coordinates the loading of test suites, generating responses from models, grading the answers, and storing the results.

#### Patterns
- **Factory Method**: The `TestLoader` is used to load test suites, acting as a factory for test suite objects.
- **Singleton**: The `ModelRegistry` is used to manage and retrieve model information, potentially acting as a singleton to ensure consistent model information across the system.

#### Dependencies
- **Imports**: `asyncio`, `time`, `logging`, `sys`, `os`, `database`, `utils`, `models.ollama_client`, `models.model_registry`, `bench.test_loader`, `bench.test_suite`, `bench.grader`, `bench.test_run`.
- **Database**: PostgreSQL tables `orch_test_runs` and `orch_test_results`.

#### Interfaces
- **Public Methods**:
  - `__init__`: Initializes the test runner.
  - `run_suite`: Executes a test suite against a model.
  - `get_run`: Retrieves a test run from the database.
  - `list_runs`: Lists test runs with optional filtering by suite ID and model ID.

#### Database
- **Tables**:
  - `orch_test_runs`: Stores metadata about test runs.
  - `orch_test_results`: Stores individual results of test questions.

#### Configuration
- **Environment Variables**: None explicitly mentioned.
- **Config Files**: None explicitly mentioned.

#### Key Logic
- **Test Execution**:
  - Loads the test suite from the database if provided by `suite_id`.
  - Determines the model ID from the model name.
  - Executes each question in the test suite using the `OllamaClient` to generate responses.
  - Grades the responses using the `Grader` class.
  - Stores the results in the database if `save_to_db` is `True`.
- **Database Operations**:
  - `_save_run_to_db`: Inserts a new test run into the `orch_test_runs` table.
  - `_update_run_in_db`: Updates the status and statistics of a test run in the `orch_test_runs` table.
  - `_save_result_to_db`: Inserts individual test results into the `orch_test_results` table.
  - `get_run`: Retrieves a test run and its results from the `orch_test_runs` and `orch_test_results` tables.
  - `list_runs`: Retrieves a list of test runs with optional filtering.

#### Integration Points
- **TestLoader**: Loads test suites from the database.
- **OllamaClient**: Generates model responses.
- **Grader**: Grades the model responses.
- **ModelRegistry**: Manages model information.
- **Database**: Stores and retrieves test run metadata and results.
- **Utils**: Provides utility functions like `generate_id` and JSON handling.

### Summary
The `TestRunner` class in `test_runner.py` is a crucial component of the Mythos system, responsible for orchestrating the execution of test suites against AI models, grading the responses, and storing the results in a PostgreSQL database. It integrates with various subsystems like `TestLoader`, `OllamaClient`, `Grader`, and `ModelRegistry` to perform its tasks efficiently.
