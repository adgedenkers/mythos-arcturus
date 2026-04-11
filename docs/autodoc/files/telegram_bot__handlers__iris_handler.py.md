# telegram_bot/handlers/iris_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 294

---

### Documentation for `telegram_bot/handlers/iris_handler.py`

#### Purpose
This file contains functions and handlers for interacting with the Iris consciousness system via a Telegram bot. It provides commands to fetch Iris status, run tests, execute arbitrary code, and queue tasks.

#### Architecture
The file consists of several asynchronous functions and two synchronous utility functions. The main functions are designed to handle specific Telegram commands and interact with the Iris system via HTTP requests. The utility functions format mode and uptime information.

#### Patterns
- **Factory Method**: Not explicitly used.
- **Singleton**: Not explicitly used.
- **Observer**: Not explicitly used.
- **Facade**: The file acts as a facade for interacting with the Iris system via Telegram commands.

#### Dependencies
- **Imports**: `os`, `logging`, `httpx`, `datetime`, `telegram`, `telegram.ext`
- **Environment Variables**: `IRIS_HOST` (default: `http://localhost:8100`)
- **Constants**: `IRIS_TIMEOUT`, `IRIS_TASK_TIMEOUT`

#### Interfaces
- **Public Functions**:
  - `get_iris_status()`: Fetches the current status of Iris.
  - `run_iris_test()`: Runs a simple test task via Iris.
  - `run_iris_code(code: str)`: Runs arbitrary code in the Iris sandbox.
  - `queue_iris_task(goal: str, name: str = None)`: Queues a task for Iris to work on.
  - `format_mode(mode: str)`: Formats the mode with an emoji.
  - `format_uptime(seconds: float)`: Formats uptime in a human-readable form.
  - `iris_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`: Handles the `/iris` command.
  - `iris_test_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`: Handles the `/iris_test` command.
  - `iris_run_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`: Handles the `/iris_run` command.
  - `iris_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`: Handles the `/iris_task` command.

#### Database
- **PostgreSQL Tables**: `datetime`, `telegram`, `from`, `Iris`

#### Configuration
- **Environment Variables**: `IRIS_HOST`
- **Constants**: `IRIS_TIMEOUT`, `IRIS_TASK_TIMEOUT`

#### Key Logic
- **HTTP Requests**: Functions like `get_iris_status`, `run_iris_test`, `run_iris_code`, and `queue_iris_task` make HTTP requests to the Iris system to fetch status, run tests, execute code, and queue tasks.
- **Error Handling**: Each function includes comprehensive error handling for HTTP requests, including timeouts and connection errors.
- **Formatting**: `format_mode` and `format_uptime` functions format mode and uptime information for better readability.
- **Command Handling**: Functions like `iris_command`, `iris_test_command`, `iris_run_command`, and `iris_task_command` handle specific Telegram commands and interact with the user via messages.

#### Integration Points
- **Telegram Bot**: The functions integrate with the Telegram bot framework to handle commands and send responses.
- **Iris System**: The functions interact with the Iris system via HTTP requests to fetch status, run tests, execute code, and queue tasks.
- **Logging**: The file uses the `logging` module to log information and errors.

### Detailed Function Descriptions

1. **`get_iris_status()`**
   - Fetches the current status of the Iris system via an HTTP GET request.
   - Handles various exceptions and returns a dictionary with the status or an error message.

2. **`run_iris_test()`**
   - Runs a simple test task via an HTTP POST request to the Iris system.
   - Handles exceptions and returns a dictionary with the test result or an error message.

3. **`run_iris_code(code: str)`**
   - Runs arbitrary code in the Iris sandbox via an HTTP POST request.
   - Handles exceptions and returns a dictionary with the execution result or an error message.

4. **`queue_iris_task(goal: str, name: str = None)`**
   - Queues a task for Iris to work on via an HTTP POST request.
   - Handles exceptions and returns a dictionary with the task queue result or an error message.

5. **`format_mode(mode: str)`**
   - Formats the mode with an emoji for better readability.

6. **`format_uptime(seconds: float)`**
   - Formats uptime in a human-readable form.

7. **`iris_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`**
   - Handles the `/iris` command to show the status of Iris and quick actions.
   - Fetches the status using `get_iris_status` and formats the response.

8. **`iris_test_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`**
   - Handles the `/iris_test` command to run a simple test.
   - Uses `run_iris_test` to execute the test and formats the response.

9. **`iris_run_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`**
   - Handles the `/iris_run` command to run arbitrary code.
   - Uses `run_iris_code` to execute the code and formats the response.

10. **`iris_task_command(update: Update, context: ContextTypes.DEFAULT_TYPE)`**
    - Handles the `/iris_task` command to queue a task for Iris.
    - Uses `queue_iris_task` to queue the task and formats the response.

This documentation provides a comprehensive overview of the `iris_handler.py` file, detailing its purpose, architecture, dependencies, interfaces, database interactions, configuration, key logic, and integration points within the Mythos system.
