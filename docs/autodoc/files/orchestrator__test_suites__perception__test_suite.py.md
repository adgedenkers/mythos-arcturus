# orchestrator/test_suites/perception/test_suite.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 541

---

### File: orchestrator/test_suites/perception/test_suite.py

#### Purpose
This file contains a test suite for validating the output of different models in the perception module of the Mythos system. It tests the JSON output, schema compliance, and classification accuracy of the models against predefined test messages.

#### Architecture
The file consists of several top-level functions that handle different aspects of the testing process:
- `validate_json_parseable`: Validates and parses JSON from raw LLM output.
- `validate_schema`: Validates the schema of the parsed JSON.
- `validate_expectations`: Validates test-specific expectations.
- `query_ollama`: Queries the Ollama model via CLI.
- `get_available_models`: Retrieves a list of available models from Ollama.
- `format_user_message`: Formats the user prompt from a test case.
- `run_tests`: Runs all test messages against all models at different temperatures.
- `print_report`: Prints a summary and details of the test results.
- `save_results`: Saves the full test results to a JSON file.
- `main`: The main function that orchestrates the test suite.

#### Patterns
- **No specific design patterns**: The file primarily consists of utility functions and does not follow any specific design patterns like factory, singleton, or observer.

#### Dependencies
- **Imports**: `json`, `time`, `sys`, `argparse`, `subprocess`, `datetime`
- **External Dependencies**: Ollama CLI, PostgreSQL database

#### Interfaces
- **Exposed Functions**: `validate_json_parseable`, `validate_schema`, `validate_expectations`, `query_ollama`, `get_available_models`, `format_user_message`, `run_tests`, `print_report`, `save_results`, `main`
- **CLI Interface**: The `main` function accepts command-line arguments for specifying models and temperatures.

#### Database
- **PostgreSQL Tables**: `datetime`, `perception_template`, `Seraphe`, `raw`, `Ollama`, `test`, `print`

#### Configuration
- **Environment Variables**: None
- **Configuration Files**: None

#### Key Logic
1. **JSON Parsing and Validation**: The `validate_json_parseable` function ensures that the raw text output from the LLM can be parsed into valid JSON, handling common issues like markdown fences and leading/trailing text.
2. **Schema Validation**: The `validate_schema` function checks that the parsed JSON contains all required fields and that the values fall within expected ranges and enums.
3. **Expectation Validation**: The `validate_expectations` function checks that the parsed JSON meets specific expectations defined for each test case.
4. **Model Querying**: The `query_ollama` function sends a query to the Ollama model via CLI and measures the response time.
5. **Test Execution**: The `run_tests` function orchestrates the execution of all test messages against all available models at different temperatures.
6. **Result Reporting**: The `print_report` function prints a summary of the test results, and the `save_results` function saves the full results to a JSON file.

#### Integration Points
- **Ollama CLI**: The `query_ollama` function interacts with the Ollama model via the CLI to get responses.
- **PostgreSQL Database**: The file references several PostgreSQL tables, indicating that it integrates with the database to retrieve and store test messages and results.
- **Command-Line Interface**: The `main` function integrates with the command-line interface to accept user input for specifying models and temperatures.

### Summary
This file serves as a comprehensive test suite for the perception module of the Mythos system, ensuring that the output from various models is valid, compliant with the expected schema, and meets specific expectations. It integrates with the Ollama model via CLI and interacts with a PostgreSQL database to manage test messages and results.
