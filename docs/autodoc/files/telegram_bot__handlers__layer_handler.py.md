# telegram_bot/handlers/layer_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 154

---

### File: `telegram_bot/handlers/layer_handler.py`

#### Purpose
This file handles Telegram bot commands related to managing prompt layers. It provides functionality to show, toggle, and reset layers, and to display detailed information about specific layers.

#### Architecture
The file consists of several asynchronous functions that handle different aspects of layer management:
- `_get_assembler`: Imports the `prompt_assembler` module dynamically to ensure a fresh module is used each time.
- `layer_command`: The main entry point for handling `/layer` commands. It parses the command arguments and delegates to other functions based on the command.
- `_show_layers`: Displays the status of all layers.
- `_toggle`: Toggles a specific layer on or off.
- `_show_info`: Displays detailed information about a specific layer.
- `_reset_all`: Disables all non-locked layers.

#### Patterns
- **Lazy Loading**: The `_get_assembler` function uses lazy loading to import the `prompt_assembler` module only when needed, ensuring that the module is fresh and up-to-date.

#### Dependencies
- `logging`: For logging purposes.
- `sys`: To manipulate the module search path.
- `telegram`: For handling Telegram updates and context.
- `prompt_assembler`: Dynamically imported for layer management functions.

#### Interfaces
- `layer_command`: Exposed to handle `/layer` commands from the Telegram bot.
- `_get_assembler`: Used internally to dynamically import the `prompt_assembler` module.
- `_show_layers`, `_toggle`, `_show_info`, `_reset_all`: Internal functions used by `layer_command` to perform specific tasks.

#### Database
- **PostgreSQL Tables**: The file indirectly references the `telegram`, `from`, and `prompt_assembler` tables in PostgreSQL, though the direct interactions with these tables are handled by the `prompt_assembler` module.

#### Configuration
- **Environment Variables**: No explicit configuration or environment variables are used in this file. The configuration is managed through the `prompt_assembler` module.

#### Key Logic
- **Layer Status Display**: `_show_layers` fetches the status of all layers and formats it for display, including icons and truncation of descriptions.
- **Layer Toggle**: `_toggle` changes the state of a specific layer and provides feedback on the success of the operation.
- **Layer Information**: `_show_info` retrieves and displays detailed information about a specific layer, including its state and notes.
- **Reset Layers**: `_reset_all` disables all non-locked layers and provides feedback on which layers were disabled.

#### Integration Points
- **Telegram Bot**: This file integrates with the Telegram bot framework to handle user commands and provide feedback.
- **Prompt Assembler**: The file interacts with the `prompt_assembler` module to manage layer states, which in turn interacts with the PostgreSQL database to store and retrieve layer configurations.

### Summary
The `layer_handler.py` file is a crucial component of the Mythos system, providing a user-friendly interface for managing prompt layers through a Telegram bot. It leverages lazy loading to ensure dynamic module imports and integrates with the `prompt_assembler` module to manage layer states, which are persisted in a PostgreSQL database.
