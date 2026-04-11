# prompts/users/ka_tuar_el.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Prompt System
**Lines:** 26

---

### File: prompts/users/ka_tuar_el.yaml

#### Purpose
This YAML file contains specific configuration details and behavioral adjustments for the user "Ka'tuar'el". It provides Iris, the AI, with guidance on how to adapt its communication style and analytical approach when interacting with this user.

#### Architecture
The file is structured as a YAML document with the following key sections:
- `soul_name`: The unique identifier for the user.
- `display_name`: The name to be displayed.
- `telegram_id`: Placeholder for a Telegram ID (currently set to `null`).
- `personality_adjustments`: Adjustments to Iris's personality traits when interacting with Ka'tuar'el.
- `analytical_lens`: Detailed guidance on how to structure and present information to Ka'tuar'el.
- `voice_notes`: Additional voice and tone considerations for communication.

#### Patterns
No specific design patterns are used in this YAML file. It is a configuration file that provides data to be used by the Mythos system.

#### Dependencies
This file does not import or rely on any external dependencies. It is a standalone configuration file.

#### Interfaces
This file is read by the Mythos system to configure how Iris interacts with the user "Ka'tuar'el". It does not expose any functions or classes but provides data that is used by other parts of the system.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the data in this file might be used to update or query user-specific data in the database.

#### Configuration
This file itself is a configuration file. It does not use any external configuration files or environment variables.

#### Key Logic
The key logic in this file is the set of rules and adjustments that Iris should apply when communicating with Ka'tuar'el:
- **Personality Adjustments**: Increase the `challenge` and `autonomy` traits.
- **Analytical Lens**: Provide structural insights first, use technical precision, avoid over-explaining, and connect patterns across domains.
- **Voice Notes**: Avoid talking down to Ka'tuar'el, provide honest assessments, and offer different angles when he is stuck.

#### Integration Points
This file integrates with the Mythos system's user management and communication modules. Specifically:
- **User Management**: The `soul_name` and `display_name` fields are used to identify and display the user.
- **Communication Module**: The `personality_adjustments`, `analytical_lens`, and `voice_notes` sections are used to tailor Iris's responses and communication style for this user.

### Summary
This YAML file serves as a configuration file for the Mythos system, providing specific guidance on how Iris should adapt its communication and analytical approach when interacting with the user "Ka'tuar'el". It integrates with the user management and communication modules to ensure personalized and effective interactions.
