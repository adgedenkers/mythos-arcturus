# telegram_bot/handlers/watchlist_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 508

---

### File: `telegram_bot/handlers/watchlist_handler.py`

#### Purpose
This file handles the `/watch` command for a Telegram bot, managing a family watchlist with streaming deep links. It processes various subcommands and user interactions to add, list, search, and modify watchlist entries.

#### Architecture
The file contains several functions that handle different aspects of the `/watch` command flow:
- `_get_conn`: Establishes a database connection.
- `_resolve_platform`: Resolves platform names to canonical keys.
- `_make_deep_link`: Builds deep links for streaming platforms.
- `_format_entry`: Formats watchlist entries for display.
- `watch_command`: Main entry point for the `/watch` command, routing to subcommands.
- `_ask_platform`, `platform_callback`, `media_type_callback`, `who_callback`: Handle the interactive process of adding a new entry to the watchlist.
- `title_received`: Handles the title input when adding a new entry.
- `_watch_list`, `_watch_search`, `_watch_set_status`, `_watch_drop`: Handle listing, searching, setting status, and dropping entries from the watchlist.
- `watch_cancel`: Cancels the add flow.
- `build_watch_handler`: Builds the `/watch` ConversationHandler.

#### Patterns
- **State Machine**: The file uses a state machine pattern to manage the conversation flow for adding a new watchlist entry.
- **Singleton**: The database connection is managed through a simple singleton pattern using `_get_conn`.

#### Dependencies
- `logging`: For logging errors and information.
- `psycopg2`: For PostgreSQL database operations.
- `datetime`, `timezone`: For handling date and time.
- `telegram`: For interacting with the Telegram bot API.
- `telegram.ext`: For handling updates and contexts.

#### Interfaces
- The file exposes several asynchronous functions that handle different parts of the `/watch` command flow, such as `watch_command`, `_ask_platform`, `platform_callback`, `media_type_callback`, `who_callback`, `_watch_list`, `_watch_search`, `_watch_set_status`, `_watch_drop`, and `watch_cancel`.
- `build_watch_handler` is used to build the ConversationHandler for the `/watch` command.

#### Database
- The file interacts with the `watchlist` table in PostgreSQL.
- It performs operations such as inserting new entries, fetching entries, and updating status.

#### Configuration
- The file uses the `DB_DSN` constant for the PostgreSQL database connection string.
- It uses the `PLATFORMS` and `PLATFORM_SHORTCUTS` dictionaries for platform information.

#### Key Logic
- **Adding a New Entry**:
  - The user is prompted to input the title, select the platform, choose the media type (show or movie), and indicate who is adding the entry.
  - The entry is then inserted into the `watchlist` table with the appropriate status (`want`).
- **Listing Entries**:
  - Fetches entries from the `watchlist` table where the status is either `want` or `watching`.
  - Formats and displays these entries with deep links to the respective platforms.
- **Searching Entries**:
  - Searches the `watchlist` table for entries matching the given term.
- **Setting Status**:
  - Updates the status of a watchlist entry based on its list position.
- **Dropping Entries**:
  - Removes a watchlist entry based on its list position.

#### Integration Points
- The file integrates with the Telegram bot API to handle user interactions and display messages.
- It interacts with the PostgreSQL database to manage watchlist entries.
- It uses the `ConversationHandler` from `telegram.ext` to manage the stateful conversation flow for adding new entries.

### Summary
This file is a crucial part of the Mythos system, handling the `/watch` command for a Telegram bot. It manages the watchlist, allowing users to add, list, search, and modify entries with deep links to streaming platforms. The file uses a state machine pattern to manage the conversation flow and interacts with a PostgreSQL database to store and retrieve watchlist entries.
