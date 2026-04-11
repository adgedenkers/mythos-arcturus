# skills/REGISTRY.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 157

---

### Documentation for `skills/REGISTRY.yaml`

#### Purpose
The `REGISTRY.yaml` file serves as a centralized registry for all skills within the Mythos system. It defines the available skills, their categories, risk tiers, dependencies, and triggers, allowing the system to dynamically discover and invoke skills based on user input.

#### Architecture
The file is structured as a YAML document with the following sections:
- **Shared Tools**: Defines computation engines that skills can reference.
- **Skills**: Lists individual skills with their metadata, including name, path, category, risk tier, tools, triggers, and summary.

#### Patterns
- **Registry Pattern**: The file acts as a registry, maintaining a list of skills and their properties.
- **Dependency Injection**: Tools are defined separately and can be referenced by multiple skills.

#### Dependencies
- **Tools**: The file references tools defined in the `tools` section.
- **Skills**: The file lists skills that can be invoked based on user triggers.

#### Interfaces
- **Discovery Interface**: The file is read by the system (e.g., Iris) to discover available skills.
- **Invocation Interface**: The file provides metadata necessary for invoking skills based on user input.

#### Database
- **No Direct Database Interaction**: The file itself does not interact with the database directly. However, the skills listed may interact with PostgreSQL, Neo4j, or Redis as part of their execution.

#### Configuration
- **Environment Variables**: The file does not directly use environment variables but relies on the system configuration for paths and runtime environments.
- **Configuration Files**: The file is a configuration file itself, defining the registry of skills.

#### Key Logic
- **Skill Registration**: The file maintains a registry of skills, their categories, and risk tiers.
- **Trigger Matching**: The file defines triggers that can be matched against user input to determine which skill to invoke.

#### Integration Points
- **Skill Invocation**: The file is read by the system (e.g., Iris) to determine which skill to invoke based on user input.
- **Tool Execution**: Skills reference tools defined in the `tools` section, which are executed as part of the skill's logic.
- **Risk Management**: The risk tier of each skill determines the level of autonomy or approval required for execution.

### Detailed Analysis

#### Shared Tools
- **Ephemeris Engine**:
  - **Name**: `ephemeris_engine`
  - **Path**: `analytical/tools/ephemeris.py`
  - **Runtime**: `/opt/mythos/.venv/bin/python3`
  - **Dependencies**: `pyswisseph`
  - **Description**: Swiss Ephemeris computation engine for astrological calculations, used by `soul_stratigraphy` and `western_tropical_natal_chart`.

#### Analytical Skills
- **Soul Stratigraphy**:
  - **Name**: `soul_stratigraphy`
  - **Path**: `analytical/soul_stratigraphy.md`
  - **Version**: `2.0`
  - **Category**: `analytical`
  - **Risk Tier**: `T1-autonomous`
  - **Tools**: `ephemeris_engine`
  - **Triggers**: Various phrases related to astrological analysis.
  - **Summary**: Tri-field astrological analysis with Swiss Ephemeris calculations.

- **Western Tropical Natal Chart**:
  - **Name**: `western_tropical_natal_chart`
  - **Path**: `analytical/western_tropical_natal_chart.md`
  - **Version**: `2.0`
  - **Category**: `analytical`
  - **Risk Tier**: `T1-autonomous`
  - **Tools**: `ephemeris_engine`
  - **Triggers**: Various phrases related to Western Tropical natal charts.
  - **Summary**: Generates or rectifies a Western Tropical natal chart with Swiss Ephemeris calculations.

#### Builder Skills
- **Build Patch**:
  - **Name**: `build_patch`
  - **Path**: `builder/build_patch.md`
  - **Category**: `builder`
  - **Risk Tier**: `T2-patch`
  - **Triggers**: Phrases related to creating and deploying patches.
  - **Summary**: Creates and deploys a numbered Mythos patch.

- **Build Feature API**:
  - **Name**: `build_feature_api`
  - **Path**: `builder/build_feature_api.md`
  - **Category**: `builder`
  - **Risk Tier**: `T2-patch`
  - **Triggers**: Phrases related to creating new API endpoints.
  - **Summary**: Designs and deploys a new FastAPI endpoint/service.

- **Build Feature Telegram Mode**:
  - **Name**: `build_feature_telegram_mode`
  - **Path**: `builder/build_feature_telegram_mode.md`
  - **Category**: `builder`
  - **Risk Tier**: `T2-patch`
  - **Triggers**: Phrases related to creating new Telegram bot modes.
  - **Summary**: Creates a new Telegram bot operating mode.

- **Build Feature Telegram Tool**:
  - **Name**: `build_feature_telegram_tool`
  - **Path**: `builder/build_feature_telegram_tool.md`
  - **Category**: `builder`
  - **Risk Tier**: `T2-patch`
  - **Triggers**: Phrases related to creating new Telegram bot tools.
  - **Summary**: Builds a discrete Telegram bot tool/command.

- **Build Feature Self**:
  - **Name**: `build_feature_self`
  - **Path**: `builder/build_feature_self.md`
  - **Category**: `builder`
  - **Risk Tier**: `T3-propose`
  - **Triggers**: Phrases related to Iris identifying a capability gap.
  - **Summary**: Meta-skill for building infrastructure for Iris, always proposing to Ka'tuar'el first.

#### Meta Skills
- **Humandoc to Skill**:
  - **Name**: `humandoc_to_skill`
  - **Path**: `meta/humandoc_to_skill.md`
  - **Category**: `meta`
  - **Risk Tier**: `T1-autonomous`
  - **Triggers**: Phrases related to converting documents into skills.
  - **Summary**: Transforms human-written documents into properly formatted Mythos skill files.

This registry file is crucial for the Mythos system to dynamically discover and invoke skills based on user input, ensuring that the system can adapt and extend its capabilities as needed.
