# mx/mx_session.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 461

---

### Documentation for `mx/mx_session.py`

#### Purpose
This file manages the Mythos shell session, providing self-healing capabilities, intent resolution, and interaction with the Ollama model for command execution and error handling.

#### Architecture
The file is organized into several sections:
1. **Configuration Loading**: Functions to load and manage configuration settings.
2. **Ollama Interaction**: Functions to interact with the Ollama model for command resolution and healing.
3. **Execution and Safety Checks**: Functions to execute commands, check for dangerous commands, and handle countdowns.
4. **Self-healing Logic**: Functions to attempt to fix failed commands.
5. **Intent Resolution**: Functions to translate natural language into shell commands.
6. **Main Loop**: The primary entry point and loop for the session.

#### Patterns
- **Singleton**: The `load_config` function ensures a single configuration dictionary is loaded and reused.
- **Factory**: The `call_ollama` function acts as a factory for generating responses from the Ollama model.

#### Dependencies
- **Standard Libraries**: `json`, `os`, `re`, `readline`, `subprocess`, `sys`, `time`, `requests`, `yaml`
- **Custom Modules**: `mx_intent`, `mx_logger`, `mx_journal`, `mx_hooks`

#### Interfaces
- **Public Functions**: `load_config`, `get_active_model`, `call_ollama`, `parse_json_response`, `run_command`, `is_dangerous`, `should_suppress`, `countdown_run`, `heal`, `resolve_via_ollama`, `main`
- **Classes**: `IntentResolver`, `MxLogger`, `MxJournal`, `mx_hooks`

#### Database
- **PostgreSQL Tables**: `collections`, `datetime`, `pathlib`, `user`, `buffer`, `mx_intent`, `mx_logger`, `mx_journal`, `mx_hooks`

#### Configuration
- **Configuration File**: `mx_config.yaml` located at `/opt/mythos/mx/mx_config.yaml`
- **Environment Variables**: None explicitly used, but paths and configurations are managed through the `load_config` function.

#### Key Logic
- **Configuration Loading**: `load_config` reads and parses the configuration file.
- **Model Selection**: `get_active_model` selects the active Ollama model based on configuration and overrides.
- **Ollama Interaction**: `call_ollama` sends requests to the Ollama model and parses the JSON response.
- **Command Execution**: `run_command` executes shell commands and captures their output.
- **Self-healing**: `heal` attempts to fix failed commands using Ollama and known patterns.
- **Intent Resolution**: `resolve_via_ollama` translates natural language into shell commands using Ollama.

#### Integration Points
- **Intent Resolver**: `mx_intent.IntentResolver` for managing and resolving intents.
- **Logger**: `mx_logger.MxLogger` for logging session events and results.
- **Journal**: `mx_journal.MxJournal` for session journaling.
- **Hooks**: `mx_hooks` for pre- and post-flight hooks to manage significant events.

### Detailed Analysis of Functions

1. **`load_config`**
   - **Purpose**: Loads the configuration from `mx_config.yaml`.
   - **Logic**: Reads the YAML file and returns the configuration as a dictionary.

2. **`get_active_model`**
   - **Purpose**: Determines the active Ollama model based on configuration and overrides.
   - **Logic**: Checks for an override file and uses it if present, otherwise falls back to the configuration.

3. **`call_ollama`**
   - **Purpose**: Sends a request to the Ollama model and returns the response.
   - **Logic**: Uses the `requests` library to send a POST request to the Ollama API and parses the JSON response.

4. **`parse_json_response`**
   - **Purpose**: Parses the JSON response from Ollama.
   - **Logic**: Cleans up the response text and parses it into a dictionary.

5. **`run_command`**
   - **Purpose**: Executes a shell command and captures its output.
   - **Logic**: Uses `subprocess.run` to execute the command and returns the exit code, stdout, and stderr.

6. **`is_dangerous`**
   - **Purpose**: Checks if a command is dangerous based on a list of dangerous commands.
   - **Logic**: Compares the command against a list of dangerous commands.

7. **`should_suppress`**
   - **Purpose**: Determines if a command should be suppressed based on a list of suppress commands.
   - **Logic**: Checks if the first word of the command is in the suppress list.

8. **`countdown_run`**
   - **Purpose**: Executes a command after a countdown, with an option to confirm dangerous commands.
   - **Logic**: Displays a countdown and prompts for confirmation if the command is dangerous.

9. **`heal`**
   - **Purpose**: Attempts to fix a failed command using known patterns and Ollama.
   - **Logic**: Uses known patterns and consults Ollama to generate and execute fix commands.

10. **`resolve_via_ollama`**
    - **Purpose**: Translates a natural language phrase into a shell command using Ollama.
    - **Logic**: Sends a request to Ollama to translate the phrase and parses the response.

11. **`main`**
    - **Purpose**: The main entry point for the session, handling command-line arguments and running the session loop.
    - **Logic**: Parses command-line arguments, loads configuration, and runs the session loop with self-healing and intent resolution.

This file is a critical component of the Mythos system, providing the core functionality for interactive shell sessions with advanced self-healing and intent resolution capabilities.
