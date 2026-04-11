# prompts/modes/sentry.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Prompt System
**Lines:** 24

---

### Documentation for `prompts/modes/sentry.yaml`

#### Purpose
This YAML file defines the configuration for the "Sentry" mode in the Mythos system, which focuses on financial tracking and life management. It specifies various parameters and instructions for the AI to operate in this mode, including personality traits, features, and specific instructions for handling financial data.

#### Architecture
The file is structured as a YAML configuration file with the following key sections:
- `name`: The name of the mode.
- `emoji`: Emoji representation of the mode.
- `description`: A brief description of the mode's purpose.
- `personality_overrides`: A set of personality traits with specific values.
- `features`: A list of features enabled in this mode.
- `voice_notes`: A list of voice notes providing guidance for the AI's behavior.
- `instructions`: Detailed instructions for the AI's behavior in this mode.
- `include_life_context`: A boolean indicating whether life context data should be included.

#### Patterns
This file does not employ any specific design patterns as it is a configuration file rather than executable code.

#### Dependencies
This file does not import or rely on any external dependencies directly. However, it is used by the Mythos system to configure the behavior of the AI in the "Sentry" mode.

#### Interfaces
This file is not an executable component and does not expose any interfaces directly. Instead, it is consumed by the Mythos system to configure the AI's behavior.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, it influences how the AI interacts with financial and life context data stored in the database.

#### Configuration
This file itself is a configuration file. It does not use any external configuration files or environment variables directly.

#### Key Logic
The key logic defined in this file is the configuration of the AI's behavior in the "Sentry" mode. This includes:
- Setting personality traits to specific values.
- Enabling features such as `perception_logging` and `entity_extraction`.
- Providing detailed instructions on how to handle financial data and life context information.

#### Integration Points
This file integrates with the Mythos system's AI configuration subsystem. The configuration defined here is used to tailor the AI's behavior when it is operating in the "Sentry" mode. Specifically, it influences:
- The AI's personality and verbosity.
- The features that are enabled or disabled.
- The way the AI processes and presents financial data and life context information.

### Summary
The `sentry.yaml` file is a configuration file that defines the behavior of the AI in the "Sentry" mode, focusing on financial tracking and life management. It sets specific personality traits, enables certain features, and provides detailed instructions for handling financial and life context data. This configuration is used by the Mythos system to tailor the AI's behavior in this mode.
