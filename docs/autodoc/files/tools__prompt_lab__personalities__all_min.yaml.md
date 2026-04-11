# tools/prompt_lab/personalities/all_min.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Tools
**Lines:** 14

---

### File: tools/prompt_lab/personalities/all_min.yaml

#### Purpose
This YAML file defines a personality configuration named "all_min" for the Mythos system, setting all slider values to their minimum levels to test the floor of each dimension.

#### Architecture
The file is structured as a simple YAML document with a top-level key-value structure. It contains:
- `name`: The name of the personality configuration.
- `description`: A brief description of the configuration.
- `sliders`: A dictionary where each key represents a dimension (e.g., verbosity, warmth) and each value represents the slider setting for that dimension.

#### Patterns
No design patterns are applicable as this is a configuration file.

#### Dependencies
This file does not import or rely on any external dependencies. It is a configuration file that is read by the Mythos system.

#### Interfaces
This file exposes configuration data to the Mythos system, specifically to the `prompt_lab` module which uses these settings to generate or modify AI responses.

#### Database
This file does not interact directly with any database tables or Neo4j labels. It is a configuration file that is used to set parameters for AI behavior.

#### Configuration
This file itself is a configuration file. It does not use any external config files or environment variables.

#### Key Logic
The key logic here is the setting of all slider values to their minimum levels to test the lower bounds of each dimension. This is used to ensure that the AI system behaves correctly at the minimum settings.

#### Integration Points
This file integrates with the `prompt_lab` module of the Mythos system. The `prompt_lab` module reads this configuration and applies the slider settings to the AI responses, ensuring that the AI behaves according to the defined personality.

### Summary
The `all_min.yaml` file is a configuration file that sets all personality sliders to their minimum values. It is used by the `prompt_lab` module to test the lower bounds of AI behavior dimensions. The file is structured in YAML format and does not have any direct dependencies or database interactions. It is a simple yet critical component for testing the floor of each dimension in the AI's personality settings.
