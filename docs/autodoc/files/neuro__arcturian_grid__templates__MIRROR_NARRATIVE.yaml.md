# neuro/arcturian_grid/templates/MIRROR_NARRATIVE.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 65

---

### Purpose
The `MIRROR_NARRATIVE.yaml` file defines a template for a function within the Mythos system, specifically for the `MIRROR` node and `NARRATIVE` layer. This template specifies the configuration and parameters required for processing and analyzing conversation exchanges, focusing on self-referential awareness and narrative context.

### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes and configurations for the `MIRROR_NARRATIVE` function. The file includes metadata, processing details, and output schema specifications.

### Patterns
This file does not directly implement any design patterns but serves as a configuration template that could be used by a factory pattern to instantiate and configure the `MIRROR_NARRATIVE` function.

### Dependencies
The file does not directly import or rely on any external libraries or modules. However, it specifies dependencies on specific AI models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) for runtime processing.

### Interfaces
The file exposes a configuration interface for the `MIRROR_NARRATIVE` function, detailing the expected input and output formats, as well as the processing parameters. This configuration is likely used by the system to instantiate and configure the function.

### Database
The file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with the database to store or retrieve data related to the conversation exchanges and analysis results.

### Configuration
The file itself is a configuration file, detailing the settings for the `MIRROR_NARRATIVE` function. It does not reference any external configuration files or environment variables.

### Key Logic
The key logic of the function is defined in the `prompt` field, which specifies the instructions for the AI models to analyze the conversation exchange. The analysis focuses on self-referential awareness and narrative context, outputting a JSON object with specific keys (`node_insight` and `narrative_placement`).

### Integration Points
The function integrates with the Mythos system's AI processing pipeline, using the specified AI models to process the conversation exchanges. The output schema is designed to be consumed by other components of the system, likely for further analysis or user feedback.

### Detailed Breakdown

1. **Metadata**:
   - `function_id`: `MIRROR_NARRATIVE`
   - `node`: `MIRROR`
   - `node_name`: `Mirror`
   - `node_domain`: `Self-referential awareness`
   - `layer`: `NARRATIVE`
   - `layer_name`: `Narrative`
   - `depth`: `7`
   - `model_tier`: `large`
   - `runtime_models`: List of AI models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`)
   - `processing`: `deep_conscious`
   - `critical_path`: `false`
   - `generated_at`: `2026-03-02T22:21:48.877815`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Prompt**:
   - The prompt instructs the AI models to analyze the conversation exchange using the `Mirror` node and `Narrative` layer. The analysis focuses on self-referential awareness and narrative context, with specific instructions to output a JSON object with `node_insight` and `narrative_placement` keys.

3. **Output Schema**:
   - The output schema is defined as a JSON object with the following properties:
     - `summary`: A 1-2 sentence summary of the analysis.
     - `confidence`: A confidence score between 0 and 1.
     - `flags`: An array of notable findings.
     - `user_reveals`: An array of insights about the user.
     - `iris_notices`: An array of insights about Iris's response tendencies.
     - `blind_spots`: An array of identified blind spots.
     - `projections`: An array of identified projections.

This configuration file is crucial for setting up and running the `MIRROR_NARRATIVE` function within the Mythos system, ensuring that the analysis is performed according to the specified parameters and output format.
