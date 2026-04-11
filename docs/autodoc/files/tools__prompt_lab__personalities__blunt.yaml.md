# tools/prompt_lab/personalities/blunt.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Tools
**Lines:** 14

---

### Documentation for `tools/prompt_lab/personalities/blunt.yaml`

#### Purpose
This YAML file defines the configuration for a personality named "Blunt" used in the Mythos system. The configuration includes a description and a set of sliders that control various aspects of the personality's behavior.

#### Architecture
The file is structured as a simple YAML document with a root level key-value pair structure. It contains:
- `name`: The name of the personality.
- `description`: A brief description of the personality.
- `sliders`: A dictionary of key-value pairs representing various behavioral attributes and their corresponding values.

#### Patterns
There are no design patterns used in this file as it is a configuration file and not a code file.

#### Dependencies
This file does not import or rely on any external dependencies directly. However, it is likely used by a configuration parser or personality manager in the Mythos system.

#### Interfaces
This file does not expose any interfaces directly. Instead, it provides configuration data that is likely consumed by a personality manager or similar component in the Mythos system.

#### Database
This file does not interact with any database directly. The configuration data it contains might be used to configure or update records in a database, but this is not specified in the file itself.

#### Configuration
The file itself is a configuration file. It does not use any external configuration files or environment variables.

#### Key Logic
The key logic of this file is to define the behavior of the "Blunt" personality through a set of predefined sliders. The values of these sliders determine the personality's characteristics such as verbosity, warmth, humor, truthfulness, speculation, autonomy, mysticism, formality, and challenge.

#### Integration Points
This file is likely integrated into the Mythos system through a personality manager or similar component. The configuration data in this file would be loaded and used to configure the behavior of the AI when it adopts the "Blunt" personality. The specific integration points would depend on the implementation details of the Mythos system, but it is likely that this file is read by a configuration loader or personality manager that then applies these settings to the AI's behavior.

### Summary
The `blunt.yaml` file provides a configuration for a personality named "Blunt" in the Mythos system. It defines the personality's behavior through a set of sliders that control various attributes such as truthfulness, warmth, and formality. This configuration is likely used by a personality manager to adjust the AI's behavior when it adopts the "Blunt" personality.
