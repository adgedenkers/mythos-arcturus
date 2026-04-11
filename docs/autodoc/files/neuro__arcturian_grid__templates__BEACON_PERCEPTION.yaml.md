# neuro/arcturian_grid/templates/BEACON_PERCEPTION.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 58

---

### Purpose
The `BEACON_PERCEPTION.yaml` file defines the configuration and parameters for a specific function within the Mythos system, specifically the `BEACON_PERCEPTION` function, which is part of the Perception layer and focuses on knowledge and information retrieval.

### Architecture
The file is structured as a YAML document with key-value pairs, defining various attributes and configurations for the `BEACON_PERCEPTION` function. It includes metadata such as function ID, node details, layer information, runtime models, processing type, and output schema.

### Patterns
This file does not directly implement any design patterns but serves as a configuration template that could be used by a factory pattern to instantiate and configure the `BEACON_PERCEPTION` function.

### Dependencies
The file does not import or rely on other files directly but is likely used by a configuration parser or a factory to instantiate the function. It references specific models (`mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`) that are required for the function's runtime.

### Interfaces
This file exposes configuration details to other parts of the system, particularly to the configuration parser or factory that will use these details to set up the `BEACON_PERCEPTION` function.

### Database
The file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with databases to retrieve or store information.

### Configuration
The file itself is a configuration file. It uses environment variables or other configuration settings to define the function's behavior, such as the `model_tier`, `runtime_models`, and `prompt`.

### Key Logic
The key logic described in the file is the configuration of the `BEACON_PERCEPTION` function, which involves:
- Analyzing user messages and assistant responses.
- Extracting literal facts without interpretation or inference.
- Outputting a JSON object with specific fields (`summary`, `confidence`, `flags`, `relevant_facts`, `data_points`, `knowledge_gaps`).

### Integration Points
This file integrates with:
- The configuration parser or factory that reads and applies the configuration.
- The runtime models (`mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`) that process the input data.
- The broader Mythos system, particularly the Perception layer, where this function is part of the knowledge and information retrieval domain.

### Summary
The `BEACON_PERCEPTION.yaml` file serves as a configuration template for the `BEACON_PERCEPTION` function within the Mythos system. It defines the function's metadata, runtime models, processing type, and output schema. This configuration is used by the system to set up and run the function, which focuses on analyzing and extracting literal facts from user messages and assistant responses.
