# neuro/arcturian_grid/templates/COMPASS_PROCESSING.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 54

---

### File: `neuro/arcturian_grid/templates/COMPASS_PROCESSING.yaml`

#### Purpose
This YAML file defines the configuration template for the `COMPASS_PROCESSING` function within the Mythos system, specifically for the `COMPASS` node in the `PROCESSING` layer. It outlines the parameters, models, and expected output schema for this function.

#### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes of the `COMPASS_PROCESSING` function. The structure includes metadata, function-specific parameters, and output schema details.

#### Patterns
No specific design patterns are used in this YAML file, as it is a configuration file rather than executable code.

#### Dependencies
This file does not directly import or rely on any other files. However, it references models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) that are likely used in the runtime environment.

#### Interfaces
The file exposes configuration details that are likely used by the runtime environment to instantiate and configure the `COMPASS_PROCESSING` function. It does not expose any direct interfaces but serves as a configuration blueprint.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the runtime environment might use this configuration to interact with databases as part of its processing.

#### Configuration
The file itself is a configuration file, specifying various parameters such as `function_id`, `node`, `layer`, `depth`, `model_tier`, and `runtime_models`. It also defines the `prompt` and `output_schema`.

#### Key Logic
The key logic is embedded in the `prompt` field, which specifies the analytical tasks to be performed by the function. The function is expected to analyze user messages and assistant responses to determine the user's actual need, forward-moving action, Iris's required action, and the conversation trajectory.

#### Integration Points
This configuration file integrates with the runtime environment of the Mythos system, particularly the `Arcturian Grid` subsystem. It is likely used to configure and instantiate the `COMPASS_PROCESSING` function within the `COMPASS` node of the `PROCESSING` layer.

### Detailed Breakdown

1. **Metadata**:
   - `function_id`: `COMPASS_PROCESSING`
   - `node`: `COMPASS`
   - `node_name`: `Compass`
   - `node_domain`: `Directional and intentional`
   - `layer`: `PROCESSING`
   - `layer_name`: `Processing`
   - `depth`: `3`
   - `model_tier`: `medium`
   - `runtime_models`: List of models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`)
   - `processing`: `conscious`
   - `critical_path`: `false`
   - `generated_at`: `2026-03-02T22:22:03.880400`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Prompt**:
   - The `prompt` field contains a detailed instruction for the function to analyze user messages and assistant responses, determining the user's actual need, forward-moving action, Iris's required action, and the conversation trajectory.

3. **Output Schema**:
   - The `output_schema` defines the expected JSON structure of the function's output, including fields such as `summary`, `confidence`, `flags`, `stated_need`, `actual_need`, `recommended_action`, and `trajectory`.

This YAML file serves as a critical configuration blueprint for the `COMPASS_PROCESSING` function, guiding the runtime environment in its instantiation and operation within the Mythos system.
