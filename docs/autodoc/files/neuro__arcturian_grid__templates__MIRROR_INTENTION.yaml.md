# neuro/arcturian_grid/templates/MIRROR_INTENTION.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 63

---

### File: `neuro/arcturian_grid/templates/MIRROR_INTENTION.yaml`

#### Purpose
This YAML file defines the configuration and specifications for the `MIRROR_INTENTION` function template within the Mythos system, specifically for the `Mirror` node in the `Intention` layer, which focuses on self-referential awareness.

#### Architecture
The file is structured as a YAML configuration file that specifies various parameters and configurations for the `MIRROR_INTENTION` function. It includes metadata, runtime models, processing details, and output schema.

#### Patterns
No specific design patterns are used in this YAML file as it is a configuration file.

#### Dependencies
This file does not directly import or rely on other files. However, it references runtime models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) that are likely defined elsewhere in the system.

#### Interfaces
This file exposes a configuration interface for the `MIRROR_INTENTION` function, which can be consumed by other parts of the Mythos system to set up and run the function.

#### Database
This file does not directly interact with any database tables or Neo4j labels.

#### Configuration
The file itself acts as a configuration file. It does not reference any external config files or environment variables but can be influenced by them indirectly through the runtime models and processing details.

#### Key Logic
The key logic is embedded in the `prompt` field, which specifies the task to be performed by the function. The function is expected to analyze user messages and assistant responses to identify user's self-revelations, response patterns, partnership dynamics, and blind spots. The output is expected to be in JSON format with specific keys (`insight` and `action`).

#### Integration Points
This file integrates with the Mythos system's runtime environment, specifically the `Mirror` node in the `Intention` layer. The configuration defined here is used to set up and run the function, and the output schema ensures consistent data handling across the system.

### Detailed Breakdown

1. **Metadata**:
   - `function_id`: `MIRROR_INTENTION`
   - `node`: `MIRROR`
   - `node_name`: `Mirror`
   - `node_domain`: `Self-referential awareness`
   - `layer`: `INTENTION`
   - `layer_name`: `Intention`
   - `depth`: `6`
   - `model_tier`: `medium`
   - `runtime_models`: `phi4:14b`, `qwen3:14b`, `mistral-small:24b`
   - `processing`: `conscious`
   - `critical_path`: `true`
   - `generated_at`: `2026-03-02T22:21:45.793923`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Prompt**:
   - The prompt specifies the task for the function, which involves analyzing user messages and assistant responses to identify various insights and actions.

3. **Output Schema**:
   - The output is expected to be a JSON object with specific properties:
     - `summary`: A 1-2 sentence summary of the analysis.
     - `confidence`: A confidence score between 0 and 1.
     - `flags`: An array of notable findings.
     - `user_reveals`: An array of user's self-revelations.
     - `iris_notices`: An array of Iris's response patterns.
     - `blind_spots`: An array of blind spots.
     - `projections`: An array of projections.

This YAML file serves as a comprehensive configuration template for the `MIRROR_INTENTION` function, ensuring that the function is set up correctly and produces consistent and structured output.
