# observatory/geometry/planetary_engine.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 666

---

### File: `observatory/geometry/planetary_engine.py`

#### Purpose
This file contains functions to compute planetary positions, aspects, alignments, and gravitational forcing vectors using the Swiss Ephemeris library and store the results in a PostgreSQL database.

#### Architecture
The file is organized into several sections:
1. **Initialization and Configuration**: Sets up logging, database connection parameters, and planet definitions.
2. **Swiss Ephemeris Helpers**: Functions to initialize the Swiss Ephemeris and convert datetime to Julian Day.
3. **Computation**: Functions to compute planetary positions, aspects, gravitational forcing vectors, and alignments.
4. **Database**: Functions to connect to the database and store computed data.

#### Patterns
- **Singleton**: The database connection (`get_db`) is a singleton pattern, ensuring a single connection is reused.
- **Factory**: Functions like `compute_positions`, `compute_aspects`, `compute_forcing_vectors`, and `detect_alignments` act as factories to produce planetary data.

#### Dependencies
- **Standard Libraries**: `json`, `logging`, `math`, `os`, `signal`, `sys`, `time`
- **External Libraries**: `psycopg2`, `psycopg2.extras`, `swisseph`
- **Environment Variables**: `MYTHOS_DB`, `POSTGRES_USER`, `POSTGRES_HOST`, `MYTHOS_DB_PORT`

#### Interfaces
- **Public Functions**: `init_ephe`, `datetime_to_jd`, `get_planet_position`, `compute_positions`, `compute_aspects`, `compute_forcing_vectors`, `detect_alignments`, `get_db`, `store_positions`, `store_aspects`, `store_forcing`, `store_alignments`, `get_geometry_summary`, `backfill_hours`, `_shutdown`, `run`
- **Private Functions**: `_shutdown` (signal handler)

#### Database
- **Tables**: `planetary_positions`, `planetary_aspects`, `planetary_forcing`, `planetary_alignments`
- **Operations**: Insert operations for storing planetary positions, aspects, forcing vectors, and alignments.

#### Configuration
- **Environment Variables**: `MYTHOS_DB`, `POSTGRES_USER`, `POSTGRES_HOST`, `MYTHOS_DB_PORT`
- **Constants**: `EPHE_PATH`, `COMPUTE_INTERVAL`, `LOG_DIR`, `LOG_FILE`

#### Key Logic
1. **Planetary Position Calculation**: Uses Swiss Ephemeris to compute geocentric ecliptic positions.
2. **Aspect Calculation**: Computes angular separations and strengths for predefined aspects (conjunction, opposition, trine, square, sextile).
3. **Gravitational Forcing Vectors**: Computes gravitational forces and their net effect.
4. **Alignment Detection**: Detects stellium, grand trine, and planetary compression patterns.

#### Integration Points
- **Swiss Ephemeris**: For planetary position calculations.
- **PostgreSQL Database**: For storing computed planetary data.
- **Logging**: For logging computation and storage operations.
- **Signal Handling**: For graceful shutdown.

### Detailed Documentation

#### Functions

1. **`init_ephe`**
   - **Purpose**: Initialize Swiss Ephemeris with the specified data path.
   - **Dependencies**: `swisseph`
   - **Database**: None

2. **`datetime_to_jd`**
   - **Purpose**: Convert a `datetime` object to Julian Day.
   - **Dependencies**: `swisseph`
   - **Database**: None

3. **`get_planet_position`**
   - **Purpose**: Get the geocentric ecliptic position for a given planet at a specific Julian Day.
   - **Dependencies**: `swisseph`
   - **Database**: None

4. **`compute_positions`**
   - **Purpose**: Compute all planetary positions for a given datetime.
   - **Dependencies**: `datetime_to_jd`, `get_planet_position`
   - **Database**: None

5. **`compute_aspects`**
   - **Purpose**: Compute all planetary aspects with continuous strength.
   - **Dependencies**: `math`
   - **Database**: None

6. **`compute_forcing_vectors`**
   - **Purpose**: Compute gravitational forcing vectors for each planet relative to Earth.
   - **Dependencies**: `math`
   - **Database**: None

7. **`detect_alignments`**
   - **Purpose**: Detect major planetary alignment patterns.
   - **Dependencies**: `itertools`
   - **Database**: None

8. **`get_db`**
   - **Purpose**: Get a PostgreSQL database connection.
   - **Dependencies**: `psycopg2`
   - **Database**: Connects to `planetary_positions`, `planetary_aspects`, `planetary_forcing`, `planetary_alignments`

9. **`store_positions`**
   - **Purpose**: Store planetary positions in the database.
   - **Dependencies**: `psycopg2`
   - **Database**: `planetary_positions`

10. **`store_aspects`**
    - **Purpose**: Store planetary aspects in the database.
    - **Dependencies**: `psycopg2`
    - **Database**: `planetary_aspects`

11. **`store_forcing`**
    - **Purpose**: Store gravitational forcing vectors in the database.
    - **Dependencies**: `psycopg2`
    - **Database**: `planetary_forcing`

12. **`store_alignments`**
    - **Purpose**: Store planetary alignments in the database.
    - **Dependencies**: `psycopg2`
    - **Database**: `planetary_alignments`

13. **`get_geometry_summary`**
    - **Purpose**: Generate a formatted summary of current planetary geometry.
    - **Dependencies**: `psycopg2`
    - **Database**: `planetary_positions`, `planetary_aspects`, `planetary_forcing`, `planetary_alignments`

14. **`backfill_hours`**
    - **Purpose**: Backfill the last N hours of planetary data.
    - **Dependencies**: `psycopg2`
    - **Database**: `planetary_positions`, `planetary_aspects`, `planetary_forcing`, `planetary_alignments`

15. **`_shutdown`**
    - **Purpose**: Handle shutdown signals.
    - **Dependencies**: `signal`
    - **Database**: None

16. **`run`**
    - **Purpose**: Main entry point to run the planetary geometry engine.
    - **Dependencies**: `time`, `signal`, `logging`
    - **Database**: Connects to `planetary_positions`, `planetary_aspects`, `planetary_forcing`, `planetary_alignments`

### Summary
This file is a crucial component of the Mythos system, responsible for computing and storing planetary positions, aspects, gravitational forcing vectors, and alignments. It integrates with the Swiss Ephemeris library for planetary calculations and the PostgreSQL database for persistent storage. The file is designed to be robust, with logging and signal handling for graceful operation.
