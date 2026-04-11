# prompts/users/seraphe.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Prompt System
**Lines:** 28

---

### File: prompts/users/seraphe.yaml

#### Purpose
This YAML file defines the user profile for "Seraphe" in the Mythos system, specifying how the AI, Iris, should adapt its behavior and analytical approach when interacting with this user.

#### Architecture
The file is structured as a YAML document with several key sections:
- `soul_name`: The internal identifier for the user.
- `display_name`: The name to be displayed to the user.
- `telegram_id`: The user's Telegram ID.
- `personality_adjustments`: A set of adjustments to the AI's personality traits when interacting with this user.
- `analytical_lens`: A detailed description of how the AI should interpret and present information to the user.
- `voice_notes`: Additional instructions for the AI's conversational tone and approach.

#### Patterns
No specific design patterns are used in this YAML file, as it is a configuration file rather than executable code.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone configuration file.

#### Interfaces
This file does not expose any interfaces. It is read by the Mythos system to configure the behavior of the AI when interacting with the user "Seraphe".

#### Database
This file does not interact directly with any database tables or Neo4j labels. It is a configuration file used by the system to adjust the AI's behavior.

#### Configuration
This file itself is a configuration file. It does not use any external config files or environment variables.

#### Key Logic
The key logic in this file is the set of instructions and adjustments that guide the AI's behavior:
- **Personality Adjustments**: The AI's personality traits are adjusted to be more warm, mystical, and speculative, while reducing the level of challenge.
- **Analytical Lens**: The AI is instructed to prioritize the user's intuitive knowing over logical analysis, to present information through feeling and resonance, and to connect patterns to cosmology.
- **Voice Notes**: The AI is instructed to be warm, collaborative, and curious, and to get excited about patterns and connections.

#### Integration Points
This file integrates with the Mythos system's user management and AI behavior adjustment subsystems. Specifically, it is likely read by a component responsible for configuring the AI's behavior based on user profiles. This could involve:
- A user management service that loads user profiles.
- An AI behavior adjustment service that applies the specified adjustments to the AI's personality and analytical approach.

### Summary
The `prompts/users/seraphe.yaml` file configures the AI, Iris, to adapt its behavior and analytical approach when interacting with the user "Seraphe". It specifies personality adjustments, detailed instructions on how to interpret and present information, and notes on the conversational tone and approach. This file is read by the Mythos system to ensure that the AI's interactions with this user are tailored to their specific needs and preferences.
