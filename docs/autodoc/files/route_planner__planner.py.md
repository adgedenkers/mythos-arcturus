# route_planner/planner.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 756

---

### Documentation for `route_planner/planner.py`

#### Purpose
The `RoutePlanner` class in `planner.py` is designed to assemble and optimize a daily schedule by merging recurring commitments with one-off errands, looking up known drive times, and optimizing the placement of float errands within time gaps using the nearest-neighbor algorithm. It also applies a "Reality Tax" to account for unexpected delays.

#### Architecture
The file contains a single class, `RoutePlanner`, with multiple methods to handle various aspects of schedule assembly and optimization. The class methods are designed to interact with a PostgreSQL database to fetch and update schedule-related data. The class maintains a cache for known routes to improve performance.

#### Patterns
- **Singleton Pattern**: The `RoutePlanner` class can be instantiated once, and its methods are stateless, making it behave like a singleton.
- **Factory Method**: The `get_db` function acts as a factory method to create a database connection.
- **Decorator Pattern**: The `reality_tax` function can be seen as a decorator that adds a buffer to drive times.

#### Dependencies
- **Imports**: `math`, `logging`, `psycopg2`, `psycopg2.extras`, `datetime`, `typing`
- **Database**: PostgreSQL tables `known_routes`, `recurring_schedules`, `known_locations`, `daily_tasks`

#### Interfaces
The `RoutePlanner` class exposes the following methods:
- `get_todays_recurring(target_date: date = None) -> List[dict]`: Fetches recurring schedule items for a given date.
- `get_todays_tasks(target_date: date = None) -> List[dict]`: Fetches one-off daily tasks for a given date.
- `get_today(target_date: date = None) -> dict`: Assembles today's full schedule, including recurring commitments and errands.
- `optimize_today(target_date: date = None) -> dict`: Optimizes the placement of errands within time gaps around recurring commitments.
- `add_errand(name, location_name, duration, hard_deadline, preferred_time, notes, target_date)`: Adds a one-off errand for a given date.
- `complete_errand(errand_id)`: Marks an errand as completed.
- `get_known_routes() -> Dict[Tuple[str, str], dict]`: Returns all known routes.
- `add_route(from_name, to_name, drive_minutes, notes, bidirectional)`: Adds or updates a known route.
- `add_recurring(name, schedule_type, time_at, location_name, days_of_week, duration, is_anchor, notes)`: Adds a new recurring schedule item.

#### Database
The class interacts with the following PostgreSQL tables:
- `known_routes`: Stores known drive times between locations.
- `recurring_schedules`: Stores recurring schedule items.
- `known_locations`: Stores known locations with coordinates.
- `daily_tasks`: Stores one-off daily tasks.

#### Configuration
- **Environment Variables**: None
- **Configuration Files**: None

#### Key Logic
- **Drive Time Calculation**: Uses a combination of exact matches from `known_routes`, a shortcut for locations within the Norwich corridor, and a haversine distance estimate for unknown routes.
- **Schedule Assembly**: Merges recurring commitments and one-off errands, sorting them by time.
- **Optimization**: Places float errands into time gaps between recurring commitments using the nearest-neighbor algorithm and applies a "Reality Tax" to account for unexpected delays.

#### Integration Points
- **Database**: The class interacts with the PostgreSQL database to fetch and update schedule-related data.
- **Other Subsystems**: The class is likely integrated with other subsystems of the Mythos system, such as a task management system for adding and completing errands, and a notification system for sending schedule updates.

### Detailed Method Descriptions

#### `RoutePlanner`
- **Class**: `RoutePlanner`
- **Docstring**: "Assembles and optimizes a daily schedule from Mythos data."
- **Methods**:
  - `__init__`: Initializes the `RoutePlanner` instance.
  - `_load_known_routes`: Loads all known routes into a lookup dictionary.
  - `_get_drive_time`: Calculates the drive time between two stops.
  - `get_todays_recurring`: Fetches recurring schedule items for a given date.
  - `get_todays_tasks`: Fetches one-off daily tasks for a given date.
  - `get_today`: Assembles today's full schedule, including recurring commitments and errands.
  - `optimize_today`: Optimizes the placement of errands within time gaps around recurring commitments.
  - `_get_home_location`: Retrieves the home location from known locations.
  - `add_errand`: Adds a one-off errand for a given date.
  - `complete_errand`: Marks an errand as completed.
  - `get_known_routes`: Returns all known routes.
  - `add_route`: Adds or updates a known route.
  - `_resolve_location`: Resolves location details from a location name.
  - `add_recurring`: Adds a new recurring schedule item.
  - `get_known_locations`: Returns all active known locations.

#### Top-level Functions
- `get_db`: Returns a psycopg2 connection to the Mythos database.
- `reality_tax`: Calculates buffer time for a leg.
- `haversine_km`: Calculates the great-circle distance between two points in kilometers.
- `estimate_drive_minutes`: Estimates the drive time between two points.
- `in_norwich_corridor`: Checks if a location is within the Norwich corridor.
- `time_to_minutes`: Converts a time object to minutes since midnight.
- `minutes_to_time_str`: Converts minutes since midnight to a human-readable time string.
- `format_schedule_telegram`: Formats a schedule dictionary into a nice Telegram message.

This documentation provides a comprehensive overview of the `RoutePlanner` class and its methods, detailing how it integrates with the Mythos system and interacts with the PostgreSQL database to manage and optimize daily schedules.
