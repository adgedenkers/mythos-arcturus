# workers/tests/perception_test_suite.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 541

---

### Purpose
The `perception_test_suite.py` file is a test suite designed to validate the output of various models from Ollama when processing test messages. It ensures that the JSON output is parseable, conforms to a predefined schema, and meets specific expectations for each test case.

### Architecture
The file consists of several top-level functions that handle different aspects of the testing process:
- `validate_json_parseable`: Parses JSON from raw LLM output.
- `validate_schema`: Validates the JSON schema.
- `validate_expectations`: Checks test-specific expectations.
- `query_ollama`: Queries Ollama via CLI.
- `get_available_models`: Retrieves a list of available models from Ollama.
- `format_user_message`: Builds the user prompt from test cases.
- `run_tests`: Runs all test messages against all models at specified temperatures.
- `print_report`: Prints a summary and details of the test results.
- `save_results`: Saves full test results to a JSON file.
- `main`: The entry point of the script.

### Patterns
No specific design patterns are used in this file. The functions are straightforward and procedural.

### Dependencies
The file imports the following modules:
- `json`: For JSON parsing and manipulation.
- `time`: For time-related operations.
- `sys`: For system-specific parameters and functions.
- `argparse`: For parsing command-line arguments.
- `subprocess`: For executing subprocesses.
- `datetime`: For date and time operations.

### Interfaces
The file exposes the following functions to other parts of the system:
- `validate_json_parseable`
- `validate_schema`
- `validate_expectations`
- `query_ollama`
- `get_available_models`
- `format_user_message`
- `run_tests`
- `print_report`
- `save_results`
- `main`

### Database
The file references the following PostgreSQL tables:
- `datetime`
- `perception_template`
- `Seraphe`
- `raw`
- `Ollama`
- `test`
- `print`

### Configuration
The file uses the following configuration:
- Command-line arguments for specifying models and temperatures.
- Environment variables are not used directly in this file.

### Key Logic
1. **JSON Parsing and Validation**:
   - `validate_json_parseable`: Strips common issues from raw text and parses JSON.
   - `validate_schema`: Checks for required fields, valid enums, and range constraints.
   - `validate_expectations`: Compares parsed JSON against expected values for each test case.

2. **Ollama Interaction**:
   - `query_ollama`: Queries Ollama via CLI and measures response time.
   - `get_available_models`: Retrieves a list of available models from Ollama.

3. **Test Execution**:
   - `run_tests`: Iterates over test messages, models, and temperatures, and collects results.
   - `print_report`: Prints a summary and details of the test results.
   - `save_results`: Saves full test results to a JSON file.

### Integration Points
- **Ollama**: The file interacts with Ollama via CLI to query models and retrieve responses.
- **PostgreSQL**: The file references several PostgreSQL tables for data storage and retrieval.
- **Command-line Interface**: The file accepts command-line arguments for specifying models and temperatures.

### Summary
The `perception_test_suite.py` file is a comprehensive test suite for validating the output of Ollama models. It ensures that the JSON output is correctly formatted, conforms to a predefined schema, and meets specific expectations for each test case. The file integrates with Ollama via CLI and PostgreSQL for data storage and retrieval.
