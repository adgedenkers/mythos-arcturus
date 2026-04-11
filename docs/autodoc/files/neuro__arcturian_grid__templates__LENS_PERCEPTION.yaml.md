# neuro/arcturian_grid/templates/LENS_PERCEPTION.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 56

---

### File: `neuro/arcturian_grid/templates/LENS_PERCEPTION.yaml`

#### Purpose
This YAML file defines the configuration for a specific function template within the Mythos system, specifically for the `LENS_PERCEPTION` node. It outlines the parameters, models, and expected output schema for analyzing user messages and assistant responses through various analytical frameworks.

#### Architecture
The file is structured as a YAML document with key-value pairs. It includes metadata about the function, runtime models, processing details, and the expected output schema.

#### Patterns
No specific design patterns are used in this YAML file as it is a configuration file rather than executable code.

#### Dependencies
- **Models**: The file references specific models (`mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`) that are required for processing.
- **Configuration**: It relies on the configuration provided in the YAML file itself.

#### Interfaces
- **Input**: The function expects a `user_message` and `assistant_response` as inputs.
- **Output**: The function outputs a JSON object with a predefined schema, including a summary, confidence score, flags, frameworks applied, interpretations, and a primary framework.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the data processed by this function might be stored or retrieved from the database by other parts of the system.

#### Configuration
The file itself acts as a configuration file, detailing the parameters and expected behavior of the `LENS_PERCEPTION` function.

#### Key Logic
The key logic is embedded in the `prompt` field, which specifies the instructions for the models to analyze the input data through various frameworks (astrology, psychology, systems, spiritual) and extract literal terms. The output is structured as a JSON object with specific fields.

#### Integration Points
- **Models**: The function integrates with the specified models (`mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`).
- **Data Processing**: It integrates with the data processing pipeline to handle the input and output data.
- **Mythos Subsystems**: The function is part of the broader Mythos system and interacts with other subsystems for data retrieval, processing, and storage.

### Detailed Breakdown

1. **Metadata**:
   - `function_id`: `LENS_PERCEPTION`
   - `node`: `LENS`
   - `node_name`: `Lens`
   - `node_domain`: `Analytical and interpretive frameworks`
   - `layer`: `PERCEPTION`
   - `layer_name`: `Perception`
   - `depth`: `1`
   - `model_tier`: `small`
   - `processing`: `unconscious`
   - `critical_path`: `false`
   - `generated_at`: `2026-03-02T21:52:12.840211`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Runtime Models**:
   - `mistral:7b`
   - `qwen2.5:7b`
   - `nous-hermes2:latest`

3. **Prompt**:
   - The prompt instructs the models to analyze the `user_message` and `assistant_response` through the specified frameworks and extract literal terms.
   - The output should be in JSON format with specific keys: `astrological`, `psychological`, `systems`, `spiritual`.

4. **Output Schema**:
   - `summary`: A 1-2 sentence summary of the analysis.
   - `confidence`: A confidence score between 0 and 1.
   - `flags`: An array of notable findings.
   - `frameworks_applied`: An array of frameworks applied.
   - `interpretations`: An array of interpretation objects.
   - `primary_framework`: The primary framework used.

This configuration file is crucial for defining how the `LENS_PERCEPTION` function operates within the Mythos system, ensuring consistent and structured analysis of input data.
