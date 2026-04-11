# orchestrator/benchmark/resonance/run_phase3.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 333

---

### Documentation for `orchestrator/benchmark/resonance/run_phase3.py`

#### Purpose
This file is part of the Mythos system's benchmarking suite, specifically for Phase 3 of the Iris Resonance Benchmark. It tests how instruction compliance varies by position in the system prompt for each resonant model.

#### Architecture
The file consists of several top-level functions:
- `call_ollama`: Sends a request to the Ollama API with a given model, system prompt, and user message, and returns the response.
- `build_base_prompt`: Constructs the base prompt for position testing.
- `inject_at_position`: Inserts an instruction at a specified position in the base prompt.
- `run_phase3`: Executes the position compliance testing for the specified models.
- `build_position_heatmap`: Aggregates and visualizes the compliance rates as a heatmap.
- `main`: Entry point for the script, parses command-line arguments and calls `run_phase3`.

#### Patterns
- **No explicit design patterns**: The file primarily consists of procedural code with no explicit use of design patterns like factory, singleton, or observer.

#### Dependencies
The file imports the following modules:
- `os`, `sys`, `json`, `time`, `re`, `argparse`, `logging`, `requests`, `yaml`
- `resonance_config` for configuration constants
- `prompt_assembler` for assembling system prompts

#### Interfaces
- **Exposed Functions**: `main` is the entry point, and `run_phase3` is the primary function for running the phase.
- **Configuration**: Uses `resonance_config` for configuration constants like `OLLAMA_HOST`, `JUDGE_MODEL`, `TIMEOUTS`, `POSITION_TEST_INSTRUCTIONS`, `POSITION_SLOTS`, and `PROMPT_CONFIGS`.

#### Database
- **PostgreSQL Tables**: References `Phase`, `datetime`, `pathlib`, `typing`, `resonance_config`, and `prompt_assembler` tables.

#### Configuration
- **Environment Variables**: No explicit environment variables are used.
- **Configuration Files**: Uses `resonance_config` for configuration constants.

#### Key Logic
1. **Prompt Construction and Injection**:
   - `build_base_prompt`: Constructs the base prompt for position testing.
   - `inject_at_position`: Inserts an instruction at a specified position in the base prompt.

2. **Ollama API Interaction**:
   - `call_ollama`: Sends a request to the Ollama API and processes the response.

3. **Position Compliance Testing**:
   - `run_phase3`: Iterates over specified models, instructions, positions, and test messages to measure compliance rates.
   - Aggregates results and writes them to a JSON file.

4. **Heatmap Generation**:
   - `build_position_heatmap`: Aggregates compliance rates and generates a heatmap for visualization.

#### Integration Points
- **Ollama API**: The script interacts with the Ollama API to send prompts and receive responses.
- **Phase 2 Grouping**: Loads resonant models from Phase 2 grouping files.
- **File System**: Writes results to files in the `/opt/mythos/orchestrator/benchmark/resonance/runs` directory.

### Detailed Function Descriptions

1. **`call_ollama`**:
   - **Purpose**: Sends a request to the Ollama API and returns the response.
   - **Parameters**: `model`, `system_prompt`, `user_message`, `timeout`
   - **Logic**: Constructs a POST request to the Ollama API, handles timeouts and errors, and processes the response.

2. **`build_base_prompt`**:
   - **Purpose**: Constructs the base prompt for position testing.
   - **Logic**: Uses `prompt_assembler` to assemble the system prompt or falls back to a minimal prompt if `prompt_assembler` is not available.

3. **`inject_at_position`**:
   - **Purpose**: Inserts an instruction at a specified position in the base prompt.
   - **Parameters**: `base_prompt`, `instruction`, `position`
   - **Logic**: Inserts the instruction at the specified position (e.g., `top`, `pre_identity`, `post_identity`, `mid_personality`, `post_voice`, `end`).

4. **`run_phase3`**:
   - **Purpose**: Executes the position compliance testing for the specified models.
   - **Parameters**: `models`
   - **Logic**: Loads resonant models from Phase 2 grouping, iterates over models, instructions, positions, and test messages, calls `call_ollama` to get responses, checks compliance, and writes results to a JSON file.

5. **`build_position_heatmap`**:
   - **Purpose**: Aggregates compliance rates and generates a heatmap for visualization.
   - **Parameters**: `run_dir`, `results_file`
   - **Logic**: Reads results from the JSON file, aggregates compliance rates, and writes the heatmap data to a JSON file.

6. **`main`**:
   - **Purpose**: Entry point for the script, parses command-line arguments and calls `run_phase3`.
   - **Logic**: Uses `argparse` to parse command-line arguments and calls `run_phase3` with the specified models.

### Summary
This file is a critical component of the Mythos system's benchmarking suite, specifically for testing instruction compliance at different positions within the system prompt. It integrates with the Ollama API, processes results, and generates visualizations to help understand the effectiveness of different prompt positions.
