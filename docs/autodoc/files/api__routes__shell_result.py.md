# api/routes/shell_result.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 81

---

### File: `api/routes/shell_result.py`

#### Purpose
This file defines routes for receiving shell command results from an iOS Shortcut and forwarding them to Telegram via a FastAPI endpoint. It also includes a health check endpoint.

#### Architecture
- **Classes**: 
  - `ShellResult`: A Pydantic model representing the shell command result, including the command, output, exit code, and an optional label.
- **Functions**:
  - `receive_shell_result`: An asynchronous function that handles POST requests to `/shell-result`, processes the shell command result, and forwards it to Telegram.
  - `ping`: An asynchronous function that handles GET requests to `/shell-result/ping` for health checks.

#### Patterns
- **Factory Pattern**: The `ShellResult` class is a Pydantic model, which can be seen as a factory for creating validated shell result objects.
- **Decorator Pattern**: The `@router.post` and `@router.get` decorators are used to define the routes.

#### Dependencies
- **Imports**:
  - `os`: For accessing environment variables.
  - `logging`: For logging messages.
  - `httpx`: For making asynchronous HTTP requests.
  - `fastapi`: For defining the API router and request handling.
  - `pydantic`: For defining the `ShellResult` model.

#### Interfaces
- **Endpoints**:
  - `POST /shell-result`: Receives shell command results and forwards them to Telegram.
  - `GET /shell-result/ping`: Health check endpoint.

#### Database
- **References**: The file does not directly interact with any database tables or Neo4j labels. The DB references listed in the metadata are likely incorrect and not relevant to this file.

#### Configuration
- **Environment Variables**:
  - `TELEGRAM_BOT_TOKEN`: Token for the Telegram bot.
  - `SHELL_API_KEY`: API key for authentication.
  - `TELEGRAM_ID_KA`: Default recipient's Telegram ID.

#### Key Logic
- **Authentication**: Checks if the `X-API-Key` header matches the `SHELL_API_KEY` environment variable.
- **Message Formatting**: Formats the shell command result into a Telegram message, including status indicators and truncation if the output exceeds Telegram's character limit.
- **Telegram Delivery**: Sends the formatted message to Telegram using the `httpx` library.

#### Integration Points
- **iOS Shortcut**: Receives command output from an iOS Shortcut.
- **Telegram**: Forwards the command output to Telegram using the Telegram Bot API.
- **FastAPI**: Integrates with the FastAPI framework to define and handle API routes.

### Detailed Breakdown

#### `ShellResult` Class
- **Purpose**: Represents the shell command result with fields for the command, output, exit code, and an optional label.
- **Attributes**:
  - `cmd`: The command that was run.
  - `output`: Combined stdout and stderr.
  - `exit_code`: Exit code of the command.
  - `label`: Optional human-readable label.

#### `receive_shell_result` Function
- **Purpose**: Processes the shell command result and forwards it to Telegram.
- **Parameters**:
  - `payload`: An instance of `ShellResult` containing the command result.
  - `request`: The incoming HTTP request object.
- **Logic**:
  - **Authentication**: Checks if the `X-API-Key` header matches the `SHELL_API_KEY`.
  - **Message Formatting**: Formats the command result into a Telegram message, including status indicators and truncation if necessary.
  - **Telegram Delivery**: Sends the message to Telegram using the `httpx` library.

#### `ping` Function
- **Purpose**: Provides a health check for the shell result endpoint.
- **Logic**: Returns a simple JSON response indicating the endpoint is operational.

### Conclusion
This file is a crucial component of the Mythos system, handling the integration between iOS Shortcuts and Telegram for command result notifications. It leverages FastAPI for defining routes and Pydantic for data validation, ensuring robust and secure communication.
