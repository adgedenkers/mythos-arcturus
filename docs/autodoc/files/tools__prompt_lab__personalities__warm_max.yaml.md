# tools/prompt_lab/personalities/warm_max.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Tools
**Lines:** 14

---

### File: tools/prompt_lab/personalities/warm_max.yaml

#### Purpose
This YAML file defines a personality profile named "Warm Max" for use in the Mythos system, specifically tailored for deeply intimate and emotionally supportive interactions.

#### Architecture
The file is structured as a YAML document with a simple key-value format. It contains metadata and configurable parameters for the personality profile.

#### Patterns
No design patterns are applicable here as this is a configuration file, not a code file.

#### Dependencies
This file does not import or rely on any external dependencies directly. However, it is likely used by other parts of the Mythos system, particularly the personality management or chatbot interaction modules.

#### Interfaces
This file is not an executable component but provides configuration data. It is consumed by other parts of the system, such as the personality management module, which might use this data to configure the behavior of AI interactions.

#### Database
This file does not interact directly with any database tables or Neo4j labels. However, the data from this file might be loaded into a database or used to configure database queries or interactions.

#### Configuration
The file itself is a configuration file. It does not use any external config files or environment variables directly. The values within this file are static and predefined.

#### Key Logic
The key logic here is the definition of the personality profile parameters. The `sliders` section defines various attributes that influence the AI's behavior, such as `verbosity`, `warmth`, `humor`, `truth`, `speculation`, `autonomy`, `mystical`, `formality`, and `challenge`.

#### Integration Points
This file is likely integrated into the Mythos system through a personality management module. The data from this file would be loaded and used to configure the AI's behavior during interactions. For example, the personality management module might read this file and use the values to adjust the AI's responses to be more warm, supportive, and less formal.

### Summary
The `warm_max.yaml` file is a configuration file that defines a personality profile named "Warm Max" with specific attributes designed for deeply intimate and emotionally supportive interactions. This file is consumed by the personality management module of the Mythos system to configure the AI's behavior based on the predefined parameters.
