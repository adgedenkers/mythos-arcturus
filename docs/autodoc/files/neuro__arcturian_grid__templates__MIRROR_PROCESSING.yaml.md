# neuro/arcturian_grid/templates/MIRROR_PROCESSING.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 65

---

### Purpose
The `MIRROR_PROCESSING.yaml` file defines the configuration for a specific function within the Arcturian Grid of the Mythos system. This function, identified as `MIRROR_PROCESSING`, is designed to analyze conversation exchanges between a user and the AI Iris, focusing on self-referential awareness and processing at depth 3.

### Architecture
The file is structured as a YAML configuration template. It contains metadata and specific instructions for the function, including details about the node, layer, depth, runtime models, and the expected output schema.

### Patterns
This file does not directly implement any design patterns but serves as a configuration template that is likely used by a factory pattern to instantiate and configure the `MIRROR_PROCESSING` function.

### Dependencies
The file does not directly import or rely on external dependencies but references specific models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) that are expected to be available in the runtime environment.

### Interfaces
The file exposes configuration details and a structured output schema to other parts of the system, particularly to the function instantiation and execution logic.

### Database
This file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with databases to store or retrieve conversation exchanges and analysis results.

### Configuration
The file itself is a configuration file that specifies various parameters for the `MIRROR_PROCESSING` function, such as the node, layer, depth, runtime models, and output schema.

### Key Logic
The key logic is embedded in the `prompt` field, which specifies the analytical task to be performed by the function. The function is expected to analyze the conversation exchange and produce a JSON object with specific insights and observations.

### Integration Points
This file integrates with the Arcturian Grid system, particularly with the function instantiation and execution logic. It also integrates with the runtime models specified (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) and the output schema expected by other parts of the system.

### Detailed Breakdown

1. **Function ID and Node Details**:
   - `function_id: MIRROR_PROCESSING`
   - `node: MIRROR`
   - `node_name: Mirror`
   - `node_domain: Self-referential awareness`
   - `layer: PROCESSING`
   - `layer_name: Processing`
   - `depth: 3`

2. **Runtime Models**:
   - `runtime_models: [phi4:14b, qwen3:14b, mistral-small:24b]`

3. **Prompt**:
   - The prompt specifies the analytical task, focusing on self-referential awareness and processing at depth 3. It instructs the function to analyze the conversation exchange and produce a JSON object with specific insights and observations.

4. **Output Schema**:
   - The output is expected to be a JSON object with the following properties:
     - `summary`: A 1-2 sentence summary of the analysis.
     - `confidence`: A confidence score between 0 and 1.
     - `flags`: An array of notable findings.
     - `user_reveals`: An array of insights about what the user reveals.
     - `iris_notices`: An array of observations about Iris's response tendencies.
     - `blind_spots`: An array of blind spots or unspoken content.
     - `projections`: An array of projections or unspoken content.

This configuration file is crucial for setting up and executing the `MIRROR_PROCESSING` function within the Mythos system, ensuring that the analysis is performed according to the specified parameters and output schema.
