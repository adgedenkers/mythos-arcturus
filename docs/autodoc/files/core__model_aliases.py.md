# core/model_aliases.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 73

---

### Documentation for `core/model_aliases.py`

#### Purpose
This file serves as the canonical registry for model aliases in the Mythos system. It provides functions to resolve aliases to full model names, check if a name is a recognized alias, and generate help text for model selection commands.

#### Architecture
The file is structured with a set of global dictionaries and several top-level functions:
- `MODEL_ALIASES`: A dictionary mapping short aliases to full model names.
- `MODEL_DESCRIPTIONS`: A dictionary mapping aliases to human-readable descriptions.
- `resolve_alias`: Resolves a short alias to a full model name.
- `is_known_alias`: Checks if a name is a recognized alias.
- `get_model_description`: Retrieves a human-readable description for an alias.
- `get_help_text`: Generates help text for model selection commands.
- `get_help_text_extended`: Generates extended help text including advanced commands.

#### Patterns
- **Singleton Pattern**: The `MODEL_ALIASES` and `MODEL_DESCRIPTIONS` dictionaries act as singletons, providing a single source of truth for model aliases and descriptions.
- **Configuration Pattern**: The default model is configured via an environment variable (`OLLAMA_MODEL`).

#### Dependencies
- `os`: Used to retrieve the default model from an environment variable.

#### Interfaces
The file exposes the following functions and variables:
- `resolve_alias(name: str) -> str`: Resolves a short alias to a full model name.
- `is_known_alias(name: str) -> bool`: Checks if a name is a recognized alias.
- `get_model_description(alias: str) -> str`: Retrieves a human-readable description for an alias.
- `get_help_text() -> str`: Generates help text for model selection commands.
- `get_help_text_extended() -> str`: Generates extended help text including advanced commands.
- `DEFAULT_MODEL`: The default model name, configurable via an environment variable.
- `MODEL_ALIASES`: Dictionary mapping short aliases to full model names.
- `MODEL_DESCRIPTIONS`: Dictionary mapping aliases to human-readable descriptions.

#### Database
The file references the following PostgreSQL tables:
- `here`
- `THIS`
- `core`

However, there are no explicit database operations performed in this file. The references to these tables might be placeholders or intended for future use.

#### Configuration
- `OLLAMA_MODEL`: An environment variable that can override the default model.

#### Key Logic
- **Alias Resolution**: The `resolve_alias` function checks if the provided name is a known alias and returns the corresponding full model name. If the name is not an alias, it returns the name unchanged.
- **Help Text Generation**: The `get_help_text` and `get_help_text_extended` functions generate formatted help text for model selection commands, including advanced options.

#### Integration Points
This file integrates with other parts of the Mythos system by providing a centralized registry for model aliases and descriptions. It is imported by other modules that need to resolve aliases or generate help text, ensuring consistency across the system. The default model and alias mappings can be used by various subsystems, such as command processors and model selectors, to ensure uniform behavior.
