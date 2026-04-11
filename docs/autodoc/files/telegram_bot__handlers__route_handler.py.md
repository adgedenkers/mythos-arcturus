# telegram_bot/handlers/route_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 412

---

### File: `telegram_bot/handlers/route_handler.py`

#### Purpose
This file contains asynchronous functions that handle various Telegram bot commands related to route planning and scheduling. These commands include showing today's schedule, adding errands, optimizing routes, managing known routes and locations, and adding recurring tasks.

#### Architecture
The file consists of several top-level asynchronous functions, each handling a specific Telegram command. Each function takes `update` and `context` as arguments, which are provided by the Telegram Bot API. The functions interact with the `RoutePlanner` class to perform operations such as fetching schedules, adding errands, and managing routes and locations.

#### Patterns
- **Factory Pattern**: The `RoutePlanner` class is used as a factory to create and manage route planning operations.
- **Singleton Pattern**: The `RoutePlanner` instance is a singleton, ensuring a single point of control for route planning operations.

#### Dependencies
- `logging`: For logging errors and information.
- `sys`: For modifying the system path to include the `route_planner` module.
- `telegram`: For handling Telegram updates and context.
- `route_planner.planner`: For route planning operations.

#### Interfaces
- **Public Functions**:
  - `handle_today(update, context)`: Handles the `/today` or `/plan` command.
  - `handle_add_errand(update, context)`: Handles the `/add_errand` command.
  - `handle_optimize(update, context)`: Handles the `/optimize` command.
  - `handle_routes(update, context)`: Handles the `/routes` command.
  - `handle_add_route(update, context)`: Handles the `/add_route` command.
  - `handle_locations(update, context)`: Handles the `/locations` command.
  - `handle_add_recurring(update, context)`: Handles the `/add_recurring` command.
  - `handle_errand_done(update, context)`: Handles the `/errand_done` command.
  - `_get_location_keywords()`: A helper function to get location keywords for fuzzy matching.

#### Database
- **PostgreSQL Tables**:
  - `datetime`: Used for date and time operations.
  - `telegram`: Used for Telegram-related operations.
  - `from`: Used for route planning.
  - `route_planner`: Used for route planning operations.

#### Configuration
- No explicit configuration files or environment variables are used in this file. However, the `RoutePlanner` class may rely on configuration settings from other parts of the system.

#### Key Logic
- **`handle_today`**: Fetches and displays today's schedule, with an option to show tomorrow's schedule.
- **`handle_add_errand`**: Adds a one-off errand for today, with optional location hints.
- **`handle_optimize`**: Re-runs optimization on today's schedule after adding errands.
- **`handle_routes`**: Displays all known routes and drive times.
- **`handle_add_route`**: Adds or updates a known route.
- **`handle_locations`**: Displays all known locations.
- **`handle_add_recurring`**: Adds a recurring task with specified time, type, and days.

#### Integration Points
- **RoutePlanner**: The `RoutePlanner` class is used to interact with the route planning subsystem.
- **Telegram Bot API**: The functions interact with the Telegram Bot API to receive and send messages.
- **PostgreSQL**: The functions rely on PostgreSQL for storing and retrieving route and schedule data.

### Detailed Analysis of Functions

#### `handle_today`
- **Purpose**: Displays today's assembled schedule.
- **Logic**: Fetches the schedule for the specified date (defaulting to today) and formats it for display. If no schedule is found, a message indicating no scheduled tasks is sent.
- **Database Interaction**: Uses the `datetime` and `route_planner` tables.

#### `handle_add_errand`
- **Purpose**: Adds a one-off errand for today.
- **Logic**: Parses the command arguments to extract the errand description and location hint. Uses fuzzy matching to resolve locations and adds the errand to the schedule.
- **Database Interaction**: Uses the `datetime` and `route_planner` tables.

#### `handle_optimize`
- **Purpose**: Re-runs optimization on today's schedule.
- **Logic**: Fetches and optimizes today's schedule, displaying the optimized route.
- **Database Interaction**: Uses the `datetime` and `route_planner` tables.

#### `handle_routes`
- **Purpose**: Displays all known routes and drive times.
- **Logic**: Fetches and formats the list of known routes for display.
- **Database Interaction**: Uses the `route_planner` table.

#### `handle_add_route`
- **Purpose**: Adds or updates a known route.
- **Logic**: Parses the command arguments to extract the route details and adds the route to the system.
- **Database Interaction**: Uses the `route_planner` table.

#### `handle_locations`
- **Purpose**: Displays all known locations.
- **Logic**: Fetches and formats the list of known locations for display.
- **Database Interaction**: Uses the `route_planner` table.

#### `handle_add_recurring`
- **Purpose**: Adds a recurring task.
- **Logic**: Parses the command arguments to extract the task details and adds the recurring task to the schedule.
- **Database Interaction**: Uses the `datetime` and `route_planner` tables.

#### `handle_errand_done`
- **Purpose**: Marks an errand as completed.
- **Logic**: Marks the specified errand as completed in the schedule.
- **Database Interaction**: Uses the `route_planner` table.

#### `_get_location_keywords`
- **Purpose**: Provides a dictionary of location keywords for fuzzy matching.
- **Logic**: Returns a dictionary of keywords and their corresponding location names.
- **Database Interaction**: No direct database interaction, but relies on the `route_planner` system for location data.
