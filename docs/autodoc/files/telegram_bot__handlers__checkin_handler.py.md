# telegram_bot/handlers/checkin_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 301

---

### File: `telegram_bot/handlers/checkin_handler.py`

#### Purpose
This file contains asynchronous functions that handle various Telegram bot commands related to routines and daily check-ins. These functions interact with the database to retrieve and update routine information and send responses back to the user.

#### Architecture
The file is structured around several top-level asynchronous functions, each handling a specific command:
- `handle_checkin`: Handles the `/checkin` command to generate and send a daily briefing.
- `handle_routines`: Handles the `/routines` command to show today's routines with completion status.
- `handle_rdone`: Handles the `/rdone` command to mark a routine as complete.
- `handle_rskip`: Handles the `/rskip` command to skip a routine for today.
- `handle_routine_add`: Handles the `/routine_add` command to add a new routine.

Each function processes the `update` and `context` parameters from the Telegram bot framework and interacts with the database or other modules to perform the required operations.

#### Patterns
- **None**: No specific design patterns are used in this file. The functions are straightforward and do not exhibit patterns like factory, singleton, or observer.

#### Dependencies
- **Imports**: 
  - `logging`: For logging errors and information.
  - `sys`: For modifying the Python path.
  - `telegram`: For interacting with the Telegram bot framework.
  - `telegram.ext`: For handling context and updates.
- **External Modules**: 
  - `routines_engine`: Contains functions for generating briefings, completing routines, skipping routines, and adding routines.

#### Interfaces
- **Exposed Functions**:
  - `handle_checkin(update, context)`: Handles the `/checkin` command.
  - `handle_routines(update, context)`: Handles the `/routines` command.
  - `handle_rdone(update, context)`: Handles the `/rdone` command.
  - `handle_rskip(update, context)`: Handles the `/rskip` command.
  - `handle_routine_add(update, context)`: Handles the `/routine_add` command.

#### Database
- **PostgreSQL Tables**:
  - `today`: Used for fetching today's routines.
  - `telegram`: Used for storing Telegram-related data.
  - `from`: Used for fetching routine origins.
  - `routines_engine`: Used for various routine operations.
  - `pending`: Used for storing pending routines.
  - `routines`: Used for storing routine definitions.

#### Configuration
- **Environment Variables**: None explicitly used in this file.
- **Config Files**: None explicitly used in this file.

#### Key Logic
- **handle_checkin**:
  - Generates a daily briefing using `generate_daily_briefing` from `routines_engine`.
  - Formats the briefing for Telegram and sends it to the user.
  - Stores routine IDs and titles in the context for future use with `/rdone` and `/rskip`.

- **handle_routines**:
  - Fetches today's routines from the database.
  - Formats the routines with completion status and sends them to the user.
  - Stores pending routine IDs and titles in the context for future use.

- **handle_rdone**:
  - Marks a routine as complete using `complete_routine` from `routines_engine`.
  - Updates the pending list in the context and informs the user.

- **handle_rskip**:
  - Skips a routine for today using `skip_routine` from `routines_engine`.
  - Updates the pending list in the context and informs the user.

- **handle_routine_add**:
  - Parses command arguments to extract routine details.
  - Inserts a new routine into the `routines` table.
  - Informs the user of the successful addition.

#### Integration Points
- **Routines Engine**: 
  - `routines_engine` is heavily integrated for generating briefings, completing routines, skipping routines, and adding routines.
- **Telegram Bot Framework**:
  - Uses `telegram` and `telegram.ext` to handle updates and send responses.
- **Database**: 
  - Interacts with PostgreSQL tables to fetch and update routine information.
- **Context**: 
  - Uses `context.user_data` to store and retrieve routine IDs and titles for subsequent commands.
