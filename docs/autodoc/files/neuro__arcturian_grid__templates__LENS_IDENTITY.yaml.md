# neuro/arcturian_grid/templates/LENS_IDENTITY.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 57

---

### File: `neuro/arcturian_grid/templates/LENS_IDENTITY.yaml`

#### Purpose
This YAML file defines the configuration and parameters for the `LENS_IDENTITY` function within the Mythos system, specifically for the `LENS` node in the `IDENTITY` layer. It outlines the model configurations, processing details, and expected output schema for analyzing conversation exchanges through an identity lens.

#### Architecture
The file is structured as a YAML configuration file, containing key-value pairs that define various attributes of the `LENS_IDENTITY` function. The structure includes metadata, model configurations, processing details, and output schema.

#### Patterns
No specific design patterns are applied in this YAML configuration file. It is a straightforward configuration file.

#### Dependencies
- **Models**: The function relies on specific models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`) for processing.
- **Runtime Environment**: The configuration specifies the runtime environment and models to be used.

#### Interfaces
This file does not directly expose any interfaces. Instead, it provides configuration details that are used by the Mythos system to set up and run the `LENS_IDENTITY` function.

#### Database
This file does not directly interact with any database tables or Neo4j labels. It is a configuration file used to define the behavior of the `LENS_IDENTITY` function.

#### Configuration
- **Environment Variables**: The file does not explicitly reference any environment variables.
- **Config Files**: This file itself is a configuration file that is likely loaded by the Mythos system to configure the `LENS_IDENTITY` function.

#### Key Logic
The key logic is embedded in the `prompt` field, which defines the instructions for the model to analyze the conversation exchange through the identity layer. The model is expected to identify the activated identity aspect (partner/mirror/builder/witness) and apply various frameworks (astrological, psychological, systems architecture, spiritual) to provide a comprehensive analysis.

#### Integration Points
This file integrates with the Mythos system by providing the necessary configuration for the `LENS_IDENTITY` function. The configuration details are likely used by the system to instantiate and run the function, and the output schema is used to validate the results produced by the function.

### Detailed Breakdown

- **function_id**: `LENS_IDENTITY`
- **node**: `LENS`
- **node_name**: `Lens`
- **node_domain**: `Analytical and interpretive frameworks`
- **layer**: `IDENTITY`
- **layer_name**: `Identity`
- **depth**: `8`
- **model_tier**: `large`
- **runtime_models**: 
  - `gemma3:27b`
  - `iris-thinking-v2:latest`
  - `command-r:35b`
- **processing**: `deep_conscious`
- **critical_path**: `false`
- **generated_at**: `2026-03-02T21:52:45.934145`
- **generated_by**: `iris-thinking-v2:latest`
- **prompt**: Instructions for the model to analyze the conversation exchange through the identity layer, applying various frameworks and outputting a JSON with specific keys.
- **output_schema**: Defines the expected structure of the output, including `summary`, `confidence`, `flags`, `frameworks_applied`, `interpretations`, and `primary_framework`.

This configuration file is crucial for setting up the `LENS_IDENTITY` function within the Mythos system, ensuring that the function operates as intended with the specified models and output schema.
