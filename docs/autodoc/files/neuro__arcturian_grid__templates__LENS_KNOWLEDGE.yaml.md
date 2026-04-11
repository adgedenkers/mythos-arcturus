# neuro/arcturian_grid/templates/LENS_KNOWLEDGE.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 57

---

### File: `neuro/arcturian_grid/templates/LENS_KNOWLEDGE.yaml`

#### Purpose
This YAML file defines a template for a function within the Mythos system, specifically for the `LENS_KNOWLEDGE` node. It outlines the configuration, runtime models, processing requirements, and expected output schema for this function.

#### Architecture
The file is structured as a YAML document with key-value pairs and nested structures. It includes metadata about the function, runtime configurations, and the expected output schema.

#### Patterns
No specific design patterns are used in this YAML file, as it is a configuration file rather than executable code.

#### Dependencies
This file does not directly import or rely on other files. However, it references runtime models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) and a model tier (`medium`), which are likely defined elsewhere in the system.

#### Interfaces
The file exposes the configuration details for the `LENS_KNOWLEDGE` function, including the prompt and output schema, which are used by other parts of the Mythos system to interact with this function.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the function it configures may interact with databases to retrieve or store data as part of its processing.

#### Configuration
The file uses environment-specific details such as the `generated_at` and `generated_by` fields, which are likely set during the generation process. It also specifies the `model_tier` and `runtime_models`, which are used to configure the function's execution environment.

#### Key Logic
The key logic is encapsulated in the `prompt` field, which defines the analytical and interpretive task to be performed. The function is expected to analyze a conversation exchange through various frameworks (astrological, psychological, systems architecture, spiritual) and produce a structured JSON output.

#### Integration Points
This file integrates with other parts of the Mythos system, particularly the runtime environment that executes the function and the components that handle the input and output data. The `prompt` and `output_schema` fields are critical for integrating this function with the broader Mythos architecture.

### Detailed Breakdown

1. **Metadata and Configuration**
   - `function_id`: `LENS_KNOWLEDGE`
   - `node`: `LENS`
   - `node_name`: `Lens`
   - `node_domain`: `Analytical and interpretive frameworks`
   - `layer`: `KNOWLEDGE`
   - `layer_name`: `Knowledge`
   - `depth`: `5`
   - `model_tier`: `medium`
   - `runtime_models`: `phi4:14b`, `qwen3:14b`, `mistral-small:24b`
   - `processing`: `conscious`
   - `critical_path`: `true`
   - `generated_at`: `2026-03-02T21:52:28.372287`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Prompt**
   - The prompt instructs the function to analyze a conversation exchange using various frameworks and return a structured JSON object.

3. **Output Schema**
   - `type`: `object`
   - `properties`:
     - `summary`: `string` (1-2 sentence summary of analysis)
     - `confidence`: `number` (between 0 and 1)
     - `flags`: `array` of `string` (notable findings)
     - `frameworks_applied`: `array` of `string`
     - `interpretations`: `array` of `object`
     - `primary_framework`: `string`
   - `required`: `summary`, `confidence`, `flags`

This YAML file serves as a comprehensive configuration template for the `LENS_KNOWLEDGE` function, detailing its purpose, runtime environment, and expected output format.
