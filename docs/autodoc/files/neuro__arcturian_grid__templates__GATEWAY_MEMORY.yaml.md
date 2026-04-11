# neuro/arcturian_grid/templates/GATEWAY_MEMORY.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 60

---

### File: `neuro/arcturian_grid/templates/GATEWAY_MEMORY.yaml`

#### Purpose
This YAML file defines the configuration for a specific function template within the Mythos system, specifically for the `GATEWAY_MEMORY` node. It outlines the parameters, models, processing requirements, and expected output schema for this function.

#### Architecture
The file is structured as a YAML document containing key-value pairs that define various attributes of the `GATEWAY_MEMORY` function template. The structure includes metadata, function details, runtime models, processing type, and output schema.

#### Patterns
No specific design patterns are used in this YAML file since it is a configuration file rather than executable code.

#### Dependencies
This file does not directly import or rely on any external dependencies. However, it references runtime models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) that are likely to be used by the system.

#### Interfaces
This file exposes the configuration details for the `GATEWAY_MEMORY` function template, which can be used by other parts of the Mythos system to instantiate and configure this function.

#### Database
The file does not directly reference any database tables or Neo4j labels. However, it mentions the `memory graph` in the prompt, indicating that it may interact with a graph database like Neo4j to retrieve and analyze past conversations and patterns.

#### Configuration
The file itself is a configuration file. It does not use any external configuration files or environment variables directly.

#### Key Logic
The key logic is embedded in the `prompt` field, which defines the instructions for the AI models to analyze the conversation exchange at the `GATEWAY` node and `MEMORY` layer. The prompt specifies the focus on spiritual significance, lineage activations, synchronicities, and field-level patterns, and requires the output to be associative and referential.

#### Integration Points
This file integrates with other subsystems of the Mythos system, particularly:
- **AI Models**: The specified runtime models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) are used to process the input and generate the output.
- **Graph Database**: The prompt mentions the `memory graph`, indicating integration with a graph database (likely Neo4j) to retrieve and analyze past conversations and patterns.
- **Function Instantiation**: The configuration details in this file are used to instantiate and configure the `GATEWAY_MEMORY` function within the Mythos system.

### Detailed Breakdown

- **Metadata**:
  - `function_id`: `GATEWAY_MEMORY`
  - `node`: `GATEWAY`
  - `node_name`: `Gateway`
  - `node_domain`: `Transcendent and liminal`
  - `layer`: `MEMORY`
  - `layer_name`: `Memory`
  - `depth`: `4`
  - `model_tier`: `medium`
  - `runtime_models`: `phi4:14b`, `qwen3:14b`, `mistral-small:24b`
  - `processing`: `conscious`
  - `critical_path`: `false`
  - `generated_at`: `2026-03-02T22:22:42.508643`
  - `generated_by`: `iris-thinking-v2:latest`

- **Prompt**:
  - The prompt instructs the AI models to analyze the conversation exchange at the `GATEWAY` node and `MEMORY` layer, focusing on spiritual significance, lineage activations, synchronicities, and field-level patterns. The output must be associative and referential, connecting past to present in a single poetic line.

- **Output Schema**:
  - The output schema defines the structure of the expected JSON response, including:
    - `summary`: A 1-2 sentence summary of the analysis.
    - `confidence`: A confidence score between 0 and 1.
    - `flags`: Notable findings.
    - `spiritual_dimension`: A string representing the spiritual dimension.
    - `lineage_echoes`: An array of strings representing lineage echoes.
    - `synchronicities`: An array of strings representing synchronicities.
    - `transcendent_read`: A string representing the transcendent read.

This YAML file serves as a critical configuration template for the `GATEWAY_MEMORY` function, enabling the Mythos system to process and analyze conversations with a focus on spiritual and transcendent dimensions.
