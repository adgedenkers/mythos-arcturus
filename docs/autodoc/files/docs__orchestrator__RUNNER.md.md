# docs/orchestrator/RUNNER.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 420

---

### Purpose
The `RUNNER.md` file documents the Test Execution Engine (TestRunner) component of the Mythos system, detailing its functionality, usage, and integration with other parts of the system. It provides comprehensive information on how to load, execute, and store test results, as well as how to interact with the database and handle errors.

### Architecture
The Test Execution Engine is composed of two primary components:
1. **TestRun**: A container for test run results and statistics.
2. **TestRunner**: The main execution engine responsible for running test suites against AI models and storing results.

#### TestRun
- **Methods**:
  - `start()`: Marks the start of a test run.
  - `complete()`: Marks the completion of a test run.
  - `add_result()`: Adds individual test results to the run.
  - `get_statistics()`: Retrieves statistics about the test run.

#### TestRunner
- **Methods**:
  - `run_suite()`: Executes a test suite against a specified model.
  - `get_run()`: Retrieves a specific test run from the database.
  - `list_runs()`: Lists recent test runs with optional filters.

### Patterns
- **Factory**: The `TestRun` and `TestRunner` classes can be seen as factory patterns that create and manage test runs.
- **Observer**: The `run_suite` method supports a `progress_callback` function, which can be seen as an observer pattern to track progress.

### Dependencies
- **Imports**: The file imports classes and functions from the `bench` module, such as `TestRunner`, `TestSuite`, `TestQuestion`, and `TestLoader`.
- **External Libraries**: Uses `asyncio` for asynchronous operations.

### Interfaces
- **Public Methods**:
  - `TestRun`: `start()`, `complete()`, `add_result()`, `get_statistics()`
  - `TestRunner`: `run_suite()`, `get_run()`, `list_runs()`

### Database
- **Tables**:
  - `orch_test_runs`: Stores test run metadata.
  - `orch_test_results`: Stores individual test results.

### Configuration
- **Environment Variables**: No specific environment variables are mentioned in the documentation.
- **Config Files**: No specific configuration files are mentioned.

### Key Logic
- **Test Execution**: The `run_suite` method executes a test suite against a specified AI model and stores the results in the database.
- **Progress Tracking**: Supports a `progress_callback` to track the progress of test execution.
- **Error Handling**: Continues execution even if individual questions fail, but raises exceptions for critical errors like non-existent suites.

### Integration Points
- **TestLoader**: Used to load test suites from the database.
- **Database**: Integrates with PostgreSQL to store and retrieve test run data.
- **AI Models**: Interacts with AI models specified by `model_name` and `model_params`.

### Detailed Analysis

#### Overview
The TestRunner is responsible for loading test suites, executing tests against AI models, grading responses, storing results in the database, and tracking performance metrics.

#### Quick Start
Provides a simple example of creating a test suite, running it, and checking the results.

#### TestRun
- **Creating a Run**: Demonstrates initializing a `TestRun` object and marking the start and completion of a run.
- **Adding Results**: Shows how to add individual test results to a run.
- **Statistics**: Retrieves and displays statistics about the test run.

#### TestRunner
- **Basic Usage**: Demonstrates running a test suite from the database.
- **Progress Tracking**: Uses a `progress_callback` to track progress.
- **Custom Model Parameters**: Allows specifying custom parameters for the AI model.
- **Without Database Storage**: Option to run tests without storing results in the database.

#### Loading Past Runs
- **Get Specific Run**: Retrieves a specific test run by ID.
- **List Recent Runs**: Lists recent test runs with optional filters.

#### Complete Example
Provides a comprehensive example of benchmarking multiple AI models against a test suite.

#### Database Schema
Describes the schema for storing test runs and individual results in PostgreSQL.

#### Error Handling
Explains how the TestRunner handles errors gracefully and provides examples of handling exceptions.

#### Performance Tips
Offers tips for parallel testing and batch processing to optimize performance.

#### Integration Example
Demonstrates the full workflow from creating a test suite to running tests and viewing results.

#### Next Steps
Outlines future phases for adding pre-built test suites and automated benchmarking.

### Conclusion
The `RUNNER.md` file serves as a comprehensive guide to the Test Execution Engine within the Mythos system, detailing its architecture, usage, and integration with other components. It provides clear examples and explanations to help users effectively utilize the TestRunner for testing AI models.
