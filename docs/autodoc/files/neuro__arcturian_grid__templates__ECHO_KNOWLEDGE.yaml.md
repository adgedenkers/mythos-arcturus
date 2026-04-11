# neuro/arcturian_grid/templates/ECHO_KNOWLEDGE.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 63

---

### File: `neuro/arcturian_grid/templates/ECHO_KNOWLEDGE.yaml`

#### Purpose
This YAML file defines the configuration and parameters for the `ECHO_KNOWLEDGE` function template within the Mythos system. It specifies details about the node, layer, models, processing requirements, and expected output schema for pattern recognition and memory analysis.

#### Architecture
The file is structured as a YAML document with key-value pairs. It includes metadata, function-specific details, runtime models, processing requirements, and output schema definitions.

#### Patterns
No specific design patterns are used in this YAML file, as it is a configuration file rather than executable code.

#### Dependencies
This file does not directly import or rely on any external dependencies. However, it references runtime models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) that are expected to be available in the system.

#### Interfaces
This file exposes configuration details for the `ECHO_KNOWLEDGE` function, which can be consumed by other parts of the Mythos system to instantiate and configure the function.

#### Database
The file does not directly reference any database tables or Neo4j labels. However, the function it configures is expected to interact with the database to retrieve past interaction references for pattern matching.

#### Configuration
The file itself is a configuration file. It does not use external config files or environment variables but can be influenced by them when instantiated in the system.

#### Key Logic
The key logic described in the file is the configuration for a function that analyzes conversation exchanges for pattern recognition and memory analysis. The function is expected to output a JSON object with specific fields (`summary`, `confidence`, `flags`, `matched_patterns`, `recurring_themes`, `cycle_indicators`, `echo_strength`).

#### Integration Points
This file integrates with the Mythos system's function instantiation and execution mechanisms. It is likely used by a function manager or orchestrator to configure and run the `ECHO_KNOWLEDGE` function, which in turn interacts with the database and runtime models to perform its analysis.

### Detailed Breakdown

1. **Metadata**:
   - `function_id`: `ECHO_KNOWLEDGE`
   - `node`: `ECHO`
   - `node_name`: `Echo`
   - `node_domain`: `Memory and pattern recognition`
   - `layer`: `KNOWLEDGE`
   - `layer_name`: `Knowledge`
   - `depth`: `5`
   - `model_tier`: `medium`
   - `runtime_models`: `phi4:14b`, `qwen3:14b`, `mistral-small:24b`
   - `processing`: `conscious`
   - `critical_path`: `true`
   - `generated_at`: `2026-03-02T21:51:00.778424`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Prompt**:
   - The prompt specifies the task for the function: to analyze conversation exchanges for pattern recognition and memory analysis, outputting a JSON object with specific fields.

3. **Output Schema**:
   - The output schema defines the structure of the JSON object that the function should return, including fields like `summary`, `confidence`, `flags`, `matched_patterns`, `recurring_themes`, `cycle_indicators`, and `echo_strength`.

This YAML file serves as a blueprint for the `ECHO_KNOWLEDGE` function, providing all necessary configuration details to ensure it operates as intended within the Mythos system.
