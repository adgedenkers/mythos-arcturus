# neuro/arcturian_grid/templates/COMPASS_IDENTITY.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 55

---

### Purpose
The `COMPASS_IDENTITY.yaml` file is a configuration template for a specific function within the Mythos system, specifically for the COMPASS node at the IDENTITY layer. It defines the parameters, models, and expected output schema for processing and analyzing conversation exchanges.

### Architecture
The file is structured as a YAML document with key-value pairs. It contains metadata about the function, configuration details for the models and runtime, and a detailed output schema.

### Patterns
No specific design patterns are used in this YAML file, as it is a configuration file rather than executable code.

### Dependencies
This file does not import or rely on other files directly. However, it specifies dependencies on specific models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) that need to be available in the runtime environment.

### Interfaces
The file exposes configuration details and an output schema that other parts of the Mythos system can use to understand how to interact with this function. It does not expose any executable logic directly.

### Database
This file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with databases as part of its runtime execution.

### Configuration
The file itself is a configuration file. It does not use any external config files or environment variables directly. However, the runtime environment must be configured to support the specified models and processing requirements.

### Key Logic
The key logic is embedded in the `prompt` field, which defines the instructions for the models to analyze the conversation exchange. The models are expected to extract specific information and output it in a structured JSON format.

### Integration Points
This file integrates with the Mythos system's runtime environment, which uses the specified models and processes the conversation exchanges according to the defined schema. It also integrates with the overall Mythos architecture by providing a standardized configuration for the COMPASS node at the IDENTITY layer.

### Detailed Breakdown

1. **Metadata**:
   - `function_id`: `COMPASS_IDENTITY`
   - `node`: `COMPASS`
   - `node_name`: `Compass`
   - `node_domain`: `Directional and intentional`
   - `layer`: `IDENTITY`
   - `layer_name`: `Identity`
   - `depth`: `8`
   - `model_tier`: `large`
   - `generated_at`: `2026-03-02T22:22:25.910462`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Runtime Models**:
   - `runtime_models`: List of models to be used (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`)

3. **Processing and Critical Path**:
   - `processing`: `deep_conscious`
   - `critical_path`: `false`

4. **Prompt**:
   - The `prompt` field contains detailed instructions for the models to analyze the conversation exchange and extract specific information.

5. **Output Schema**:
   - `output_schema`: Defines the expected JSON output structure with required fields (`summary`, `confidence`, `flags`) and optional fields (`stated_need`, `actual_need`, `recommended_action`, `trajectory`).

This configuration ensures that the COMPASS node at the IDENTITY layer processes conversation exchanges in a standardized and structured manner, providing valuable insights into the user's needs and the appropriate actions to take.
