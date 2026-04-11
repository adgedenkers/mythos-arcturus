# config/conversation_modes.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Configuration
**Lines:** 105

---

### File: config/conversation_modes.yaml

#### Purpose
This YAML file serves as the configuration source for defining different conversation modes in the Mythos system. Each mode specifies parameters for the Ollama model, such as temperature, context size, and allowed tools, which influence the behavior of the AI in different contexts.

#### Architecture
The file is structured as a YAML document with the following sections:
- `default_model`: Specifies the default model to be used.
- `deep_model`: Specifies the model to be used for deep analysis.
- `default_config`: Contains default configuration parameters that can be overridden by specific modes.
- `modes`: A dictionary of different conversation modes, each with its own set of parameters.
- `user_routes`: Maps specific Telegram user IDs to their default conversation modes.

#### Patterns
- **Configuration Pattern**: The file acts as a centralized configuration store, allowing for easy management and modification of conversation modes.

#### Dependencies
- This file is likely imported and read by a configuration manager or a service that handles conversation modes, such as `chat_mode.py`.

#### Interfaces
- The file exposes configuration data to other parts of the system, particularly to services that need to determine the appropriate behavior based on the selected conversation mode.

#### Database
- This file does not directly interact with any database tables or Neo4j labels. However, the configuration data it provides may influence how data is processed or retrieved from the database.

#### Configuration
- The file itself is a configuration file, and it does not rely on external configuration files or environment variables. However, the values within it can be overridden or extended by other parts of the system.

#### Key Logic
- The key logic involves defining and organizing different conversation modes with specific parameters that control the behavior of the Ollama model. This includes settings like `temperature`, `num_ctx`, `thinking`, and `allowed_tools`.

#### Integration Points
- This file integrates with the `chat_mode.py` service, which likely reads this configuration to determine the appropriate behavior for different conversation modes.
- It also integrates with the user management system, which uses the `user_routes` section to determine the default mode for specific users.

### Detailed Breakdown of Configuration Sections

#### `default_model` and `deep_model`
- `default_model`: Specifies the default model to be used, which is `"qwen3:30b-a3b"`.
- `deep_model`: Specifies the model to be used for deep analysis, which is `"qwen3:32b"`.

#### `default_config`
- Contains default configuration parameters that can be overridden by specific modes:
  - `thinking`: Whether the AI should simulate thinking before responding.
  - `temperature`: Controls the randomness of the AI's responses.
  - `num_ctx`: The context size for the model.
  - `num_predict`: The number of tokens to predict.

#### `modes`
- A dictionary of different conversation modes, each with its own set of parameters:
  - `command`: Quick commands, lookups, diagnostics.
  - `hearthfire`: Default warm conversation mode.
  - `conversation`: General back-and-forth.
  - `deep`: Complex analysis, multi-step reasoning.
  - `oracle`: Spiritual guidance, channeling, field work.
  - `forge`: Technical work, code generation, system building.
  - `scribe`: Documentation, writing, report generation.
  - `sentry`: System monitoring, diagnostics, security.
  - `night_cycle`: Full context, deep processing.
  - `seraphe`: Seraphe-specific conversation mode.

Each mode includes parameters such as `thinking`, `temperature`, `num_ctx`, `allowed_tools`, and `system_layers`.

#### `user_routes`
- Maps specific Telegram user IDs to their default conversation modes:
  - `8069190169`: Default mode is `"seraphe"`.
  - `7811548479`: Default mode is `"hearthfire"`.

This configuration allows for personalized AI behavior based on the user's preferences and context.
