# neuro/arcturian_grid/generate_grid.py

**Language:** python
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 674

---

### File: `neuro/arcturian_grid/generate_grid.py`

#### Purpose
This file is responsible for generating prompt templates for a 9x9 grid of nodes and layers using a local LLM via Ollama. It reads configuration from YAML files, applies corrections, and writes the generated templates to disk.

#### Architecture
The file consists of several top-level functions that handle different aspects of the template generation process:
- **YAML Loaders**: Functions to load nodes, layers, and corrections from YAML files.
- **Correction Engine**: Functions to apply corrections based on specific criteria.
- **Meta-Prompt Builder**: Functions to build the meta-prompt that instructs the LLM to generate the prompt templates.
- **LLM Interaction**: Functions to call the Ollama LLM and extract the generated prompt from the response.
- **Template Writing**: Functions to write the generated templates to disk and manage the grid index.

#### Patterns
- **Factory Method**: The `build_schema` function can be seen as a factory method that generates a schema based on the node ID.
- **Configuration Management**: The use of constants and configuration maps (e.g., `MODEL_TIER_MAP`, `PROCESSING_MAP`) to manage different configurations.

#### Dependencies
- **Standard Libraries**: `argparse`, `json`, `os`, `re`, `sys`, `time`
- **External Libraries**: `requests`, `yaml`
- **Local Modules**: None

#### Interfaces
- **Public Functions**: 
  - `generate_grid`: The main function that orchestrates the template generation process.
  - `main`: Entry point for the script, parses command-line arguments and calls `generate_grid`.
- **Helper Functions**: 
  - `load_nodes`, `load_layers`, `load_corrections`: Load data from YAML files.
  - `get_applicable_corrections`: Applies corrections based on specific criteria.
  - `build_meta_prompt`: Builds the meta-prompt for the LLM.
  - `call_ollama`: Calls the Ollama LLM to generate the prompt.
  - `extract_prompt_from_response`: Extracts the prompt from the LLM's JSON response.
  - `write_template`, `write_grid_index`: Writes the generated templates and grid index to disk.
  - `find_broken_templates`, `generate_fallback_prompt`, `print_seeds`: Additional utility functions for managing and inspecting the templates.

#### Database
- **PostgreSQL Tables**: 
  - `datetime`: Used for logging or tracking timestamps.
  - `pathlib`: Used for file path management.
  - `findings`: Used for storing findings or results.
  - `the`: Placeholder or typo, likely not used.

#### Configuration
- **Environment Variables**: 
  - `OLLAMA_MODEL`: Default model for the LLM.
- **Constants**: 
  - `SCRIPT_DIR`, `DEFAULT_NODES`, `DEFAULT_LAYERS`, `DEFAULT_OUTPUT`, `DEFAULT_MODEL`, `OLLAMA_CHAT_URL`, `MIN_PROMPT_LENGTH`, `MODEL_TIER_MAP`, `PROCESSING_MAP`.

#### Key Logic
- **Template Generation**: The core logic involves loading nodes and layers, building a meta-prompt, calling the LLM to generate the prompt, and writing the generated prompt to disk.
- **Correction Application**: Corrections are applied based on specific criteria (node, layer, function, model tier).
- **Fallback Mechanism**: If the generated prompt is shorter than `MIN_PROMPT_LENGTH`, a fallback prompt is generated.

#### Integration Points
- **Ollama LLM**: The script interacts with the Ollama LLM via HTTP requests to generate prompt templates.
- **File System**: The script reads from and writes to the file system to load configuration and save generated templates.
- **Command Line Interface**: The script can be invoked from the command line with various options to control the generation process.

### Detailed Function Descriptions

- **`build_schema(node_id: str) -> dict`**: Builds an output schema deterministically based on the provided `node_id`.
- **`load_nodes(path: Path) -> list[dict]`**: Loads nodes from a YAML file.
- **`load_layers(path: Path) -> list[dict]`**: Loads layers from a YAML file.
- **`load_corrections(path: Path) -> list[dict]`**: Loads corrections from a YAML file.
- **`get_applicable_corrections(corrections, node_id, layer_id, function_id, model_tier)`**: Filters and returns applicable corrections based on the given criteria.
- **`build_meta_prompt(node: dict, layer: dict, corrections: list[str]) -> str`**: Constructs a meta-prompt for the LLM to generate a specific prompt template.
- **`call_ollama(prompt: str, model: str) -> str`**: Calls the Ollama LLM to generate a prompt based on the provided meta-prompt.
- **`extract_prompt_from_response(raw: str) -> str`**: Extracts the prompt string from the LLM's JSON response.
- **`generate_fallback_prompt(node: dict, layer: dict) -> str`**: Generates a fallback prompt if the primary generation fails.
- **`write_template(output_dir: Path, node: dict, layer: dict, prompt_text: str, schema: dict, generation_model: str)`**: Writes the generated template to disk.
- **`write_grid_index(output_dir: Path, nodes: list[dict], layers: list[dict])`**: Writes the grid index to disk.
- **`find_broken_templates(output_dir: Path)`**: Finds templates with prompts shorter than `MIN_PROMPT_LENGTH`.
- **`generate_grid(nodes_path: Path, layers_path: Path, output_dir: Path, model: str, corrections_path: Path, filter_nodes: list[str], filter_layers: list[str], dry_run: bool, verbose: bool, retry_broken: bool, max_retries: int)`**: Main function that orchestrates the template generation process.
- **`print_seeds(output_dir: Path)`**: Prints the seeds used for template generation.
- **`main()`**: Entry point for the script, parses command-line arguments and calls `generate_grid`.

This file is a crucial part of the Mythos system, enabling the generation of contextually appropriate prompt templates for the Arcturian Grid.
