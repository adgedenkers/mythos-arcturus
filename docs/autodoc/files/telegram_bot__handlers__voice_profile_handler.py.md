# telegram_bot/handlers/voice_profile_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 83

---

### File: `telegram_bot/handlers/voice_profile_handler.py`

#### 1. Purpose
This file handles the `/voice` command for the Telegram bot, allowing users to switch between different voice profiles (e.g., Claude, GPT-4o, Iris) and view the current profile and available options.

#### 2. Architecture
- **Functions**: 
  - `voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`: The main function that processes the `/voice` command.
- **Data Flow**: 
  - The function receives an `Update` object and `ContextTypes` object from the Telegram bot framework.
  - It retrieves the current voice profile and available profiles from the `prompt_assembler` module.
  - It sets a new voice profile based on the user's input and sends a response back to the user.

#### 3. Patterns
- **Singleton**: The `logger` object is a singleton instance of the logging module.
- **Facade**: The `voice_command` function acts as a facade, abstracting the complexity of handling voice profiles and providing a simple interface to the Telegram bot.

#### 4. Dependencies
- **Imports**: 
  - `logging`: For logging errors and information.
  - `telegram`: For handling the `Update` and `ContextTypes` objects.
  - `prompt_assembler`: For getting and setting voice profiles and listing available profiles.
- **Database References**: 
  - `telegram` table in PostgreSQL.
  - `from` table in PostgreSQL.
  - `prompt_assembler` table in PostgreSQL.

#### 5. Interfaces
- **Exposed Functions**: 
  - `voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`: This function is exposed to the Telegram bot framework to handle the `/voice` command.

#### 6. Database
- **Tables/Labels**: 
  - `telegram`: Likely used for storing Telegram-related data.
  - `from`: Likely used for storing data related to the source of the command.
  - `prompt_assembler`: Likely used for storing voice profiles and related data.

#### 7. Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### 8. Key Logic
- **Business Logic**: 
  - **Retrieve Current Profile and List Available Profiles**: If no arguments are provided, the function retrieves the current voice profile and lists all available profiles.
  - **Set New Voice Profile**: If arguments are provided, the function attempts to set the new voice profile based on the user's input. It normalizes common aliases and provides feedback on success or failure.
  - **Logging**: Logs errors if the `prompt_assembler` module cannot be imported.

#### 9. Integration Points
- **Telegram Bot Framework**: Integrates with the Telegram bot framework to handle the `/voice` command.
- **Prompt Assembler Module**: Integrates with the `prompt_assembler` module to get and set voice profiles and list available profiles.

### Summary
The `voice_profile_handler.py` file is responsible for handling the `/voice` command in the Telegram bot. It interacts with the `prompt_assembler` module to manage voice profiles, providing users with the ability to switch between different profiles and view the current and available options. The file is designed to be robust, handling cases where the `prompt_assembler` module is not available and normalizing common aliases for voice profiles.
