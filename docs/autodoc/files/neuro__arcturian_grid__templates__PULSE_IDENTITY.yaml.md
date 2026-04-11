# neuro/arcturian_grid/templates/PULSE_IDENTITY.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 83

---

### File: `neuro/arcturian_grid/templates/PULSE_IDENTITY.yaml`

#### Purpose
This YAML file defines the configuration for the `PULSE_IDENTITY` function within the Mythos system, specifically for analyzing the emotional and energetic field at the Identity layer (depth 8).

#### Architecture
The file is structured as a YAML configuration template, containing metadata and configuration details for the `PULSE_IDENTITY` function. It includes fields such as `function_id`, `node`, `node_domain`, `layer`, `depth`, `model_tier`, `runtime_models`, `processing`, `prompt`, and `output_schema`.

#### Patterns
This file does not implement any design patterns as it is a configuration file rather than executable code.

#### Dependencies
- **Models**: The file specifies the runtime models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) that will be used for processing.
- **Configuration**: The configuration itself is a dependency for the runtime system to understand the function's behavior and requirements.

#### Interfaces
- **Prompt**: The `prompt` field defines the input format and instructions for the models to process the conversation exchange.
- **Output Schema**: The `output_schema` defines the expected JSON structure of the output, including required fields and their types.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the processed data might be stored in a database as part of the broader Mythos system.

#### Configuration
- **Environment Variables**: No explicit environment variables are used in this file.
- **Config Files**: This file itself is a configuration file used by the Mythos system to configure the `PULSE_IDENTITY` function.

#### Key Logic
The key logic is embedded in the `prompt` field, which instructs the models to analyze the emotional tone, energy level, and identity aspect of the conversation exchange. The output is expected to be in a specific JSON format with predefined keys.

#### Integration Points
- **Mythos Subsystems**: This configuration is likely used by the Mythos subsystem responsible for processing and analyzing conversation exchanges. The output from this function might be integrated into other subsystems for further analysis or decision-making.

### Detailed Breakdown

1. **Metadata**:
   - `function_id`: `PULSE_IDENTITY`
   - `node`: `PULSE`
   - `node_name`: `Pulse`
   - `node_domain`: `Emotional and energetic field`
   - `layer`: `IDENTITY`
   - `layer_name`: `Identity`
   - `depth`: `8`
   - `model_tier`: `large`
   - `runtime_models`: `gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`
   - `processing`: `deep_conscious`
   - `critical_path`: `false`
   - `generated_at`: `2026-03-02T21:52:07.296005`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Prompt**:
   - The prompt instructs the models to analyze the conversation exchange between the user and assistant, focusing on the emotional tone, energy level, and identity aspect. The output should be in a specific JSON format with predefined keys.

3. **Output Schema**:
   - The output schema defines the expected JSON structure, including required fields such as `summary`, `confidence`, `flags`, `primary_emotion`, `secondary_emotions`, `energy_level`, `energy_direction`, and `tension_points`.

This configuration file is crucial for setting up the `PULSE_IDENTITY` function within the Mythos system, ensuring that the models process the conversation exchanges in a consistent and structured manner.
