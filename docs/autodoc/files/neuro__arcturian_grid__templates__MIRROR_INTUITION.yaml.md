# neuro/arcturian_grid/templates/MIRROR_INTUITION.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 62

---

### File: `neuro/arcturian_grid/templates/MIRROR_INTUITION.yaml`

#### Purpose
This YAML file defines the configuration for a specific function template within the Mythos system, specifically for the `MIRROR` node at the `INTUITION` layer, which is designed to process self-referential awareness at a depth of 2.

#### Architecture
The file is structured as a YAML configuration file with key-value pairs, defining various attributes and parameters for the function template. It includes metadata, processing details, runtime models, and output schema.

#### Patterns
No specific design patterns are used in this configuration file as it is purely declarative and does not contain any executable code or logic.

#### Dependencies
This file does not directly import or rely on any other files or modules. However, it references runtime models (`mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`) and a model tier (`small`), which are likely defined elsewhere in the system.

#### Interfaces
This file exposes configuration details that are used by other parts of the Mythos system to instantiate and configure the function template. Specifically, it provides the function ID, node details, layer details, and output schema.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the configuration details it provides are likely used by the system to manage and store function execution data in the underlying databases.

#### Configuration
The file uses environment-specific details such as the `model_tier` and `runtime_models`, which are likely configured based on the system's current setup and requirements.

#### Key Logic
The key logic is embedded in the `prompt` field, which defines the instructions for the AI models to process the user message and assistant response, focusing on self-referential awareness and subtle shifts in the relationship. The output is expected to be in JSON format with specific keys (`felt_sense`, `unspoken_revelation`, `relationship_undertone`).

#### Integration Points
This file integrates with other subsystems of the Mythos system, particularly the runtime environment that executes the AI models and processes the user messages. The configuration details defined here are used to set up and configure these runtime environments.

### Detailed Breakdown

- **function_id**: `MIRROR_INTUITION` — Unique identifier for the function template.
- **node**: `MIRROR` — The node in the system where this function is applied.
- **node_name**: `Mirror` — Human-readable name for the node.
- **node_domain**: `Self-referential awareness` — Domain of the node.
- **layer**: `INTUITION` — Layer in the system where this function operates.
- **layer_name**: `Intuition` — Human-readable name for the layer.
- **depth**: `2` — Depth level within the layer.
- **model_tier**: `small` — Tier of the model to be used.
- **runtime_models**: List of models (`mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`) that can be used for processing.
- **processing**: `unconscious` — Type of processing.
- **critical_path**: `false` — Indicates whether this function is on the critical path.
- **generated_at**: `2026-03-02T22:21:28.707615` — Timestamp when the template was generated.
- **generated_by**: `iris-thinking-v2:latest` — Model used to generate the template.
- **prompt**: Instructions for the AI models to process the user message and assistant response.
- **output_schema**: JSON schema defining the expected output format with keys like `summary`, `confidence`, `flags`, `user_reveals`, `iris_notices`, `blind_spots`, and `projections`.

This configuration file is crucial for setting up and managing the specific function template within the Mythos system, ensuring that the AI models process the data according to the defined parameters and output schema.
