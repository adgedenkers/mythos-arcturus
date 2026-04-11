# prompts/prompt_layers.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Prompt System
**Lines:** 97

---

### File: prompts/prompt_layers.yaml

#### Purpose
This YAML file defines the configuration for various prompt layers used in the Mythos system. Each layer represents a specific aspect of the AI's context and behavior, and the file specifies whether each layer is enabled, its description, and any associated files or notes.

#### Architecture
The file is structured as a YAML dictionary with a top-level key `layers`. Each value under `layers` is another dictionary representing a specific prompt layer. Each layer dictionary contains keys such as `enabled`, `file`, `description`, `notes`, and sometimes additional metadata like `profile` or `default_mode`.

#### Patterns
- **Configuration Pattern**: The file serves as a configuration store, allowing dynamic enabling and disabling of different layers.
- **Layering Pattern**: The layers are designed to be stacked, with each layer potentially adding more specific context or behavior to the AI's response.

#### Dependencies
- **Files**: The file references other files like `iris_identity.md`, `iris_awareness.md`, and `iris_reference.md`.
- **Environment**: The file is likely read by a Python script or configuration manager.

#### Interfaces
- **Configuration Interface**: The file is used to configure the AI's behavior and context layers. It is likely read by a configuration manager or a script that initializes the AI's prompt layers.
- **Dynamic Enabling**: The `enabled` field allows for dynamic enabling and disabling of layers, which can be controlled programmatically.

#### Database
- **PostgreSQL**: The `db_memory` layer references the `chat_messages` table in PostgreSQL.
- **Neo4j**: No direct Neo4j references are present in this file, but the layers may interact with Neo4j through other subsystems.

#### Configuration
- **Environment Variables**: The file does not directly use environment variables, but the `enabled` fields could be controlled by environment variables or configuration settings.
- **Config Files**: This file itself is a configuration file that other parts of the system read to determine which prompt layers to use.

#### Key Logic
- **Layer Management**: The key logic revolves around managing different layers of context and behavior for the AI. Each layer can be enabled or disabled, and the system dynamically constructs the AI's prompt based on the enabled layers.
- **Dynamic Context**: The `life_context` and `db_memory` layers dynamically inject live data and past conversation history, respectively, into the AI's context.

#### Integration Points
- **Chat Assistant**: The file is likely integrated with the chat assistant subsystem, which reads the configuration to build the AI's prompt dynamically.
- **Skill Engine**: The `skill_results` layer integrates with the skill engine to inject live skill results into the AI's response.
- **Research Framework**: The `research` layer integrates with the research framework to route messages through research nodes.
- **PostgreSQL**: The `life_context` and `db_memory` layers integrate with PostgreSQL to fetch live data and past conversation history.
- **Neo4j**: Although not directly referenced, the layers may interact with Neo4j through other subsystems for context and data retrieval.

### Summary
The `prompt_layers.yaml` file serves as a configuration store for the Mythos system's AI prompt layers. It defines various layers that can be enabled or disabled, each providing specific context or behavior to the AI. The file is read by the chat assistant and other subsystems to dynamically construct the AI's prompt, integrating with PostgreSQL and potentially Neo4j for data retrieval.
