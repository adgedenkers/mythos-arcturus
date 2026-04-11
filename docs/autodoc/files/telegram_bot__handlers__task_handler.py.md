# telegram_bot/handlers/task_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 524

---

### File: `telegram_bot/handlers/task_handler.py`

#### Purpose
This file handles task-related commands for the Mythos Telegram Bot, allowing users to add, list, mark as done, and drop tasks. It interacts with a PostgreSQL database to store and retrieve task information.

#### Architecture
The file consists of several top-level functions and an asynchronous command handler. The functions are organized to handle specific task operations such as adding tasks, listing tasks, marking tasks as done, and dropping tasks. The `task_command` function acts as the main entry point for handling various subcommands.

#### Patterns
- **Factory Method**: The `get_db_connection` function can be considered a factory method for creating a PostgreSQL database connection.
- **Command Pattern**: The `task_command` function acts as a command dispatcher, delegating tasks to specific subcommand handlers like `task_add`, `task_list`, etc.

#### Dependencies
- **Standard Libraries**: `os`, `logging`, `re`, `datetime`
- **External Libraries**: `telegram`, `psycopg2`, `telegram.ext`

#### Interfaces
- **Telegram Bot API**: The file interacts with the Telegram Bot API through the `Update` and `ContextTypes.DEFAULT_TYPE` objects.
- **Database**: The file interacts with the PostgreSQL database through the `get_db_connection` function.

#### Database
- **Tables**: The file interacts with the `idea_backlog` table in the PostgreSQL database.
- **Operations**: The file performs `INSERT`, `SELECT`, and `UPDATE` operations on the `idea_backlog` table.

#### Configuration
- **Environment Variables**: The file uses environment variables for database connection details (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`).

#### Key Logic
- **Task Addition**: The `task_add` function parses command arguments to extract task details, priority, and due date, then inserts the task into the `idea_backlog` table.
- **Task Listing**: The `task_list` function retrieves tasks from the `idea_backlog` table and formats them for display.
- **Due Date Parsing**: The `parse_due_date` function converts flexible due date formats into `datetime` objects.
- **Due Date Formatting**: The `format_due_date` function formats `datetime` objects into human-readable strings.

#### Integration Points
- **Telegram Bot**: The file integrates with the Telegram Bot API to handle user commands and send responses.
- **Database**: The file integrates with the PostgreSQL database to store and retrieve task information.
- **Logging**: The file uses Python's `logging` module to log errors and important information.

### Detailed Analysis

#### Functions

1. **`get_db_connection`**
   - **Purpose**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
   - **Dependencies**: `os`, `psycopg2`
   - **Returns**: A PostgreSQL database connection object.

2. **`parse_due_date`**
   - **Purpose**: Parses flexible due date formats into `datetime` objects.
   - **Arguments**: `date_str` (string representing the due date)
   - **Returns**: A `datetime` object or `None` if the date cannot be parsed.

3. **`format_due_date`**
   - **Purpose**: Formats `datetime` objects into human-readable strings for display.
   - **Arguments**: `due_date` (a `datetime` object)
   - **Returns**: A formatted string representing the due date.

4. **`task_command`**
   - **Purpose**: Handles the `/task` command and dispatches to subcommand handlers.
   - **Arguments**: `update`, `context`
   - **Subcommands**: `add`, `list`, `due`, `done`, `drop`, `all`
   - **Returns**: None (sends responses via the Telegram Bot API)

5. **`tasks_command`**
   - **Purpose**: Alias for the `/task list` command.
   - **Arguments**: `update`, `context`
   - **Returns**: None (sends responses via the Telegram Bot API)

6. **`task_add`**
   - **Purpose**: Adds a new task to the `idea_backlog` table.
   - **Arguments**: `update`, `context`, `args`
   - **Returns**: None (sends responses via the Telegram Bot API)

7. **`task_list`**
   - **Purpose**: Lists open tasks from the `idea_backlog` table.
   - **Arguments**: `update`, `context`, `show_all`
   - **Returns**: None (sends responses via the Telegram Bot API)

8. **`task_due`**
   - **Purpose**: Lists tasks with due dates, sorted by due date.
   - **Arguments**: `update`, `context`
   - **Returns**: None (sends responses via the Telegram Bot API)

9. **`task_done`**
   - **Purpose**: Marks a task as done in the `idea_backlog` table.
   - **Arguments**: `update`, `context`, `task_num`
   - **Returns**: None (sends responses via the Telegram Bot API)

10. **`task_drop`**
    - **Purpose**: Drops/dismisses a task from the `idea_backlog` table.
    - **Arguments**: `update`, `context`, `task_num`
    - **Returns**: None (sends responses via the Telegram Bot API)

### Summary
This file serves as the primary handler for task-related operations in the Mythos Telegram Bot. It provides a robust interface for users to manage tasks through the Telegram platform, leveraging PostgreSQL for data storage and retrieval. The file is well-structured, with clear separation of concerns and efficient handling of asynchronous operations.
