# orchestrator/benchmark/resonance/run_phase1.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 633

---

### File: orchestrator/benchmark/resonance/run_phase1.py

#### Purpose
This file is responsible for running Phase 1 of the Iris Resonance Benchmark, which involves generating prompts based on specified configurations, sending these prompts to AI models via Ollama, and evaluating the responses for resonance and anti-patterns.

#### Architecture
The file is structured around several top-level functions that handle different aspects of the benchmark process:
- `build_prompt_for_config`: Builds a system prompt based on a given configuration.
- `_build_with_real_assembler`: Uses the actual `prompt_assembler` to build the prompt.
- `_build_standalone`: Fallback method to build prompts without the `prompt_assembler`.
- `call_ollama`: Sends a prompt to an Ollama model and retrieves the response.
- `check_anti_patterns`, `check_length`, `check_fabrication`: Functions to evaluate the response for various criteria.
- `judge_resonance`: Uses a judge model to score the resonance dimensions of the response.
- `check_model_available`: Checks if a model is available in Ollama.
- `run_phase1`: Orchestrates the entire Phase 1 process.
- `main`: Entry point for the script.

#### Patterns
- **Factory Method Pattern**: `build_prompt_for_config` acts as a factory method that decides whether to use `_build_with_real_assembler` or `_build_standalone` based on the availability of the `prompt_assembler`.
- **Singleton Pattern**: The `prompt_assembler` is treated as a singleton, ensuring that only one instance is used throughout the process.

#### Dependencies
- Standard libraries: `os`, `sys`, `json`, `time`, `hashlib`, `argparse`, `logging`, `traceback`, `requests`, `yaml`, `re`.
- Custom modules: `prompt_assembler`, `resonance_config`.

#### Interfaces
- Exposes the `run_phase1` function to other parts of the system, which is the main entry point for running the benchmark.
- Provides utility functions like `call_ollama`, `check_anti_patterns`, `check_length`, `check_fabrication`, `judge_resonance`, and `check_model_available` for internal use.

#### Database
- **PostgreSQL**: References tables such as `datetime`, `pathlib`, `typing`, `prompt_assembler`, `resonance_config`, `the`, `files`, `personality`, `thinking`, `judge`.
- **Neo4j**: References the `tag` label.

#### Configuration
- Uses environment variables and configuration files from `resonance_config` such as `ALL_MODELS`, `JUDGE_MODEL`, `OLLAMA_HOST`, `PROMPT_CONFIGS`, `RESONANCE_PROMPTS`, `RESONANCE_DIMENSIONS`, `TIMEOUTS`.

#### Key Logic
- **Prompt Generation**: The `build_prompt_for_config` function is crucial for generating prompts that reflect the specified configurations. It either uses the real `prompt_assembler` or falls back to a standalone method.
- **Ollama Interaction**: The `call_ollama` function sends prompts to Ollama and retrieves responses, handling timeouts and errors.
- **Response Evaluation**: Functions like `check_anti_patterns`, `check_length`, `check_fabrication`, and `judge_resonance` evaluate the responses for various criteria, including anti-patterns, length, fabrication, and resonance dimensions.

#### Integration Points
- **Prompt Assembler**: Integrates with the `prompt_assembler` module to build prompts.
- **Ollama API**: Connects to the Ollama API to send prompts and receive responses.
- **Judge Model**: Uses a judge model to score the resonance dimensions of the responses.
- **Configuration Files**: Reads configuration files to determine models, prompts, and other parameters.
- **Logging**: Uses the `logging` module to log the progress and errors during the benchmark process.

### Summary
This file is a critical component of the Mythos system, responsible for running the Iris Resonance Benchmark Phase 1. It orchestrates the generation of prompts, interaction with Ollama models, and evaluation of responses, ensuring that the AI models meet the specified resonance criteria.
