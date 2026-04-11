# workers/lunar_calendar_worker.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 183

---

### File: workers/lunar_calendar_worker.py

#### Purpose
This file contains the logic for a long-lived background process that monitors for new moon events and automatically generates Seraphe's lunar calendar for the upcoming cycle. It also sends a Telegram notification when the calendar is ready.

#### Architecture
The file consists of several functions that handle different aspects of calendar generation and notification:
- `get_telegram_config`: Loads Telegram configuration from environment variables or a config file.
- `send_telegram`: Sends a Telegram message.
- `moon_phase_angle`: Calculates the moon phase angle.
- `is_new_moon_today`: Determines if today is within 12 hours of a new moon.
- `next_month`: Calculates the next month.
- `calendar_exists`: Checks if a calendar for a given year and month already exists.
- `generate_calendar`: Generates the lunar calendar for a given year and month.
- `run`: Main loop that checks for new moon events and triggers calendar generation.

#### Patterns
- **Singleton Pattern**: The `logging` module is configured once at the start of the script.
- **Polling Pattern**: The `run` function continuously checks for new moon events at regular intervals.

#### Dependencies
- `os`: For environment variable access and directory operations.
- `sys`: For path manipulation and exiting the script.
- `time`: For sleep operations.
- `logging`: For logging events.
- `subprocess`: For running the calendar generation script.
- `requests`: For sending Telegram messages.
- `swisseph`: For astronomical calculations.
- `datetime`: For date and time operations.
- `pathlib`: For file path operations.

#### Interfaces
- `get_telegram_config`: Returns Telegram configuration.
- `send_telegram`: Sends a Telegram message.
- `moon_phase_angle`: Calculates the moon phase angle.
- `is_new_moon_today`: Checks if today is within 12 hours of a new moon.
- `next_month`: Calculates the next month.
- `calendar_exists`: Checks if a calendar exists for a given year and month.
- `generate_calendar`: Generates the lunar calendar for a given year and month.
- `run`: Main function that runs the worker loop.

#### Database
- **PostgreSQL Tables**: `datetime`, `pathlib`, `environment`, `config`
  - These tables are likely used for storing configuration and state information, but the specific interactions are not detailed in the provided code.

#### Configuration
- Environment Variables: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- Config File: `/opt/mythos/config/telegram.conf` (for Telegram configuration)

#### Key Logic
1. **New Moon Detection**: Uses `is_new_moon_today` to check if today is within 12 hours of a new moon.
2. **Calendar Generation**: Uses `generate_calendar` to generate the lunar calendar for the next month if a new moon is detected.
3. **Telegram Notification**: Uses `send_telegram` to notify users when the calendar is ready.
4. **Polling Loop**: The `run` function continuously checks for new moon events and triggers calendar generation at regular intervals.

#### Integration Points
- **Telegram Integration**: Sends notifications via Telegram using the `send_telegram` function.
- **Calendar Generator**: Uses a separate script (`seraphe_lunar_generator.py`) to generate the calendar.
- **Logging**: Uses the `logging` module to log events to both the console and a file.
- **Environment and Configuration**: Loads configuration from environment variables and a config file.

### Summary
The `lunar_calendar_worker.py` script is a background worker that monitors for new moon events and automatically generates lunar calendars for Seraphe. It integrates with Telegram for notifications and uses external scripts and libraries for astronomical calculations and calendar generation. The script is designed to run continuously, checking for new moon events and generating calendars as needed.
