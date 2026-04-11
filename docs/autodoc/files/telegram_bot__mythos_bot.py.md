# telegram_bot/mythos_bot.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 1314

---

### Purpose
The `mythos_bot.py` file is the main entry point for the Mythos Telegram bot. It handles various commands and interactions, including session management, command handling, and logging activities. The bot supports multiple modes (chat, sell, db) and integrates with various subsystems for tasks like photo analysis, database queries, and chat context management.

### Architecture
The file consists of several top-level functions and imports numerous modules for handling different commands and functionalities. The architecture is designed around the Telegram bot framework, with each command handler function responsible for a specific action. The session management is handled in-memory, with session data stored in the `SESSIONS` dictionary.

### Patterns
- **Singleton Pattern**: The `SESSIONS` dictionary acts as a singleton to manage user sessions.
- **Command Pattern**: Each command (e.g., `/start`, `/help`, `/status`) is handled by a dedicated function, adhering to the command pattern.
- **Observer Pattern**: The bot observes incoming messages and commands, triggering appropriate handlers.

### Dependencies
- **Imports**: The file imports modules from various parts of the Mythos system, including `requests`, `os`, `asyncio`, `logging`, `uuid`, and `dotenv`.
- **External Modules**: It also imports multiple handlers from different modules, such as `astro_chart_handler`, `chat_mode`, `sell_mode`, `finance_handler`, `voice_handler`, and more.

### Interfaces
- **Command Handlers**: Functions like `start`, `help_command`, `status_command`, `mode_command`, `personality_command`, `clear_command`, `done_command`, `undo_command`, `convo_command`, `endconvo_command`, `model_command`, `photos_command`, `inventory_wrapper`, `export_wrapper`, `handle_photo`, `_process_buffered_message`, `handle_message`, `error_handler`, `quote_cmd`, `grocery_cmd`, `shop_cmd`, `define_cmd`, `define_callback`, `people_cmd`.
- **Session Management**: Functions like `get_or_create_session` and `log_activity` manage session data and activity logging.

### Database
- **PostgreSQL Tables**: The file interacts with several PostgreSQL tables such as `astro_chart_handler`, `telegram_bot`, `core`, `prompt_assembler`, `handlers`, `grocery_skill`, and more.
- **Neo4j Labels**: No direct Neo4j interactions are mentioned in the provided code snippet.

### Configuration
- **Environment Variables**: The bot uses environment variables for configuration, such as `API_KEY_TELEGRAM_BOT` and `TELEGRAM_BOT_TOKEN`.
- **Dotenv**: The `load_dotenv` function is used to load environment variables from a `.env` file.

### Key Logic
- **Session Management**: The `get_or_create_session` function fetches or creates a session for a user, storing session data in the `SESSIONS` dictionary.
- **Activity Logging**: The `log_activity` function logs activities to the session for status reporting.
- **Command Handling**: Each command handler function processes specific commands, such as `/start`, `/help`, `/status`, and more.
- **Message Buffering**: The `handle_message` function buffers multi-chunk messages before processing them.

### Integration Points
- **Handlers**: The bot integrates with various handlers for different functionalities, such as `chat_mode`, `sell_mode`, `finance_handler`, `voice_handler`, `media_handler`, and more.
- **APIs**: The bot interacts with external APIs via `requests` for fetching user data and other operations.
- **Subsystem Integration**: The bot integrates with subsystems like `Ollama`, `Neo4j`, `PostgreSQL`, and `Redis` through various handlers and modules.

### Detailed Analysis of Key Functions

#### `get_or_create_session`
- **Purpose**: Fetches or creates a session for a Telegram user.
- **Logic**: Uses `requests` to fetch user data from an API and stores it in the `SESSIONS` dictionary.
- **Dependencies**: Depends on `requests` and `API_URL`, `API_KEY_TELEGRAM_BOT`.

#### `log_activity`
- **Purpose**: Logs activities to the session for status reporting.
- **Logic**: Appends activity details to the session's activity log.
- **Dependencies**: None.

#### `start`
- **Purpose**: Handles the `/start` command.
- **Logic**: Fetches or creates a session, logs the start activity, and sends a welcome message.
- **Dependencies**: Depends on `get_or_create_session` and `log_activity`.

#### `help_command`
- **Purpose**: Handles the `/help` command.
- **Logic**: Sends a help text message with various commands and their descriptions.
- **Dependencies**: None.

#### `status_command`
- **Purpose**: Handles the `/status` command.
- **Logic**: Fetches the session, checks the current mode, and sends a status message with mode-specific details.
- **Dependencies**: Depends on `get_or_create_session` and `is_sell_mode`.

#### `mode_command`
- **Purpose**: Handles the `/mode` command to switch modes.
- **Logic**: Switches the session's mode and sends a confirmation message.
- **Dependencies**: Depends on `get_or_create_session`.

#### `clear_command`
- **Purpose**: Handles the `/clear` command to reset chat context.
- **Logic**: Clears the chat context in the session.
- **Dependencies**: Depends on `get_or_create_session`.

#### `handle_message`
- **Purpose**: Handles text messages, buffering multi-chunk messages.
- **Logic**: Buffers messages and processes them after a delay.
- **Dependencies**: Depends on `asyncio`.

#### `error_handler`
- **Purpose**: Handles errors.
- **Logic**: Logs errors and sends an error message.
- **Dependencies**: Depends on `logging`.

#### `main`
- **Purpose**: Starts the bot.
- **Logic**: Initializes the bot and starts polling for updates.
- **Dependencies**: Depends on `Application`, `CommandHandler`, `MessageHandler`, `CallbackQueryHandler`, and other handlers.

### Conclusion
The `mythos_bot.py` file is the core of the Mythos Telegram bot, handling user sessions, commands, and interactions with various subsystems. It integrates with multiple modules and external services, providing a comprehensive interface for users to interact with the Mythos system.
