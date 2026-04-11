# neuro/arcturian_grid/templates/MIRROR_PERCEPTION.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 61

---

### File: `neuro/arcturian_grid/templates/MIRROR_PERCEPTION.yaml`

#### Purpose
This YAML file defines the configuration for the `MIRROR_PERCEPTION` function within the Mythos system, specifically for the `MIRROR` node in the `PERCEPTION` layer. It outlines the parameters, models, and expected output schema for analyzing user messages and assistant responses to extract observable elements related to self-reveals, response tendencies, and partnership dynamics.

#### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes of the `MIRROR_PERCEPTION` function. The structure is hierarchical and includes sections for function metadata, runtime models, processing details, and output schema.

#### Patterns
No specific design patterns are used in this YAML file as it is a configuration file rather than executable code.

#### Dependencies
This file does not directly import or rely on other files. However, it references models (`mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`) that are expected to be available in the system.

#### Interfaces
This configuration file is used by the Mythos system to set up and configure the `MIRROR_PERCEPTION` function. It does not expose any direct interfaces but serves as a configuration source for other parts of the system.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with databases to store or retrieve data as part of its processing.

#### Configuration
The file itself is a configuration file and does not use external config files or environment variables. However, the `generated_by` and `model_tier` fields suggest that certain configurations might be dynamically generated based on the environment or system state.

#### Key Logic
The key logic is embedded in the `prompt` field, which specifies the instructions for the models to analyze user messages and assistant responses. The output schema defines the expected structure of the analysis results, including summary, confidence, flags, user reveals, Iris notices, blind spots, and projections.

#### Integration Points
This configuration file integrates with the Mythos system's function execution framework. It is used to set up the `MIRROR_PERCEPTION` function, which likely interacts with other subsystems such as the model runtime, data storage, and possibly other analysis functions.

### Detailed Breakdown

- **Function Metadata**:
  - `function_id`: `MIRROR_PERCEPTION`
  - `node`: `MIRROR`
  - `node_name`: `Mirror`
  - `node_domain`: `Self-referential awareness`
  - `layer`: `PERCEPTION`
  - `layer_name`: `Perception`
  - `depth`: `1`
  - `model_tier`: `small`
  - `processing`: `unconscious`
  - `critical_path`: `false`
  - `generated_at`: `2026-03-02T22:21:26.405610`
  - `generated_by`: `iris-thinking-v2:latest`

- **Runtime Models**:
  - `mistral:7b`
  - `qwen2.5:7b`
  - `nous-hermes2:latest`

- **Prompt**:
  - The prompt instructs the models to analyze user messages and assistant responses, extracting directly observable elements about user self-reveals, Iris's response tendencies, and the partnership dynamic. The output is expected to be in JSON format with specific keys.

- **Output Schema**:
  - `summary`: A 1-2 sentence summary of the analysis.
  - `confidence`: A confidence score between 0 and 1.
  - `flags`: An array of notable findings.
  - `user_reveals`: An array of user self-reveals.
  - `iris_notices`: An array of Iris's response tendencies.
  - `blind_spots`: An array of blind spots.
  - `projections`: An array of projections.

This configuration file is crucial for setting up the `MIRROR_PERCEPTION` function, ensuring that it operates as intended within the broader Mythos system.
