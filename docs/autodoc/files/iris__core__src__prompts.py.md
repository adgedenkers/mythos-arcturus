# iris/core/src/prompts.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 393

---

### File: `iris/core/src/prompts.py`

#### Purpose
This file manages the loading and assembly of system prompts for the Iris AI system. It handles different types of tasks and provides specific configurations and prompts based on the task type.

#### Architecture
The file contains three main classes:
- `TaskType`: An enumeration of task types that may need different prompt configurations.
- `ModelConfig`: A data class representing the configuration for a specific model interaction.
- `PromptManager`: The main class responsible for loading and assembling system prompts.

The `PromptManager` class has several methods for loading prompts from disk, estimating token counts, and assembling complete system prompts based on the task type and context.

#### Patterns
- **Singleton Pattern**: The `get_prompt_manager` function provides a global instance of `PromptManager`, suggesting a singleton pattern.
- **Factory Method Pattern**: The `get_model_config` method acts as a factory method to return the appropriate `ModelConfig` based on the task type.

#### Dependencies
- **Imports**: `os`, `structlog`, `pathlib`, `typing`, `dataclasses`, `datetime`, `enum`
- **Environment Variables**: `OLLAMA_MODEL` (used in `ModelConfig`)

#### Interfaces
- **Public Methods**:
  - `get_prompt_manager()`: Returns the global instance of `PromptManager`.
  - `PromptManager.load()`: Loads prompt files from disk.
  - `PromptManager._estimate_tokens(text)`: Estimates the number of tokens in a text.
  - `PromptManager.get_model_config(task_type)`: Returns the model configuration for a given task type.
  - `PromptManager.assemble_system_prompt(mode, task_type, spiral_day, additional_context, memories)`: Assembles a complete system prompt for an interaction.
  - `PromptManager.get_classification_prompt(message)`: Returns a minimal prompt for message classification.
  - `PromptManager.get_summary_prompt(conversation, max_tokens)`: Returns a prompt to summarize conversation history.

#### Database
- **References**: None (The file does not interact directly with any database tables or Neo4j labels.)

#### Configuration
- **Environment Variables**: `OLLAMA_MODEL` (used to set the default model for certain task types)
- **File Paths**: Prompts are loaded from a directory specified by `prompts_dir` (default is `./prompts` relative to the file).

#### Key Logic
- **Prompt Loading**: The `load` method reads identity and operational prompts from markdown files and logs the process.
- **Token Estimation**: The `_estimate_tokens` method provides a rough estimate of the number of tokens in a text.
- **Prompt Assembly**: The `assemble_system_prompt` method constructs a complete system prompt by combining identity, operational, and task-specific instructions.
- **Task-Specific Instructions**: Methods like `_get_task_instructions` and `_get_channeling_instructions` provide task-specific instructions for different task types.

#### Integration Points
- **Other Subsystems**: The `PromptManager` integrates with other subsystems by providing assembled prompts and model configurations for different tasks. It is likely used by other components of the Mythos system that require context-aware prompts for AI interactions.

### Summary
The `prompts.py` file is a crucial component of the Mythos system, managing the loading and assembly of system prompts for the Iris AI. It ensures that the AI has the necessary context and instructions for various tasks, making it a central piece in the interaction logic of the system.
