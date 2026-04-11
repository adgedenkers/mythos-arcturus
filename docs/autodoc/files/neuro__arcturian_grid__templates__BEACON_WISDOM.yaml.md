# neuro/arcturian_grid/templates/BEACON_WISDOM.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 80

---

### File: `neuro/arcturian_grid/templates/BEACON_WISDOM.yaml`

#### Purpose
This YAML file defines the configuration for the `BEACON_WISDOM` function template, which is designed to analyze conversation exchanges through the lens of knowledge and information retrieval, focusing on deep wisdom and transcendent insights.

#### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes and settings for the `BEACON_WISDOM` function template. The configuration includes metadata, model specifications, processing details, and the expected output schema.

#### Patterns
This file does not implement any design patterns as it is a configuration file. However, it serves as a template for the `BEACON_WISDOM` function, which can be considered a form of template pattern.

#### Dependencies
This file does not directly import or rely on any external libraries or modules. Instead, it provides configuration data that is used by other parts of the Mythos system.

#### Interfaces
This configuration file is used by the Mythos system to define the behavior and expected output of the `BEACON_WISDOM` function. It does not expose any direct interfaces but serves as input to the system's function execution logic.

#### Database
The configuration specifies that the function should integrate data from the knowledge graph, PostgreSQL (financial, calendar, task data), and past conversations. However, it does not directly define any database tables or Neo4j labels.

#### Configuration
The file uses the following configuration settings:
- `function_id`: `BEACON_WISDOM`
- `node`: `BEACON`
- `node_name`: `Beacon`
- `node_domain`: `Knowledge and information retrieval`
- `layer`: `WISDOM`
- `layer_name`: `Wisdom`
- `depth`: `9`
- `model_tier`: `large`
- `runtime_models`: List of models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`)
- `processing`: `deep_conscious`
- `critical_path`: `true`
- `generated_at`: `2026-03-02T22:20:34.953418`
- `generated_by`: `fallback`

#### Key Logic
The key logic is embedded in the `prompt` field, which specifies the task of analyzing conversation exchanges through the lens of knowledge and information retrieval, focusing on deep wisdom and transcendent insights. The prompt also specifies the core question to answer and the format of the output.

#### Integration Points
This configuration file integrates with the following subsystems of the Mythos system:
- **Knowledge Graph**: For retrieving facts.
- **PostgreSQL**: For retrieving financial, calendar, and task data.
- **Past Conversations**: For context and historical data.
- **Models**: The specified models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) are used to process the input and generate the output.

The output schema is defined to ensure that the function returns a structured JSON response with specific fields (`summary`, `confidence`, `flags`, `relevant_facts`, `data_points`, `knowledge_gaps`).

### Summary
This YAML file serves as a configuration template for the `BEACON_WISDOM` function, defining its purpose, dependencies, and expected output schema. It integrates with various subsystems of the Mythos system to provide deep and transcendent analysis of conversation exchanges.
