# neuro/arcturian_grid/templates/ANCHOR_PROCESSING.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 70

---

### Purpose
The `ANCHOR_PROCESSING.yaml` file defines the configuration and specifications for the `ANCHOR_PROCESSING` function within the Mythos system. This function is designed to process and analyze conversations through the lens of physical and structural reality, extracting and interpreting physical/logistical details and providing structured outputs.

### Architecture
The file is structured as a YAML document with several key sections:
- Metadata: Information about the function, including its ID, node, domain, layer, depth, and generation details.
- Configuration: Details about the runtime models, processing type, and critical path status.
- Prompt: A detailed instruction for the AI models on how to process the input data.
- Output Schema: A JSON schema defining the structure of the output data.

### Patterns
No specific design patterns are directly applicable to this YAML configuration file. However, the structure follows a template pattern, where the configuration is standardized for different functions within the system.

### Dependencies
This file does not directly import any dependencies. However, it relies on the following:
- AI models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`)
- The `iris-thinking-v2:latest` model for generation

### Interfaces
The file exposes the following interfaces to other parts of the system:
- **Function ID**: `ANCHOR_PROCESSING`
- **Prompt**: A detailed instruction for AI models
- **Output Schema**: A JSON schema defining the structure of the output data

### Database
This file does not directly interact with any database tables or Neo4j labels. However, the processed data and outputs might be stored in the PostgreSQL or Neo4j databases as part of the broader Mythos system.

### Configuration
The file uses the following configuration details:
- **Model Tier**: `medium`
- **Runtime Models**: `phi4:14b`, `qwen3:14b`, `mistral-small:24b`
- **Prompt**: Detailed instruction for AI models
- **Output Schema**: JSON schema for output structure

### Key Logic
The key logic revolves around the prompt, which instructs the AI models to:
1. Analyze the conversation exchange between a user message and an assistant response.
2. Extract physical/logistical details such as time, place, location, physical objects, logistics, scheduling, body state, health, environment, infrastructure, or hardware.
3. Interpret the meaning by applying relevant frameworks, making connections, and explaining significance.
4. Output a JSON object with two keys: `physical_details` (structured list of extracted facts) and `interpretation` (analytical explanation of meaning/significance using frameworks).

### Integration Points
This file integrates with other subsystems of the Mythos system in the following ways:
- **AI Models**: The specified models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) are used to process the input data.
- **Data Processing Pipeline**: The output schema and prompt are used to ensure consistent and structured processing of data.
- **Data Storage**: The processed data and outputs might be stored in the PostgreSQL or Neo4j databases.
- **User Interface**: The structured output can be used to provide meaningful and structured insights to users or other parts of the system.

This YAML configuration file is a crucial component of the Mythos system, defining how the `ANCHOR_PROCESSING` function operates and ensuring consistent and structured processing of physical and structural reality data.
