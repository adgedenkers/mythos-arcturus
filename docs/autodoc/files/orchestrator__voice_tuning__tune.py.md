# orchestrator/voice_tuning/tune.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 628

---

### File: orchestrator/voice_tuning/tune.py

#### Purpose
This file contains the logic for tuning the voice of the AI model "Iris" by running a series of voice tasks against the model, judging the responses, and storing the results. It also provides functionality to compare different tuning iterations and list past iterations.

#### Architecture
The file consists of several top-level functions and a class `JSONLWriter`:
- **Top-level Functions**:
  - `build_system_prompt`: Assembles a system prompt from enabled layers in `prompt_layers.yaml`.
  - `call_ollama`: Sends a request to the Ollama API to get a response from the model.
  - `judge_response`: Evaluates the model's response based on a predefined rubric.
  - `run_tuning`: Executes the tuning process for a given model and task filter.
  - `compare_runs`: Compares two tuning iterations.
  - `list_runs`: Lists all past tuning iterations.
  - `main`: Entry point for the script.
  - `load_summary`: Loads the summary of a tuning run.
- **Class**:
  - `JSONLWriter`: A class for writing records to a JSONL file.

#### Patterns
- **Factory Method**: The `build_system_prompt` function can be seen as a factory method that dynamically constructs the system prompt based on the configuration.
- **Singleton**: The `JSONLWriter` class could be used as a singleton to manage the writing process to a JSONL file.

#### Dependencies
- **Imports**: `os`, `sys`, `json`, `uuid`, `time`, `yaml`, `argparse`, `threading`, `requests`, `pathlib`, `datetime`, `typing`.
- **External Services**: Ollama API (`http://localhost:11434`).

#### Interfaces
- **Exposed Functions**: `build_system_prompt`, `call_ollama`, `judge_response`, `run_tuning`, `compare_runs`, `list_runs`, `load_summary`.
- **Class Methods**: `JSONLWriter.__init__`, `JSONLWriter.write`.

#### Database
- **References**: The file does not directly interact with the database but references `prompt_layers.yaml` and other files on disk.

#### Configuration
- **Config Files**: `prompt_layers.yaml`, `personality.yaml`, `voice.yaml`.
- **Environment Variables**: None explicitly used.

#### Key Logic
- **Prompt Assembly**: The `build_system_prompt` function reads `prompt_layers.yaml` and assembles a system prompt from all enabled layers.
- **Ollama API Call**: The `call_ollama` function sends a request to the Ollama API to get a response from the model.
- **Response Judging**: The `judge_response` function evaluates the model's response based on a predefined rubric.
- **Tuning Process**: The `run_tuning` function orchestrates the tuning process, including calling the model, judging the responses, and storing the results.
- **Comparison and Listing**: The `compare_runs` and `list_runs` functions provide functionality to compare different tuning iterations and list past iterations.

#### Integration Points
- **Ollama API**: The file integrates with the Ollama API to get responses from the AI model.
- **File System**: The file reads and writes to various files on disk, including `prompt_layers.yaml`, `personality.yaml`, `voice.yaml`, and JSONL files for storing results.
- **Command Line Interface**: The `main` function provides a command-line interface for running the tuning process, comparing iterations, and listing past iterations.

### Detailed Analysis

#### `build_system_prompt` Function
- **Purpose**: Assembles a system prompt from enabled layers in `prompt_layers.yaml`.
- **Logic**: Reads `prompt_layers.yaml`, checks if each layer is enabled, and reads the corresponding file content to build the prompt.

#### `call_ollama` Function
- **Purpose**: Sends a request to the Ollama API to get a response from the model.
- **Logic**: Constructs a JSON payload with the system prompt and user message, sends a POST request to the Ollama API, and returns the response.

#### `judge_response` Function
- **Purpose**: Evaluates the model's response based on a predefined rubric.
- **Logic**: Uses the `judge_rubric` associated with the task to score the response.

#### `run_tuning` Function
- **Purpose**: Executes the tuning process for a given model and task filter.
- **Logic**: Iterates over the voice tasks, calls the model, judges the responses, and stores the results.

#### `compare_runs` Function
- **Purpose**: Compares two tuning iterations.
- **Logic**: Loads the summary files of the two iterations and compares the results.

#### `list_runs` Function
- **Purpose**: Lists all past tuning iterations.
- **Logic**: Reads the directory containing past runs and lists them.

#### `JSONLWriter` Class
- **Purpose**: Writes records to a JSONL file.
- **Methods**: `__init__` initializes the writer with a path, `write` writes a record to the file.

#### `main` Function
- **Purpose**: Entry point for the script, providing a command-line interface.
- **Logic**: Parses command-line arguments, calls the appropriate functions based on the arguments, and handles the tuning process, comparison, and listing.

#### `load_summary` Function
- **Purpose**: Loads the summary of a tuning run.
- **Logic**: Reads the summary file of a run and returns its content.
