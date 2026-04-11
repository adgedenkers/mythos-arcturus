# prompts/modes/scribe.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Prompt System
**Lines:** 29

---

### File: prompts/modes/scribe.yaml

#### Purpose
This YAML file defines the configuration for the "scribe" mode in the Mythos system, which is tailored for document-oriented work, emphasizing formal structure and long-form output.

#### Architecture
The file is structured as a YAML document with several key sections:
- `name`: The name of the mode.
- `emoji`: An emoji representing the mode.
- `description`: A brief description of the mode.
- `personality_overrides`: Adjustments to the AI's personality traits.
- `features`: Enabled or disabled features specific to this mode.
- `voice_notes`: Additional notes about the AI's voice in this mode.
- `instructions`: Detailed instructions for the AI to follow in this mode.

#### Patterns
This file does not use any design patterns as it is a configuration file rather than executable code.

#### Dependencies
This file does not import or rely on any external dependencies. It is a configuration file that is likely read by the Mythos system to configure the AI behavior in "scribe" mode.

#### Interfaces
This file does not expose any interfaces. It is a configuration file that is consumed by the Mythos system to configure the AI's behavior.

#### Database
This file does not interact with any database tables or Neo4j labels directly. It is a configuration file that is used to set up the AI's behavior in the "scribe" mode.

#### Configuration
This file itself is a configuration file. It does not use any external config files or environment variables but provides configuration for the AI's behavior in "scribe" mode.

#### Key Logic
The key logic in this file is the configuration of the AI's behavior in "scribe" mode:
- **Personality Overrides**: Adjusts the AI's verbosity, formality, humor, and autonomy.
- **Features**: Enables perception logging and disables entity extraction and web search.
- **Voice Notes and Instructions**: Provides guidelines for the AI to maintain a structured and formal writing style while still maintaining Iris's voice.

#### Integration Points
This file integrates with the Mythos system's AI configuration subsystem. The configuration defined here is likely loaded and applied when the AI is set to "scribe" mode, affecting how the AI generates text and structures its output.

### Summary
The `scribe.yaml` file configures the "scribe" mode in the Mythos system, emphasizing formal and structured output. It adjusts the AI's personality traits, enables specific features, and provides detailed instructions to ensure the AI produces well-structured documents while maintaining a formal tone and Iris's voice.
