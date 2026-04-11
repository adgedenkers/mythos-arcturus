# tools/prompt_lab/profiles/full_stack.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Tools
**Lines:** 13

---

### File: tools/prompt_lab/profiles/full_stack.yaml

#### Purpose
This YAML file defines the configuration profile for the "full_stack" setup, which represents the complete set of active layers that the AI system (Iris) uses in a production environment.

#### Architecture
The file is structured as a simple YAML document with a root-level dictionary containing:
- `name`: The name of the profile.
- `description`: A brief description of the profile.
- `layers`: A dictionary where each key represents a layer and each value is a boolean indicating whether the layer is active.

#### Patterns
No design patterns are applicable as this is a configuration file, not a code file.

#### Dependencies
This file does not import or rely on any external dependencies directly. It is used by the system to configure the active layers.

#### Interfaces
This file does not expose any interfaces directly. Instead, it is read by the system to configure the active layers dynamically.

#### Database
This file does not interact with any database tables or Neo4j labels directly. It is a configuration file used to determine which layers are active.

#### Configuration
This file itself is a configuration file. It does not use any external config files or environment variables directly. However, it is likely read by the system to configure the active layers based on the environment.

#### Key Logic
The key logic here is the definition of the active layers. Each layer being set to `true` indicates that it should be active in the production environment. The layers include:
- `identity`
- `personality`
- `voice`
- `mode`
- `user_profile`
- `dynamic_context`
- `life_context`
- `skills`

#### Integration Points
This file integrates with the Mythos system's configuration management subsystem. It is likely read by a configuration loader or manager that processes this file to activate the specified layers. The layers themselves are part of the broader Mythos architecture and are integrated into the AI's decision-making and response generation processes.

### Summary
The `full_stack.yaml` file serves as a configuration profile for the Mythos system, specifying which layers should be active in a production environment. It is read by the system's configuration management subsystem to ensure that the AI (Iris) operates with all layers enabled, as it would in a production setting.
