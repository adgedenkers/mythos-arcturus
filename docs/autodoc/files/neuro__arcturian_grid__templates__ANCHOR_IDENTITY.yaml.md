# neuro/arcturian_grid/templates/ANCHOR_IDENTITY.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 71

---

### Purpose
The `ANCHOR_IDENTITY.yaml` file defines a configuration template for a specific function within the Mythos system, specifically for the `ANCHOR` node within the `IDENTITY` layer. This configuration specifies the parameters, models, and expected output schema for processing and analyzing conversation exchanges.

### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes and parameters for the function. The structure includes metadata, model configurations, processing details, and output schema.

### Patterns
No specific design patterns are used in this file as it is a configuration file rather than executable code.

### Dependencies
This file does not directly import or rely on any external dependencies. However, it references specific models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) that are expected to be available in the system.

### Interfaces
The file exposes a configuration interface to other parts of the Mythos system, particularly to the components responsible for loading and interpreting function configurations. It does not expose any direct functions or classes.

### Database
This file does not interact directly with any database tables or Neo4j labels. It is a configuration file that defines the behavior and expected output of a function.

### Configuration
The file itself serves as a configuration file, defining various parameters and settings for the function. It does not use any external configuration files or environment variables.

### Key Logic
The key logic is embedded in the `prompt` field, which defines the instructions for the models to analyze the conversation exchange. The prompt specifies the extraction of physical/logistical details and the identification of the activated identity aspect, with the output structured as a JSON object.

### Integration Points
This file integrates with the Mythos system's function loading and execution mechanisms. Specifically, it is likely used by a component that loads function configurations, initializes the specified models, and processes input data according to the defined prompt and output schema.

### Detailed Breakdown

1. **Metadata**:
   - `function_id`: `ANCHOR_IDENTITY`
   - `node`: `ANCHOR`
   - `node_name`: `Anchor`
   - `node_domain`: `Physical and structural reality`
   - `layer`: `IDENTITY`
   - `layer_name`: `Identity`
   - `depth`: `8`
   - `model_tier`: `large`
   - `runtime_models`: List of models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`)
   - `processing`: `deep_conscious`
   - `critical_path`: `false`
   - `generated_at`: `2026-03-02T21:50:40.325374`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Prompt**:
   - The prompt specifies the analysis of conversation exchanges through the `ANCHOR` node and `IDENTITY` layer, focusing on physical/logistical details and identity aspects. The output is expected to be a JSON object with specific keys (`node_analysis`, `layer_insight`).

3. **Output Schema**:
   - The output schema defines the structure of the expected JSON output, including properties like `summary`, `confidence`, `flags`, `locations`, `times`, `people`, `objects`, `actions`, and `environment`. The `summary` and `confidence` fields are required.

This configuration file is critical for defining the behavior and expected output of the `ANCHOR_IDENTITY` function within the Mythos system, ensuring consistent and structured analysis of conversation exchanges.
