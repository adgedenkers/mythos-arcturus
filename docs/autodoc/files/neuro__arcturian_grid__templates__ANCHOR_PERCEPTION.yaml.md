# neuro/arcturian_grid/templates/ANCHOR_PERCEPTION.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 68

---

### Purpose
The `ANCHOR_PERCEPTION.yaml` file defines a configuration template for a function within the Mythos system, specifically for the `ANCHOR` node at the `PERCEPTION` layer. This function is designed to analyze input messages and responses to extract directly observable physical and logistical details, outputting the results in a structured JSON format.

### Architecture
The file is structured as a YAML document that contains metadata and configuration details for the function. It includes fields such as `function_id`, `node`, `node_domain`, `layer`, `depth`, `model_tier`, `runtime_models`, `processing`, `critical_path`, `generated_at`, `generated_by`, `prompt`, and `output_schema`.

### Patterns
No specific design patterns are used in this YAML configuration file, as it is a static configuration file rather than executable code.

### Dependencies
This configuration file does not import or rely on any external dependencies directly. However, it references runtime models (`mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`) that need to be available in the system.

### Interfaces
This file exposes configuration details that are used by the Mythos system to instantiate and configure the function. The `prompt` and `output_schema` fields are particularly important as they define the input and output expectations for the function.

### Database
This configuration file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with databases through the Mythos system's runtime environment.

### Configuration
The file itself is a configuration file that is likely generated and used by the Mythos system. It does not reference any external configuration files or environment variables directly.

### Key Logic
The key logic is embedded in the `prompt` field, which defines the instructions for the AI models to extract directly observable physical and logistical details from the input messages and responses. The `output_schema` defines the expected JSON structure for the output, ensuring consistency in the results.

### Integration Points
This configuration file integrates with the Mythos system's function management and execution subsystems. The `function_id`, `node`, `layer`, and `runtime_models` fields are critical for the system to correctly instantiate and execute the function. The `prompt` and `output_schema` are used by the AI models to process the input and generate the output, respectively.

### Summary
The `ANCHOR_PERCEPTION.yaml` file serves as a configuration template for a function within the Mythos system, defining its role in extracting observable physical and logistical details from input messages and responses. It specifies the function's metadata, runtime models, processing requirements, and expected output schema, ensuring that the function operates as intended within the broader system architecture.
