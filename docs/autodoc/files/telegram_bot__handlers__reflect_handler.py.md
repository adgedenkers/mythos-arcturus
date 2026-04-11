# telegram_bot/handlers/reflect_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 148

---

### Documentation for `telegram_bot/handlers/reflect_handler.py`

#### Purpose
This file contains Telegram command handlers for the Iris self-reflection system. It provides three main functionalities:
1. `/iris_reflect` for a full 9-layer self-reflection.
2. `/iris_status` for a brief status check.
3. `/iris_caps` for listing all capabilities with their health status.

#### Architecture
The file consists of four top-level functions:
1. `_is_authorized(update: Update) -> bool`: Checks if the user is authorized to use the commands.
2. `handle_iris_reflect(update: Update, context: ContextTypes.DEFAULT_TYPE)`: Handles the `/iris_reflect` command.
3. `handle_iris_status(update: Update, context: ContextTypes.DEFAULT_TYPE)`: Handles the `/iris_status` command.
4. `handle_iris_caps(update: Update, context: ContextTypes.DEFAULT_TYPE)`: Handles the `/iris_caps` command.

Each handler function checks if the user is authorized before proceeding with the respective command logic.

#### Patterns
- **Singleton**: The `AUTHORIZED_USERS` list acts as a singleton, storing the authorized user IDs.
- **Facade**: The `_is_authorized` function acts as a facade to encapsulate the authorization logic.

#### Dependencies
- **Standard Libraries**: `sys`, `logging`, `os`, `datetime`
- **External Libraries**: `dotenv` for loading environment variables, `telegram` and `telegram.ext` for handling Telegram updates and context.
- **Internal Modules**: `iris.self_model.introspection` for introspection functionalities.

#### Interfaces
- **Public Functions**: 
  - `_is_authorized(update: Update) -> bool`
  - `handle_iris_reflect(update: Update, context: ContextTypes.DEFAULT_TYPE)`
  - `handle_iris_status(update: Update, context: ContextTypes.DEFAULT_TYPE)`
  - `handle_iris_caps(update: Update, context: ContextTypes.DEFAULT_TYPE)`

#### Database
- **PostgreSQL Tables**: 
  - `datetime`
  - `telegram`
  - `from`
  - `dotenv`
  - `iris` (multiple references)

#### Configuration
- **Environment Variables**: 
  - `TELEGRAM_ADMIN_CHAT_ID`
  - `TELEGRAM_ID_KA`
  - `TELEGRAM_ID_SERAPHE`

#### Key Logic
- **Authorization Check**: Each handler function first checks if the user is authorized using `_is_authorized`.
- **Reflection Generation**: `handle_iris_reflect` uses `generate_reflection` from `iris.self_model.introspection` to generate a full 9-layer self-reflection.
- **Status Check**: `handle_iris_status` uses `generate_brief_status` to generate a brief status check.
- **Capability Health Check**: `handle_iris_caps` uses `get_capability_health` to list all capabilities with their health status.

#### Integration Points
- **Telegram Bot**: The handlers are integrated with the Telegram bot framework, specifically using `Update` and `ContextTypes.DEFAULT_TYPE` to interact with user messages.
- **Iris Self-Model**: The handlers rely on the `iris.self_model.introspection` module for introspection functionalities, which provides the core logic for self-reflection, status checks, and capability health checks.

### Detailed Breakdown

#### `_is_authorized(update: Update) -> bool`
- **Purpose**: Checks if the user sending the command is authorized.
- **Logic**: Compares the user's ID against the `AUTHORIZED_USERS` list. If the list is empty, all users are authorized.

#### `handle_iris_reflect(update: Update, context: ContextTypes.DEFAULT_TYPE)`
- **Purpose**: Handles the `/iris_reflect` command, providing a full 9-layer self-reflection.
- **Logic**: 
  - Checks authorization.
  - Generates a reflection using `generate_reflection`.
  - Splits the reflection into chunks if it exceeds Telegram's 4096 character limit.

#### `handle_iris_status(update: Update, context: ContextTypes.DEFAULT_TYPE)`
- **Purpose**: Handles the `/iris_status` command, providing a brief status check.
- **Logic**: 
  - Checks authorization.
  - Generates a brief status using `generate_brief_status`.

#### `handle_iris_caps(update: Update, context: ContextTypes.DEFAULT_TYPE)`
- **Purpose**: Handles the `/iris_caps` command, listing all capabilities with their health status.
- **Logic**: 
  - Checks authorization.
  - Retrieves capability health using `get_capability_health`.
  - Formats and sends the list of capabilities, handling large outputs by truncating if necessary.

This file is a critical component of the Mythos system, enabling the Iris self-model to provide self-awareness and status information through the Telegram interface.
