# telegram_bot/send_notification.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 79

---

### File: `telegram_bot/send_notification.py`

#### Purpose
This file contains a standalone script to send notifications via the Telegram Bot API to a specified chat or a default admin chat. It is used by various services within the Mythos system to send alerts or updates.

#### Architecture
- **Functions**:
  - `send_message(text: str, chat_id: str = None)`: Asynchronously sends a message to a specified chat ID or a default chat ID if none is provided.
  - `main()`: Parses command-line arguments and calls `send_message` with the provided message and chat ID.

- **Data Flow**:
  - The script reads environment variables for the bot token and default chat ID.
  - It uses `httpx` to make asynchronous HTTP requests to the Telegram Bot API.
  - Command-line arguments are parsed using `argparse` to provide flexibility in specifying the message and chat ID.

#### Patterns
- **Singleton**: The logging configuration is a singleton pattern, ensuring a single logger instance is used throughout the script.
- **Command Line Interface (CLI)**: The script follows a CLI pattern, allowing it to be invoked from the command line with arguments.

#### Dependencies
- **Imports**:
  - `os`: For accessing environment variables.
  - `sys`: For system-specific parameters and functions.
  - `asyncio`: For asynchronous programming.
  - `logging`: For logging messages.
  - `httpx`: For making asynchronous HTTP requests.
  - `argparse`: For parsing command-line arguments.
  - `pathlib`: For handling file paths.
  - `dotenv`: For loading environment variables from a `.env` file.

#### Interfaces
- **Exposed Functions**:
  - `send_message(text: str, chat_id: str = None)`: Asynchronously sends a message via the Telegram Bot API.
  - `main()`: Entry point for the script, parses command-line arguments and invokes `send_message`.

#### Database
- **References**:
  - No direct database interactions are performed in this file. However, it relies on environment variables loaded from a `.env` file, which might be managed in a database elsewhere in the system.

#### Configuration
- **Environment Variables**:
  - `TELEGRAM_BOT_TOKEN`: Bot token for the Telegram Bot API.
  - `TELEGRAM_ADMIN_CHAT_ID`: Default chat ID for sending notifications.

- **Configuration Files**:
  - `.env`: Environment variables are loaded from this file using `dotenv`.

#### Key Logic
- **Main Logic**:
  - The `send_message` function constructs a payload with the message text and chat ID, then sends an HTTP POST request to the Telegram Bot API.
  - If the initial request fails due to formatting issues, it retries without the `parse_mode` parameter.
  - The `main` function parses command-line arguments and invokes `send_message` with the provided message and chat ID.

#### Integration Points
- **Mythos Subsystems**:
  - This script is intended to be used by other services within the Mythos system, such as the patch monitor, to send notifications via the Telegram Bot API.
  - It relies on environment variables that might be managed or configured by other parts of the Mythos system, such as the configuration management service.

### Summary
The `send_notification.py` script is a standalone utility for sending notifications via the Telegram Bot API. It is designed to be invoked from the command line and integrates with other Mythos services by providing a simple interface for sending messages. The script handles asynchronous HTTP requests and retries in case of formatting issues, ensuring robust notification delivery.
