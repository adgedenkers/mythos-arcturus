# mx/mx_config.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 35

---

### File: mx/mx_config.yaml

#### Purpose
This YAML configuration file contains settings for the Mythos shell session (`mx`), including configurations for Ollama, session parameters, and lists of dangerous and suppress-heal commands.

#### Architecture
The file is structured into several sections:
- `ollama`: Configuration for Ollama, including host, fallback model, and timeout.
- `session`: Parameters for the session buffer size, healing attempts, countdown, and directories for logs, patterns, and intents.
- `dangerous_commands`: List of commands that require explicit confirmation before execution.
- `suppress_heal`: List of commands where a non-zero exit is expected and should not trigger healing.

#### Patterns
No design patterns are directly applicable to this configuration file, as it is a static data file rather than executable code.

#### Dependencies
This file does not import or rely on any external modules or libraries. It is a configuration file that is read by the Mythos shell session (`mx`) to set up its behavior.

#### Interfaces
The file exposes configuration settings that are read by the `mx` shell session. These settings are used to initialize various parameters and behaviors of the shell session.

#### Database
This file does not directly interact with any database tables or Neo4j labels. However, it may indirectly influence how data is processed or logged within the system.

#### Configuration
The file itself is a configuration file. It is read by the `mx` shell session to configure its behavior. It does not use any external configuration files or environment variables directly, but it may be influenced by environment variables or other configuration files that are used to set up the `mx` session.

#### Key Logic
The key logic of this file is to provide configuration settings that control the behavior of the `mx` shell session, including:
- Ollama connection details and timeout settings.
- Session buffer size and healing parameters.
- Lists of dangerous and suppress-heal commands.

#### Integration Points
This configuration file integrates with the `mx` shell session, which is part of the Mythos system. The `mx` shell session reads this configuration file to set up its environment and behavior. The settings in this file influence how the `mx` session interacts with Ollama, handles session data, and manages dangerous commands and healing logic.

### Detailed Explanation of Sections

1. **Ollama Configuration (`ollama` section)**
   - `host`: Specifies the host and port for the Ollama service.
   - `fallback_model`: Specifies the fallback model to use if no active model is set.
   - `timeout`: Specifies the timeout for Ollama requests.

2. **Session Parameters (`session` section)**
   - `buffer_size`: Number of recent commands to keep in context for Ollama.
   - `max_heal_attempts`: Maximum number of self-heal attempts before giving up.
   - `countdown_seconds`: Countdown before automatically running a fix.
   - `log_dir`: Directory for session logs.
   - `pattern_dir`: Directory for session patterns.
   - `intent_dir`: Directory for session intents.

3. **Dangerous Commands (`dangerous_commands` section)**
   - List of commands that require explicit confirmation before execution to prevent accidental data loss or system shutdown.

4. **Suppress Heal Commands (`suppress_heal` section)**
   - List of commands where a non-zero exit is expected and should not trigger the healing process.

This configuration file is crucial for setting up the behavior of the `mx` shell session, ensuring that it operates safely and efficiently within the Mythos system.
