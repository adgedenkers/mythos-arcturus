# prompts/voices/gpt4o.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Prompt System
**Lines:** 89

---

### File: prompts/voices/gpt4o.yaml

#### Purpose
This YAML file defines the voice profile for the GPT-4o model within the Mythos system. It specifies the formatting, cadence rules, and stylistic guidelines to ensure the model's responses are structured, confident, and editorially polished.

#### Architecture
The file is organized into several sections:
- **General Information**: Contains the name and description of the voice profile.
- **Cadence Rules**: Defines the default format, use of punctuation, and stylistic preferences.
- **Formatting Discipline**: Specifies when and how to use formatting elements like bullets, headers, bold text, and code blocks.
- **Anti-Patterns**: Lists common stylistic issues to avoid and suggests better alternatives.
- **Positive Patterns**: Provides examples of good stylistic practices to follow.

#### Patterns
This file does not directly implement design patterns but serves as a configuration file that guides the implementation of the GPT-4o model's voice in the Mythos system.

#### Dependencies
This YAML file does not import or rely on any external dependencies. It is a configuration file that is likely read by a Python script or another component of the Mythos system.

#### Interfaces
This file is not an executable script but a configuration file. It is read by other parts of the Mythos system, particularly the components responsible for generating and formatting text responses from the GPT-4o model.

#### Database
This file does not interact with any database tables or Neo4j labels directly. It is a configuration file that influences the text generation process.

#### Configuration
This file itself is a configuration file. It does not use any external config files or environment variables but is likely referenced by other parts of the system.

#### Key Logic
The key logic in this file is the definition of the voice profile for GPT-4o. It specifies:
- **Cadence Rules**: How the model should structure its responses, including the use of punctuation and sentence structure.
- **Formatting Discipline**: When and how to use formatting elements like bullets, headers, bold text, and code blocks.
- **Anti-Patterns**: Common stylistic issues to avoid and suggestions for better alternatives.
- **Positive Patterns**: Good stylistic practices to follow.

#### Integration Points
This file integrates with the text generation and formatting components of the Mythos system. Specifically, it is likely used by:
- **Text Generation Engine**: To ensure that the generated text adheres to the specified voice profile.
- **Formatting Engine**: To apply the specified formatting rules to the generated text.

### Summary
The `gpt4o.yaml` file is a configuration file that defines the voice profile for the GPT-4o model in the Mythos system. It specifies the formatting, cadence rules, and stylistic guidelines to ensure that the model's responses are structured, confident, and editorially polished. This file is read by other components of the Mythos system to guide the text generation and formatting processes.
