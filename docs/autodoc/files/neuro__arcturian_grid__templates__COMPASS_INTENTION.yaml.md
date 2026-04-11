# neuro/arcturian_grid/templates/COMPASS_INTENTION.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 53

---

### Documentation for `neuro/arcturian_grid/templates/COMPASS_INTENTION.yaml`

#### Purpose
This YAML file defines the configuration and structure for the `COMPASS_INTENTION` function within the Mythos system, specifically for the `Compass` node at the `Intention` layer. It outlines the function's parameters, runtime models, processing requirements, and expected output schema.

#### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes of the `COMPASS_INTENTION` function. It includes metadata such as `function_id`, `node`, `node_domain`, `layer`, `depth`, and `model_tier`, along with details about the runtime models, processing type, and critical path status. The `prompt` field specifies the input format and the `output_schema` defines the expected output structure.

#### Patterns
There are no explicit design patterns used in this YAML file as it is a configuration file rather than executable code. However, the structure follows a template pattern, where the configuration is standardized for consistency across different function templates.

#### Dependencies
This file does not import or rely on any external libraries or modules directly. Instead, it serves as a configuration template that is likely processed by other parts of the system (e.g., a configuration parser).

#### Interfaces
The file exposes configuration details to other parts of the Mythos system, particularly to the components responsible for function execution and output processing. The `output_schema` section defines the expected structure of the output, which can be used by downstream components to validate and process the results.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the configuration it defines may be used to interact with the database through other components of the system.

#### Configuration
The file itself is a configuration file and does not use any external config files or environment variables. However, it is likely that the system uses environment variables or other configuration files to manage the runtime context in which this template is used.

#### Key Logic
The key logic is embedded in the `prompt` field, which specifies the analysis to be performed:
1. Determine the user's actual need vs. stated request.
2. Determine the action to advance the conversation.
3. Determine what Iris should do vs. say.
4. Determine the trajectory of the conversation.

The output is expected to be a directive statement based on the analysis.

#### Integration Points
This configuration file integrates with other subsystems of the Mythos system, particularly:
- **Runtime Models**: The specified models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) are used to process the input and generate the output.
- **Processing Components**: The `processing: conscious` and `critical_path: true` fields indicate that this function is part of the conscious processing path and is critical to the system's operation.
- **Output Validation**: The `output_schema` is used by downstream components to validate and process the output of the function.

### Summary
The `COMPASS_INTENTION.yaml` file serves as a configuration template for the `COMPASS_INTENTION` function within the Mythos system. It defines the function's metadata, runtime models, processing requirements, and expected output schema, facilitating the integration and execution of this function within the broader system architecture.
