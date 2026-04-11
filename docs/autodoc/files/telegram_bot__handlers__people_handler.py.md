# telegram_bot/handlers/people_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 469

---

### File: `telegram_bot/handlers/people_handler.py`

#### Purpose
This file handles various subcommands related to managing people records in the Mythos system via a Telegram bot. It provides functionalities to add, search, list, view, edit, and delete people records stored in a PostgreSQL database.

#### Architecture
The file consists of several top-level functions that handle different subcommands:
- `get_db_connection`: Establishes a connection to the PostgreSQL database.
- `handle_people`: Routes the incoming text to the appropriate subcommand handler.
- `_add_person`: Adds a new person to the database.
- `_search_people`: Searches for people based on a query.
- `_list_people`: Lists all people in the database.
- `_view_person`: Views detailed information about a specific person.
- `_edit_person`: Edits a specific field of a person's record.
- `_delete_person`: Deletes a person's record.
- `_parse_date`: Parses a date string.
- `_parse_time`: Parses a time string.

#### Patterns
- **No explicit design patterns**: The file primarily uses procedural programming with no explicit design patterns like factory, singleton, or observer.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors and information.
- `psycopg2`: For interacting with PostgreSQL.
- `dotenv`: For loading environment variables from a `.env` file.

#### Interfaces
- `handle_people(text: str) -> str`: Exposes the main entry point for handling `/people` subcommands. It takes a string of text and returns a string response.

#### Database
- **Tables**: 
  - `people`: Stores person records.
  - `datetime`: (Not explicitly used in the provided code but referenced in the imports).
  - `typing`: (Not explicitly used in the provided code but referenced in the imports).
  - `psycopg2`: (Not a table but a library for PostgreSQL interaction).
  - `dotenv`: (Not a table but a library for environment variable management).
  - `fields`: (Not explicitly used in the provided code but referenced in the imports).
  - `decomposed`: (Not explicitly used in the provided code but referenced in the imports).

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_PORT`

#### Key Logic
- **Adding a Person**: `_add_person` parses the input text, validates required fields, and inserts a new record into the `people` table.
- **Searching People**: `_search_people` queries the `people` table based on the provided query and returns matching records.
- **Listing People**: `_list_people` retrieves all records from the `people` table and formats them into a list.
- **Viewing a Person**: `_view_person` retrieves detailed information about a specific person based on ID or name.
- **Editing a Person**: `_edit_person` updates a specific field of a person's record in the `people` table.
- **Deleting a Person**: `_delete_person` removes a person's record from the `people` table.

#### Integration Points
- **Telegram Bot**: This file integrates with the Telegram bot to handle `/people` commands.
- **PostgreSQL Database**: The file interacts with the PostgreSQL database to manage people records.
- **Environment Configuration**: The file uses environment variables for database connection settings, loaded via `dotenv`.

### Detailed Analysis

#### `get_db_connection`
- **Purpose**: Establishes a connection to the PostgreSQL database using environment variables.
- **Logic**: Uses `psycopg2.connect` to create a connection with parameters from environment variables.

#### `handle_people`
- **Purpose**: Routes the incoming text to the appropriate subcommand handler.
- **Logic**: Splits the input text into command and arguments, then calls the corresponding handler function.

#### `_add_person`
- **Purpose**: Adds a new person to the database.
- **Logic**: Parses the input text, validates required fields, and inserts a new record into the `people` table. Handles date and time parsing, and ensures unique `canonical_id`.

#### `_search_people`
- **Purpose**: Searches for people based on a query.
- **Logic**: Queries the `people` table based on the provided query and returns matching records.

#### `_list_people`
- **Purpose**: Lists all people in the database.
- **Logic**: Retrieves all records from the `people` table and formats them into a list.

#### `_view_person`
- **Purpose**: Views detailed information about a specific person.
- **Logic**: Retrieves detailed information about a specific person based on ID or name.

#### `_edit_person`
- **Purpose**: Edits a specific field of a person's record.
- **Logic**: Updates a specific field of a person's record in the `people` table.

#### `_delete_person`
- **Purpose**: Deletes a person's record.
- **Logic**: Removes a person's record from the `people` table.

#### `_parse_date`
- **Purpose**: Parses a date string.
- **Logic**: Converts a date string to a `datetime` object.

#### `_parse_time`
- **Purpose**: Parses a time string.
- **Logic**: Converts a time string to a `datetime.time` object.

This file is a crucial part of the Mythos system, providing essential functionality for managing people records through a Telegram bot interface.
