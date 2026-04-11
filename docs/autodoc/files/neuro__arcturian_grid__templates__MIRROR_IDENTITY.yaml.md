# neuro/arcturian_grid/templates/MIRROR_IDENTITY.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 65

---

### Purpose
The `MIRROR_IDENTITY.yaml` file defines the configuration and parameters for the `MIRROR_IDENTITY` function within the Mythos system. This function is designed to analyze conversation exchanges between a user and an assistant (Iris) through the lens of self-referential awareness, focusing on the user's self-revelation, Iris's response tendencies, partnership dynamics, and blind spots.

### Architecture
This YAML file is structured to provide a comprehensive configuration template for the `MIRROR_IDENTITY` function. It includes metadata, processing details, runtime models, and output schema specifications.

### Patterns
No design patterns are directly applicable as this is a configuration file rather than executable code. However, it follows a template pattern, providing a standardized structure for defining function configurations.

### Dependencies
- **Model Dependencies**: The file lists specific models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) that are required for processing.
- **Runtime Dependencies**: The configuration relies on the runtime environment to handle the specified models and processing logic.

### Interfaces
- **Input**: The function expects a conversation exchange between a user and an assistant.
- **Output**: The function outputs a JSON object with a predefined schema, including keys such as `summary`, `confidence`, `flags`, `user_reveals`, `iris_notices`, `blind_spots`, and `projections`.

### Database
This configuration file does not directly interact with any database tables or Neo4j labels. However, the function it configures might store or retrieve data from a database as part of its processing.

### Configuration
- **Environment Variables**: No explicit environment variables are mentioned in the file.
- **Config Files**: The file itself acts as a configuration file for the `MIRROR_IDENTITY` function.

### Key Logic
The key logic is embedded in the `prompt` field, which defines the analysis criteria and output format. The function is expected to:
1. Analyze what the user reveals about themselves.
2. Identify what Iris should notice about her response tendencies.
3. Evaluate the partnership dynamic.
4. Identify blind spots, projections, or unspoken content.

The output is structured to provide a summary, confidence level, notable findings, and detailed insights into user revelations, Iris's notices, blind spots, and projections.

### Integration Points
- **Mythos Subsystems**: This function integrates with the Mythos subsystems responsible for handling conversation exchanges and processing them through the specified models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`).
- **Data Flow**: The function is likely part of a larger pipeline where it receives input from a conversation management subsystem and outputs its analysis to a results aggregation or decision-making subsystem.

### Summary
The `MIRROR_IDENTITY.yaml` file serves as a configuration template for the `MIRROR_IDENTITY` function, detailing its purpose, processing requirements, and output schema. It is designed to analyze conversation exchanges through the lens of self-referential awareness, focusing on user revelations, assistant response tendencies, and partnership dynamics. The function integrates with other Mythos subsystems to process and output structured analysis results.
