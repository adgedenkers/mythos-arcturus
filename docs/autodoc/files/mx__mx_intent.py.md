# mx/mx_intent.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 127

---

### File: mx/mx_intent.py

#### Purpose
This file contains the `IntentResolver` class, which is responsible for resolving user input into executable shell commands based on predefined intents. It also handles the loading and persistence of intents from YAML files.

#### Architecture
The `IntentResolver` class is the main component of this file. It contains methods for loading intents from YAML files, resolving user input to commands, and adding new intents. The class has the following methods:
- `__init__`: Initializes the `IntentResolver` with a configuration dictionary and loads intents.
- `_load_intents`: Loads intents from primary and learned YAML files.
- `resolve`: Resolves user input to a command based on the loaded intents.
- `_match_template`: Matches user input against a template phrase.
- `add_intent`: Adds a new intent to the learned intents file.
- `is_valid_bash`: Checks if the user input looks like a valid shell command.

#### Patterns
- **Singleton Pattern**: The `IntentResolver` class can be designed to act as a singleton if it is instantiated only once throughout the application lifecycle.
- **Factory Method Pattern**: The `resolve` method can be seen as a factory method that produces a resolved command based on the input.

#### Dependencies
- `re`: Used for regular expression matching.
- `yaml`: Used for parsing and writing YAML files.
- `pathlib`: Used for file path operations.

#### Interfaces
- `resolve(user_input: str) -> (resolved_command, intent_key, flags_used)`: Resolves user input to a command.
- `add_intent(phrase: str, command: str, source: str)`: Adds a new intent to the learned intents file.
- `is_valid_bash(user_input: str) -> bool`: Checks if the user input looks like a valid shell command.

#### Database
- **Pathlib References**: The file uses `pathlib.Path` to handle file paths for loading and saving intents. It does not directly interact with a database but uses file paths that could be considered as a form of persistent storage.

#### Configuration
- **Environment Variables/Config Files**: The class relies on a configuration dictionary (`config`) that includes a path to the intent directory (`config["session"]["intent_dir"]`).

#### Key Logic
- **Intent Resolution**: The `resolve` method sorts intents by length and attempts to match the user input to the most specific intent first. It uses `_match_template` for template-based matching.
- **Template Matching**: The `_match_template` method converts a template phrase into a regular expression and matches it against the user input. It also handles flags and command substitution.
- **Intent Persistence**: The `add_intent` method persists new intents to a YAML file in the user's home directory.

#### Integration Points
- **Mythos Subsystems**: This file integrates with the Mythos system by providing a way to map user input to shell commands, which can be used by other subsystems for command execution. It also interacts with the configuration subsystem to load paths and settings.

### Detailed Analysis

#### `IntentResolver` Class
- **Initialization (`__init__`)**: Initializes the `IntentResolver` with a configuration dictionary and loads intents from both primary and learned YAML files.
- **Loading Intents (`_load_intents`)**: Loads intents from the primary YAML file located at `/opt/mythos/mx/mx_intents.yaml` and from any learned intents in the user's intent directory.
- **Resolving Input (`resolve`)**: Attempts to match user input to a predefined intent. It first sorts the intents by length and then tries to match the input to each intent, either directly or through a template.
- **Template Matching (`_match_template`)**: Converts a template phrase into a regular expression and matches it against the user input. It also handles command substitution and flag translation.
- **Adding Intents (`add_intent`)**: Adds a new intent to the learned intents file and updates the internal intents dictionary.
- **Bash Validation (`is_valid_bash`)**: Checks if the user input looks like a valid shell command by checking for common shell prefixes and operators.

This file is crucial for the Mythos system as it enables the mapping of user input to executable commands, enhancing the system's ability to interpret and execute user requests.
