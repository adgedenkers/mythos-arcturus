# neuro/arcturian_grid/templates/COMPASS_NARRATIVE.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 61

---

### Purpose
The `COMPASS_NARRATIVE.yaml` file defines a function template for the Mythos system, specifically for the `COMPASS` node and `NARRATIVE` layer. This template specifies the configuration and parameters for processing and analyzing conversation exchanges through the lenses of directionality and narrative depth.

### Architecture
The file is structured as a YAML document with various key-value pairs that define the function's properties and behavior. It includes metadata, model specifications, processing details, and the expected output schema.

### Patterns
No specific design patterns are used in this YAML file, as it is a configuration file rather than executable code.

### Dependencies
The file depends on the following models for runtime processing:
- `gemma3:27b`
- `iris-thinking-v2:latest`
- `command-r:35b`

### Interfaces
The file does not expose any direct interfaces but serves as a configuration template for the Mythos system's function execution framework.

### Database
This YAML file does not directly interact with any database tables or Neo4j labels. However, the function it defines might interact with the database through the Mythos system's runtime environment.

### Configuration
The file uses the following configuration settings:
- `function_id`: `COMPASS_NARRATIVE`
- `node`: `COMPASS`
- `node_domain`: `Directional and intentional`
- `layer`: `NARRATIVE`
- `layer_name`: `Narrative`
- `depth`: `7`
- `model_tier`: `large`
- `runtime_models`: List of models to be used
- `processing`: `deep_conscious`
- `critical_path`: `false`
- `generated_at`: Timestamp of generation
- `generated_by`: Model used to generate the template

### Key Logic
The key logic is embedded in the `prompt` field, which specifies the instructions for the AI models to analyze the conversation exchange:
- **Compass Analysis**: Identify the actual intent, next action, and trajectory.
- **Narrative Placement**: Place the exchange in the larger story context, identifying the current chapter and arc.

The output is expected to be a JSON object with specific keys (`compass_analysis` and `narrative_placement`), and the schema is defined in the `output_schema` section.

### Integration Points
This YAML file integrates with the Mythos system's function execution framework, which uses the specified models and processing settings to execute the function. The function is part of the `COMPASS` node and `NARRATIVE` layer, and it is designed to be used in conjunction with other components of the Mythos system for comprehensive analysis and processing of conversation exchanges.
