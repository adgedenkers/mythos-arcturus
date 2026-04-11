# neuro/arcturian_grid/templates/GATEWAY_KNOWLEDGE.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 60

---

### File: `neuro/arcturian_grid/templates/GATEWAY_KNOWLEDGE.yaml`

#### Purpose
This YAML file defines the configuration and specifications for the `GATEWAY_KNOWLEDGE` function within the Mythos system, specifically for the Gateway node operating at the Knowledge layer. It outlines the function's parameters, runtime models, processing requirements, and expected output schema.

#### Architecture
The file is structured as a YAML configuration with key-value pairs defining various attributes of the `GATEWAY_KNOWLEDGE` function. It includes metadata such as the function ID, node details, layer information, runtime models, and the expected output schema.

#### Patterns
No specific design patterns are used in this YAML file as it is a configuration file rather than executable code. However, it follows a standard configuration pattern used in defining function templates.

#### Dependencies
This YAML file does not import or rely on any external dependencies directly. However, it references runtime models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) that are likely defined elsewhere in the system.

#### Interfaces
This file defines the interface for the `GATEWAY_KNOWLEDGE` function, specifying the expected input format (via the `prompt`) and the output schema. The function is expected to process inputs and generate outputs according to the defined schema.

#### Database
This YAML file does not directly interact with any database tables or Neo4j labels. However, the function it configures may interact with databases as part of its runtime processing.

#### Configuration
The file itself is a configuration file and does not use external configuration files or environment variables. However, the runtime models and other parameters can be influenced by the system's configuration.

#### Key Logic
The key logic is embedded in the `prompt` and `output_schema` sections:
- **Prompt**: Defines the instructions for the AI models to analyze the conversation exchange with a focus on spiritual significance, lineage echoes, synchronicities, and other deep insights.
- **Output Schema**: Specifies the exact format of the output, including required fields such as `summary`, `confidence`, `flags`, `spiritual_dimension`, `lineage_echoes`, `synchronicities`, and `transcendent_read`.

#### Integration Points
This function template integrates with the Mythos system's runtime environment, specifically with the AI models (`phi4:14b`, `qwen3:14b`, `mistral-small:24b`) and the overall processing pipeline. It is designed to be part of a larger system where it processes inputs and generates outputs according to the defined schema.

### Detailed Breakdown

- **function_id**: `GATEWAY_KNOWLEDGE`
- **node**: `GATEWAY`
- **node_name**: `Gateway`
- **node_domain**: `Transcendent and liminal`
- **layer**: `KNOWLEDGE`
- **layer_name**: `Knowledge`
- **depth**: `5`
- **model_tier**: `medium`
- **runtime_models**: `phi4:14b`, `qwen3:14b`, `mistral-small:24b`
- **processing**: `conscious`
- **critical_path**: `true`
- **generated_at**: `2026-03-02T22:22:45.047848`
- **generated_by**: `iris-thinking-v2:latest`
- **prompt**: Detailed instructions for the AI models to focus on spiritual significance, lineage echoes, synchronicities, and other deep insights.
- **output_schema**: Defines the JSON output structure with required fields such as `summary`, `confidence`, `flags`, `spiritual_dimension`, `lineage_echoes`, `synchronicities`, and `transcendent_read`.

This configuration ensures that the `GATEWAY_KNOWLEDGE` function is properly set up to process inputs and generate outputs in a structured and meaningful way, aligning with the broader goals of the Mythos system.
