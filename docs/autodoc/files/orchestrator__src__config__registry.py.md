# orchestrator/src/config/registry.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 174

---

### File: orchestrator/src/config/registry.py

#### Purpose
This file contains the `RegistryLoader` class, which reads a YAML configuration file (`prompt_registry.yaml`) to assemble and manage prompts for different workers in the Mythos system. It provides methods to retrieve model configurations and assemble both system and user prompts based on specified conditions and context.

#### Architecture
- **Class**: `RegistryLoader`
  - **Methods**:
    - `__init__`: Initializes the class by loading the registry YAML file.
    - `get_version`: Returns the version of the registry.
    - `get_model`: Retrieves the model configuration for a specified worker.
    - `assemble_prompt`: Assembles the full system prompt for a worker based on conditions and context.
    - `assemble_user_prompt`: Assembles the user prompt template for a worker.
    - `_check_condition`: Evaluates a component condition.
    - `_load_source`: Loads content from a file source.
    - `_substitute`: Performs simple variable substitution in text.

#### Patterns
- **Singleton**: The `RegistryLoader` class can be considered a singleton as it is designed to be instantiated once and reused, though it is not explicitly enforced.
- **Factory**: The `_load_source` method can be seen as a factory method for loading content from different sources.

#### Dependencies
- **Imports**: `os`, `yaml`, `sys`, `typing`
- **Configuration File**: `/opt/mythos/workers/prompt_registry.yaml`

#### Interfaces
- **Public Methods**:
  - `get_version()`: Returns the registry version.
  - `get_model(worker_name)`: Retrieves model configuration for a worker.
  - `assemble_prompt(worker_name, context=None, fast_path=False)`: Assembles the full system prompt for a worker.
  - `assemble_user_prompt(worker_name, context=None)`: Assembles the user prompt template for a worker.
- **Private Methods**:
  - `_check_condition(condition, context)`: Evaluates a component condition.
  - `_load_source(source, context)`: Loads content from a file source.
  - `_substitute(text, context)`: Performs simple variable substitution.

#### Database
- **PostgreSQL Tables**: `registry_loader`, `typing`, `a` (These seem to be placeholders or misinterpretations, as there are no actual database operations in the code.)

#### Configuration
- **Environment Variables**: None
- **Config Files**: `prompt_registry.yaml` located at `/opt/mythos/workers/prompt_registry.yaml`

#### Key Logic
- **Prompt Assembly**: The `assemble_prompt` method reads the registry to determine the components and conditions for assembling the prompt. It checks conditions, loads sources, and performs substitutions based on the provided context.
- **Model Configuration**: The `get_model` method retrieves the model configuration for a worker, including model name, temperature, number of predictions, and timeout.
- **Condition Evaluation**: The `_check_condition` method evaluates conditions to determine if a component should be included in the prompt.

#### Integration Points
- **Mythos Subsystems**: This class integrates with other subsystems by providing assembled prompts and model configurations. It is likely used by worker components such as `perception`, `query_builder`, `query_validator`, and `iris`.
- **CLI**: The file includes a CLI for dumping assembled prompts for inspection, which can be useful for debugging and testing.

### Detailed Documentation

#### Class: `RegistryLoader`
- **Initialization**:
  - The `__init__` method loads the `prompt_registry.yaml` file and initializes the `version` attribute.
- **Methods**:
  - `get_version()`: Returns the version of the registry.
  - `get_model(worker_name)`: Retrieves the model configuration for a specified worker, including model name, temperature, number of predictions, and timeout.
  - `assemble_prompt(worker_name, context=None, fast_path=False)`: Assembles the full system prompt for a worker based on conditions and context. It checks conditions, loads sources, and performs substitutions.
  - `assemble_user_prompt(worker_name, context=None)`: Assembles the user prompt template for a worker by performing variable substitutions.
  - `_check_condition(condition, context)`: Evaluates a component condition to determine if it should be included in the prompt.
  - `_load_source(source, context)`: Loads content from a file source, performing substitutions if necessary.
  - `_substitute(text, context)`: Performs simple variable substitution in text.

#### CLI Usage
The file includes a CLI for dumping assembled prompts for inspection, which can be invoked by running the script directly with command-line arguments specifying the worker and optional fast path flag.

```bash
python registry.py <worker_name> [--fast]
```

This CLI is useful for debugging and testing the prompt assembly logic.
