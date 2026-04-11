# neuro/arcturian_grid/templates/LENS_WISDOM.yaml

**Language:** yaml
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 58

---

### File: `neuro/arcturian_grid/templates/LENS_WISDOM.yaml`

#### Purpose
This YAML file defines the configuration and parameters for the `LENS_WISDOM` function within the Mythos system, specifically for the `LENS` node operating at the `WISDOM` layer. It outlines the function's ID, domain, depth, runtime models, processing type, and output schema.

#### Architecture
The file is structured as a YAML configuration template that specifies various attributes and parameters for the `LENS_WISDOM` function. It includes sections for function ID, node details, layer details, runtime models, processing type, and output schema.

#### Patterns
- **Configuration Pattern**: The file serves as a configuration template, defining the parameters and settings for the function.

#### Dependencies
- **Runtime Models**: The function relies on specific AI models (`gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`).
- **Processing Type**: The function uses `deep_conscious` processing.

#### Interfaces
- **Input**: The function expects a `prompt` that includes placeholders for `user_message` and `assistant_response`.
- **Output**: The function outputs a JSON object with a specific schema defined in the `output_schema` section.

#### Database
- **No Direct Database Interaction**: This file does not directly interact with any database tables or Neo4j labels. However, the function it configures might interact with databases through other components of the system.

#### Configuration
- **Environment Variables**: No explicit environment variables are mentioned, but the configuration could be influenced by environment settings.
- **Config Files**: This file itself is a configuration file that can be used to instantiate the function within the Mythos system.

#### Key Logic
- **Prompt Analysis**: The function is designed to analyze a conversation exchange between a user and an assistant using various analytical frameworks (astrological, psychological, systems architecture, spiritual).
- **Output Synthesis**: The function synthesizes the analysis into a concise JSON object with a summary, confidence level, flags, frameworks applied, interpretations, and primary framework.

#### Integration Points
- **Mythos Subsystems**: This function integrates with other subsystems of the Mythos platform, particularly those responsible for AI model execution and data processing. It is likely called by higher-level orchestration logic that handles the conversation exchange and integrates the analysis into a broader context.

### Detailed Breakdown

#### Function ID and Node Details
- `function_id`: `LENS_WISDOM`
- `node`: `LENS`
- `node_name`: `Lens`
- `node_domain`: `Analytical and interpretive frameworks`
- `layer`: `WISDOM`
- `layer_name`: `Wisdom`
- `depth`: `9`

#### Runtime Models
- `runtime_models`: `gemma3:27b`, `iris-thinking-v2:latest`, `command-r:35b`

#### Processing Type
- `processing`: `deep_conscious`

#### Prompt
- The prompt is a string that includes placeholders for `user_message` and `assistant_response`, and specifies the analytical frameworks to be applied.

#### Output Schema
- **Type**: `object`
- **Properties**:
  - `summary`: `string` (1-2 sentence summary of analysis)
  - `confidence`: `number` (confidence level between 0 and 1)
  - `flags`: `array` of `string` (notable findings)
  - `frameworks_applied`: `array` of `string` (frameworks used in analysis)
  - `interpretations`: `array` of `object` (interpretations)
  - `primary_framework`: `string` (primary framework used)

#### Generated Information
- `generated_at`: `2026-03-02T21:58:28.344859`
- `generated_by`: `iris-thinking-v2:latest`

This YAML file serves as a comprehensive configuration template for the `LENS_WISDOM` function, detailing its operational parameters and expected output schema.
