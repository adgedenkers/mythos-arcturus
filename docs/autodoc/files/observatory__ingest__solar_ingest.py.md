# observatory/ingest/solar_ingest.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 697

---

### Documentation for `observatory/ingest/solar_ingest.py`

#### Purpose
This file is responsible for fetching real-time solar and space weather data from various APIs (NOAA DSCOVR, SWPC, and NASA DONKI) and ingesting this data into a PostgreSQL database. It also includes logic for detecting solar wind events and summarizing current conditions.

#### Architecture
The file is structured into several functional components:
1. **Configuration and Logging**: Sets up environment variables, logging, and database connection parameters.
2. **Database Operations**: Functions for upserting different types of solar and geomagnetic data into PostgreSQL.
3. **Data Fetchers**: Functions for fetching data from NOAA and NASA APIs.
4. **Event Detection**: Functions for detecting solar wind events.
5. **Main Execution**: Functions for running the ingestion service and handling shutdown signals.

#### Patterns
- **Singleton Pattern**: The `get_db` function ensures a single database connection is reused.
- **Factory Pattern**: The `fetch_*` functions act as factories to produce data rows from API responses.

#### Dependencies
- **Standard Libraries**: `json`, `logging`, `os`, `signal`, `sys`, `time`
- **External Libraries**: `psycopg2`, `psycopg2.extras`, `requests`

#### Interfaces
- **Public Functions**:
  - `upsert_solar_wind(conn, rows)`: Upserts solar wind readings.
  - `upsert_geomag(conn, rows)`: Upserts geomagnetic index readings.
  - `upsert_flares(conn, rows)`: Upserts solar flare events.
  - `upsert_cmes(conn, rows)`: Upserts CME events.
  - `insert_solar_wind_event(conn, event)`: Inserts a detected solar wind event.
  - `safe_float(val)`: Converts a value to a float or returns `None`.
  - `parse_noaa_timestamp(ts_str)`: Parses a NOAA timestamp.
  - `fetch_solar_wind()`: Fetches solar wind data from NOAA DSCOVR.
  - `kp_to_storm_level(kp)`: Converts Kp index to a storm level.
  - `fetch_geomagnetic()`: Fetches geomagnetic indices from NOAA SWPC.
  - `fetch_donki_flares()`: Fetches solar flares from NASA DONKI.
  - `fetch_donki_cmes()`: Fetches CMEs from NASA DONKI.
  - `detect_solar_wind_events(conn)`: Detects solar wind events.
  - `get_current_conditions(conn)`: Gets a summary of current solar/space weather conditions.
  - `_shutdown(signum, frame)`: Handles shutdown signals.
  - `run()`: Main execution function.

#### Database
- **Tables**:
  - `solar_wind_readings`: Stores solar wind readings.
  - `geomagnetic_indices`: Stores geomagnetic indices.
  - `solar_flares`: Stores solar flare events.
  - `cme_events`: Stores CME events.
  - `solar_wind_events`: Stores detected solar wind events.

#### Configuration
- **Environment Variables**:
  - `MYTHOS_DB`, `MYTHOS_DB_USER`, `MYTHOS_DB_HOST`, `MYTHOS_DB_PORT`: Database connection parameters.
  - `NASA_API_KEY`: API key for NASA DONKI.

#### Key Logic
- **Data Fetching**: Functions like `fetch_solar_wind`, `fetch_geomagnetic`, `fetch_donki_flares`, and `fetch_donki_cmes` fetch data from APIs and parse it into a structured format.
- **Data Insertion**: Functions like `upsert_solar_wind`, `upsert_geomag`, `upsert_flares`, and `upsert_cmes` insert or update data in the PostgreSQL database.
- **Event Detection**: `detect_solar_wind_events` checks recent solar wind data for high-speed streams and shocks.
- **Condition Summarization**: `get_current_conditions` provides a summary of current solar and space weather conditions.

#### Integration Points
- **Data Sources**: Integrates with NOAA DSCOVR, SWPC, and NASA DONKI APIs.
- **Database**: Integrates with PostgreSQL for storing and querying solar and space weather data.
- **Systemd Service**: Designed to run as a systemd service, polling data on configurable intervals.
- **Logging**: Logs to both file and standard output for monitoring and debugging.

This file is a critical component of the Mythos system, ensuring that real-time solar and space weather data is continuously ingested and processed, providing a robust foundation for further analysis and decision-making.
