# tools/orchestration_test.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 1101

---

### File: tools/orchestration_test.py

#### Purpose
This file contains a test harness for evaluating the effectiveness of different AI models in generating a Python CLI tool for a Spiral Time Calculator. It orchestrates three rounds of testing: raw model output, model output with a constitution, and an orchestrated design and code generation process.

#### Architecture
The file consists of several top-level functions that handle different aspects of the testing process:
- `extract_python`: Extracts Python code from a model response.
- `score_code`: Scores the generated code on multiple quality dimensions.
- `test_execution`: Tests if the code runs and is importable.
- `test_math`: Tests the correctness of the Spiral Time math.
- `call_model`: Calls a model and returns the response.
- `call_model_multiturn`: Calls a model with a full message history.
- `run_round1`, `run_round2`, `run_round3`: Execute the three rounds of testing.
- `build_comparison`: Builds the final comparison table.
- `main`: The main entry point for the script.

#### Patterns
- **Factory Method**: The `call_model` and `call_model_multiturn` functions can be seen as factory methods for generating model responses.
- **Singleton**: The `Client` object from the `ollama` module is instantiated once and reused.

#### Dependencies
- **Standard Libraries**: `os`, `sys`, `ast`, `time`, `json`, `shutil`, `argparse`, `subprocess`, `tempfile`.
- **Third-party Libraries**: `pathlib`, `dotenv`, `ollama`.

#### Interfaces
- **Functions**: The file exposes several functions that can be called from other parts of the system, such as `extract_python`, `score_code`, `test_execution`, `test_math`, `call_model`, `call_model_multiturn`, `run_round1`, `run_round2`, `run_round3`, `build_comparison`, and `main`.

#### Database
- **PostgreSQL**: The file references several tables and labels in PostgreSQL, but these references are likely placeholders or misinterpretations of the actual code. The actual database interactions are not present in the provided code snippet.

#### Configuration
- **Environment Variables**: The file uses `os.getenv` to load environment variables, particularly `OLLAMA_HOST`.
- **Dotenv**: The `dotenv` library is used to load environment variables from a `.env` file located at `/opt/mythos/.env`.

#### Key Logic
- **Model Calls**: The `call_model` and `call_model_multiturn` functions handle the interaction with AI models to generate code.
- **Code Scoring**: The `score_code` function evaluates the generated code on multiple dimensions, including syntax, execution, math correctness, and adherence to design principles.
- **Execution Testing**: The `test_execution` function checks if the generated code runs and is importable.
- **Math Testing**: The `test_math` function verifies the correctness of the Spiral Time math calculations.
- **Round Execution**: The `run_round1`, `run_round2`, and `run_round3` functions execute the three rounds of testing, each with different configurations and prompts.

#### Integration Points
- **Ollama Client**: The file integrates with the `ollama` client to call AI models.
- **File System**: The file interacts with the file system to write and read generated code and results.
- **Command Line Interface**: The `argparse` module is used to handle command-line arguments for running specific rounds or models.

### Summary
This file serves as a comprehensive test harness for evaluating the effectiveness of different AI models in generating a Python CLI tool for a Spiral Time Calculator. It orchestrates three rounds of testing, each with different configurations and prompts, and evaluates the generated code on multiple quality dimensions. The file integrates with the `ollama` client to call AI models and interacts with the file system to manage generated code and results.
