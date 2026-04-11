# tools/iris_test_rig.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 762

---

### File: tools/iris_test_rig.py

#### Purpose
This file contains the implementation for running test suites against AI models using the Iris Test Rig. It assembles a system prompt from real files on disk, freezes it, and uses this prompt to test various models against predefined test cases. The results are scored and summarized.

#### Architecture
The file consists of several top-level functions and constants:
- **Constants**: `DEFAULT_OLLAMA_OPTIONS`, `DEFAULT_USER`, `SERAPHE_USER_INFO`, `SUITES`, `CORPORATE_OPENERS`, `CORPORATE_CLOSERS`, `HEDGING_PHRASES`, `ASSISTANT_PATTERNS`, `META_PATTERNS`.
- **Functions**: `score_response`, `build_frozen_prompt`, `get_pulled_models`, `run_single_test`, `run_suite`, `build_summary`, `main`.

#### Patterns
- **Singleton**: The `Client` object from the `ollama` module is instantiated once and reused.
- **Factory**: The `assemble_system_prompt` function acts as a factory to create the system prompt based on the provided user information and mode.

#### Dependencies
- **Standard Libraries**: `os`, `sys`, `time`, `json`, `argparse`, `datetime`, `typing`, `pathlib`.
- **Mythos Libraries**: `dotenv`, `ollama`, `prompt_assembler`.

#### Interfaces
- **Public Functions**: `score_response`, `build_frozen_prompt`, `get_pulled_models`, `run_single_test`, `run_suite`, `build_summary`.
- **Main Entry Point**: `main` function for command-line execution.

#### Database
- **PostgreSQL Tables**: The file references several tables (`the`, `datetime`, `typing`, `pathlib`, `dotenv`, `ollama`, `prompt_assembler`, `voice`, `what`, `real`, `disk`, `chat_assistant`), but does not directly interact with them. These references are likely placeholders or misinterpretations from the provided metadata.

#### Configuration
- **Environment Variables**: `OLLAMA_HOST` is loaded from `.env` file.
- **Command-line Arguments**: `argparse` is used to parse command-line arguments for specifying models, test suites, and other options.

#### Key Logic
1. **Prompt Assembly**: `build_frozen_prompt` assembles the system prompt from real files on disk and saves it to `~/iris_test_prompt.txt`.
2. **Model Testing**: `run_single_test` sends a single message to a model and measures the response time.
3. **Suite Execution**: `run_suite` runs a series of test cases against a model and collects results.
4. **Response Scoring**: `score_response` evaluates the response text against predefined quality criteria and returns a score dictionary.
5. **Summary Building**: `build_summary` compiles a summary scorecard from the test results.

#### Integration Points
- **Ollama Client**: The `Client` object from the `ollama` module is used to interact with the AI models.
- **Prompt Assembler**: The `assemble_system_prompt` function from `prompt_assembler` is used to build the system prompt.
- **Command-line Interface**: The `main` function integrates with the command-line interface to provide options for running tests and specifying models.

### Detailed Documentation

#### score_response
- **Purpose**: Scores a response against predefined quality criteria and returns a score dictionary.
- **Parameters**: `text` (response text), `test_case` (test case dictionary).
- **Logic**: Evaluates the response for corporate openers, closers, hedging phrases, assistant patterns, and meta patterns. Returns a dictionary with word count, issues, and pass/fail status.

#### build_frozen_prompt
- **Purpose**: Assembles the system prompt from real files on disk and returns the frozen prompt string.
- **Parameters**: `user_info` (user information dictionary), `mode` (mode string), `flag_overrides` (overrides dictionary).
- **Logic**: Uses `assemble_system_prompt` to build the prompt and saves it to `~/iris_test_prompt.txt`.

#### get_pulled_models
- **Purpose**: Retrieves a list of pulled model names, excluding non-chat models.
- **Parameters**: None.
- **Logic**: Filters out non-chat models from the list of available models.

#### run_single_test
- **Purpose**: Sends a single message to a model and returns the response text and elapsed time.
- **Parameters**: `model` (model name), `system_prompt` (system prompt string), `messages_so_far` (conversation history), `user_message` (user message), `options` (options dictionary).
- **Logic**: Uses the `Client` to send the message and measures the response time.

#### run_suite
- **Purpose**: Runs a test suite against a model and appends results to the output.
- **Parameters**: `suite_name` (suite name), `suite_cases` (test cases list), `model` (model name), `system_prompt` (system prompt string), `options` (options dictionary), `output` (output list), `results` (results list), `verbose` (verbose flag).
- **Logic**: Iterates through test cases, runs each test using `run_single_test`, and scores the responses using `score_response`.

#### build_summary
- **Purpose**: Builds a summary scorecard from the test results.
- **Parameters**: `results` (results list), `output` (output list).
- **Logic**: Compiles a summary of the test results and appends it to the output.

#### main
- **Purpose**: Main entry point for command-line execution.
- **Parameters**: None.
- **Logic**: Parses command-line arguments, sets up the test environment, and runs the specified test suites using `run_suite`.
