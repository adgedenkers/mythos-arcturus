# astrology/spiral/transit_pressure.py

**Language:** python
**Stream:** SEN
**Module:** Astrology Engine
**Lines:** 408

---

### File: astrology/spiral/transit_pressure.py

#### Purpose
This file contains functions to compute and persist transit-to-natal aspects for a given date in the Mythos system. It uses the Swiss Ephemeris library to calculate planetary positions and PostgreSQL to store the results.

#### Architecture
The file consists of several top-level functions that handle different aspects of transit pressure computation and persistence:
- `_get_conn`: Establishes a database connection.
- `_get_transiting_positions`: Computes ecliptic longitudes for transiting planets.
- `_get_transiting_positions_yesterday`: Computes positions for the day before the target date.
- `_load_natal_positions`: Loads natal ecliptic longitudes from the database.
- `_normalize_lon`: Normalizes longitude to the range 0-360.
- `_angular_distance`: Calculates the shortest arc between two ecliptic longitudes.
- `_find_aspects`: Checks for major aspects between transiting and natal longitudes.
- `_is_applying`: Determines if a transit is applying or separating.
- `_get_threshold`: Determines the threshold level for an orb value.
- `compute_daily_pressure`: Computes all transit-to-natal aspects for a given date.
- `persist_pressure`: Persists the computed aspects into the database.
- `run_daily_pressure`: Combines computation and persistence into a single pipeline.
- `get_todays_pressure`: Fetches today's transit pressure from the database.
- `format_pressure_brief`: Formats the transit pressure as a natural-language summary.
- `_fmt`: Helper function for formatting aspects.

#### Patterns
- **Singleton Pattern**: `_get_conn` is used to ensure a single database connection is established.
- **Factory Method Pattern**: `_get_transiting_positions` and `_get_transiting_positions_yesterday` can be seen as factory methods that produce the necessary planetary positions.

#### Dependencies
- `logging`: For logging errors and information.
- `os`: For environment variable access.
- `psycopg2`: For PostgreSQL database operations.
- `psycopg2.extras`: For additional PostgreSQL utilities.
- `swisseph`: For Swiss Ephemeris planetary calculations.

#### Interfaces
- `compute_daily_pressure`: Computes aspects and returns a list of aspect dictionaries.
- `persist_pressure`: Persists aspects into the database and returns the count of records written.
- `run_daily_pressure`: Combines computation and persistence and returns the aspect list.
- `get_todays_pressure`: Fetches today's transit pressure from the database.
- `format_pressure_brief`: Formats the transit pressure as a natural-language summary.

#### Database
- **Tables/Labels**:
  - `astro_chart_points`: Stores natal ecliptic longitudes.
  - `astro_natal_house_cusps`: Stores house cusps for ASC and MC.
  - `spiral_transit_pressure`: Stores computed transit pressure records.

#### Configuration
- Environment Variable: `DATABASE_URL` for database connection.

#### Key Logic
- **Aspect Calculation**: `_find_aspects` checks for major aspects between transiting and natal longitudes.
- **Orb Calculation**: `_angular_distance` calculates the shortest arc between two longitudes.
- **Applying/Seperating Determination**: `_is_applying` determines if a transit is applying or separating.
- **Threshold Determination**: `_get_threshold` determines the threshold level for an orb value.

#### Integration Points
- **Swiss Ephemeris**: `_get_transiting_positions` and `_get_transiting_positions_yesterday` use the Swiss Ephemeris library to compute planetary positions.
- **Database**: `_load_natal_positions`, `persist_pressure`, and `get_todays_pressure` interact with the PostgreSQL database to load and store transit pressure data.
- **Logging**: `logging` is used throughout the file to log errors and information.

### Summary
This file is a crucial component of the Mythos system, responsible for computing and persisting transit-to-natal aspects. It leverages the Swiss Ephemeris library for planetary calculations and interacts with PostgreSQL for data storage and retrieval. The functions are designed to be modular and reusable, with clear interfaces for integration into the broader system.
