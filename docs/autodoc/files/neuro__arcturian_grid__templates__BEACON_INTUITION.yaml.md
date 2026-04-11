# neuro/arcturian_grid/templates/BEACON_INTUITION.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 57

---

### File: `neuro/arcturian_grid/templates/BEACON_INTUITION.yaml`

#### Purpose
This YAML file defines the configuration for the `BEACON_INTUITION` function within the Mythos system, specifically tailored for the `BEACON` node in the `INTUITION` layer. It outlines the function's metadata, runtime models, processing type, and expected output schema.

#### Architecture
The file is structured as a YAML document with key-value pairs. It includes metadata such as function ID, node details, layer information, runtime models, processing type, and output schema. The output schema is defined using JSON Schema to specify the structure of the expected output.

#### Patterns
No specific design patterns are used in this YAML file. It serves as a configuration template and does not contain executable logic.

#### Dependencies
This file does not directly import or rely on other files. However, it references runtime models (`mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`) which are expected to be available in the system.

#### Interfaces
This file does not expose any interfaces directly. Instead, it provides configuration data that is likely consumed by other parts of the Mythos system, such as the runtime environment that executes the function.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with databases to retrieve or store relevant data points and knowledge gaps.

#### Configuration
The file itself is a configuration file. It uses environment variables or configuration settings to define the function's behavior, such as the `model_tier` and `runtime_models`.

#### Key Logic
The key logic is encapsulated in the `prompt` field, which defines the task for the function:
- Analyze the `user_message` and `assistant_response` to capture the felt-sense, subtext, and unspoken energy.
- Integrate relevant knowledge (e.g., financial data, past context) to inform this impression.
- Output a JSON object with a key `impression` containing a sensory, subtle description.

#### Integration Points
This configuration file integrates with other parts of the Mythos system, particularly:
- The runtime environment that executes the function based on the specified models.
- The data retrieval and storage subsystems to fetch and store relevant data points and knowledge gaps.
- The output processing subsystem that handles the structured JSON output according to the defined schema.

### Summary
The `BEACON_INTUITION.yaml` file serves as a configuration template for a specific function within the Mythos system. It defines the function's metadata, runtime models, processing type, and output schema. The function is designed to analyze and capture subtle impressions from user and assistant interactions, integrating relevant knowledge to provide a structured output. This configuration is consumed by the runtime environment to execute the function and process its output.
