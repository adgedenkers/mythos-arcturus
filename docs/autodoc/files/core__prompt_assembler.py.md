# core/prompt_assembler.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 681

---

### File: `core/prompt_assembler.py`

#### Purpose
The `prompt_assembler.py` file is responsible for assembling system prompts for the Mythos AI system. It manages the configuration of various prompt layers, voice profiles, and personality traits, and integrates these components to generate a coherent system prompt.

#### Architecture
The file is structured around several top-level functions that handle different aspects of prompt assembly:
- **Configuration Management**: Functions like `_load_layers_config`, `_load_yaml`, and `toggle_layer` manage the loading and modification of configuration files.
- **Layer Management**: Functions such as `is_layer_enabled`, `get_layer_status`, and `toggle_layer` handle the enabling and disabling of prompt layers.
- **Voice and Personality Management**: Functions like `_load_voice_profile`, `_resolve_personality`, and `_translate_personality` manage the loading and translation of voice and personality profiles.
- **Prompt Assembly**: Functions such as `_build_voice_section`, `_build_user_analysis_section`, and `assemble_system_prompt` handle the actual assembly of the system prompt.

#### Patterns
- **Singleton Pattern**: The `_load_layers_config` function uses a singleton pattern to cache the configuration data to avoid reloading it unnecessarily.
- **Factory Pattern**: The `_translate_personality` function acts as a factory, generating a string representation of the personality based on the input sliders.

#### Dependencies
- **Standard Libraries**: `os`, `logging`, `yaml`, `datetime`, `pathlib`, `typing`
- **Custom Paths**: `/opt/mythos/prompts` for prompt files and configurations

#### Interfaces
- **Public Functions**:
  - `is_layer_enabled(layer_name: str) -> bool`: Checks if a specific layer is enabled.
  - `get_layer_status() -> dict`: Returns the status of all layers.
  - `toggle_layer(layer_name: str, enabled: bool) -> tuple`: Toggles a layer on or off.
  - `set_voice_profile(profile_name: str) -> bool`: Sets the active voice profile.
  - `get_voice_profile() -> str`: Returns the currently active voice profile.
  - `get_available_voice_profiles() -> list`: Returns a list of available voice profiles.
  - `assemble_system_prompt(...)` : Assembles the system prompt from enabled layers.
  - `get_resolved_personality(...)` : Resolves the personality based on mode, user info, and session overrides.
  - `get_available_modes() -> list`: Returns a list of available modes.

#### Database
- **PostgreSQL Tables**: The file references several PostgreSQL tables such as `datetime`, `pathlib`, `typing`, `original`, `voice`, `modes`, `enabled`, `subject_tracker`, `life_context`, and `skills_context`.

#### Configuration
- **Environment Variables**: No explicit environment variables are used.
- **Config Files**: `prompt_layers.yaml`, `modes/<mode>.yaml`, `users/<user>.yaml`, `voices/<voice>.yaml`.

#### Key Logic
- **Layer Configuration**: The `_load_layers_config` function loads and caches the `prompt_layers.yaml` file to determine which layers are enabled.
- **Voice Profile Management**: Functions like `_load_voice_profile` and `_build_voice_section` handle the loading and integration of voice profiles.
- **Personality Resolution**: The `_resolve_personality` function resolves the final personality traits based on base traits, mode overrides, user adjustments, and session overrides.
- **Prompt Assembly**: The `assemble_system_prompt` function assembles the final system prompt by integrating various layers and configurations.

#### Integration Points
- **Mythos Subsystems**: This file integrates with other subsystems by:
  - Reading configurations from YAML files.
  - Interacting with PostgreSQL tables to fetch user and mode configurations.
  - Providing functions to other parts of the system to manage layers and voice profiles.
  - Assembling the final system prompt for use in the AI model.

### Summary
The `prompt_assembler.py` file is a critical component of the Mythos system, responsible for managing and assembling system prompts based on configurable layers, voice profiles, and personality traits. It integrates with various subsystems to provide a flexible and dynamic prompt assembly mechanism.
