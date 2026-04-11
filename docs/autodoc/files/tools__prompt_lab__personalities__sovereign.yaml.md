# tools/prompt_lab/personalities/sovereign.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Tools
**Lines:** 15

---

### File: tools/prompt_lab/personalities/sovereign.yaml

#### Purpose
This YAML file defines the configuration for the "Sovereign" personality used in the Mythos system, specifically within the `prompt_lab` tool. It sets parameters for the personality's behavior, including its traits and characteristics.

#### Architecture
The file is structured as a YAML document with key-value pairs. It contains:
- A `name` field that identifies the personality.
- A `description` field that provides a brief description of the personality's role and characteristics.
- A `sliders` section that contains various traits (e.g., verbosity, warmth, humor, truth, speculation, autonomy, mystical, formality, challenge) each with a numeric value between 0 and 100.

#### Patterns
This file does not follow any specific design pattern as it is a configuration file. However, it uses a key-value structure that is common in configuration files.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone configuration file.

#### Interfaces
This file is used by the `prompt_lab` tool to configure the behavior of the "Sovereign" personality. It does not expose any interfaces directly but is read by the `prompt_lab` tool to set the personality's traits.

#### Database
This file does not interact with any database tables or Neo4j labels directly. It is a configuration file that is used to set the behavior of the personality within the `prompt_lab` tool.

#### Configuration
This file itself is a configuration file. It does not use any external configuration files or environment variables. The values within the file are static and predefined.

#### Key Logic
The key logic of this file is to define the behavior of the "Sovereign" personality through the `sliders` section. Each trait (e.g., `verbosity`, `warmth`, `humor`, etc.) is set to a specific value that determines how the personality behaves when used in the `prompt_lab` tool.

#### Integration Points
This file integrates with the `prompt_lab` tool, which reads the configuration to set the behavior of the "Sovereign" personality. The `prompt_lab` tool likely uses this configuration to tailor the responses and interactions of the AI based on the defined traits.

### Summary
The `sovereign.yaml` file is a configuration file that defines the "Sovereign" personality for the `prompt_lab` tool in the Mythos system. It sets various traits and characteristics that determine the behavior of the personality, such as verbosity, warmth, humor, truth, speculation, autonomy, mystical, formality, and challenge. This file is read by the `prompt_lab` tool to configure the personality's behavior, ensuring that it aligns with the specified traits and characteristics.
