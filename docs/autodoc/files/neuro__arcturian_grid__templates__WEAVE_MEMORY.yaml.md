# neuro/arcturian_grid/templates/WEAVE_MEMORY.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 58

---

### Purpose
The `WEAVE_MEMORY.yaml` file is a configuration template for the WEAVE node within the MEMORY layer of the Mythos system. It defines the parameters, models, and expected output schema for processing relational and connective tissue data at a depth of 4, focusing on memory.

### Architecture
The file is structured as a YAML configuration file with key-value pairs. It includes metadata, function-specific parameters, and an output schema definition. The output schema is defined using JSON Schema, specifying the structure of the expected JSON output.

### Patterns
No specific design patterns are used in this YAML file as it is a configuration file rather than executable code.

### Dependencies
This file does not import or rely on any external dependencies directly. However, it references models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) that are expected to be available in the system.

### Interfaces
The file exposes the following key interfaces:
- **Function ID**: `WEAVE_MEMORY`
- **Prompt**: A template for generating prompts to be processed by the models.
- **Output Schema**: A JSON Schema defining the structure of the output.

### Database
This file does not directly interact with any database tables or Neo4j labels. However, the models it references are expected to interact with the underlying data storage (PostgreSQL, Neo4j, Redis) to retrieve and process relational and connective tissue data.

### Configuration
The file uses the following configuration parameters:
- **function_id**: `WEAVE_MEMORY`
- **node**: `WEAVE`
- **node_domain**: `Relational and connective tissue`
- **layer**: `MEMORY`
- **depth**: `4`
- **model_tier**: `medium`
- **runtime_models**: List of models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`)
- **processing**: `conscious`
- **critical_path**: `false`
- **generated_at**: Timestamp of generation
- **generated_by**: Model used for generation (`iris-thinking-v2:latest`)

### Key Logic
The key logic is embedded in the prompt, which instructs the models to analyze the conversation exchange between a user message and an assistant response. The models are expected to identify connections to past conversations, relationships, active threads, and social dynamics, and output a JSON object with the specified schema.

### Integration Points
This file integrates with other parts of the Mythos system through:
- **Models**: The specified models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) are expected to be available and capable of processing the prompts.
- **Data Storage**: The models are expected to interact with the underlying data storage (PostgreSQL, Neo4j, Redis) to retrieve and process the necessary data.
- **Output Handling**: The output schema defines how the results from the models should be structured, which can be consumed by other parts of the system for further processing or display.

### Summary
The `WEAVE_MEMORY.yaml` file serves as a configuration template for the WEAVE node in the MEMORY layer of the Mythos system. It specifies the parameters, models, and expected output schema for processing relational and connective tissue data, focusing on memory and social dynamics. The file integrates with the underlying models and data storage to provide structured analysis outputs.
