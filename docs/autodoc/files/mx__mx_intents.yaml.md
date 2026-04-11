# mx/mx_intents.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 161

---

### Documentation for `mx/mx_intents.yaml`

#### Purpose
This YAML file serves as a registry for custom intents in the Mythos system, mapping user phrases to specific shell commands. It acts as a configuration file for the Ollama component, enabling users to interact with the system through natural language commands.

#### Architecture
The file is structured as a dictionary where each key is a user phrase and the value is another dictionary containing the `command` to be executed and optional `flags` for additional command-line arguments.

#### Patterns
- **Configuration Pattern**: The file is a configuration file that stores a set of key-value pairs, where each key is a user phrase and the value is the corresponding shell command.
- **Command Pattern**: Each entry maps a phrase to a specific shell command, which can be executed directly.

#### Dependencies
- **Ollama**: The Ollama component of the Mythos system uses this file to map user inputs to shell commands.
- **System Services**: The file relies on various system services and utilities like `systemctl`, `journalctl`, `psql`, `cypher-shell`, `redis-cli`, and custom scripts.

#### Interfaces
- **Input**: User phrases (e.g., "api restart", "db tables").
- **Output**: Shell commands that are executed by the system.

#### Database
- **PostgreSQL**: Commands related to database tables and data retrieval (e.g., "db tables", "db count").
- **Neo4j**: Commands to query Neo4j database (e.g., "neo4j").
- **Redis**: Commands to interact with Redis (e.g., "redis", "redis queues").

#### Configuration
- **Environment Variables**: Uses `$NEO4J_PASSWORD` for Neo4j commands.
- **File Paths**: References specific file paths for custom scripts and data files (e.g., `/opt/mythos/bin/lunar-report`, `/opt/mythos/docs/TODO.md`).

#### Key Logic
- **Mapping Phrases to Commands**: The primary logic is to map user phrases to shell commands. The longest matching phrase is used.
- **Handling Flags**: For commands with flags, the YAML file specifies how to map short-form flags to long-form flags.

#### Integration Points
- **Ollama**: The Ollama component reads this file to understand the mapping between user phrases and shell commands.
- **System Services**: The commands in the file interact with various system services and utilities, such as `systemctl` for managing services, `journalctl` for logs, and custom scripts for specific functionalities.

### Detailed Breakdown

#### Services Section
- **"api restart"**: Restarts the Mythos API service using `systemctl`.
- **"bot status"**: Checks the status of the Mythos bot service.
- **"services"**: Lists all Mythos-related services using `systemctl`.

#### Patch System Section
- **"streams"**: Displays information about streams using a Python script.
- **"patch status"**: Checks the patch status using a custom script.
- **"pi {patch}"**: Installs a patch with optional flags.

#### Database Section
- **"db tables"**: Lists PostgreSQL tables.
- **"db count"**: Counts rows in the `transactions` table.
- **"db balances"**: Retrieves account balances from PostgreSQL.
- **"db bills"**: Lists active recurring bills from PostgreSQL.
- **"neo4j"**: Queries Neo4j to get label counts.
- **"redis"**: Checks the length of a Redis stream.
- **"redis queues"**: Lists Redis keys matching a pattern.

#### Astrology Section
- **"seraphe lunar"**: Generates a lunar report for the subject "seraphe".
- **"adge transits"**: Generates transits for the subject "adge".
- **"sky"**: Generates a sky report.

#### IRIS / PROMPT Section
- **"prompt test"**: Runs a test script for IRIS prompts.
- **"prompt debug"**: Runs a debug script for IRIS prompts.

#### Logs Section
- **"logs api"**: Displays logs for the Mythos API service.
- **"logs all"**: Displays logs for multiple services.

#### Quick Nav Section
- **"todo"**: Displays the TODO list.
- **"arch"**: Displays the architecture document.
- **"docs"**: Lists all documents in the `/opt/mythos/docs/` directory.

This YAML file is central to the Mythos system's command interface, providing a flexible and extensible way to interact with various system components through natural language commands.
