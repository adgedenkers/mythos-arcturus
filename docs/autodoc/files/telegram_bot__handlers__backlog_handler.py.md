# telegram_bot/handlers/backlog_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 380

---

### File: `telegram_bot/handlers/backlog_handler.py`

#### Purpose
This file handles the `/backlog` command for the Mythos Telegram Bot, providing functionality to list, filter, and update the status of backlog items stored in a PostgreSQL database.

#### Architecture
The file consists of several top-level functions:
- `get_db_connection`: Establishes a connection to the PostgreSQL database.
- `backlog_command`: Handles the `/backlog` command and delegates to other functions based on the command arguments.
- `backlog_stream_summary`: Provides a summary of open items per stream.
- `backlog_list`: Lists backlog items based on specified filters.
- `backlog_set_status`: Updates the status of a specific backlog item.

#### Patterns
- **Singleton Pattern**: The `get_db_connection` function can be considered a singleton pattern as it provides a single connection to the PostgreSQL database.
- **Command Pattern**: The `backlog_command` function acts as a dispatcher for different commands, delegating to specific handlers based on the input arguments.

#### Dependencies
- **Standard Libraries**: `os`, `logging`
- **External Libraries**: `psycopg2`, `telegram`, `telegram.ext`

#### Interfaces
- **Telegram Bot API**: The functions interact with the Telegram bot API through `Update` and `ContextTypes.DEFAULT_TYPE`.
- **Database Interaction**: Functions interact with the PostgreSQL database to retrieve and update backlog items.

#### Database
- **Tables**: `idea_backlog`, `task`, `documentation`
- **Operations**: 
  - `SELECT` queries to retrieve backlog items, count open items per stream, and update item status.
  - `UPDATE` queries to change the status of backlog items.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_PORT`

#### Key Logic
- **Backlog Command Handling**: The `backlog_command` function parses the command arguments and delegates to appropriate handlers (`backlog_list`, `backlog_stream_summary`, `backlog_set_status`).
- **Stream Summary**: The `backlog_stream_summary` function queries the database to count open items per stream and formats the response.
- **Backlog Listing**: The `backlog_list` function constructs a SQL query based on the provided filters (scope, show_all, stream_filter) and retrieves the backlog items.
- **Status Update**: The `backlog_set_status` function updates the status of a specific backlog item based on the provided item number and new status.

#### Integration Points
- **Telegram Bot**: The functions are integrated with the Telegram bot framework, receiving and responding to user commands.
- **PostgreSQL Database**: The functions interact with the PostgreSQL database to retrieve and update backlog items.
- **Context Management**: The `ContextTypes.DEFAULT_TYPE` is used to manage user-specific data, such as the list of backlog item IDs for status updates.

### Detailed Function Descriptions

1. **`get_db_connection`**
   - **Purpose**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
   - **Dependencies**: `psycopg2`, `os`

2. **`backlog_command`**
   - **Purpose**: Handles the `/backlog` command and delegates to other functions based on the command arguments.
   - **Dependencies**: `Update`, `ContextTypes.DEFAULT_TYPE`
   - **Key Logic**: Parses the command arguments and delegates to `backlog_list`, `backlog_stream_summary`, or `backlog_set_status` based on the input.

3. **`backlog_stream_summary`**
   - **Purpose**: Provides a summary of open items per stream.
   - **Dependencies**: `get_db_connection`
   - **Key Logic**: Queries the database to count open items per stream and formats the response.

4. **`backlog_list`**
   - **Purpose**: Lists backlog items based on specified filters.
   - **Dependencies**: `get_db_connection`
   - **Key Logic**: Constructs a SQL query based on the provided filters (scope, show_all, stream_filter) and retrieves the backlog items.

5. **`backlog_set_status`**
   - **Purpose**: Updates the status of a specific backlog item.
   - **Dependencies**: `get_db_connection`
   - **Key Logic**: Validates the item number, retrieves the item ID from the context, and updates the status in the database.

This file is a critical component of the Mythos Telegram Bot, providing comprehensive functionality for managing and displaying the development backlog.
