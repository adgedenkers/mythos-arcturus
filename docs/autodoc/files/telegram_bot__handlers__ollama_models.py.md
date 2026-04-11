# telegram_bot/handlers/ollama_models.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 480

---

### File: `telegram_bot/handlers/ollama_models.py`

#### Purpose
This file contains functions and command handlers for managing Ollama models via a Telegram bot. It handles operations such as listing models, pulling new models, setting active models, and showing the status of pull operations.

#### Architecture
The file is organized into several sections:
1. **Global State**: Manages global variables like `ACTIVE_PULLS` and `USER_MODEL_OVERRIDE` for tracking pull operations and user-specific model overrides.
2. **Ollama API Helpers**: Functions to interact with the Ollama API for listing models and checking if a model exists.
3. **Background Pull Task**: Asynchronous function to handle model pulling in the background.
4. **Command Handlers**: Functions to handle specific Telegram commands like `/models`, `/pull`, `/pulling`, `/setmodel`, and `/removemodel`.

#### Patterns
- **Singleton Pattern**: The global state (`ACTIVE_PULLS` and `USER_MODEL_OVERRIDE`) is managed as singletons to ensure consistency across the application.
- **Observer Pattern**: The `_pull_model_background` function updates the `ACTIVE_PULLS` dictionary to reflect the progress of pull operations, which can be observed by other parts of the system.

#### Dependencies
- **Standard Libraries**: `os`, `asyncio`, `logging`, `time`, `datetime`, `typing`
- **External Libraries**: `httpx`, `json`

#### Interfaces
- **Command Handlers**: Exposes several command handlers (`models_command`, `pull_command`, `pulling_command`, `setmodel_command`, `removemodel_command`) to handle Telegram commands.
- **Helper Functions**: Exposes helper functions (`ollama_list_models`, `ollama_model_exists`, `format_size`, `_pull_model_background`, `_save_overrides`, `_load_overrides`, `get_active_model`) for internal use and potential reuse in other parts of the system.

#### Database
- **PostgreSQL Tables**: References to `datetime`, `typing`, `file`, `Ollama`, `handlers`, `core` tables, though the specific operations are not detailed in the provided code.

#### Configuration
- **Environment Variables**: Uses `OLLAMA_HOST` and `OLLAMA_MODEL` environment variables to configure the Ollama host and default model.

#### Key Logic
- **Model Management**: Functions to list, check existence, and pull models from the Ollama API.
- **Background Task Management**: `_pull_model_background` manages the background task for pulling models, updating progress, and notifying users via Telegram.
- **Override Handling**: `_save_overrides` and `_load_overrides` manage user-specific model overrides, persisting them to a file for cross-process access.

#### Integration Points
- **Telegram Bot**: Integrates with the Telegram bot framework to handle commands and send notifications.
- **Ollama API**: Interacts with the Ollama API to list and pull models.
- **File System**: Persists model overrides to a file for cross-process consistency.

### Detailed Analysis of Functions

1. **_save_overrides**
   - **Purpose**: Persist model overrides to a file for cross-process access.
   - **Logic**: Converts `USER_MODEL_OVERRIDE` dictionary keys to strings for JSON serialization and writes to `OVERRIDE_FILE`.

2. **_load_overrides**
   - **Purpose**: Load model overrides from a file.
   - **Logic**: Reads `OVERRIDE_FILE` and updates `USER_MODEL_OVERRIDE` dictionary.

3. **ollama_list_models**
   - **Purpose**: Fetch all pulled models from the Ollama API.
   - **Logic**: Uses `httpx` to make an asynchronous GET request to the Ollama API and returns the list of models.

4. **ollama_model_exists**
   - **Purpose**: Check if a model is already pulled.
   - **Logic**: Calls `ollama_list_models` and checks if the model name exists in the list.

5. **format_size**
   - **Purpose**: Format a byte count to a human-readable string.
   - **Logic**: Converts bytes to KB, MB, or GB based on the size.

6. **_pull_model_background**
   - **Purpose**: Pull a model in the background and update progress.
   - **Logic**: Uses `httpx` to stream the pull operation, updates `ACTIVE_PULLS` with progress, and sends Telegram notifications.

7. **models_command**
   - **Purpose**: List all pulled Ollama models with details.
   - **Logic**: Fetches models from Ollama API, formats details, and sends a message to the user.

8. **pull_command**
   - **Purpose**: Pull a new model in the background.
   - **Logic**: Checks if the model is already pulled or being pulled, starts a background pull task, and sends a notification.

9. **pulling_command**
   - **Purpose**: Show the status of active/recent pull operations.
   - **Logic**: Formats and sends the status of `ACTIVE_PULLS` to the user.

10. **setmodel_command**
    - **Purpose**: Set the active model for Iris chat.
    - **Logic**: Updates `USER_MODEL_OVERRIDE` and persists changes.

11. **removemodel_command**
    - **Purpose**: Remove a pulled model from Ollama.
    - **Logic**: Not fully implemented in the provided code.

12. **get_active_model**
    - **Purpose**: Get the active model for a user.
    - **Logic**: Loads overrides from file and returns the active model for the given user.

This file serves as a critical component of the Mythos system, enabling seamless interaction with the Ollama model registry through a Telegram bot interface.
