# neuro/arcturian_grid/templates/WEAVE_PERCEPTION.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 58

---

### Documentation for `WEAVE_PERCEPTION.yaml`

#### Purpose
This YAML file defines the configuration and parameters for the `WEAVE_PERCEPTION` function within the Mythos system. It specifies the node, layer, depth, models to be used, and the expected output schema for processing literal connections from user messages and assistant responses.

#### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes and settings for the `WEAVE_PERCEPTION` function. It includes metadata, runtime configurations, and output schema details.

#### Patterns
No specific design patterns are used in this YAML file. It is a simple configuration file that defines the parameters and structure for the function.

#### Dependencies
This YAML file does not directly import or rely on other files or modules. However, it specifies models (`mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`) that the function will use for processing.

#### Interfaces
The file exposes the configuration details for the `WEAVE_PERCEPTION` function, which can be consumed by other parts of the Mythos system to configure and execute the function.

#### Database
This YAML file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with the database to store or retrieve data based on the connections it identifies.

#### Configuration
The file uses environment variables or configuration settings to define the function's behavior, such as the `model_tier`, `runtime_models`, and `prompt`.

#### Key Logic
The key logic described in this YAML file is the extraction of literal connections from user messages and assistant responses. The function is expected to output a JSON object containing various fields like `summary`, `confidence`, `flags`, `connections`, `active_threads`, and `relationship_dynamics`.

#### Integration Points
This YAML file integrates with the Mythos system's function execution framework, which reads and applies these configurations to execute the `WEAVE_PERCEPTION` function. It also integrates with the specified models (`mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`) for processing the input data.

### Detailed Breakdown

1. **Metadata**:
   - `function_id`: `WEAVE_PERCEPTION`
   - `node`: `WEAVE`
   - `node_name`: `Weave`
   - `node_domain`: `Relational and connective tissue`
   - `layer`: `PERCEPTION`
   - `layer_name`: `Perception`
   - `depth`: `1`
   - `model_tier`: `small`
   - `processing`: `unconscious`
   - `critical_path`: `false`
   - `generated_at`: `2026-03-02T22:20:37.716167`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Runtime Models**:
   - `mistral:7b`
   - `qwen2.5:7b`
   - `nous-hermes2:latest`

3. **Prompt**:
   - The prompt instructs the models to extract literal connections from the user message and assistant response, focusing on people relationships, topic links, project references, and social dynamics.

4. **Output Schema**:
   - `summary`: A 1-2 sentence summary of the analysis.
   - `confidence`: A confidence score between 0 and 1.
   - `flags`: An array of notable findings.
   - `connections`: An array of concrete phrases representing connections.
   - `active_threads`: An array of active threads.
   - `relationship_dynamics`: An array of relationship dynamics.

This YAML file serves as a configuration template for the `WEAVE_PERCEPTION` function, defining how it should process input data and what output structure it should produce.
