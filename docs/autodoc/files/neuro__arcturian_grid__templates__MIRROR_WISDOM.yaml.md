# neuro/arcturian_grid/templates/MIRROR_WISDOM.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 65

---

### File: `neuro/arcturian_grid/templates/MIRROR_WISDOM.yaml`

#### Purpose
This YAML file defines the configuration and specifications for the `MIRROR_WISDOM` function template within the Mythos system. It outlines the parameters, models, processing requirements, and expected output schema for the function.

#### Architecture
The file is structured as a YAML document with key-value pairs. It contains metadata, configuration settings, and an output schema definition. The structure is flat and does not involve classes or functions, as it is a configuration file.

#### Patterns
This file does not employ any design patterns as it is a configuration file and not a code file.

#### Dependencies
This file does not import or rely on any external modules or libraries. It is a standalone configuration file.

#### Interfaces
This file defines the interface for the `MIRROR_WISDOM` function template, including the expected input and output schema. It specifies the models to be used, the processing type, and the required output format.

#### Database
This file does not interact directly with any databases. It is a configuration file and does not contain logic for reading or writing to databases.

#### Configuration
The file does not use any external configuration files or environment variables. All configuration is embedded within the YAML file itself.

#### Key Logic
The key logic is embedded in the `prompt` field, which defines the instructions for the AI models to analyze the conversation exchange between the user and the assistant. The prompt specifies the focus areas and the expected output format.

#### Integration Points
This file integrates with the Mythos system's AI processing pipeline, specifically with the `MIRROR` node and `WISDOM` layer. It configures the function to use specific AI models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) and defines the expected output schema.

### Detailed Breakdown

1. **Metadata**:
   - `function_id`: `MIRROR_WISDOM`
   - `node`: `MIRROR`
   - `node_name`: `Mirror`
   - `node_domain`: `Self-referential awareness`
   - `layer`: `WISDOM`
   - `layer_name`: `Wisdom`
   - `depth`: `9`
   - `model_tier`: `large`
   - `runtime_models`: List of models to be used (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`)
   - `processing`: `deep_conscious`
   - `critical_path`: `true`
   - `generated_at`: `2026-03-02T22:21:54.446923`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Prompt**:
   - The prompt is a string that instructs the AI models to analyze the conversation exchange between the user and the assistant. It focuses on self-referential awareness and wisdom, emphasizing the user's revelations, Iris's response tendencies, and the partnership dynamic.

3. **Output Schema**:
   - `type`: `object`
   - `properties`:
     - `summary`: `string` (1-2 sentence summary of analysis)
     - `confidence`: `number` (between 0 and 1)
     - `flags`: `array` of `string` (notable findings)
     - `user_reveals`: `array` of `string`
     - `iris_notices`: `array` of `string`
     - `blind_spots`: `array` of `string`
     - `projections`: `array` of `string`
   - `required`: `summary`, `confidence`, `flags`

This YAML file serves as a comprehensive configuration template for the `MIRROR_WISDOM` function within the Mythos system, ensuring that the AI models process the input data according to the specified parameters and produce the expected output schema.
