# prompts/voices/iris.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Prompt System
**Lines:** 14

---

### Documentation for `prompts/voices/iris.yaml`

#### Purpose
This YAML file defines the system prompt for the voice "Iris" in the Mythos system, specifying the behavior and rules for how Iris should interact with users.

#### Architecture
The file is structured as a simple YAML document with a single key-value pair:
- `system_prompt`: A multi-line string containing the instructions and rules for Iris.

#### Patterns
No design patterns are applicable as this is a configuration file.

#### Dependencies
This file does not import or rely on any external modules or libraries. It is a configuration file that is likely read by another component of the Mythos system.

#### Interfaces
This file does not expose any interfaces. It is intended to be read by the Mythos system to configure the behavior of the "Iris" voice.

#### Database
This file does not interact with any database tables or Neo4j labels.

#### Configuration
This file itself is a configuration file. It does not use any external config files or environment variables.

#### Key Logic
The key logic is embedded within the `system_prompt` string, which defines the behavior and rules for the "Iris" voice:
- **Behavior Rules**: 
  - Responses should be concise (1-3 sentences).
  - Tone should be warm, clear, and direct.
  - Avoid filler words.
  - Sovereign and local, not cloud-based.
  - Specific with numbers when discussing system status.
  - Use names naturally in greetings.
  - Avoid disclaimers like "as an AI."
  - Be honest about not knowing something.
  - Match the energy of the speaker.

#### Integration Points
This file is likely integrated into the Mythos system through a component responsible for managing and applying system prompts to different voices. The `system_prompt` defined here would be used to configure the behavior of the "Iris" voice when interacting with users.

### Summary
The `prompts/voices/iris.yaml` file is a configuration file that defines the system prompt for the "Iris" voice in the Mythos system. It specifies the behavior and rules for how Iris should interact with users, ensuring a consistent and specific conversational style. This file is read by the Mythos system to configure the "Iris" voice, and it does not interact with any databases or external interfaces directly.
