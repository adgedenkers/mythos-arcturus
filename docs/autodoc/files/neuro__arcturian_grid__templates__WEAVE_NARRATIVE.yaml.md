# neuro/arcturian_grid/templates/WEAVE_NARRATIVE.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 61

---

### Purpose
The `WEAVE_NARRATIVE.yaml` file defines the configuration and specifications for the `WEAVE_NARRATIVE` function within the Mythos system. This function is designed to analyze conversation exchanges to extract relational and connective tissue information, focusing on relationships, active threads/projects, and social dynamics.

### Architecture
The file is structured as a YAML configuration file, containing metadata and configuration details for the `WEAVE_NARRATIVE` function. It includes fields such as `function_id`, `node`, `node_name`, `node_domain`, `layer`, `layer_name`, `depth`, `model_tier`, `runtime_models`, `processing`, `critical_path`, `generated_at`, `generated_by`, `prompt`, and `output_schema`.

### Patterns
No specific design patterns are used in this configuration file. It is a straightforward YAML configuration file.

### Dependencies
This file does not directly import or rely on any external dependencies. However, it references runtime models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) that need to be available in the system.

### Interfaces
This file defines the interface for the `WEAVE_NARRATIVE` function, specifying the expected input prompt and the output schema. The output schema is defined as a JSON object with specific properties and required fields.

### Database
This file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with the database to retrieve or store information related to active threads, relationships, and social dynamics.

### Configuration
The file itself is a configuration file. It does not use any external configuration files or environment variables. The configuration is embedded within the YAML file itself.

### Key Logic
The key logic is embedded in the `prompt` field, which specifies the instructions for the runtime models to analyze the conversation exchanges. The analysis focuses on relationships, active threads, and social dynamics, and the output is expected to be in a specific JSON format.

### Integration Points
This function integrates with other subsystems of the Mythos system, particularly the runtime models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`). It also integrates with the data retrieval and storage mechanisms to access and store information related to active threads, relationships, and social dynamics.

### Detailed Breakdown

1. **Metadata and Configuration**:
   - `function_id`: `WEAVE_NARRATIVE`
   - `node`: `WEAVE`
   - `node_name`: `Weave`
   - `node_domain`: `Relational and connective tissue`
   - `layer`: `NARRATIVE`
   - `layer_name`: `Narrative`
   - `depth`: `7`
   - `model_tier`: `large`
   - `runtime_models`: `gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`
   - `processing`: `deep_conscious`
   - `critical_path`: `false`
   - `generated_at`: `2026-03-02T22:21:00.838627`
   - `generated_by`: `iris-thinking-v2:latest`

2. **Prompt**:
   - The prompt specifies the instructions for the runtime models to analyze the conversation exchanges, focusing on relationships, active threads, and social dynamics. The output is expected to be in a specific JSON format.

3. **Output Schema**:
   - The output schema is defined as a JSON object with the following properties:
     - `summary`: A 1-2 sentence summary of the analysis.
     - `confidence`: A confidence score between 0 and 1.
     - `flags`: An array of notable findings.
     - `connections`: An array of objects representing connections.
     - `active_threads`: An array of strings representing active threads.
     - `relationship_dynamics`: An array of strings representing relationship dynamics.

This configuration file is crucial for defining the behavior and expected output of the `WEAVE_NARRATIVE` function within the Mythos system.
