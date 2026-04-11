# neuro/arcturian_grid/templates/COMPASS_MEMORY.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 55

---

### Purpose
The `COMPASS_MEMORY.yaml` file defines the configuration for a specific node in the Mythos system, specifically the `COMPASS` node at the `MEMORY` layer. This configuration specifies the function ID, node details, processing requirements, and the expected output schema for the node.

### Architecture
The file is structured as a YAML document with key-value pairs that define various attributes of the node. The structure includes:
- **Metadata**: Information about the node, layer, and generation details.
- **Function ID**: Unique identifier for the node.
- **Node and Layer Details**: Descriptions and identifiers for the node and layer.
- **Runtime Models**: List of models that can be used for processing.
- **Processing Details**: Information about the processing type and critical path status.
- **Prompt**: A template for the prompt that will be used to generate responses.
- **Output Schema**: Definition of the expected JSON output structure.

### Patterns
The file does not directly implement any design patterns as it is a configuration file. However, it follows a template pattern for defining node configurations within the Mythos system.

### Dependencies
- **Models**: The configuration relies on specific models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) for processing.
- **Prompt**: The configuration uses a specific prompt template for generating responses.

### Interfaces
The file exposes the following interfaces:
- **Function ID**: `COMPASS_MEMORY`
- **Prompt Template**: Used to generate responses based on user and assistant interactions.
- **Output Schema**: Defines the structure of the JSON output.

### Database
The file does not directly interact with any database tables or Neo4j labels. However, it references the `MEMORY` layer, which implies that it may interact with a memory graph stored in Neo4j.

### Configuration
- **Environment Variables**: The file does not explicitly use any environment variables.
- **Config Files**: The file itself is a configuration file that is used to define the behavior of the `COMPASS` node at the `MEMORY` layer.

### Key Logic
The key logic is embedded in the prompt template, which guides the processing of user and assistant interactions. The prompt focuses on:
- Analyzing the conversation exchange at the `MEMORY` layer.
- Identifying the user's actual needs and recommended actions.
- Connecting the current interaction to past conversations and exchanges in the memory graph.

### Integration Points
- **Mythos Subsystems**: The node integrates with the overall Mythos system, particularly with the `MEMORY` layer and the models specified for processing.
- **Prompt Generation**: The prompt template is used to generate responses, which are then processed by the specified models.
- **Output Handling**: The output schema defines how the results are structured and returned to the system.

### Summary
The `COMPASS_MEMORY.yaml` file is a configuration file that defines the behavior of the `COMPASS` node at the `MEMORY` layer within the Mythos system. It specifies the function ID, node details, processing requirements, and the expected output schema. The file does not directly interact with databases but relies on specific models and a prompt template for processing user and assistant interactions.
