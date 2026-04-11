# neuro/arcturian_grid/templates/WEAVE_PROCESSING.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 59

---

### Purpose
This YAML file defines the configuration and specifications for the `WEAVE_PROCESSING` function within the Mythos system, specifically for the `WEAVE` node in the `PROCESSING` layer. It outlines the parameters, models, and expected output schema for processing relational and connective tissue data.

### Architecture
The file is structured as a YAML document with key-value pairs. It includes metadata, function-specific details, and the expected output schema. The structure is flat, with no nested classes or functions, as it is a configuration file.

### Patterns
No design patterns are used in this YAML file as it is a configuration file and not executable code.

### Dependencies
This file does not directly import or rely on any external dependencies. However, it references models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) that the system will use for processing.

### Interfaces
This file defines the interface for the `WEAVE_PROCESSING` function, including the expected input prompt format and the output schema. It does not expose any functions or classes directly but serves as a configuration template for the function.

### Database
This file does not directly interact with any database tables or Neo4j labels. However, the processing it describes may involve reading from or writing to such databases, depending on the implementation details of the `WEAVE_PROCESSING` function.

### Configuration
The file itself is a configuration file, defining various parameters for the `WEAVE_PROCESSING` function. It does not reference any external configuration files or environment variables.

### Key Logic
The key logic described in this file is the processing of relational and connective tissue data through the specified models. The prompt instructs the models to focus on specific aspects of the data (relationships, connections, project relations, social dynamics) and to output a structured JSON object.

### Integration Points
This file integrates with the Mythos system's processing layer, specifically the `WEAVE` node. It defines how the `WEAVE_PROCESSING` function should operate, including the models to use and the expected output format. The function is likely invoked by other parts of the system that handle the input data and process it according to the specifications defined here.

### Detailed Breakdown

1. **Metadata**: 
   - `function_id`: `WEAVE_PROCESSING`
   - `node`: `WEAVE`
   - `node_name`: `Weave`
   - `node_domain`: `Relational and connective tissue`
   - `layer`: `PROCESSING`
   - `layer_name`: `Processing`
   - `depth`: `3`
   - `model_tier`: `medium`
   - `runtime_models`: `phi4:14b`, `qwen3:14b`, `mistral-small:24b`
   - `processing`: `conscious`
   - `critical_path`: `false`
   - `generated_at`: `2026-03-02T22:20:43.998182`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Prompt**:
   - The prompt instructs the models to analyze the conversation exchange between a user message and an assistant response, focusing on relationships, connections, project relations, and social dynamics. The output should be a JSON object with specific keys.

3. **Output Schema**:
   - `summary`: A 1-2 sentence summary of the analysis.
   - `confidence`: A confidence score between 0 and 1.
   - `flags`: An array of notable findings.
   - `connections`: An array of objects representing connections.
   - `active_threads`: An array of strings representing active threads.
   - `relationship_dynamics`: An array of strings representing relationship dynamics.

This YAML file serves as a blueprint for the `WEAVE_PROCESSING` function, ensuring that the processing is consistent and adheres to the specified requirements.
