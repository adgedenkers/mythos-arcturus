# neuro/arcturian_grid/templates/ANCHOR_NARRATIVE.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 85

---

### File: `neuro/arcturian_grid/templates/ANCHOR_NARRATIVE.yaml`

#### Purpose
This YAML file defines the configuration and parameters for a specific function template within the Mythos system, specifically for the `ANCHOR_NARRATIVE` function. It outlines the structure, runtime models, processing requirements, and expected output schema for analyzing conversation exchanges.

#### Architecture
The file is structured as a YAML document with key-value pairs that define various attributes and configurations. It includes sections for function metadata, runtime models, processing details, and output schema.

#### Patterns
There are no explicit design patterns used in this YAML file as it is a configuration file rather than executable code.

#### Dependencies
This YAML file does not directly import or rely on other files but is used by the Mythos system to configure and run the `ANCHOR_NARRATIVE` function. It references specific models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) that are presumably available in the system.

#### Interfaces
The file exposes configuration details for the `ANCHOR_NARRATIVE` function, which can be consumed by the Mythos system to instantiate and run the function. It does not expose any direct interfaces but serves as a configuration blueprint.

#### Database
This YAML file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with databases to store or retrieve data as part of its processing.

#### Configuration
The file itself is a configuration file and does not reference any external config files or environment variables. However, it defines the configuration for the `ANCHOR_NARRATIVE` function.

#### Key Logic
The key logic is embedded in the `prompt` field, which specifies the instructions for analyzing the conversation exchange. The prompt instructs the model to extract physical/logistical reality and place the exchange in the larger narrative context, formatting the output as a JSON object with specific keys.

#### Integration Points
This YAML file integrates with the Mythos system's function execution framework. The configuration defined here is used to set up and run the `ANCHOR_NARRATIVE` function, which likely interacts with other subsystems such as the model execution layer, data storage, and possibly user interfaces or APIs for input and output.

### Detailed Breakdown

- **Function Metadata**:
  - `function_id`: `ANCHOR_NARRATIVE`
  - `node`: `ANCHOR`
  - `node_name`: `Anchor`
  - `node_domain`: `Physical and structural reality`
  - `layer`: `NARRATIVE`
  - `layer_name`: `Narrative`
  - `depth`: `7`
  - `model_tier`: `large`
  - `processing`: `deep_conscious`
  - `critical_path`: `false`

- **Runtime Models**:
  - `gemma3:27b`
  - `iris-thinking-v2:latest`
  - `command-r:35b`

- **Prompt**:
  - The prompt instructs the model to analyze the conversation exchange through two lenses: physical/logistical reality and narrative context. The output should be a JSON object with keys `node` and `layer`.

- **Output Schema**:
  - The output is expected to be a JSON object with the following properties:
    - `summary`: A 1-2 sentence summary of the analysis.
    - `confidence`: A confidence score between 0 and 1.
    - `flags`: An array of notable findings.
    - `locations`: An array of locations.
    - `times`: An array of times.
    - `people`: An array of people.
    - `objects`: An array of objects.
    - `actions`: An array of actions.
    - `environment`: A string describing the environment.

This YAML file serves as a comprehensive configuration for the `ANCHOR_NARRATIVE` function, detailing its purpose, runtime environment, and expected output format, ensuring consistent and structured processing within the Mythos system.
