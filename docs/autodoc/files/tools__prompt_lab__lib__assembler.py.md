# tools/prompt_lab/lib/assembler.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 364

---

### File: `tools/prompt_lab/lib/assembler.py`

#### Purpose
This file contains functions to assemble system prompts for the Mythos AI system by loading and processing various configuration files and applying a cascade of overrides to generate a final prompt.

#### Architecture
The file is organized into several top-level functions that handle different aspects of prompt assembly:
- **Loading Functions**: `load_yaml`, `load_text`, `load_profile`, `load_personality_preset`, `load_test_messages`
- **Translation Functions**: `translate_personality`
- **Building Functions**: `build_voice_section`, `build_user_section`
- **Resolution Functions**: `resolve_personality`
- **Main Assembly Function**: `assemble`

Each function is designed to handle a specific part of the prompt assembly process, making the file modular and easy to maintain.

#### Patterns
- **Factory Method Pattern**: The `load_yaml` and `load_text` functions can be seen as factory methods that produce data structures (dict or str) based on file content.
- **Cascade Pattern**: The `resolve_personality` function applies a cascade of overrides to a base set of personality sliders, which is a form of the cascade pattern.

#### Dependencies
- **Standard Libraries**: `os`, `logging`, `yaml`, `sys`, `datetime`, `typing`, `pathlib`
- **Custom Paths**: `PROD_PROMPTS_DIR` and `LAB_DIR` are defined to point to production and lab directories respectively.

#### Interfaces
The file exposes the following functions to other parts of the system:
- `load_yaml`
- `load_text`
- `load_profile`
- `load_personality_preset`
- `load_test_messages`
- `translate_personality`
- `build_voice_section`
- `build_user_section`
- `resolve_personality`
- `assemble`

#### Database
The file does not directly interact with any database tables or Neo4j labels. However, it references several tables in comments, which are likely used in other parts of the system:
- `layer`, `file`, `pathlib`, `datetime`, `typing`, `the`, `personalities`, `messages`, `voice`, `layers`, `life_context`, `skills_context`

#### Configuration
The file uses the following configuration:
- `PROD_PROMPTS_DIR`: Path to the production prompts directory.
- `LAB_DIR`: Path to the lab directory for overrides and testing.

#### Key Logic
1. **Loading Files**: Functions like `load_yaml` and `load_text` handle the loading of YAML and text files, returning default values on failure.
2. **Personality Translation**: `translate_personality` converts numeric sliders into natural language instructions based on predefined ranges.
3. **Voice and User Section Building**: `build_voice_section` and `build_user_section` construct sections of the prompt based on voice configurations and user profiles.
4. **Personality Resolution**: `resolve_personality` applies a cascade of overrides to base personality sliders.
5. **Prompt Assembly**: `assemble` combines all the layers into a final prompt based on a profile configuration.

#### Integration Points
- **Production Prompt Assembler**: The `assemble` function is designed to work similarly to the production prompt assembler but allows toggling individual layers on/off for testing.
- **Profile Configurations**: The `load_profile` function loads layer profiles from a specific directory.
- **Personality Presets**: The `load_personality_preset` function loads personality presets from a specific directory.
- **Dynamic Context**: The `assemble` function includes dynamic context based on the current time and user profile.

### Summary
The `assembler.py` file is a crucial component of the Mythos system, responsible for assembling system prompts by loading and processing various configuration files. It uses a modular approach with well-defined functions for each step of the assembly process, making it easy to test and maintain. The file integrates with other parts of the system by loading configuration files and applying a cascade of overrides to generate the final prompt.
