# neuro/arcturian_grid/templates/COMPASS_KNOWLEDGE.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 54

---

### Purpose
This YAML file defines the configuration for the `COMPASS_KNOWLEDGE` function template within the Mythos system. It specifies the parameters, models, and expected output schema for processing and analyzing conversation exchanges at the `Compass` node and `Knowledge` layer.

### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes of the `COMPASS_KNOWLEDGE` function. The configuration includes metadata, model specifications, processing details, and output schema.

### Patterns
No specific design patterns are used in this YAML file as it is a configuration file rather than executable code.

### Dependencies
This file does not directly import or rely on other files or modules. However, it specifies dependencies on runtime models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`), which are required for processing.

### Interfaces
The file exposes configuration details to other parts of the Mythos system, particularly to the components responsible for initializing and running the `COMPASS_KNOWLEDGE` function.

### Database
This file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with databases to retrieve or store conversation data.

### Configuration
The file itself is a configuration file. It does not use external config files or environment variables but relies on the values defined within it.

### Key Logic
The key logic described in this file is the configuration for processing and analyzing conversation exchanges. The `prompt` field specifies the instructions for the models to analyze the conversation and generate an authoritative, data-informed analysis. The `output_schema` defines the expected JSON structure of the analysis output.

### Integration Points
This configuration file integrates with the Mythos system's runtime environment, specifically with the components responsible for initializing and running the `COMPASS_KNOWLEDGE` function. It also integrates with the models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) specified for processing the conversation exchanges.

### Detailed Breakdown

1. **Metadata**:
   - `function_id`: `COMPASS_KNOWLEDGE`
   - `node`: `COMPASS`
   - `node_name`: `Compass`
   - `node_domain`: `Directional and intentional`
   - `layer`: `KNOWLEDGE`
   - `layer_name`: `Knowledge`
   - `depth`: `5`
   - `model_tier`: `medium`
   - `runtime_models`: `phi4:14b`, `qwen3:14b`, `mistral-small:24b`
   - `processing`: `conscious`
   - `critical_path`: `true`
   - `generated_at`: `2026-03-02T22:22:13.881769`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Prompt**:
   - The prompt instructs the models to analyze the conversation exchange at the `Compass` node and `Knowledge` layer, focusing on the user's actual needs, the right next action, Iris's required action, and the conversation trajectory.

3. **Output Schema**:
   - The output is expected to be a JSON object with the following properties:
     - `summary`: A 1-2 sentence summary of the analysis.
     - `confidence`: A confidence score between 0 and 1.
     - `flags`: An array of notable findings.
     - `stated_need`: The stated need of the user.
     - `actual_need`: The actual need of the user.
     - `recommended_action`: The recommended next action.
     - `trajectory`: The conversation trajectory.
   - The `required` fields are `summary`, `confidence`, and `flags`.

This configuration file is crucial for setting up the `COMPASS_KNOWLEDGE` function within the Mythos system, ensuring that the conversation analysis is performed with the specified models and that the output adheres to the defined schema.
