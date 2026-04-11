# workers/registry_loader.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 174

---

### File: workers/registry_loader.py

#### Purpose
This file contains the `RegistryLoader` class, which reads a YAML configuration file (`prompt_registry.yaml`) to assemble system and user prompts for different workers based on specified conditions and context variables.

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
- **Data Flow**: The class reads a YAML file to load the registry, then uses this data to assemble prompts based on worker names and context variables.

#### Patterns
- **Singleton**: The class could be used as a singleton to ensure a single instance manages the registry data.
- **Factory**: The class acts as a factory for assembling prompts based on different worker configurations.

#### Dependencies
- **Imports**: `os`, `yaml`, `sys`, `typing`
- **External Files**: `/opt/mythos/workers/prompt_registry.yaml`

#### Interfaces
- **Public Methods**:
  - `get_version()`: Returns the version of the registry.
  - `get_model(worker_name)`: Retrieves the model configuration for a specified worker.
  - `assemble_prompt(worker_name, context=None, fast_path=False)`: Assembles the full system prompt for a worker.
  - `assemble_user_prompt(worker_name, context=None)`: Assembles the user prompt template for a worker.
- **Private Methods**:
  - `_check_condition(condition, context)`: Evaluates a component condition.
  - `_load_source(source, context)`: Loads content from a file source.
  - `_substitute(text, context)`: Performs simple variable substitution in text.

#### Database
- **PostgreSQL Tables**: `registry_loader`, `typing`, `a` (These seem to be placeholders or errors in the documentation, as they are not used in the actual code.)

#### Configuration
- **Environment Variables**: None
- **Config Files**: `/opt/mythos/workers/prompt_registry.yaml`

#### Key Logic
- **Prompt Assembly**: The `assemble_prompt` method reads the registry to determine which components to include based on conditions and context. It sorts components by order and performs variable substitution.
- **Condition Evaluation**: The `_check_condition` method evaluates conditions like "always", "context_available", and "speaker_file_exists" to determine if a component should be included.
- **File Loading**: The `_load_source` method reads content from a file if the source is specified as a file path.

#### Integration Points
- **CLI Integration**: The file includes a CLI interface to dump assembled prompts for inspection.
- **Worker Configuration**: The class integrates with the worker configuration stored in `prompt_registry.yaml` to provide dynamic prompt generation based on worker-specific rules and conditions.

### Detailed Method Descriptions

- **`__init__(self, path=REGISTRY_PATH)`**:
  - **Purpose**: Initializes the `RegistryLoader` by loading the registry from the specified YAML file.
  - **Parameters**: `path` (default: `/opt/mythos/workers/prompt_registry.yaml`)

- **`get_version(self)`**:
  - **Purpose**: Returns the version of the registry.

- **`get_model(self, worker_name)`**:
  - **Purpose**: Retrieves the model configuration for a specified worker.
  - **Parameters**: `worker_name` (name of the worker)

- **`assemble_prompt(self, worker_name, context=None, fast_path=False)`**:
  - **Purpose**: Assembles the full system prompt for a worker based on conditions and context.
  - **Parameters**: 
    - `worker_name` (name of the worker)
    - `context` (optional dictionary of template variables for substitution)
    - `fast_path` (optional boolean to use fast path components for iris)

- **`assemble_user_prompt(self, worker_name, context=None)`**:
  - **Purpose**: Assembles the user prompt template for a worker.
  - **Parameters**: 
    - `worker_name` (name of the worker)
    - `context` (optional dictionary of template variables for substitution)

- **`_check_condition(self, condition, context)`**:
  - **Purpose**: Evaluates a component condition.
  - **Parameters**: 
    - `condition` (condition string)
    - `context` (dictionary of context variables)

- **`_load_source(self, source, context)`**:
  - **Purpose**: Loads content from a file source.
  - **Parameters**: 
    - `source` (source string, typically a file path)
    - `context` (dictionary of context variables)

- **`_substitute(self, text, context)`**:
  - **Purpose**: Performs simple variable substitution in text.
  - **Parameters**: 
    - `text` (text string to substitute variables in)
    - `context` (dictionary of context variables)

### CLI Usage
The file includes a CLI interface to dump assembled prompts for inspection. This can be run directly from the command line to test and inspect prompt generation for different workers and conditions.
