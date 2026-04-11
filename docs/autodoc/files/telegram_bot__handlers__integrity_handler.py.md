# telegram_bot/handlers/integrity_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 280

---

### File: `telegram_bot/handlers/integrity_handler.py`

#### Purpose
This file contains the command handlers for the Telegram bot to manage integrity scans and display statistics. It interacts with the Mythos system to perform various integrity checks and report the results.

#### Architecture
The file consists of several top-level functions:
- `_is_authorized`: Checks if a chat is authorized to use integrity commands.
- `handle_integrity`: Handles the `/integrity` command, which can run different types of integrity scans or show statistics.
- `_handle_scan`: Executes the specified components of the integrity scan.
- `_handle_stats`: Displays graph statistics.
- `_handle_quick`: Provides a quick health summary.

#### Patterns
- **Singleton Pattern**: The `logger` object is a singleton used for logging.
- **Factory Pattern**: The `handle_integrity` function acts as a factory to dispatch to specific handlers based on the subcommand.

#### Dependencies
- **Standard Libraries**: `os`, `sys`, `time`, `logging`, `asyncio`
- **External Libraries**: `telegram`, `telegram.ext`
- **Internal Modules**: `integrity.graph`, `integrity.file_scanner`, `integrity.function_extractor`, `integrity.table_scanner`, `integrity.service_scanner`

#### Interfaces
- **Public Functions**:
  - `handle_integrity(update: Update, context: ContextTypes.DEFAULT_TYPE)`: Entry point for the `/integrity` command.
- **Private Functions**:
  - `_is_authorized(chat_id: int)`: Checks if a chat is authorized.
  - `_handle_scan(update, files=False, funcs=False, tables=False, services=False)`: Runs the specified scan components.
  - `_handle_stats(update)`: Displays graph statistics.
  - `_handle_quick(update)`: Provides a quick health summary.

#### Database
- **PostgreSQL Tables**:
  - `datetime`
  - `telegram`
  - `from`
  - `integrity` (multiple references)
- **Neo4j Labels**:
  - `IntegrityFile`
  - `IntegrityDirectory`
  - `IntegrityFunction`
  - `IntegrityTable`
  - `IntegrityColumn`
  - `IntegrityService`
  - `IMPORTS`

#### Configuration
- **Environment Variables**:
  - `MYTHOS_ROOT`: Path to the Mythos root directory.
  - `TELEGRAM_AUTHORIZED_CHATS`: Comma-separated list of authorized chat IDs.
  - `TELEGRAM_CHAT_ID`: Main bot chat ID.

#### Key Logic
1. **Authorization Check**:
   - `_is_authorized` checks if the chat is authorized to run integrity commands.
2. **Command Handling**:
   - `handle_integrity` parses the subcommand and dispatches to `_handle_scan`, `_handle_stats`, or `_handle_quick`.
3. **Scan Execution**:
   - `_handle_scan` performs file, function, table, and service scans using Neo4j and reports the results.
4. **Statistics Display**:
   - `_handle_stats` queries Neo4j to display various graph statistics.
5. **Quick Health Summary**:
   - `_handle_quick` provides a quick summary of file counts, function counts, and service health.

#### Integration Points
- **Telegram Bot**:
  - The `handle_integrity` function is registered in `mythos_bot.py` to handle the `/integrity` command.
- **Integrity Subsystem**:
  - The file interacts with the `integrity` module to perform scans and retrieve statistics.
- **Logging**:
  - Uses the `logger` object from `logging` to log errors and information.

### Summary
This file is a crucial part of the Mythos system, enabling the Telegram bot to perform integrity scans and display statistics. It integrates with the Neo4j graph database and PostgreSQL for data retrieval and storage, and it adheres to the design patterns of singleton and factory to manage command dispatch and logging.
