# prompts/modes/oracle.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Prompt System
**Lines:** 40

---

### File: prompts/modes/oracle.yaml

#### Purpose
This YAML file defines the configuration for the "Oracle" mode in the Mythos system, which is focused on research, numerology, astrology, and harmonic analysis.

#### Architecture
The file is structured as a YAML document with several top-level keys:
- `name`: The name of the mode.
- `emoji`: An emoji representing the mode.
- `description`: A brief description of the mode.
- `personality_overrides`: A set of overrides for the AI's personality traits.
- `features`: A list of features enabled or disabled for this mode.
- `sub_modes`: Definitions for sub-modes within the Oracle mode.
- `voice_notes`: General notes for the AI's voice in this mode.
- `instructions`: Detailed instructions for the AI's behavior in this mode.

#### Patterns
No specific design patterns are used since this is a configuration file, not executable code.

#### Dependencies
This file does not import or rely on any external dependencies directly. It is used by the Mythos system to configure the Oracle mode.

#### Interfaces
This file exposes configuration data to the Mythos system, specifically for the Oracle mode. The data is used to customize the behavior and personality of the AI in this mode.

#### Database
This file does not interact directly with any database tables or Neo4j labels. However, the configuration defined here may influence how the AI interacts with data stored in the database.

#### Configuration
This file itself acts as a configuration file. It does not use any external config files or environment variables directly.

#### Key Logic
The key logic in this file is the configuration of the Oracle mode, including:
- Personality traits (`personality_overrides`).
- Enabled features (`features`).
- Sub-modes and their descriptions (`sub_modes`).
- Voice notes and instructions for the AI (`voice_notes`, `instructions`).

#### Integration Points
This file integrates with the Mythos system's AI configuration subsystem. The data from this file is used to customize the AI's behavior and responses in the Oracle mode. It influences how the AI processes and presents information related to numerology, astrology, and harmonic analysis.

### Detailed Breakdown

- **Personality Overrides**: The AI's personality is adjusted with higher values for speculation, mystical, verbosity, and truth. This makes the AI more speculative, mystical, verbose, and truthful in its responses.

- **Features**: The `perception_logging` and `entity_extraction` features are enabled, while `web_search` is disabled (though it can be enabled by a patch).

- **Sub-Modes**:
  - `compare`: Allows comparison of multiple subjects' charts, numbers, and patterns.
  - `resonance`: Focuses on deep harmonic analysis and soul connections.

- **Voice Notes**: These provide guidance on how the AI should present its findings, emphasizing thoroughness and technical accuracy.

- **Instructions**: Detailed guidelines for the AI's behavior, including showing calculation steps, identifying significant numbers, and connecting findings to tarot correspondences.

This configuration ensures that the Oracle mode operates with a specific focus and personality, tailored for research and analysis in numerology, astrology, and harmonic studies.
