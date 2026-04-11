# prompts/voices/claude.yaml

**Language:** yaml
**Stream:** LOG
**Module:** Prompt System
**Lines:** 128

---

### Documentation for `prompts/voices/claude.yaml`

#### Purpose
This YAML file defines the voice profile for Claude, a character in the Mythos system. It specifies the stylistic and linguistic rules that ensure Claude's responses are warm, direct, and prose-first, avoiding typical LLM-speak.

#### Architecture
The file is structured into several sections:
- **General Information**: Contains the name and description of the voice profile.
- **Cadence Rules**: Defines the stylistic rules for response formatting.
- **Formatting Discipline**: Specifies when and how to use bullets, headers, bold text, and code blocks.
- **Anti-Patterns**: Lists common stylistic mistakes to avoid.
- **Positive Patterns**: Lists stylistic elements to encourage.

#### Patterns
- **Configuration Pattern**: The file acts as a configuration file, setting parameters and rules for the Claude voice profile.

#### Dependencies
- **Voice Profile System**: This file is part of the broader voice profile system within Mythos, which likely includes other YAML files for different voices.
- **Text Generation Engine**: The text generation engine (likely integrated with Ollama) uses this configuration to generate responses.

#### Interfaces
- **Voice Profile Interface**: This file is read by the text generation engine to configure the voice profile for Claude. It does not expose any functions or classes but provides data to the engine.

#### Database
- **No Direct Database Interaction**: This file does not interact directly with any database tables or Neo4j labels. It is a configuration file used by the text generation engine.

#### Configuration
- **Environment Variables**: No environment variables are used directly in this file.
- **Configuration Files**: This file itself is a configuration file used by the text generation engine to customize Claude's responses.

#### Key Logic
- **Stylistic Rules Enforcement**: The key logic revolves around enforcing the specified stylistic rules to ensure Claude's responses are consistent with the defined voice profile.
- **Anti-Patterns and Positive Patterns**: The file specifies both anti-patterns to avoid and positive patterns to encourage, ensuring that Claude's responses are warm, direct, and avoid typical LLM-speak.

#### Integration Points
- **Text Generation Engine**: This file integrates with the text generation engine to configure Claude's voice profile. The engine reads this file to understand how to format and style Claude's responses.
- **Voice Profile System**: It is part of a larger system that manages different voice profiles, and this file is one of the profiles used by the system.

### Summary
The `prompts/voices/claude.yaml` file is a configuration file that defines the voice profile for Claude in the Mythos system. It specifies stylistic rules, anti-patterns, and positive patterns to ensure Claude's responses are warm, direct, and avoid typical LLM-speak. The file is read by the text generation engine to configure Claude's responses, ensuring consistency with the defined voice profile.
