# neuro/arcturian_grid/templates/MIRROR_MEMORY.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 63

---

### Purpose
The `MIRROR_MEMORY.yaml` file is a configuration template for a specific function within the Mythos system, specifically designed to analyze conversation exchanges through the lens of self-referential awareness and memory. It defines the parameters, models, and expected output schema for the `MIRROR_MEMORY` function.

### Architecture
The file is structured as a YAML document, containing metadata and configuration details for the `MIRROR_MEMORY` function. It includes sections for function identification, node and layer details, model configurations, processing type, and output schema.

### Patterns
This file does not directly implement any design patterns but serves as a configuration template that is likely used by a factory pattern to instantiate and configure the `MIRROR_MEMORY` function.

### Dependencies
- **Models**: The function relies on specific AI models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) for processing.
- **System**: The configuration is used by the Mythos system to set up and run the `MIRROR_MEMORY` function.

### Interfaces
The file exposes the following configuration details to the Mythos system:
- `function_id`: Identifier for the function.
- `node`: Node identifier (`MIRROR`).
- `node_domain`: Domain of the node (`Self-referential awareness`).
- `layer`: Layer identifier (`MEMORY`).
- `depth`: Depth level (`4`).
- `model_tier`: Model tier (`medium`).
- `runtime_models`: List of models to be used.
- `processing`: Type of processing (`conscious`).
- `critical_path`: Indicates if the function is on a critical path (`false`).
- `prompt`: The prompt template for the AI models.
- `output_schema`: The expected JSON schema for the output.

### Database
The function is expected to interact with the memory graph stored in Neo4j, connecting past conversations, exchanges, patterns, or stored knowledge.

### Configuration
- **Environment Variables**: No explicit environment variables are used.
- **Config Files**: This file itself is a configuration file used by the Mythos system.

### Key Logic
The key logic involves:
- **Prompt Generation**: The prompt template is used to generate a specific query for the AI models.
- **Output Parsing**: The output from the AI models is expected to conform to the defined JSON schema.

### Integration Points
- **Mythos System**: The configuration is used by the Mythos system to set up and run the `MIRROR_MEMORY` function.
- **AI Models**: The function integrates with the specified AI models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) for processing.
- **Neo4j**: The function is expected to interact with the Neo4j graph database to retrieve and store memory-related data.

### Summary
The `MIRROR_MEMORY.yaml` file is a configuration template for the `MIRROR_MEMORY` function within the Mythos system. It defines the function's parameters, models, and expected output schema, and is used to set up and run the function within the system. The function is designed to analyze conversation exchanges through self-referential awareness and memory, leveraging specific AI models and interacting with the Neo4j graph database.
