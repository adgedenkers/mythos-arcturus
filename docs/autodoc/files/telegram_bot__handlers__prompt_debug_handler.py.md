# telegram_bot/handlers/prompt_debug_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 94

---

### Purpose
The `prompt_debug_handler.py` file handles the `/prompt_debug` command in the Telegram bot, providing different views of the last assembled system prompt, including a summary, full text, and feature flag states.

### Architecture
- **Functions**: The file contains one primary function, `prompt_debug_command`, which processes the `/prompt_debug` command.
- **Data Flow**: The function fetches prompt data from an API, processes it based on the command arguments, and sends the appropriate response back to the user via the Telegram bot.

### Patterns
- **None**: This file does not use any specific design patterns like factory, singleton, or observer. It is a straightforward function handling a specific command.

### Dependencies
- **Imports**: The file imports `logging`, `requests`, and `os` for logging, making HTTP requests, and accessing environment variables, respectively.
- **Telegram Libraries**: It also imports `Update` and `ContextTypes` from the `telegram` and `telegram.ext` modules to interact with the Telegram bot framework.

### Interfaces
- **Exposes**: The `prompt_debug_command` function is exposed to handle the `/prompt_debug` command. It takes `update` and `context` as parameters, which are standard in the Telegram bot framework.

### Database
- **References**: The file references the `telegram`, `from`, and `API` tables in PostgreSQL, though it does not directly interact with them. Instead, it fetches data from an API endpoint, which likely interacts with these tables.

### Configuration
- **Environment Variables**: The file uses `API_KEY_TELEGRAM_BOT` from the environment to authenticate API requests.

### Key Logic
- **API Request**: The function makes a GET request to the API endpoint `https://mythos-api.denkers.co/debug/last_prompt` to fetch the last assembled system prompt.
- **Response Handling**: Depending on the command arguments (`full` or `flags`), it processes and formats the response data to send back to the user.
- **Error Handling**: It includes basic error handling to catch and report any exceptions that occur during the API request or response processing.

### Integration Points
- **Telegram Bot Framework**: The function integrates with the Telegram bot framework by using `Update` and `ContextTypes` to handle incoming commands and send responses.
- **Mythos API**: The function integrates with the Mythos API to fetch the last assembled system prompt, which is crucial for debugging and tuning the prompt layers.

### Detailed Breakdown
1. **API Request**: The function constructs an API request to fetch the last assembled prompt, including token count and feature flags.
2. **Command Handling**: Based on the command arguments, it decides whether to show the full prompt, just the flags, or a summary.
3. **Response Formatting**: It formats the response text appropriately, using Markdown for formatting and handling large text chunks by breaking them into smaller messages.
4. **Error Reporting**: It catches and reports any errors that occur during the API request or response processing, ensuring the bot provides feedback to the user in case of issues.

This file is a critical component of the Mythos system, enabling users to inspect and debug the system prompt, which is essential for tuning and maintaining the system's performance and functionality.
