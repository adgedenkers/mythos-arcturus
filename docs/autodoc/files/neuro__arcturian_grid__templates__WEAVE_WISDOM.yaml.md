# neuro/arcturian_grid/templates/WEAVE_WISDOM.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 59

---

### File: neuro/arcturian_grid/templates/WEAVE_WISDOM.yaml

#### Purpose
This YAML file defines the configuration for a function template named `WEAVE_WISDOM` within the Mythos system. It specifies the parameters, models, processing type, and output schema for the function, which is designed to analyze conversation exchanges through a lens of relational and connective tissue, focusing on wisdom.

#### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes of the function template. The structure includes metadata, runtime models, processing type, and output schema.

#### Patterns
No specific design patterns are used in this YAML file, as it is a configuration file rather than executable code.

#### Dependencies
- **Runtime Models**: The function relies on specific models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) for processing.
- **Prompt Template**: The function uses a predefined prompt template for generating the analysis.

#### Interfaces
- **Input**: The function expects input in the form of a conversation exchange (`{user_message}` and `{assistant_response}`).
- **Output**: The function outputs a JSON object with a specific schema, including fields like `summary`, `confidence`, `flags`, `connections`, `active_threads`, and `relationship_dynamics`.

#### Database
This YAML file does not directly interact with any database tables or Neo4j labels. However, the function it defines may interact with the database through the runtime models and the processing logic.

#### Configuration
- **Environment Variables**: No explicit environment variables are mentioned in the file.
- **Configuration Files**: This file itself serves as a configuration file for the `WEAVE_WISDOM` function template.

#### Key Logic
The key logic is embedded in the prompt template, which instructs the runtime models to analyze the conversation exchange through the lens of relational and connective tissue, focusing on wisdom. The output is expected to be a JSON object with specific fields, including a synthesized statement of the analysis.

#### Integration Points
- **Runtime Models**: The function integrates with the specified runtime models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) for processing the input.
- **Output Schema**: The function integrates with the downstream components that consume the JSON output, ensuring the output adheres to the defined schema.

### Summary
The `WEAVE_WISDOM.yaml` file configures a function template for analyzing conversation exchanges through a lens of relational and connective tissue, focusing on wisdom. It specifies the runtime models, processing type, and output schema, ensuring the function integrates seamlessly with the Mythos system's architecture.
