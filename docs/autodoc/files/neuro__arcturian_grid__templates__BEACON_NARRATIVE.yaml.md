# neuro/arcturian_grid/templates/BEACON_NARRATIVE.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 80

---

### Purpose
The `BEACON_NARRATIVE.yaml` file defines a template for a specific function within the Mythos system, specifically for analyzing conversation exchanges within the context of knowledge and information retrieval at the Narrative depth level.

### Architecture
The file is structured as a YAML configuration template that defines various parameters and settings for the `BEACON_NARRATIVE` function. It includes metadata, processing details, and the structure of the expected output.

### Patterns
This file does not directly implement design patterns but serves as a configuration template that can be used by other components of the system, such as a factory pattern to instantiate specific function instances.

### Dependencies
The file does not directly import or rely on any external libraries or modules. Instead, it is a configuration file that is likely read and processed by other parts of the Mythos system.

### Interfaces
This file exposes configuration details to other parts of the Mythos system, particularly to the components that handle the execution and processing of the `BEACON_NARRATIVE` function.

### Database
The file references data sources such as the knowledge graph, PostgreSQL (for financial, calendar, and task data), and past conversations. However, it does not directly interact with the database; it specifies the data sources that should be queried during the function's execution.

### Configuration
The file itself is a configuration file that is used to set up the `BEACON_NARRATIVE` function. It does not rely on external configuration files or environment variables but can be influenced by them.

### Key Logic
The key logic described in this file is the prompt that guides the analysis of the conversation exchange. The prompt instructs the model to analyze the exchange within the context of a larger narrative, focusing on facts from the knowledge graph, data from PostgreSQL, and information from past conversations. The output is expected to be in JSON format with specific fields like `summary`, `confidence`, `flags`, `relevant_facts`, `data_points`, and `knowledge_gaps`.

### Integration Points
This file integrates with other subsystems of the Mythos platform, particularly:
- **Knowledge Graph**: For retrieving relevant facts.
- **PostgreSQL**: For financial, calendar, and task data.
- **Conversation History**: For past exchanges.
- **Model Execution**: The models specified (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) will be used to process the prompt and generate the output.
- **Output Handling**: The output schema is defined to ensure consistent and structured responses.

### Summary
The `BEACON_NARRATIVE.yaml` file serves as a configuration template for a specific function within the Mythos system. It defines the parameters, data sources, and expected output format for analyzing conversation exchanges within the context of knowledge and information retrieval. The file integrates with various subsystems of the Mythos platform to provide a comprehensive narrative analysis.
