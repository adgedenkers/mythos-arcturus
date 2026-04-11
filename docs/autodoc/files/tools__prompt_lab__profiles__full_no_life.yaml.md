# tools/prompt_lab/profiles/full_no_life.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Tools
**Lines:** 13

---

### Documentation for `tools/prompt_lab/profiles/full_no_life.yaml`

#### Purpose
This YAML file defines a configuration profile named `full_no_life` for the Mythos system, specifying which layers of the prompt generation process should be included or excluded. Specifically, it includes layers for identity, personality, voice, mode, user profile, and dynamic context, while excluding life context and skills.

#### Architecture
The file is structured as a simple YAML document with key-value pairs. The main structure includes:
- `name`: The name of the profile.
- `description`: A brief description of the profile.
- `layers`: A dictionary specifying the inclusion or exclusion of various layers in the prompt generation process.

#### Patterns
No design patterns are applicable here as this is a configuration file, not a code file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a configuration file that is likely read by other parts of the Mythos system.

#### Interfaces
This file does not expose any interfaces. It is a configuration file that is read by other components of the Mythos system to determine the layers to include in the prompt generation process.

#### Database
This file does not interact with any database tables or Neo4j labels directly. It is a configuration file used to guide the prompt generation process.

#### Configuration
This file itself is a configuration file. It does not use any external configuration files or environment variables.

#### Key Logic
The key logic in this file is the configuration of the prompt generation layers. The logic is encoded in the boolean values for each layer, indicating whether that layer should be included (`true`) or excluded (`false`).

#### Integration Points
This file is likely integrated into the Mythos system through a configuration reader or loader that parses this YAML file and uses the specified layers to configure the prompt generation process. The `full_no_life` profile would be used to generate prompts that include identity, personality, voice, mode, user profile, and dynamic context layers, but exclude life context and skills.

### Summary
The `full_no_life.yaml` file is a configuration profile for the Mythos system that specifies which layers of the prompt generation process should be included or excluded. It is used to configure the prompt generation process to include specific layers while excluding others, ensuring that the generated prompts adhere to the specified profile.
