# neuro/arcturian_grid/templates/PULSE_KNOWLEDGE.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 72

---

### Documentation for `neuro/arcturian_grid/templates/PULSE_KNOWLEDGE.yaml`

#### Purpose
This YAML file defines the configuration and structure for the `PULSE_KNOWLEDGE` function within the Mythos system. It specifies the parameters, models, and output schema for analyzing conversations at the intersection of the "Pulse" node (emotional and energetic field) and the "Knowledge" layer (depth 5).

#### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes of the function. It includes metadata, runtime models, processing details, and output schema.

#### Patterns
No specific design patterns are applied as this is a configuration file rather than executable code.

#### Dependencies
This file does not directly import or rely on other files. However, it references runtime models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) and a specific model tier (`medium`).

#### Interfaces
This file exposes configuration details to the Mythos system, which uses these details to instantiate and configure the `PULSE_KNOWLEDGE` function.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the function it configures may interact with databases to retrieve or store data relevant to the analysis.

#### Configuration
This file itself serves as a configuration file. It does not use external config files or environment variables.

#### Key Logic
The key logic is embedded in the `prompt` field, which instructs the model to analyze the conversation exchange at the intersection of the "Pulse" node and "Knowledge" layer. The output is expected to be a JSON object with specific fields (`node_analysis`, `layer_analysis`).

#### Integration Points
This file integrates with the Mythos system's function instantiation and execution pipeline. The configuration details defined here are used to set up and run the `PULSE_KNOWLEDGE` function, which likely interacts with other subsystems for data retrieval and processing.

### Detailed Breakdown

- **function_id**: `PULSE_KNOWLEDGE`
- **node**: `PULSE`
- **node_name**: `Pulse`
- **node_domain**: `Emotional and energetic field`
- **layer**: `KNOWLEDGE`
- **layer_name**: `Knowledge`
- **depth**: `5`
- **model_tier**: `medium`
- **runtime_models**: 
  - `phi4:14b`
  - `qwen3:14b`
  - `mistral-small:24b`
- **processing**: `conscious`
- **critical_path**: `true`
- **generated_at**: `2026-03-02T21:51:53.421897`
- **generated_by**: `iris-thinking-v2:latest`
- **prompt**: A detailed instruction for the model to analyze the conversation exchange, focusing on emotional tone, energy level, tension, and relevant accumulated understanding.
- **output_schema**: Defines the expected JSON structure of the output, including fields like `summary`, `confidence`, `flags`, `primary_emotion`, `secondary_emotions`, `energy_level`, `energy_direction`, and `tension_points`.

This configuration ensures that the `PULSE_KNOWLEDGE` function is properly set up to analyze conversations in a structured and consistent manner, leveraging specific models and output formats.
