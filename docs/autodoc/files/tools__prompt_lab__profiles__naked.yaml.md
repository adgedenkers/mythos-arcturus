# tools/prompt_lab/profiles/naked.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Tools
**Lines:** 14

---

### File: tools/prompt_lab/profiles/naked.yaml

#### Purpose
This YAML file defines a profile named "naked" for the Prompt Lab tool within the Mythos system. The profile specifies that no system prompt or additional layers should be applied, allowing the raw model to operate without any guidance or context.

#### Architecture
The file is structured as a simple YAML document with key-value pairs. It contains metadata about the profile and a list of boolean flags for various layers that can be applied to the model.

#### Patterns
No design patterns are used since this is a configuration file and not executable code.

#### Dependencies
This YAML file does not import or rely on any external dependencies. It is a standalone configuration file.

#### Interfaces
This file does not expose any interfaces. It is used as a configuration input by the Prompt Lab tool to set up the model's behavior.

#### Database
This file does not interact with any database tables or Neo4j labels. It is purely a configuration file.

#### Configuration
The file itself is a configuration file. It does not use any external config files or environment variables. The configuration is static and defined within the file.

#### Key Logic
The key logic here is the definition of the "naked" profile, which disables all layers that might influence the model's behavior. This allows the model to operate in its most raw and unguided state, providing a baseline for comparison against other profiles.

#### Integration Points
This file integrates with the Prompt Lab tool within the Mythos system. The tool reads this configuration to determine how to set up the model for processing prompts. Specifically, the `layers` section is used to disable all layers, ensuring that the model operates without any additional context or guidance.

### Detailed Breakdown

- **name**: `naked` — The name of the profile.
- **description**: `"Raw model, no system prompt. Baseline for comparison."` — A brief description of the profile's purpose.
- **layers**: A dictionary where each key represents a layer that can be applied to the model, and each value is a boolean indicating whether that layer is enabled (`false` in this case). The layers include:
  - `identity`: `false`
  - `personality`: `false`
  - `voice`: `false`
  - `mode`: `false`
  - `user_profile`: `false`
  - `dynamic_context`: `false`
  - `life_context`: `false`
  - `skills`: `false`

This configuration ensures that the model operates without any additional layers or context, providing a pure baseline for comparison with other profiles that might include these layers.
