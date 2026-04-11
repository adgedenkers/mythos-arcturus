# tools/iris_ab_sweep.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 671

---

### File: tools/iris_ab_sweep.py

#### Purpose
This file contains the logic for performing an A/B sweep to test the impact of different configuration settings on various chat models. It systematically varies one setting at a time and measures the impact on model responses.

#### Architecture
The file is organized into several top-level functions that handle different aspects of the sweep process:
- `score_compact`: Scores the responses based on predefined metrics.
- `build_baseline_prompt`: Constructs the baseline prompt from disk.
- `build_custom_prompt`: Builds a custom prompt with specific overrides.
- `get_sweep_configs`: Defines all sweep variations.
- `get_chat_models`: Retrieves chat-capable models.
- `run_message`: Runs a single message through a model and returns the response and elapsed time.
- `run_sweep_config`: Runs all test messages against one config+model combo.
- `format_sweep_results`: Formats the sweep results into a comparison table.
- `main`: The entry point for the script.

#### Patterns
- **Factory Pattern**: `build_baseline_prompt` and `build_custom_prompt` act as factory methods to create different types of prompts.
- **Singleton Pattern**: The `Client` object from the `ollama` module is instantiated once and reused.

#### Dependencies
- Standard libraries: `os`, `sys`, `time`, `json`, `copy`, `argparse`, `datetime`, `typing`, `pathlib`, `dotenv`.
- Custom modules: `ollama`, `prompt_assembler`.

#### Interfaces
- **Exposed Functions**: `score_compact`, `build_baseline_prompt`, `build_custom_prompt`, `get_sweep_configs`, `get_chat_models`, `run_message`, `run_sweep_config`, `format_sweep_results`, `main`.
- **CLI Interface**: The script can be invoked with various command-line arguments to control the sweep behavior.

#### Database
- **References**: The file references several tables and labels in PostgreSQL, including `disk`, `datetime`, `typing`, `pathlib`, `dotenv`, `ollama`, `prompt_assembler`, `each`, `what`, and `disk`. However, these are not actual database tables but rather references to modules and data structures.

#### Configuration
- **Environment Variables**: `OLLAMA_HOST` is loaded from `.env` to configure the Ollama client.
- **Configuration Files**: The script reads configuration files like `personality.yaml` and `voice.yaml` from disk.

#### Key Logic
- **Prompt Construction**: The script constructs different prompts based on the baseline and custom overrides.
- **Sweep Configurations**: It defines various sweep configurations to test different settings like temperature, personality sliders, and identity.
- **Scoring**: Responses are scored based on predefined metrics like word count, bullet points, and presence of specific phrases.
- **Execution**: The script runs each configuration against a set of test messages and collects the results.

#### Integration Points
- **Ollama Client**: The script uses the `ollama` client to interact with chat models.
- **Prompt Assembler**: It leverages functions from `prompt_assembler` to build and customize prompts.
- **CLI Arguments**: The script integrates with the command-line interface to accept user-defined models and sweep types.

### Detailed Analysis

#### `score_compact`
- **Purpose**: Scores the responses based on predefined metrics.
- **Logic**: Converts the text to lowercase, splits it into words and lines, and checks for specific phrases and patterns.

#### `build_baseline_prompt`
- **Purpose**: Constructs the baseline prompt from disk.
- **Logic**: Uses the `assemble_system_prompt` function from `prompt_assembler` to build the prompt.

#### `build_custom_prompt`
- **Purpose**: Builds a custom prompt with specific overrides.
- **Logic**: Loads and resolves personality settings, builds voice and user sections, and assembles the prompt.

#### `get_sweep_configs`
- **Purpose**: Defines all sweep variations.
- **Logic**: Constructs different configurations for temperature, personality sliders, and identity.

#### `get_chat_models`
- **Purpose**: Retrieves chat-capable models.
- **Logic**: Placeholder function; actual implementation not shown.

#### `run_message`
- **Purpose**: Runs a single message through a model and returns the response and elapsed time.
- **Logic**: Uses the Ollama client to send the message and measure the response time.

#### `run_sweep_config`
- **Purpose**: Runs all test messages against one config+model combo.
- **Logic**: Iterates over test messages and collects the results.

#### `format_sweep_results`
- **Purpose**: Formats the sweep results into a comparison table.
- **Logic**: Organizes the results and formats them for easy comparison.

#### `main`
- **Purpose**: The entry point for the script.
- **Logic**: Parses command-line arguments, runs the sweep configurations, and formats the results.

This file is a comprehensive tool for systematically testing and comparing different configurations of chat models, providing valuable insights into how specific settings affect model performance and output.
