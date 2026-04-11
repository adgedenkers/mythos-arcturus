# telegram_bot/handlers/spiral_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 133

---

### Documentation for `telegram_bot/handlers/spiral_handler.py`

#### Purpose
This file contains the logic for handling the `/spiral` command and its subcommands in the Telegram bot. It interacts with the Mythos system to provide information about the current spiral position, reset the spiral, show epoch history, and force-generate today's morning brief.

#### Architecture
The file consists of several functions:
- `register`: Registers the `/spiral` command handler with the Telegram application.
- `handle_spiral`: Main handler that processes the `/spiral` command and its subcommands.
- `_handle_status`: Handles the `status` subcommand to show the current spiral position and transit pressure.
- `_handle_reset`: Handles the `reset` subcommand to reset the spiral to today as the new Cycle 1, Day 1.
- `_handle_history`: Handles the `history` subcommand to show the epoch history.
- `_handle_force_brief`: Handles the `brief` subcommand to force-generate today's morning brief.

#### Patterns
- **Command Pattern**: The `handle_spiral` function acts as a dispatcher for different subcommands.
- **Error Handling**: Each subcommand function includes error handling to log and notify the user of any issues.

#### Dependencies
- **Imports**: `logging`, `sys`, `datetime`
- **External Modules**: `telegram.ext` for `CommandHandler`
- **Internal Modules**: `astrology.spiral` for spiral-related functions

#### Interfaces
- **Exposes**: `register` function to register the `/spiral` command handler with the Telegram application.
- **Internal Functions**: `_handle_status`, `_handle_reset`, `_handle_history`, `_handle_force_brief` are called internally by `handle_spiral`.

#### Database
- **PostgreSQL Tables**: `datetime`, `telegram`, `astrology` are referenced for various operations.

#### Configuration
- **Environment Variables**: None explicitly used.
- **System Path**: `/opt/mythos` is added to the system path to import internal modules.

#### Key Logic
- **Status Handling**: Retrieves and displays the current spiral position and transit pressure.
- **Reset Logic**: Resets the spiral to today as the new Cycle 1, Day 1 and logs the reason for the reset.
- **History Handling**: Retrieves and displays the epoch history.
- **Brief Handling**: Forces the generation of today's morning brief, bypassing delivery tracking.

#### Integration Points
- **Telegram Bot**: Integrates with the Telegram bot to handle `/spiral` commands and their subcommands.
- **Astrology Module**: Interacts with the `astrology.spiral` module to get spiral status, reset spiral, get epoch history, and build brief context.

### Detailed Breakdown

#### `register` Function
- **Purpose**: Registers the `/spiral` command handler with the Telegram application.
- **Parameters**: `application` (Telegram application instance).
- **Logic**: Adds a `CommandHandler` for the `/spiral` command, pointing to the `handle_spiral` function.

#### `handle_spiral` Function
- **Purpose**: Dispatches the `/spiral` command to the appropriate subcommand handler.
- **Parameters**: `update` (Telegram update object), `context` (Telegram context object).
- **Logic**: Checks the subcommand from `context.args` and calls the corresponding handler function (`_handle_status`, `_handle_reset`, `_handle_history`, `_handle_force_brief`).

#### `_handle_status` Function
- **Purpose**: Shows the current spiral position and transit pressure.
- **Parameters**: `update` (Telegram update object), `context` (Telegram context object).
- **Logic**: Calls `get_spiral_status` from `astrology.spiral` and sends the result back to the user.

#### `_handle_reset` Function
- **Purpose**: Resets the spiral to today as the new Cycle 1, Day 1.
- **Parameters**: `update` (Telegram update object), `context` (Telegram context object), `extra_args` (additional arguments).
- **Logic**: Calls `reset_spiral` from `astrology.spiral` with a reason and sends the new position back to the user.

#### `_handle_history` Function
- **Purpose**: Shows the epoch history.
- **Parameters**: `update` (Telegram update object), `context` (Telegram context object).
- **Logic**: Calls `get_epoch_history` from `astrology.spiral` and formats the history to send back to the user.

#### `_handle_force_brief` Function
- **Purpose**: Forces the generation of today's morning brief.
- **Parameters**: `update` (Telegram update object), `context` (Telegram context object).
- **Logic**: Calls `build_brief_context` from `astrology.spiral` with `force=True` and sends the brief back to the user.

This file is a critical component of the Mythos system, providing the Telegram bot with the ability to interact with the spiral time tracking and astrology modules.
