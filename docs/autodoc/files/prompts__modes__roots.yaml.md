# prompts/modes/roots.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Prompt System
**Lines:** 27

---

### File: prompts/modes/roots.yaml

#### Purpose
This YAML file defines the configuration and behavior of the "Roots" mode in the Mythos system, which is specifically tailored for genealogy and bloodline research.

#### Architecture
The file is structured as a YAML document with the following sections:
- **Metadata**: Contains the mode's name, emoji, and description.
- **Personality Overrides**: Adjusts the AI's personality traits for this mode.
- **Features**: Enables or disables specific features relevant to the mode.
- **Voice Notes**: Provides guidance on the AI's tone and terminology.
- **Instructions**: Detailed guidelines for the AI's behavior in this mode.

#### Patterns
This file does not directly implement any design patterns but serves as a configuration file that influences the behavior of the AI system.

#### Dependencies
This file does not import any external dependencies directly. However, it relies on the Mythos system's configuration and personality management modules to apply these settings.

#### Interfaces
This file exposes configuration settings to the Mythos system, which are used to adjust the AI's behavior and output when operating in the "Roots" mode.

#### Database
The file indirectly references database entities such as `GenPerson` data, which likely refers to genealogical person entities stored in the system's database (PostgreSQL or Neo4j).

#### Configuration
The file itself is a configuration file that can be adjusted to modify the behavior of the AI in the "Roots" mode. It does not directly reference any external configuration files or environment variables but can be influenced by them.

#### Key Logic
The key logic in this file is the configuration of the AI's behavior for genealogy research. This includes:
- Adjusting personality traits to be more speculative, mystical, and verbose.
- Enabling features like `perception_logging` and `entity_extraction`.
- Providing specific instructions and voice notes to guide the AI's output and tone.

#### Integration Points
This file integrates with the following subsystems of the Mythos system:
- **Personality Management**: Adjusts the AI's personality based on the defined overrides.
- **Feature Management**: Enables or disables specific features relevant to genealogy research.
- **Instruction Handling**: Provides detailed instructions for the AI to follow in this mode.
- **Data Handling**: References `GenPerson` data, indicating integration with the genealogical data storage and retrieval subsystems.

### Summary
The `roots.yaml` file is a configuration file that defines the behavior of the Mythos AI system in the "Roots" mode, which is focused on genealogy and bloodline research. It adjusts personality traits, enables specific features, and provides detailed instructions and voice notes to guide the AI's output and behavior in this mode. The file integrates with various subsystems of the Mythos system to ensure the AI operates effectively in the context of genealogical research.
