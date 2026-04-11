# telegram_bot/handlers/inspect_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 735

---

### File: `telegram_bot/handlers/inspect_handler.py`

#### Purpose
This file contains the implementation for the `/inspect` command handler in the Mythos Telegram bot. It provides various file and database inspection commands, ensuring security and access control.

#### Architecture
The file is structured around several top-level functions that handle different commands (`cmd_cat`, `cmd_head`, `cmd_tail`, etc.). These functions are designed to perform specific tasks such as reading files, listing directories, and executing database queries. The main entry point is the `handle_inspect` function, which processes incoming Telegram updates and routes them to the appropriate command handler.

#### Patterns
- **Factory Method**: The `handle_inspect` function acts as a factory method, creating and invoking the appropriate command handler based on the user input.
- **Singleton**: The logging instance `logger` is a singleton, ensuring consistent logging across the module.

#### Dependencies
- **Standard Libraries**: `os`, `re`, `subprocess`, `tempfile`, `logging`, `pathlib`
- **Telegram Bot API**: `telegram`, `telegram.ext`

#### Interfaces
- **Public Functions**:
  - `handle_inspect(update, context)`: Entry point for processing `/inspect` commands.
  - `get_help_text()`: Returns help text for the `/inspect` command.
- **Private Functions**:
  - `_is_blocked_path(path_str)`: Checks if a path matches blocked patterns.
  - `_resolve_path(relative)`: Resolves a relative path to an absolute path.
  - `_run(cmd, timeout)`: Runs a shell command safely.
  - `_deliver(update, header, content)`: Sends result inline or as a file.
  - `_send_as_file(update, header, content)`: Sends content as a file attachment.
  - `_escape_html(text)`: Escapes HTML special characters for Telegram.

#### Database
- **PostgreSQL**:
  - `Telegram`: Used for logging or storing Telegram-related data.
  - `pg_stat_user_tables`: Used for read-only queries to get table statistics.
- **Neo4j**: 
  - `Cypher` queries for read-only operations.

#### Configuration
- **Environment Variables**:
  - `TELEGRAM_ID_KA`, `TELEGRAM_ID_SERAPHE`: Used to authorize specific Telegram user IDs.
- **Constants**:
  - `MYTHOS_ROOT`: Path to the root directory of the Mythos system.
  - `MAX_MSG_LEN`, `MAX_FILE_LEN`, `MAX_TREE_DEPTH`, `MAX_LINES_DEFAULT`: Configuration for message and file size limits.

#### Key Logic
- **Security Checks**:
  - `_is_blocked_path`: Ensures that sensitive files are not accessed.
  - `_resolve_path`: Ensures that paths are within the allowed root directories.
- **Command Execution**:
  - `cmd_cat`, `cmd_head`, `cmd_tail`, `cmd_ls`, `cmd_tree`, `cmd_wc`, `cmd_find`, `cmd_grep`, `cmd_git`, `cmd_sql`, `cmd_cypher`, `cmd_service`: Each function handles a specific command, performing file operations, directory listings, and database queries.
- **Output Handling**:
  - `_deliver`, `_send_as_file`: Manages how the output is delivered to the user, either inline or as a file attachment.

#### Integration Points
- **Telegram Bot API**: The `handle_inspect` function integrates with the Telegram bot framework to receive and process user commands.
- **Filesystem and Databases**: The file interacts with the Mythos filesystem and databases (PostgreSQL and Neo4j) to perform various inspection tasks.
- **Logging**: Uses the `logging` module to log activities and errors.

### Detailed Documentation

#### `_is_blocked_path(path_str)`
- **Purpose**: Checks if a given path matches any of the blocked patterns.
- **Logic**: Uses a regular expression to match the path against a list of blocked patterns.

#### `_resolve_path(relative)`
- **Purpose**: Resolves a relative path to an absolute path, ensuring it stays within the allowed root directories.
- **Logic**: Uses `Path.resolve()` to resolve the path and checks if it is within the `MYTHOS_ROOT`.

#### `_run(cmd, timeout)`
- **Purpose**: Runs a shell command safely with a timeout.
- **Logic**: Uses `subprocess.run` to execute the command and captures the output.

#### `cmd_cat(args)`
- **Purpose**: Reads a file and returns its content.
- **Logic**: Resolves the path, checks for security, and reads the file content.

#### `cmd_head(args)`
- **Purpose**: Returns the first N lines of a file.
- **Logic**: Resolves the path, reads the file, and returns the first N lines.

#### `cmd_tail(args)`
- **Purpose**: Returns the last N lines of a file.
- **Logic**: Resolves the path, reads the file, and returns the last N lines.

#### `cmd_ls(args)`
- **Purpose**: Lists the contents of a directory.
- **Logic**: Resolves the path, lists directory entries, and formats the output.

#### `cmd_tree(args)`
- **Purpose**: Displays a directory tree.
- **Logic**: Uses the `tree` command to generate a directory tree and formats the output.

#### `cmd_wc(args)`
- **Purpose**: Provides line, word, and byte counts for a file.
- **Logic**: Uses the `wc` command to generate counts and formats the output.

#### `cmd_find(args)`
- **Purpose**: Finds files by pattern.
- **Logic**: Uses the `find` command to locate files and formats the output.

#### `cmd_grep(args)`
- **Purpose**: Searches file contents for a pattern.
- **Logic**: Uses the `grep` command to search for patterns and formats the output.

#### `cmd_git(args)`
- **Purpose**: Performs read-only Git operations.
- **Logic**: Executes Git commands and formats the output.

#### `cmd_sql(args)`
- **Purpose**: Executes read-only PostgreSQL queries.
- **Logic**: Executes SQL queries and formats the output.

#### `cmd_cypher(args)`
- **Purpose**: Executes read-only Neo4j Cypher queries.
- **Logic**: Executes Cypher queries and formats the output.

#### `cmd_service(args)`
- **Purpose**: Checks the status of Mythos services using `systemctl`.
- **Logic**: Executes `systemctl` commands and formats the output.

#### `_alias_patches`, `_alias_schema`, `_alias_nodes`, `_alias_services`, `_alias_env`, `_alias_version`
- **Purpose**: Provide shortcuts for common inspection tasks.
- **Logic**: Each function returns a predefined output or invokes a specific command.

#### `get_help_text()`
- **Purpose**: Returns the help text for the `/inspect` command.
- **Logic**: Generates a formatted help message.

#### `handle_inspect(update, context)`
- **Purpose**: Main entry point for processing `/inspect` commands.
- **Logic**: Parses the command, routes it to the appropriate handler, and delivers the result.

#### `_deliver(update, header, content)`
- **Purpose**: Sends the result to the user, either inline or as a file attachment.
- **Logic**: Checks the size of the content and decides whether to send it inline or as a file.

#### `_send_as_file(update, header, content)`
- **Purpose**: Sends content as a file attachment.
- **Logic**: Creates a temporary file, writes the content, and sends it as a file attachment.

#### `_escape_html(text)`
- **Purpose**: Escapes HTML special characters for Telegram.
- **Logic**: Uses `html.escape` to escape special characters.

### Conclusion
The `inspect_handler.py` file provides a comprehensive set of tools for inspecting the Mythos filesystem and databases through a Telegram bot interface. It ensures security and access control while providing a user-friendly and powerful command set.
