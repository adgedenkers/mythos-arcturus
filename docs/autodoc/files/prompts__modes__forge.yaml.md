# prompts/modes/forge.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Prompt System
**Lines:** 29

---

### Documentation for `prompts/modes/forge.yaml`

#### 1. Purpose
This YAML file defines the configuration for the "Forge" mode in the Mythos system, which is focused on system administration and infrastructure management.

#### 2. Architecture
The file is structured as a YAML document with several key sections:
- **Metadata**: Contains the mode name, emoji, and description.
- **Personality Overrides**: Adjusts the personality traits for this mode.
- **Features**: Enables or disables specific features like perception logging, entity extraction, and web search.
- **Voice Notes**: Provides guidance on how to communicate in this mode.
- **Instructions**: Outlines the key priorities and behaviors expected in Forge mode.

#### 3. Patterns
There are no design patterns used in this YAML file as it is a configuration file and not executable code.

#### 4. Dependencies
This YAML file does not import or rely on any external dependencies. It is a standalone configuration file.

#### 5. Interfaces
This file does not expose any interfaces directly. Instead, it is read by the Mythos system to configure the behavior of the AI in Forge mode.

#### 6. Database
This file does not interact with any database tables or Neo4j labels directly. It is a configuration file that influences the behavior of the AI.

#### 7. Configuration
This file itself is a configuration file that is used to set up the Forge mode. It does not rely on any external configuration files or environment variables.

#### 8. Key Logic
The key logic in this file is the configuration of the Forge mode, which includes:
- Setting personality overrides to ensure the AI behaves appropriately for system administration tasks.
- Enabling specific features like perception logging.
- Providing voice notes to guide the AI's communication style.
- Outlining the instructions for the AI to prioritize accurate system state awareness, precise technical recommendations, and service health consciousness.

#### 9. Integration Points
This file integrates with the Mythos system's AI configuration subsystem. The system reads this file to understand how to behave in Forge mode, adjusting its personality, features, and communication style accordingly. It is likely that the Mythos system has a component that loads these YAML files and applies the configurations to the AI's behavior.

### Summary
The `forge.yaml` file is a configuration file that defines the behavior of the Mythos AI in Forge mode, which is focused on system administration and infrastructure management. It sets specific personality traits, enables certain features, and provides guidance on how the AI should communicate in this mode. The file is read by the Mythos system to configure the AI's behavior, ensuring it is precise and focused on technical tasks.
