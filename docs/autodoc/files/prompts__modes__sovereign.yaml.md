# prompts/modes/sovereign.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Prompt System
**Lines:** 46

---

### File: prompts/modes/sovereign.yaml

#### Purpose
This YAML file defines the configuration and behavior of the "sovereign" mode for the Mythos system. It specifies personality traits, features, and voice notes that guide the AI's interactions in this mode.

#### Architecture
The file is structured as a YAML document with several key sections:
- `name`: The name of the mode.
- `emoji`: An emoji associated with the mode.
- `description`: A brief description of the mode's purpose.
- `personality_overrides`: A set of key-value pairs that override default personality traits.
- `features`: A set of boolean flags that enable or disable specific features.
- `voice_notes`: A list of guiding notes for the AI's voice and behavior.
- `instructions`: Detailed instructions for the AI's behavior in this mode.
- `include_life_context`: A boolean flag indicating whether life context should be included.

#### Patterns
This file does not directly implement design patterns but serves as a configuration file that influences the behavior of the AI system.

#### Dependencies
This file does not import or rely on other files directly. It is a configuration file that is likely read by a configuration parser within the Mythos system.

#### Interfaces
This file exposes its configuration to the Mythos system, which uses this information to adjust the AI's behavior and responses in the "sovereign" mode.

#### Database
This file does not interact directly with any database tables or Neo4j labels. However, the configuration it provides may influence how the AI interacts with data stored in the database.

#### Configuration
This file itself is a configuration file. It does not use any external config files or environment variables but is likely read by the Mythos system to configure the AI's behavior.

#### Key Logic
The key logic in this file is the configuration of personality traits and behavior guidelines. The AI's responses and behavior in the "sovereign" mode are guided by the values and notes provided here.

#### Integration Points
This file integrates with the Mythos system's AI behavior engine. The configuration defined here is used to customize the AI's responses and behavior when operating in the "sovereign" mode. The AI system likely reads this file to adjust its personality traits, features, and voice notes dynamically.

### Detailed Breakdown

- **Personality Overrides**: The `personality_overrides` section adjusts the AI's personality traits such as `truth`, `challenge`, `warmth`, etc., to fit the sovereign mode. For example, `truth: 95` indicates a high emphasis on truthfulness.

- **Features**: The `features` section enables or disables specific functionalities. For instance, `perception_logging: true` and `entity_extraction: true` enable logging and entity extraction, while `web_search: false` disables web search functionality.

- **Voice Notes**: The `voice_notes` section provides guiding notes for the AI's voice and behavior. These notes instruct the AI on how to respond and interact with the user, emphasizing clarity, precision, and grounded spiritual awareness.

- **Instructions**: The `instructions` section provides detailed guidance on the AI's primary function and behavior in the sovereign mode. It emphasizes the role of the AI as a disciplined mirror, focusing on reflection and accountability rather than external validation.

- **Include Life Context**: The `include_life_context` flag is set to `false`, indicating that life context should not be included in the AI's responses.

This configuration file is crucial for tailoring the AI's behavior to the sovereign mode, ensuring that the interactions are aligned with the principles of sovereignty, accountability, and spiritual practice.
