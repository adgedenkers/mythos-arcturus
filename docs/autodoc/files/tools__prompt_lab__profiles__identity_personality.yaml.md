# tools/prompt_lab/profiles/identity_personality.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Tools
**Lines:** 13

---

### File: tools/prompt_lab/profiles/identity_personality.yaml

#### Purpose
This YAML file defines a profile named `identity_personality` that specifies which layers of a character's attributes are active. It focuses on the identity and personality traits, while deactivating other layers such as voice, mode, user profile, dynamic context, life context, and skills.

#### Architecture
The file is structured as a simple YAML document with a top-level key `name` and a `description`. It also contains a `layers` section, which is a dictionary of boolean values indicating which layers are active (`true`) or inactive (`false`).

#### Patterns
No design patterns are applicable as this is a configuration file, not a code file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone configuration file.

#### Interfaces
This file is used as a configuration by other parts of the Mythos system, particularly by the `prompt_lab` tool, to determine which layers of a character's attributes should be considered active.

#### Database
This file does not interact directly with any database tables or Neo4j labels. It is a configuration file used to set up the state of the system.

#### Configuration
This file itself is a configuration file. It does not use any external config files or environment variables.

#### Key Logic
The key logic here is the configuration of layers. The `layers` section defines which layers are active (`true`) or inactive (`false`). This configuration is used to tailor the behavior of the character in the `prompt_lab` tool.

#### Integration Points
This file integrates with the `prompt_lab` tool within the Mythos system. The `prompt_lab` tool reads this configuration to determine which layers of the character's attributes to consider when generating prompts or responses. Specifically, it uses the `identity` and `personality` layers while ignoring the others.

### Summary
The `identity_personality.yaml` file is a configuration file that specifies which layers of a character's attributes are active. It is used by the `prompt_lab` tool to tailor the character's behavior based on the defined layers. The file is simple and does not interact with any external systems or databases directly.
