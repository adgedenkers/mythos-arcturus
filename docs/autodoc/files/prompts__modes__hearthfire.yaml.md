# prompts/modes/hearthfire.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Prompt System
**Lines:** 15

---

### File: prompts/modes/hearthfire.yaml

#### Purpose
This YAML file defines the configuration for the "Hearthfire" mode in the Mythos system, which is designed for spiritual and personal conversations. It includes settings for various features, personality overrides, and specific instructions for the AI's behavior.

#### Architecture
The file is structured as a YAML document with key-value pairs and nested lists. The main sections include:
- `name`: The name of the mode.
- `emoji`: An emoji representing the mode.
- `description`: A brief description of the mode's purpose.
- `personality_overrides`: A dictionary for overriding default personality traits.
- `features`: A dictionary of boolean flags for enabling/disabling specific features.
- `voice_notes`: A list of notes guiding the AI's behavior and tone.
- `instructions`: Additional instructions for the AI.
- `include_life_context`: A boolean flag indicating whether life context should be included.

#### Patterns
This file does not use any design patterns as it is a configuration file rather than executable code.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone configuration file.

#### Interfaces
This file is used by the Mythos system's configuration management module to set up the "Hearthfire" mode. It does not expose any interfaces directly but is read by the system to configure the mode's behavior.

#### Database
This file does not interact with any database tables or Neo4j labels directly. It is used to configure the system's behavior and does not perform any database operations.

#### Configuration
This file itself is a configuration file. It does not use any external configuration files or environment variables. Its settings are used to configure the behavior of the "Hearthfire" mode.

#### Key Logic
The key logic in this file is the configuration of the "Hearthfire" mode. It specifies that:
- Perception logging and entity extraction are enabled.
- Web search is disabled.
- The AI should focus on spiritual and personal topics.
- The AI should be present, warm, and real.

#### Integration Points
This file integrates with the Mythos system's configuration management module, which reads this file to set up the "Hearthfire" mode. The settings defined here influence the behavior of the AI when operating in this mode, affecting how it processes and responds to user inputs.

### Summary
The `hearthfire.yaml` file is a configuration file that defines the settings for the "Hearthfire" mode in the Mythos system. It specifies that the mode should focus on spiritual and personal conversations, enabling certain features like perception logging and entity extraction, while disabling others like web search. The file is read by the system's configuration management module to configure the AI's behavior in this mode.
