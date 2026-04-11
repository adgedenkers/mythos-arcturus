# neuro/arcturian_grid/templates/COMPASS_WISDOM.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 55

---

### File: `neuro/arcturian_grid/templates/COMPASS_WISDOM.yaml`

#### Purpose
This YAML file defines the configuration and parameters for the `COMPASS_WISDOM` function template within the Arcturian Grid of the Mythos system. It specifies the model configurations, processing details, and expected output schema for analyzing directional and intentional conversations at the Wisdom layer.

#### Architecture
The file is structured as a YAML configuration with key-value pairs that define various attributes of the `COMPASS_WISDOM` function. It includes metadata, model configurations, processing details, and output schema.

#### Patterns
No design patterns are directly applicable since this is a configuration file, not a code file.

#### Dependencies
This file does not directly import or rely on other files or modules. However, it references specific models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) that must be available in the system.

#### Interfaces
This file exposes the configuration details for the `COMPASS_WISDOM` function, which can be used by other parts of the system to instantiate and configure this function.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the function it configures may interact with the database to retrieve or store conversation data.

#### Configuration
The file uses environment variables and configuration settings to define the function's behavior, such as `function_id`, `node`, `layer`, `depth`, `runtime_models`, `processing`, `critical_path`, `prompt`, and `output_schema`.

#### Key Logic
The key logic is embedded in the `prompt` field, which defines the instructions for the AI model to analyze the conversation exchange and provide a synthesized response. The `output_schema` defines the expected JSON structure of the output, including fields like `summary`, `confidence`, `flags`, `stated_need`, `actual_need`, `recommended_action`, and `trajectory`.

#### Integration Points
This configuration file integrates with the Mythos system's AI model management and processing pipeline. It is used to configure the `COMPASS_WISDOM` function, which is likely part of a larger conversation analysis and decision-making process within the system.

### Detailed Breakdown

- **function_id**: `COMPASS_WISDOM` — Unique identifier for the function.
- **node**: `COMPASS` — Node in the Arcturian Grid.
- **node_name**: `Compass` — Human-readable name for the node.
- **node_domain**: `Directional and intentional` — Domain of the node.
- **layer**: `WISDOM` — Layer in the Arcturian Grid.
- **layer_name**: `Wisdom` — Human-readable name for the layer.
- **depth**: `9` — Depth level of the layer.
- **model_tier**: `large` — Tier of the model.
- **runtime_models**: List of models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) to be used for processing.
- **processing**: `deep_conscious` — Type of processing.
- **critical_path**: `true` — Indicates if this function is on the critical path.
- **generated_at**: `2026-03-02T22:22:31.829564` — Timestamp of generation.
- **generated_by**: `iris-thinking-v2:latest` — Model used for generation.
- **prompt**: Detailed instructions for the AI model to analyze the conversation and provide a synthesized response.
- **output_schema**: JSON schema defining the expected output structure, including fields like `summary`, `confidence`, `flags`, `stated_need`, `actual_need`, `recommended_action`, and `trajectory`.

This YAML file serves as a critical configuration point for the `COMPASS_WISDOM` function, ensuring that the AI models are correctly instructed and that the output is structured in a way that can be easily integrated into the larger Mythos system.
