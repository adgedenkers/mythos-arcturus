# eval/ollama_grinder.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 520

---

### Documentation for `eval/ollama_grinder.py`

#### Purpose
This file implements the Ollama Grinder, a multi-pass build engine that takes a build plan, feeds each step to a local Ollama model with cumulative context, tests the output after each step, and loops on the final step until all tests pass.

#### Architecture
The file consists of several top-level functions that handle different aspects of the build process:
- `build_pass_prompt`: Constructs the prompt for a single build pass.
- `call_ollama`: Invokes the Ollama model and returns the response.
- `extract_python`: Extracts Python code from the model's response.
- `run_parse_check`: Checks if the generated code parses as valid Python.
- `run_import_check`: Ensures the code has the required `SkillBase` structure.
- `run_behavioral_test`: Runs behavioral tests on the generated code.
- `grind`: Executes the full build plan step by step.
- `main`: Entry point for the script.

#### Patterns
- **No specific design patterns**: The file primarily consists of utility functions and does not implement any specific design patterns like factory, singleton, or observer.

#### Dependencies
- **Imports**: `argparse`, `ast`, `json`, `os`, `re`, `subprocess`, `sys`, `textwrap`, `time`, `datetime`, `pathlib`, `typing`
- **External Services**: Ollama model via HTTP requests

#### Interfaces
- **Exposed Functions**: `build_pass_prompt`, `call_ollama`, `extract_python`, `run_parse_check`, `run_import_check`, `run_behavioral_test`, `grind`
- **Entry Point**: `main` function

#### Database
- **PostgreSQL Tables**: `a`, `ollama_builder`, `scratch`, `zero`, `datetime`, `pathlib`, `typing`, `previous`, `SCHEMA`, `LAST`, `model`, `engine`

#### Configuration
- **Environment Variables**: None explicitly used
- **Configuration Files**: `build_plan.json` (specified via command-line argument)

#### Key Logic
- **Build Pass Prompt Construction**: `build_pass_prompt` constructs the prompt for each build pass, incorporating previous code, context, and errors.
- **Ollama Model Invocation**: `call_ollama` sends the prompt to the Ollama model and retrieves the response.
- **Python Code Extraction**: `extract_python` extracts the Python code from the model's response.
- **Code Validation**: `run_parse_check` and `run_import_check` validate the generated code for syntax and structure.
- **Behavioral Testing**: `run_behavioral_test` runs the generated code against test cases to ensure it behaves as expected.
- **Grinder Engine**: `grind` orchestrates the entire build process, iterating over build steps, invoking the model, and validating the output.

#### Integration Points
- **Ollama Model**: The file integrates with the Ollama model via HTTP requests to generate Python code.
- **PostgreSQL Database**: The file interacts with several PostgreSQL tables to manage build plans, context, and results.
- **File System**: The file reads build plans from JSON files and writes generated code and test results to the file system.
- **Command Line**: The `main` function parses command-line arguments to configure the build process.

### Detailed Analysis of Functions

#### `build_pass_prompt`
- **Purpose**: Constructs the prompt for a single build pass.
- **Parameters**: `pass_info`, `current_code`, `context`, `errors`
- **Logic**: Combines the current code, build instructions, context, and errors into a single prompt string.

#### `call_ollama`
- **Purpose**: Invokes the Ollama model and returns the response.
- **Parameters**: `model`, `prompt`, `system`, `temperature`, `timeout`
- **Logic**: Sends a POST request to the Ollama model with the provided parameters and returns the response.

#### `extract_python`
- **Purpose**: Extracts Python code from the model's response.
- **Parameters**: `response`
- **Logic**: Uses regular expressions to extract Python code from the response string.

#### `run_parse_check`
- **Purpose**: Checks if the generated code parses as valid Python.
- **Parameters**: `code`
- **Logic**: Uses `ast.parse` to validate the code and returns a dictionary indicating success or failure.

#### `run_import_check`
- **Purpose**: Ensures the code has the required `SkillBase` structure.
- **Parameters**: `code`
- **Logic**: Parses the code and checks for the presence of a `SkillBase` subclass and an `async execute` method.

#### `run_behavioral_test`
- **Purpose**: Runs the generated code against test cases.
- **Parameters**: `code`, `test_cases`, `results_dir`
- **Logic**: Writes the code and test cases to temporary files, runs a test script, and collects the results.

#### `grind`
- **Purpose**: Executes the full build plan step by step.
- **Parameters**: `plan_path`, `model`, `max_retries`, `verbose`, `temperature`
- **Logic**: Reads the build plan, iterates over build steps, invokes the model, and validates the output.

#### `main`
- **Purpose**: Entry point for the script.
- **Parameters**: None
- **Logic**: Parses command-line arguments and calls the `grind` function with the provided configuration.
