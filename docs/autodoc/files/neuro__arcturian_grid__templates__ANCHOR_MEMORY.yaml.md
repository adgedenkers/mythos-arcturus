# neuro/arcturian_grid/templates/ANCHOR_MEMORY.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 70

---

### Purpose
The `ANCHOR_MEMORY.yaml` file is a configuration template for a specific function within the Mythos system, specifically for the `ANCHOR` node and `MEMORY` layer. It defines the parameters, models, and schema for processing and analyzing user messages and assistant responses in the context of physical and structural reality.

### Architecture
The file is structured as a YAML document with key-value pairs and nested structures to define various attributes and configurations. It includes metadata, function-specific details, and output schema.

### Patterns
No specific design patterns are used in this YAML configuration file. It is a straightforward configuration file that defines the structure and parameters for a function.

### Dependencies
This file does not directly import or rely on other files or modules. However, it specifies runtime models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) that are required for processing.

### Interfaces
The file exposes the following key interfaces:
- `function_id`: Identifier for the function (`ANCHOR_MEMORY`).
- `prompt`: The prompt template used for processing user messages and assistant responses.
- `output_schema`: The expected JSON schema for the output.

### Database
This file does not directly interact with any database tables or Neo4j labels. However, the `MEMORY` layer likely involves querying a Neo4j graph database to identify past conversations and patterns.

### Configuration
The file uses environment-specific details such as the `generated_by` and `generated_at` fields, which are auto-generated. It also specifies the `model_tier` and `runtime_models` which can be configured based on the system's needs.

### Key Logic
The key logic involves processing user messages and assistant responses through the `ANCHOR` node and `MEMORY` layer. The `prompt` field specifies the exact instructions for extracting physical/logistical details and identifying associative past references in the memory graph.

### Integration Points
This configuration file integrates with the following subsystems:
- **Runtime Models**: The specified models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) are used for processing.
- **Neo4j Graph Database**: The `MEMORY` layer likely queries the Neo4j graph database to identify past conversations and patterns.
- **FastAPI**: The function is likely exposed as an endpoint in the FastAPI application, using the defined `output_schema`.

### Summary
The `ANCHOR_MEMORY.yaml` file serves as a configuration template for a function in the Mythos system, defining how user messages and assistant responses are processed through the `ANCHOR` node and `MEMORY` layer. It specifies the runtime models, processing instructions, and output schema, and integrates with the Neo4j graph database for memory-related queries.
