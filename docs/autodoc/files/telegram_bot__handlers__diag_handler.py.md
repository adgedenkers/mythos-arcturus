# telegram_bot/handlers/diag_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 453

---

### Purpose
The `diag_handler.py` file in the `telegram_bot/handlers` directory provides diagnostic functionality for the Mythos system. It includes various functions to gather system diagnostics such as hardware status, database status, service statuses, and more. These diagnostics can be requested via a Telegram bot command `/diag`.

### Architecture
The file is organized into several top-level functions, each responsible for gathering specific types of diagnostics. The main functions include:
- `_run`: A helper function to execute shell commands.
- `diag_hw`, `diag_services`, `diag_bot`, `diag_db`, `diag_docker`, `diag_ollama`, `diag_redis`, `diag_net`, `diag_patches`, `diag_api`, `diag_workers`: Functions to gather diagnostics for hardware, services, bot, databases, Docker, Ollama, Redis, network, patches, API, and worker services, respectively.
- `run_diagnostics`: Combines the output of the specified diagnostic blocks.
- `get_help_text`: Generates help text for the `/diag` command.
- `handle_diag`: Handles the `/diag` command from the Telegram bot.

### Patterns
No specific design patterns are used in this file. The functions are straightforward and procedural.

### Dependencies
The file imports the following modules:
- `os`: For interacting with the operating system.
- `subprocess`: To run shell commands.
- `tempfile`: For handling temporary files.
- `logging`: For logging purposes.
- `datetime`: For timestamp generation.
- `pathlib`: For path manipulation.
- `telegram`: For handling Telegram bot updates and context.
- `telegram.ext`: For handling context types in the Telegram bot.

### Interfaces
The file exposes the following functions to other parts of the system:
- `handle_diag(update, context)`: Handles the `/diag` command from the Telegram bot.
- `run_diagnostics(blocks)`: Runs specified diagnostic blocks and returns the combined output.
- `get_help_text()`: Returns help text for the `/diag` command.

### Database
The file references the following PostgreSQL tables:
- `datetime`
- `pathlib`
- `telegram`
- `from`
- `pg_stat_user_tables`

### Configuration
The file uses the following environment variables:
- `TELEGRAM_ID_KA`
- `TELEGRAM_ID_SERAPHE`
- `NEO4J_PASSWORD`

### Key Logic
The key logic involves:
- Running shell commands to gather system information.
- Combining the results of different diagnostic blocks into a single output.
- Handling the `/diag` command from the Telegram bot and returning the diagnostics as a text file or inline text.

### Integration Points
The file integrates with the following subsystems:
- **Telegram Bot**: Handles the `/diag` command and sends the diagnostic results back to the user.
- **System Services**: Gathers status information from various system services (e.g., PostgreSQL, Neo4j, Docker, Ollama).
- **Databases**: Queries PostgreSQL and Neo4j for status and usage information.
- **File System**: Reads files and directories for version and patch information.
- **Network**: Checks listening ports and network status.
- **Logging**: Logs diagnostic information for troubleshooting.

### Detailed Function Descriptions

1. **`_run(cmd: str, timeout: int = 20) -> str`**
   - **Purpose**: Executes a shell command and returns the combined stdout and stderr.
   - **Logic**: Uses `subprocess.run` to execute the command and captures the output.

2. **`diag_hw() -> str`**
   - **Purpose**: Collects hardware diagnostics including disk, memory, GPU, uptime, and load.
   - **Logic**: Runs various shell commands to gather information and formats the output.

3. **`diag_services() -> str`**
   - **Purpose**: Collects status information for all Mythos systemd services.
   - **Logic**: Uses `systemctl` to list and gather status information for services.

4. **`diag_bot() -> str`**
   - **Purpose**: Collects status and recent logs for the bot service.
   - **Logic**: Uses `systemctl` and `journalctl` to gather status and log information.

5. **`diag_db() -> str`**
   - **Purpose**: Collects status information for PostgreSQL and Neo4j databases.
   - **Logic**: Uses `systemctl`, `psql`, and `cypher-shell` to gather database status and usage information.

6. **`diag_docker() -> str`**
   - **Purpose**: Collects status information for Docker containers and Iris core.
   - **Logic**: Uses `docker` and `curl` to gather container status and Iris core information.

7. **`diag_ollama() -> str`**
   - **Purpose**: Collects status information for Ollama models and running models.
   - **Logic**: Uses `ollama` and `systemctl` to gather model status and service information.

8. **`diag_redis() -> str`**
   - **Purpose**: Collects status information for Redis including keyspace and memory usage.
   - **Logic**: Uses `redis-cli` to gather Redis status and usage information.

9. **`diag_net() -> str`**
   - **Purpose**: Collects network diagnostics including listening ports and network info.
   - **Logic**: Uses `ss` and `grep` to gather network information.

10. **`diag_patches() -> str`**
    - **Purpose**: Collects version, recent tags, and patch information.
    - **Logic**: Uses `cat`, `git`, and `ls` to gather version and patch information.

11. **`diag_api() -> str`**
    - **Purpose**: Collects status information for the FastAPI gateway.
    - **Logic**: Uses `systemctl` and `curl` to gather service status and health check information.

12. **`diag_workers() -> str`**
    - **Purpose**: Collects status information for all worker services.
    - **Logic**: Uses `systemctl` and `journalctl` to gather worker service status and log information.

13. **`run_diagnostics(blocks: list[str] | None = None) -> str`**
    - **Purpose**: Runs specified diagnostic blocks and returns the combined output.
    - **Logic**: Iterates over the specified blocks and calls the corresponding diagnostic functions.

14. **`get_help_text() -> str`**
    - **Purpose**: Generates help text for the `/diag` command.
    - **Logic**: Constructs a formatted string with available diagnostic blocks and usage instructions.

15. **`handle_diag(update, context) -> None`**
    - **Purpose**: Handles the `/diag` command from the Telegram bot.
    - **Logic**: Parses the command arguments, runs the specified diagnostics, and sends the results back to the user.
