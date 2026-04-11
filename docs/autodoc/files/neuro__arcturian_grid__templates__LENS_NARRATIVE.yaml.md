# neuro/arcturian_grid/templates/LENS_NARRATIVE.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 60

---

### File: `neuro/arcturian_grid/templates/LENS_NARRATIVE.yaml`

#### Purpose
This YAML file defines the configuration and parameters for the `LENS_NARRATIVE` function within the Mythos system. It specifies the function's role in analyzing conversational exchanges through various analytical frameworks and placing them within a larger narrative context.

#### Architecture
The file is structured as a YAML configuration template. It includes metadata, function parameters, runtime models, and output schema details. The configuration is designed to be easily parsed and used by the Mythos system to instantiate and execute the `LENS_NARRATIVE` function.

#### Patterns
- **Configuration Pattern**: The file serves as a configuration template, defining how the function should be set up and executed.
- **Template Pattern**: The file acts as a template for generating and executing the `LENS_NARRATIVE` function.

#### Dependencies
- **Runtime Models**: The function relies on specific AI models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) for processing.
- **Mythos System**: The file is part of the Mythos system and is used by the system's runtime to configure and execute the function.

#### Interfaces
- **Input**: The function expects a `prompt` with placeholders for `{user_message}` and `{assistant_response}`.
- **Output**: The function outputs a JSON object with a predefined schema, including `summary`, `confidence`, `flags`, `frameworks_applied`, `interpretations`, and `primary_framework`.

#### Database
- **No Direct Database Interaction**: This file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with databases indirectly through the Mythos system.

#### Configuration
- **Environment Variables**: No explicit environment variables are used in this file.
- **Config Files**: This file itself is a configuration file used by the Mythos system to configure the `LENS_NARRATIVE` function.

#### Key Logic
- **Prompt Generation**: The function generates a prompt for the AI models to analyze the conversation exchange through various analytical frameworks and place it within a larger narrative context.
- **Output Schema**: The function ensures that the output adheres to a specific JSON schema, ensuring consistency and structure in the analysis results.

#### Integration Points
- **Mythos System Runtime**: The configuration defined in this file is used by the Mythos system runtime to instantiate and execute the `LENS_NARRATIVE` function.
- **AI Models**: The function integrates with specific AI models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) for processing the conversational exchanges.
- **Data Flow**: The function receives input data (conversation exchanges) and outputs structured analysis results, which can be further processed or stored by the Mythos system.

### Summary
The `LENS_NARRATIVE.yaml` file serves as a configuration template for the `LENS_NARRATIVE` function in the Mythos system. It defines the function's parameters, runtime models, and output schema, enabling the system to analyze conversational exchanges through various analytical frameworks and place them within a larger narrative context. The file is integral to the Mythos system's runtime, ensuring consistent and structured analysis results.
