# neuro/arcturian_grid/templates/ANCHOR_INTENTION.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 68

---

### File: `neuro/arcturian_grid/templates/ANCHOR_INTENTION.yaml`

#### Purpose
This YAML file defines a template for a function within the Mythos system, specifically for the `ANCHOR` node at the `INTENTION` layer, which focuses on extracting actionable intentions from user messages and assistant responses related to physical and structural reality.

#### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes of the function template. It includes metadata, runtime configurations, and the expected output schema.

#### Patterns
- **Configuration Pattern**: The file serves as a configuration template, defining the structure and behavior of a function within the system.

#### Dependencies
- **Runtime Models**: The function relies on specific models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) for processing.
- **Prompt**: The function uses a predefined prompt to guide the model's analysis.

#### Interfaces
- **Input**: The function expects `user_message` and `assistant_response` as inputs.
- **Output**: The function outputs a JSON object with a predefined schema, including `summary`, `confidence`, `flags`, `locations`, `times`, `people`, `objects`, `actions`, and `environment`.

#### Database
- **No Direct Database Interaction**: This template does not directly interact with any database tables or Neo4j labels. However, the processed data might be stored or referenced in the system's databases.

#### Configuration
- **Environment Variables**: No explicit environment variables are used in this template.
- **Config Files**: This file itself serves as a configuration file for the function.

#### Key Logic
- **Prompt Analysis**: The function analyzes the `user_message` and `assistant_response` to extract physical/logistical details and derive actionable intentions.
- **Output Schema**: The function ensures that the output adheres to a well-defined JSON schema, providing structured data for further processing.

#### Integration Points
- **Mythos Subsystems**: This function template integrates with the broader Mythos system, particularly with the `Arcturian Grid` and the `Ollama` model runtime. It is designed to be part of a larger workflow where user messages and assistant responses are processed to extract meaningful insights.

### Detailed Breakdown

1. **Metadata**:
   - `function_id`: `ANCHOR_INTENTION`
   - `node`: `ANCHOR`
   - `node_name`: `Anchor`
   - `node_domain`: `Physical and structural reality`
   - `layer`: `INTENTION`
   - `layer_name`: `Intention`
   - `depth`: `6`
   - `model_tier`: `medium`
   - `runtime_models`: `phi4:14b`, `qwen3:14b`, `mistral-small:24b`
   - `processing`: `conscious`
   - `critical_path`: `true`
   - `generated_at`: `2026-03-02T21:50:33.841096`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Prompt**:
   - The prompt guides the model to analyze the input messages and extract physical/logistical details and actionable intentions.

3. **Output Schema**:
   - `summary`: A 1-2 sentence summary of the analysis.
   - `confidence`: A confidence score between 0 and 1.
   - `flags`: An array of notable findings.
   - `locations`: An array of locations.
   - `times`: An array of times.
   - `people`: An array of people.
   - `objects`: An array of objects.
   - `actions`: An array of actions.
   - `environment`: A string describing the environment.

This YAML file serves as a critical configuration template for the Mythos system, ensuring that the function behaves as intended and integrates seamlessly with other components of the system.
