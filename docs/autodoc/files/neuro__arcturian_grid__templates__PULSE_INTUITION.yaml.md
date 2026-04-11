# neuro/arcturian_grid/templates/PULSE_INTUITION.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 70

---

### File: `neuro/arcturian_grid/templates/PULSE_INTUITION.yaml`

#### Purpose
This YAML file defines the configuration for the `PULSE_INTUITION` function template within the Mythos system, specifically for the `PULSE` node operating at the `INTUITION` layer. It outlines the parameters, models, processing requirements, and expected output schema for this function.

#### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes of the `PULSE_INTUITION` function. The structure includes metadata, function-specific details, and output schema.

#### Patterns
No design patterns are directly applicable to this YAML file as it is a configuration file rather than executable code.

#### Dependencies
This file does not directly import or rely on other files or modules. However, it references models (`mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`) and a specific function template generator (`iris-thinking-v2:latest`).

#### Interfaces
This file exposes configuration details that are used by the Mythos system to instantiate and configure the `PULSE_INTUITION` function. It does not expose any direct interfaces but serves as a configuration source for the system.

#### Database
This file does not directly interact with any database tables or Neo4j labels. It is a configuration file and does not perform database operations.

#### Configuration
The file itself is a configuration file and does not reference external configuration files or environment variables. It contains all necessary configuration details within its content.

#### Key Logic
The key logic described in this file is the configuration of the `PULSE_INTUITION` function, including the models to be used (`mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`), the processing type (`unconscious`), and the expected output schema. The `prompt` field specifies the instructions for the models to analyze the `user_message` and `assistant_response` focusing on emotional tone, energy level, and other emotional aspects.

#### Integration Points
This file integrates with the Mythos system by providing configuration details for the `PULSE_INTUITION` function. It is used by the system to set up the function with the specified models, processing type, and output schema. The function is part of the `PULSE` node in the `INTUITION` layer, and it is expected to analyze emotional and energetic fields based on the provided `prompt`.

### Summary of Key Fields
- **function_id**: `PULSE_INTUITION`
- **node**: `PULSE`
- **node_domain**: `Emotional and energetic field`
- **layer**: `INTUITION`
- **depth**: `2`
- **model_tier**: `small`
- **runtime_models**: `mistral:7b`, `qwen2.5:7b`, `nous-hermes2:latest`
- **processing**: `unconscious`
- **prompt**: Instructions for analyzing emotional and energetic fields
- **output_schema**: JSON object with keys for summary, confidence, flags, primary emotion, secondary emotions, energy level, energy direction, and tension points

This YAML file serves as a comprehensive configuration template for the `PULSE_INTUITION` function within the Mythos system, ensuring that the function is correctly set up to perform its intended analysis.
