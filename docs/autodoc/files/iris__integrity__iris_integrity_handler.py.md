# iris/integrity/iris_integrity_handler.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 68

---

### File: `iris/integrity/iris_integrity_handler.py`

#### Purpose
This file contains the `iris_integrity_handler` function, which processes the `/iris_integrity` command in the Telegram interface. It handles various subcommands to perform integrity checks and report the system's health status.

#### Architecture
- **Function**: `iris_integrity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE)`
  - This asynchronous function handles the `/iris_integrity` command and its subcommands.
  - It dynamically imports necessary functions from `iris_integrity` module based on the subcommand.
  - The function processes different subcommands (`scan`, `full`, `context`, and default status) and constructs appropriate responses.

#### Patterns
- **Dynamic Import**: The function dynamically imports required modules and functions based on the subcommand.
- **Command Pattern**: The function acts as a dispatcher for different subcommands, each with its own logic.

#### Dependencies
- **Imports**: `logging`, `sys`
- **Dynamic Imports**: `iris_integrity` module for functions like `run_integrity_scan`, `read_latest_integrity_report`, `build_health_summary`, `format_telegram_report`, `format_iris_context`.

#### Interfaces
- **Exposed Function**: `iris_integrity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE)`
  - This function is exposed to handle the `/iris_integrity` command in the Telegram interface.

#### Database
- **PostgreSQL Tables**: `telegram`, `from`, `iris_integrity`, `latest`
  - These tables are referenced for integrity checks and reporting.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
- **Subcommand Handling**:
  - `scan`: Runs a fast integrity scan and reports the health summary.
  - `full`: Runs a full integrity scan and reports the health summary.
  - `context`: Reports the current context of the system.
  - Default: Reports the health summary from the latest scan.

- **Dynamic Import and Function Execution**:
  - The function dynamically imports and executes the necessary functions based on the subcommand.

#### Integration Points
- **Telegram Interface**: The function integrates with the Telegram interface to handle the `/iris_integrity` command.
- **Iris Integrity Module**: The function dynamically imports and uses functions from the `iris_integrity` module to perform integrity checks and build health summaries.

### Detailed Breakdown

#### `iris_integrity_handler` Function
- **Parameters**:
  - `update`: The incoming Telegram update object.
  - `context`: The context object for the Telegram bot.

- **Subcommand Handling**:
  - **`scan`**: Runs a fast integrity scan and builds a health summary.
  - **`full`**: Runs a full integrity scan and builds a health summary.
  - **`context`**: Builds and formats the current context of the system.
  - **Default**: Reports the health summary from the latest scan.

- **Dynamic Import**:
  - The function dynamically imports necessary functions from the `iris_integrity` module to handle different subcommands.

- **Logging**:
  - Uses the `logging` module to log actions and errors.

- **Database Interaction**:
  - References PostgreSQL tables `telegram`, `from`, `iris_integrity`, and `latest` for integrity checks and reporting.

### Example Usage
- **Command**: `/iris_integrity scan`
  - Response: Runs a fast integrity scan and reports the health summary.

- **Command**: `/iris_integrity full`
  - Response: Runs a full integrity scan and reports the health summary.

- **Command**: `/iris_integrity context`
  - Response: Reports the current context of the system.

- **Command**: `/iris_integrity`
  - Response: Reports the health summary from the latest scan.

This file is crucial for maintaining and reporting the health and integrity of the Mythos system through the Telegram interface.
