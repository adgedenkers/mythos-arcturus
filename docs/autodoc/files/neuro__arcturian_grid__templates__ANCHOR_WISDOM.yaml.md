# neuro/arcturian_grid/templates/ANCHOR_WISDOM.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 79

---

### File: `neuro/arcturian_grid/templates/ANCHOR_WISDOM.yaml`

#### Purpose
This YAML file defines a template for a function in the Mythos system, specifically for the `ANCHOR_WISDOM` node. It outlines the configuration, processing requirements, and output schema for analyzing conversation exchanges through the lenses of physical reality and deep wisdom.

#### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes and settings for the `ANCHOR_WISDOM` function. It includes sections for function metadata, runtime models, processing instructions, and output schema.

#### Patterns
This file does not directly implement design patterns but serves as a configuration template that can be used by other parts of the system to instantiate and configure the `ANCHOR_WISDOM` function.

#### Dependencies
The file relies on the following runtime models:
- `gemma3:27b`
- `iris-thinking-v2:latest`
- `command-r:35b`

It also depends on the Mythos system's configuration and runtime environment to interpret and use this template.

#### Interfaces
This file exposes the following configuration details to other parts of the system:
- `function_id`, `node`, `node_name`, `node_domain`, `layer`, `layer_name`, `depth`, `model_tier`, `runtime_models`, `processing`, `critical_path`, `generated_at`, `generated_by`, `prompt`, `output_schema`.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the configuration it provides could be used to generate or update records in the Mythos system's database.

#### Configuration
The file does not explicitly reference any external configuration files or environment variables. However, it is likely that the system uses environment variables or configuration files to manage the runtime models and other settings.

#### Key Logic
The key logic is embedded in the `prompt` field, which specifies the instructions for analyzing conversation exchanges:
1. **Node Analysis (ANCHOR)**: Extract physical, structural, or logistical reality from the conversation.
2. **Layer Analysis (WISDOM DEPTH 9)**: Synthesize the elements into the deepest truth, focusing on transcendent and essential synthesis.

The output schema defines the structure of the analysis results, including fields like `summary`, `confidence`, `flags`, `locations`, `times`, `people`, `objects`, `actions`, and `environment`.

#### Integration Points
This template integrates with the Mythos system's processing pipeline, particularly with the runtime models specified (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`). It also connects with the system's configuration and runtime environment to manage and execute the analysis tasks.

### Summary
The `ANCHOR_WISDOM.yaml` file serves as a configuration template for the `ANCHOR_WISDOM` function in the Mythos system. It specifies the function's metadata, runtime models, processing instructions, and output schema, enabling the system to perform deep and structured analysis of conversation exchanges.
