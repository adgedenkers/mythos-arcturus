# tools/prompt_lab/personalities/default.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Tools
**Lines:** 14

---

### File: tools/prompt_lab/personalities/default.yaml

#### Purpose
This YAML file defines the default personality settings for the Mythos system, which are used as the baseline for comparison in production environments.

#### Architecture
The file is structured as a simple YAML document with key-value pairs. It contains a `name` field, a `description`, and a `sliders` section that holds various personality traits and their corresponding values.

#### Patterns
There are no design patterns used in this YAML file as it is a configuration file, not a code file.

#### Dependencies
This file does not import or rely on any external dependencies directly. However, it is likely read by a configuration parser in the Mythos system.

#### Interfaces
This file exposes configuration settings to the Mythos system, particularly to the personality management subsystem. The settings are used to configure the behavior of AI models.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, the settings defined here might be used to configure or update records in a database related to personality settings.

#### Configuration
The file itself is a configuration file. It does not use any external config files or environment variables directly. However, the values in this file might be overridden by environment-specific configurations or environment variables in the running system.

#### Key Logic
The key logic here is the definition of personality traits and their values. These values are used to modulate the behavior of AI models in the Mythos system. For example, the `verbosity` slider might control how verbose the AI responses are, and the `truth` slider might control how truthful the AI is in its responses.

#### Integration Points
This file integrates with the personality management subsystem of the Mythos system. The settings defined here are likely loaded into memory and used to configure the behavior of AI models at runtime. The subsystem might also allow for dynamic updates or overrides of these settings based on user input or other system configurations.

### Detailed Breakdown of the YAML Content

- **name**: `default`
  - This field identifies the personality configuration as the default one.
  
- **description**: `"Production defaults. Baseline for comparison."`
  - This provides a brief description of the purpose of this configuration.

- **sliders**: 
  - **verbosity**: `75`
    - Controls the verbosity of the AI's responses.
  - **warmth**: `75`
    - Controls the warmth or friendliness of the AI's responses.
  - **humor**: `35`
    - Controls the level of humor in the AI's responses.
  - **truth**: `90`
    - Controls the truthfulness of the AI's responses.
  - **speculation**: `65`
    - Controls the level of speculative responses from the AI.
  - **autonomy**: `50`
    - Controls the level of autonomy in the AI's decision-making.
  - **mystical**: `70`
    - Controls the mystical or supernatural elements in the AI's responses.
  - **formality**: `25`
    - Controls the formality of the AI's language.
  - **challenge**: `55`
    - Controls the level of challenge or difficulty in the AI's responses.

These settings collectively define the default personality of the AI models in the Mythos system, providing a baseline for comparison and customization.
