# neuro/arcturian_grid/templates/BEACON_IDENTITY.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 80

---

### File: `neuro/arcturian_grid/templates/BEACON_IDENTITY.yaml`

#### Purpose
This YAML file defines a template for a function within the Mythos system, specifically for the `BEACON` node at the `IDENTITY` layer. It outlines the configuration and parameters for processing information retrieval and analysis tasks related to identity.

#### Architecture
The file is structured as a YAML document with key-value pairs that define various attributes of the function template. It includes metadata, runtime configurations, and the expected output schema.

#### Patterns
This file does not directly implement any design patterns but serves as a configuration template that could be used by a factory pattern to instantiate specific function instances.

#### Dependencies
- **Runtime Models**: The file specifies a list of models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) that can be used for processing.
- **Database**: It references data from PostgreSQL and Neo4j (knowledge graph).

#### Interfaces
- **Prompt**: The file defines a prompt that is used to guide the analysis of conversation exchanges.
- **Output Schema**: The file specifies the expected JSON schema for the output, including properties like `summary`, `confidence`, `flags`, `relevant_facts`, `data_points`, and `knowledge_gaps`.

#### Database
- **PostgreSQL**: The prompt references data from PostgreSQL (financial, calendar, task).
- **Neo4j**: The prompt references facts from the knowledge graph.

#### Configuration
- **Environment Variables**: The file does not directly use environment variables but relies on the configuration of the runtime models and the data sources.
- **Config Files**: The file itself is a configuration file that can be used to configure a specific function instance.

#### Key Logic
- **Prompt Logic**: The prompt guides the analysis of the conversation exchange, focusing on the identity of the user and the relevant aspects of their interaction.
- **Output Schema**: The output is expected to be in JSON format with specific fields that summarize the analysis, provide confidence levels, and list relevant facts and data points.

#### Integration Points
- **PostgreSQL**: The function integrates with PostgreSQL to retrieve financial, calendar, and task data.
- **Neo4j**: The function integrates with Neo4j to retrieve facts from the knowledge graph.
- **Runtime Models**: The function integrates with the specified runtime models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) to process the conversation exchange.
- **Arcturian Grid**: The function is part of the Arcturian Grid and is configured to operate within the `BEACON` node at the `IDENTITY` layer.

### Summary
This YAML file serves as a configuration template for a function within the Mythos system, specifically for the `BEACON` node at the `IDENTITY` layer. It defines the processing logic, runtime models, and expected output schema for analyzing conversation exchanges through the lens of identity. The file integrates with PostgreSQL and Neo4j to retrieve relevant data and is designed to be used within the broader Arcturian Grid architecture.
