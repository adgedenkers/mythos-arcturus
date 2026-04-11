# neuro/arcturian_grid/templates/GATEWAY_NARRATIVE.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 61

---

### File: `neuro/arcturian_grid/templates/GATEWAY_NARRATIVE.yaml`

#### Purpose
This YAML file defines the configuration and parameters for the `GATEWAY_NARRATIVE` function within the Mythos system. It specifies details such as the function ID, node information, layer details, runtime models, and the expected output schema.

#### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes and parameters. It does not contain any classes or functions directly but serves as a configuration template for the `GATEWAY_NARRATIVE` function.

#### Patterns
No design patterns are directly applicable since this is a configuration file. However, it follows a template pattern, providing a standardized structure for defining function configurations.

#### Dependencies
This file does not directly import or rely on any external dependencies. It is a configuration file that will be used by other parts of the system to configure the `GATEWAY_NARRATIVE` function.

#### Interfaces
This file exposes configuration details that are used by other parts of the system, particularly the runtime environment that processes the `GATEWAY_NARRATIVE` function. The configuration includes details such as the function ID, node information, layer details, and runtime models.

#### Database
This file does not directly interact with any database tables or Neo4j labels. It is a configuration file that defines the behavior and parameters for the `GATEWAY_NARRATIVE` function.

#### Configuration
The file uses several configuration parameters:
- `function_id`: `GATEWAY_NARRATIVE`
- `node`: `GATEWAY`
- `node_name`: `Gateway`
- `node_domain`: `Transcendent and liminal`
- `layer`: `NARRATIVE`
- `layer_name`: `Narrative`
- `depth`: `7`
- `model_tier`: `large`
- `runtime_models`: A list of models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`)
- `processing`: `deep_conscious`
- `critical_path`: `false`
- `generated_at`: `2026-03-02T22:22:52.298162`
- `generated_by`: `iris-thinking-v2:latest`
- `prompt`: A detailed prompt for the function
- `output_schema`: A JSON schema defining the expected output structure

#### Key Logic
The key logic of this configuration file is to define the parameters and expected behavior of the `GATEWAY_NARRATIVE` function. The `prompt` field specifies the detailed instructions for the function, including the analysis of conversation exchanges and the expected output format.

#### Integration Points
This configuration file integrates with the runtime environment that processes the `GATEWAY_NARRATIVE` function. It provides the necessary parameters and schema for the function to operate correctly within the Mythos system. The `runtime_models` field specifies the models that will be used to process the function, and the `output_schema` defines the expected output structure.

### Summary
The `GATEWAY_NARRATIVE.yaml` file is a configuration template for the `GATEWAY_NARRATIVE` function within the Mythos system. It defines the function's parameters, runtime models, and expected output schema, and serves as a standardized configuration for the function's operation within the system.
