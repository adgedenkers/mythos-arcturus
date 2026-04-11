# eval/ollama_builder.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 987

---

### File: eval/ollama_builder.py

#### Purpose
This file contains functions and a class to construct prompts for Ollama, call the Ollama model, extract Python code from the model's response, validate the generated code structurally and behaviorally, and compute a composite score based on the validation results.

#### Architecture
The file consists of several top-level functions and a class `ValidationResult`:
- **Top-level Functions**: Functions like `build_prompt`, `call_ollama`, `extract_python`, `validate_structural`, `run_behavioral_tests`, `compute_composite_score`, `compare_to_gold`, `run_challenge`, and `main`.
- **Class**: `ValidationResult` is used to store and manage validation results.

#### Patterns
- **No explicit design patterns**: The code does not explicitly use design patterns like factory, singleton, or observer. It is a straightforward procedural and object-oriented approach.

#### Dependencies
- **Imports**: The file imports various modules such as `argparse`, `ast`, `json`, `os`, `re`, `subprocess`, `sys`, `textwrap`, `time`, `datetime`, `difflib`, `pathlib`, and `typing`.

#### Interfaces
- **Exposed Functions**: The file exposes several functions that can be called from other parts of the system, such as `build_prompt`, `call_ollama`, `extract_python`, `validate_structural`, `run_behavioral_tests`, `compute_composite_score`, `compare_to_gold`, and `run_challenge`.

#### Database
- **References**: The file references several PostgreSQL tables and entities, such as `datetime`, `difflib`, `pathlib`, `typing`, `engine`, `challenge`, `schema`, `Ollama`, `model`, `first`, `markdown`, `file`, `test`, and `gold`.

#### Configuration
- **Environment Variables**: The file does not use any environment variables directly. However, it relies on the `argparse` module to parse command-line arguments.
- **Constants**: The file uses constants like `EVAL_DIR`, `CHALLENGES_DIR`, `RESULTS_DIR`, and `SKILL_MD_PATH` to define paths.

#### Key Logic
- **Prompt Construction**: The `build_prompt` function constructs a prompt for Ollama based on the challenge specification and skill reference.
- **Ollama Integration**: The `call_ollama` function sends a request to the Ollama model and returns the response.
- **Python Code Extraction**: The `extract_python` function extracts Python code from the model's response, handling fenced code blocks and markers.
- **Structural Validation**: The `validate_structural` function parses the generated code and checks for syntax errors, class definitions, required attributes, and the `execute` method.
- **Behavioral Testing**: The `run_behavioral_tests` function writes the generated code to a temporary file, imports it, and runs it against test cases.
- **Composite Scoring**: The `compute_composite_score` function computes a composite score based on structural validation, gold standard comparison, and behavioral tests.
- **Gold Standard Comparison**: The `compare_to_gold` function compares the generated code to a gold standard.
- **Challenge Execution**: The `run_challenge` function orchestrates the entire challenge evaluation loop, including prompt construction, model calls, validation, and scoring.

#### Integration Points
- **Mythos System**: The file integrates with the Mythos system by using the `engine.base` module for skill base classes and by interacting with PostgreSQL tables and entities.
- **Ollama Model**: The file interacts with the Ollama model via HTTP requests to `http://localhost:11434/api/generate`.
- **File System**: The file reads and writes to the file system for challenge specifications, results, and temporary files.

### Detailed Function Descriptions

#### `build_prompt`
- **Purpose**: Constructs the full prompt for Ollama from the challenge specification and skill reference.
- **Parameters**: `spec`, `skill_reference`, `errors`
- **Returns**: A string containing the full prompt.

#### `call_ollama`
- **Purpose**: Sends a request to the Ollama model and returns the response text.
- **Parameters**: `model`, `prompt`, `system`, `temperature`, `timeout`
- **Returns**: A string containing the response text.

#### `extract_python`
- **Purpose**: Extracts Python code from the model's response, stripping any markdown fences.
- **Parameters**: `response`
- **Returns**: A string containing the extracted Python code.

#### `validate_structural`
- **Purpose**: Validates the generated code structurally without executing it.
- **Parameters**: `code`, `spec`
- **Returns**: A `ValidationResult` object containing the validation results.

#### `run_behavioral_tests`
- **Purpose**: Executes the generated skill against test cases and returns a dictionary with pass/fail per test case and an overall behavioral score.
- **Parameters**: `code`, `spec`, `results_dir`, `iteration`, `verbose`
- **Returns**: A dictionary containing the test results and behavioral score.

#### `compute_composite_score`
- **Purpose**: Computes the composite score based on structural validation, gold standard comparison, and behavioral tests.
- **Parameters**: `validation`, `gold_comparison`, `behavioral`
- **Returns**: A tuple containing the composite score and a breakdown dictionary.

#### `compare_to_gold`
- **Purpose**: Compares the generated code to a gold standard.
- **Parameters**: `generated`, `gold_path`
- **Returns**: A string containing the comparison result.

#### `run_challenge`
- **Purpose**: Runs a complete challenge evaluation loop.
- **Parameters**: `challenge_path`, `model`, `max_iterations`, `verbose`, `temperature`
- **Returns**: None

#### `main`
- **Purpose**: Entry point for the script, parses command-line arguments and runs the challenge.
- **Parameters**: None
- **Returns**: None

#### `ValidationResult`
- **Purpose**: Stores and manages validation results.
- **Methods**: `__init__`, `ok`, `score`, `to_dict`
- **Properties**: `ok`, `score`

### Example Usage
```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a challenge evaluation loop.")
    parser.add_argument("--challenge", required=True, help="Path to the challenge spec JSON file.")
    parser.add_argument("--model", required=True, help="Name of the Ollama model to use.")
    parser.add_argument("--max-iterations", type=int, default=5, help="Maximum number of iterations.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("--temperature", type=float, default=0.3, help="Temperature for the Ollama model.")
    args = parser.parse_args()

    run_challenge(args.challenge, args.model, args.max_iterations, args.verbose, args.temperature)
```

This script can be run from the command line to evaluate a challenge using the specified Ollama model and parameters.
