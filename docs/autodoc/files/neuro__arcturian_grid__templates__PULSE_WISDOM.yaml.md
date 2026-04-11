# neuro/arcturian_grid/templates/PULSE_WISDOM.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 72

---

### File: `neuro/arcturian_grid/templates/PULSE_WISDOM.yaml`

#### Purpose
This YAML file defines the configuration and parameters for the `PULSE_WISDOM` function within the Mythos system. It specifies the function's ID, domain, layer, models to be used, processing type, and the expected output schema.

#### Architecture
The file is structured as a YAML configuration file with key-value pairs. It includes metadata about the function, such as its ID, node, layer, and depth. It also specifies the models to be used for processing, the type of processing, and the expected output schema in JSON format.

#### Patterns
No specific design patterns are used in this YAML file as it is a configuration file rather than executable code.

#### Dependencies
This file does not directly import or rely on any external libraries or modules. However, it references models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) and expects the system to have these models available for runtime.

#### Interfaces
This file provides configuration details that are used by other parts of the Mythos system, particularly the runtime environment that processes the function. It does not expose any direct interfaces but serves as a configuration source.

#### Database
This file does not directly interact with any database tables or Neo4j labels. It is a configuration file that is used to set up the function's behavior.

#### Configuration
The file itself is a configuration file. It does not use any external configuration files or environment variables but relies on the values defined within it.

#### Key Logic
The key logic is embedded in the `prompt` field, which defines the instructions for the AI models to analyze the conversation exchange. The expected output is a JSON object with specific fields (`node_analysis` and `layer_insight`), which are further detailed in the `output_schema`.

#### Integration Points
This file integrates with the Mythos system's runtime environment, which uses the specified models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) to process the `PULSE_WISDOM` function. It also integrates with the system's data processing pipelines to handle the input and output according to the defined schema.

### Detailed Breakdown

- **Function ID**: `PULSE_WISDOM`
- **Node**: `PULSE` (Domain: Emotional and energetic field)
- **Layer**: `WISDOM` (Depth: 9)
- **Models**: `gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`
- **Processing Type**: `deep_conscious`
- **Prompt**: The prompt instructs the AI models to analyze the conversation exchange, focusing on emotional tone, energy level, tension/ease, and emotional trajectory. It also requires the AI to provide a transcendent summary and essential truth from an eternal perspective.
- **Output Schema**: The output is expected to be a JSON object with fields such as `summary`, `confidence`, `flags`, `primary_emotion`, `secondary_emotions`, `energy_level`, `energy_direction`, and `tension_points`.

This configuration file is crucial for setting up the `PULSE_WISDOM` function within the Mythos system, ensuring that the AI models process the input data according to the specified requirements and produce the expected output format.
