# neuro/arcturian_grid/templates/WEAVE_IDENTITY.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 59

---

### Purpose
The `WEAVE_IDENTITY.yaml` file defines the configuration and parameters for a specific function within the Mythos system, specifically the `WEAVE_IDENTITY` function operating at the `IDENTITY` layer of the `WEAVE` node. This function is designed to analyze conversation exchanges through the lens of relational connections and identity.

### Architecture
The file is structured as a YAML configuration file, containing metadata and configuration details for the `WEAVE_IDENTITY` function. It includes fields for function ID, node details, layer details, runtime models, processing type, and the expected output schema.

### Patterns
No design patterns are directly applicable to this YAML configuration file as it is a static configuration file rather than executable code.

### Dependencies
- **Runtime Models**: The function relies on specific AI models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) for processing.
- **Configuration**: The file itself is a dependency for the system to configure the `WEAVE_IDENTITY` function.

### Interfaces
- **Input**: The function expects a conversation exchange between a user message and an assistant response.
- **Output**: The function outputs a JSON object with keys `summary`, `confidence`, `flags`, `connections`, `active_threads`, and `relationship_dynamics`.

### Database
This configuration file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with the database to store or retrieve data related to the analysis.

### Configuration
- **Environment Variables**: No environment variables are explicitly mentioned in the file.
- **Config Files**: This file itself is a configuration file used by the Mythos system to set up the `WEAVE_IDENTITY` function.

### Key Logic
The key logic is embedded in the `prompt` field, which specifies the instructions for the AI models to analyze the conversation exchange. The analysis focuses on:
1. Relationships between people and topics.
2. Links to active threads/projects.
3. Social dynamics and partnership patterns.
The output is expected to provide a summary, confidence level, notable findings, connections, active threads, and relationship dynamics.

### Integration Points
- **Mythos Subsystems**: This function integrates with the AI runtime subsystems (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) and potentially with the database subsystem for storing/retrieving data related to the analysis.
- **Other Nodes/Layers**: The function operates within the `WEAVE` node at the `IDENTITY` layer and may interact with other nodes and layers for comprehensive analysis.

### Summary
The `WEAVE_IDENTITY.yaml` file serves as a configuration template for the `WEAVE_IDENTITY` function, detailing its purpose, runtime dependencies, and expected output schema. It is crucial for setting up the function within the Mythos system to perform relational and identity-based analysis on conversation exchanges.
