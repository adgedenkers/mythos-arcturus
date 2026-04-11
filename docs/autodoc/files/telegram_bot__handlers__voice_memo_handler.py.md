# telegram_bot/handlers/voice_memo_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 325

---

### File: `telegram_bot/handlers/voice_memo_handler.py`

#### Purpose
This file contains the logic for handling voice memo commands in the Mythos Telegram bot. It provides functionality to list recent voice memos, show the full transcript of a specific memo, and perform full-text searches across transcripts.

#### Architecture
The file consists of several functions that handle different aspects of voice memo management:
- `get_db_conn`: Establishes a connection to the PostgreSQL database.
- `format_duration`: Converts seconds into a human-readable duration format.
- `format_timestamp`: Formats a datetime or timestamp for display.
- `handle_voice_memos`: The main function that routes the user's command to the appropriate subcommand handler.
- `_list_memos`: Lists the last 5 voice memos with their status.
- `_show_transcript`: Retrieves and displays the full transcript of a specific voice memo.
- `_search_memos`: Performs a full-text search across voice memo transcripts.
- `_split_text`: Splits a large text into smaller chunks to fit within Telegram's message length limits.

#### Patterns
- **Singleton Pattern**: The `get_db_conn` function can be considered a singleton pattern as it provides a single point of access to the database connection.
- **Command Pattern**: The `handle_voice_memos` function acts as a command handler, routing different commands to specific subcommand handlers.

#### Dependencies
- `os`: For environment variable access.
- `logging`: For logging errors and information.
- `psycopg2`: For PostgreSQL database operations.
- `datetime`: For date and time manipulation.
- `typing`: For type hints.
- `dotenv`: For loading environment variables from a `.env` file.

#### Interfaces
- `handle_voice_memos(update, context)`: Exposes the main entry point for handling voice memo commands.
- `_list_memos(update)`: Internal function to list recent voice memos.
- `_show_transcript(update, memo_id)`: Internal function to show the full transcript of a specific memo.
- `_search_memos(update, search_term)`: Internal function to perform full-text searches across transcripts.

#### Database
- **PostgreSQL Tables**: 
  - `voice_memos`: Used to store voice memo details such as ID, filename, status, duration, speaker count, creation time, and transcripts.
  - `patches`, `voice_handler`, `datetime`, `typing`, `dotenv`, `human`, `chunks`: These are not directly used in the file, but might be referenced in other parts of the system.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: Configured via `.env` file for database connection settings.

#### Key Logic
- **Listing Memos**: `_list_memos` retrieves the last 5 voice memos from the `voice_memos` table and formats the output for display.
- **Showing Transcript**: `_show_transcript` fetches the full transcript of a specific memo, handling large texts by splitting them into chunks.
- **Searching Transcripts**: `_search_memos` performs a full-text search using PostgreSQL's full-text search capabilities and returns the top 5 results.

#### Integration Points
- **Telegram Bot**: Integrates with the Telegram bot framework, receiving commands via `update` and `context` parameters.
- **Database**: Connects to the PostgreSQL database to retrieve and manipulate voice memo data.
- **Environment Configuration**: Loads configuration from a `.env` file for database connection settings.

### Summary
This file is a critical component of the Mythos Telegram bot, providing functionality to manage and interact with voice memos. It handles listing, showing transcripts, and searching across voice memos, all while integrating with the PostgreSQL database and the Telegram bot framework.
