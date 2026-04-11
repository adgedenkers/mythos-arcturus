# orchestrator/benchmark/resonance/run_phase4.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 331

---

### File: `orchestrator/benchmark/resonance/run_phase4.py`

#### Purpose
This file contains the logic to run Phase 4 of the Iris Resonance Benchmark, which tests the effectiveness of different padding types around a target instruction to control how a model treats it. The file includes functions to build prompts, call the Ollama API, and analyze the results.

#### Architecture
The file is structured around several top-level functions:
- `call_ollama`: Sends a request to the Ollama API with a given model, system prompt, and user message.
- `build_base_prompt`: Constructs a base system prompt for the Ollama API.
- `build_padded_prompt`: Builds a prompt with the target instruction wrapped in padding.
- `run_phase4`: Executes the padding experiment by iterating over models, instructions, padding configurations, and test messages.
- `build_padding_analysis`: Analyzes the results of the padding experiment.
- `main`: Entry point for the script, parses command-line arguments and calls `run_phase4`.

#### Patterns
- **Factory Method**: `build_base_prompt` and `build_padded_prompt` can be seen as factory methods that create different types of prompts.
- **Singleton**: The logging setup uses a singleton pattern to ensure consistent logging throughout the script.

#### Dependencies
- **Standard Libraries**: `os`, `sys`, `json`, `time`, `re`, `argparse`, `logging`, `requests`
- **Custom Modules**: `resonance_config`, `prompt_assembler`

#### Interfaces
- **Exposed Functions**: `main` is the entry point for the script, and `run_phase4` is the primary function that orchestrates the experiment.
- **Configuration**: The script reads configuration from `resonance_config` and `prompt_assembler`.

#### Database
- **PostgreSQL Tables**: The file references several tables, but they are not directly interacted with in this script. The references are likely for context or future integration points:
  - `the`, `datetime`, `pathlib`, `typing`, `resonance_config`, `prompt_assembler`, `Phase`, `instructions`

#### Configuration
- **Environment Variables**: `OLLAMA_HOST` and `TIMEOUTS` are read from `resonance_config`.
- **Command-Line Arguments**: The script accepts `--models` as a command-line argument.

#### Key Logic
- **Prompt Construction**: The script constructs prompts with varying padding configurations to test how they affect model compliance.
- **API Interaction**: Uses the `requests` library to send API requests to the Ollama service.
- **Result Analysis**: Aggregates and analyzes the results to determine the effectiveness of different padding types.

#### Integration Points
- **Ollama API**: The script interacts with the Ollama API to send prompts and receive responses.
- **Resonance Config**: Configuration details are sourced from `resonance_config`.
- **Prompt Assembler**: The base prompt is constructed using `prompt_assembler`.
- **File System**: The script writes results to files in a specified directory (`RUNS_DIR`).

### Detailed Breakdown of Functions

1. **`call_ollama`**
   - **Purpose**: Sends a request to the Ollama API with a given model, system prompt, and user message.
   - **Parameters**: `model`, `system_prompt`, `user_message`, `timeout`
   - **Logic**: Uses `requests.post` to send a JSON payload to the Ollama API and processes the response.

2. **`build_base_prompt`**
   - **Purpose**: Constructs a base system prompt for the Ollama API.
   - **Logic**: Imports `assemble_system_prompt` from `prompt_assembler` to build the prompt. Falls back to a default prompt if the import fails.

3. **`build_padded_prompt`**
   - **Purpose**: Builds a prompt with the target instruction wrapped in padding.
   - **Parameters**: `base`, `instruction`, `padding_type`, `padding_lines`, `pad_before`, `pad_after`
   - **Logic**: Constructs a prompt by appending padding lines before and/or after the target instruction.

4. **`run_phase4`**
   - **Purpose**: Executes the padding experiment by iterating over models, instructions, padding configurations, and test messages.
   - **Parameters**: `models`
   - **Logic**: Iterates over models, instructions, padding configurations, and test messages to build prompts and call the Ollama API. Logs and writes results to a file.

5. **`build_padding_analysis`**
   - **Purpose**: Analyzes the results of the padding experiment.
   - **Parameters**: `run_dir`, `results_file`
   - **Logic**: Reads results from a file, aggregates compliance rates, and prints and saves the analysis.

6. **`main`**
   - **Purpose**: Entry point for the script, parses command-line arguments and calls `run_phase4`.
   - **Logic**: Uses `argparse` to parse command-line arguments and calls `run_phase4` with the provided models.

### Summary
This script is a critical component of the Mythos system, specifically for benchmarking and analyzing the effectiveness of padding techniques in controlling model behavior. It integrates with the Ollama API and uses structured logging and file I/O to manage and analyze the experiment results.
