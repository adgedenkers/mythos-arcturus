# tools/prompt_lab/personalities/oracle_deep.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Tools
**Lines:** 14

---

### File: tools/prompt_lab/personalities/oracle_deep.yaml

#### Purpose
This YAML file defines the configuration for the "Oracle Deep" personality in the Mythos system, which is characterized by deep cosmological awareness, intuitive leaps, and high levels of speculation.

#### Architecture
The file is structured as a YAML document with a top-level key `name` and a `description` field. It also contains a `sliders` section that defines various attributes with numeric values.

#### Patterns
No design patterns are applicable as this is a configuration file, not a code file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a configuration file that is likely read by another part of the Mythos system.

#### Interfaces
This file does not expose any interfaces. It is a configuration file that is consumed by other parts of the system, likely by a personality management module.

#### Database
This file does not interact with any database tables or Neo4j labels directly. It is a configuration file that might be used to configure a personality in a database or memory.

#### Configuration
This file itself is a configuration file. It does not use any external configuration files or environment variables.

#### Key Logic
The key logic here is the configuration of the personality attributes. The `sliders` section defines the personality traits with specific numeric values, which are used to modulate the behavior of the AI when this personality is selected.

#### Integration Points
This file is likely integrated into the Mythos system through a personality management module. The values defined here would be used to configure the behavior of the AI when the "Oracle Deep" personality is selected. The integration points would include:
- **Personality Management Module**: This module reads the configuration and applies the personality traits to the AI's responses.
- **AI Response Generation**: The personality traits defined here influence the generation of AI responses, making them more mystical, speculative, and formal as specified.

### Summary
The `oracle_deep.yaml` file is a configuration file that defines the "Oracle Deep" personality within the Mythos system. It specifies various attributes such as verbosity, warmth, humor, truth, speculation, autonomy, mystical, formality, and challenge, each with a numeric value. This configuration is likely read by a personality management module to influence the AI's behavior when this personality is selected.
