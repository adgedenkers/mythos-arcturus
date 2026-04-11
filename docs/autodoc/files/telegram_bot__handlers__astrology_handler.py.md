# telegram_bot/handlers/astrology_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 462

---

### File: `telegram_bot/handlers/astrology_handler.py`

#### Purpose
This file contains the logic for handling astrology-related commands in the Mythos Telegram bot, including showing natal charts, planet positions, house cusps, and comparisons between charts.

#### Architecture
The file consists of several top-level functions:
- `get_db_connection`: Establishes a connection to the PostgreSQL database.
- `execute_query`: Executes a given SQL query and returns the results.
- `handle_chart`: Handles the `/chart` command to show natal charts or comparisons.
- `handle_planets`: Handles the `/planets` command to show planet positions.
- `handle_houses`: Handles the `/houses` command to show house cusps.
- `handle_aspects`: Handles the `/aspects` command to show natal aspects (not fully shown in the provided code).
- `handle_group_planets`: Handles the `/group_planets` command to find all people with a planet in a specific sign (not fully shown in the provided code).
- `register_handlers`: Registers the astrology command handlers with the Telegram bot application.

#### Patterns
- **Singleton**: The `get_db_connection` function can be considered a singleton pattern as it provides a single connection to the database.
- **Factory**: The `execute_query` function can be seen as a factory method for executing database queries.

#### Dependencies
- `logging`: For logging purposes.
- `os`: For accessing environment variables.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `typing`: For type hints.
- `telegram`: For interacting with the Telegram bot API.
- `telegram.ext`: For handling updates and context in the Telegram bot.

#### Interfaces
- `handle_chart`, `handle_planets`, `handle_houses`, `handle_aspects`, `handle_group_planets`: These functions are designed to be called by the Telegram bot framework in response to specific commands.
- `register_handlers`: This function is used to register the command handlers with the Telegram bot application.

#### Database
- **Tables**:
  - `astro_charts`: Stores information about astrology charts.
  - `astro_placements`: Stores planet placements within charts.
  - `astro_house_cusps`: Stores house cusps for charts.
  - `astro_aspects`: Stores aspects within charts (not fully shown in the provided code).

#### Configuration
- Environment variables are loaded from `/opt/mythos/.env` using `dotenv.load_dotenv`.
- PostgreSQL connection details are retrieved from environment variables:
  - `POSTGRES_HOST`
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_PORT`

#### Key Logic
- **`handle_chart`**:
  - Handles both single natal charts and bi-wheel comparisons.
  - Queries the `astro_charts` and `astro_placements` tables to retrieve chart and planet data.
  - Formats the data into a human-readable string and sends it back to the user via Telegram.

- **`handle_planets`**:
  - Retrieves and formats planet positions for a given chart.
  - Queries the `astro_charts` and `astro_placements` tables to get the necessary data.

- **`handle_houses`**:
  - Retrieves and formats house cusps for a given chart.
  - Queries the `astro_charts` and `astro_house_cusps` tables to get the necessary data.

#### Integration Points
- The functions in this file are integrated with the Telegram bot framework via the `register_handlers` function, which registers them as command handlers.
- The PostgreSQL database is accessed through the `get_db_connection` and `execute_query` functions, which are used by the astrology command handlers to retrieve and format data.

### Summary
This file provides the core functionality for handling astrology-related commands in the Mythos Telegram bot. It integrates with the PostgreSQL database to retrieve chart and planet data, formats this data into a readable format, and sends it back to the user via Telegram. The file is well-structured with clear separation of concerns, making it easy to maintain and extend.
