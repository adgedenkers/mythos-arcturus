# observatory/ingest/seismic_ingest.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 471

---

### File: `observatory/ingest/seismic_ingest.py`

#### Purpose
This file contains the logic for ingesting earthquake data from the USGS GeoJSON feed, detecting clusters of earthquakes, finding antipodal pairs, and generating a summary of recent seismic activity.

#### Architecture
The file is organized into several sections:
1. **Configuration**: Environment variables for database connection and logging.
2. **Geo Math**: Functions for calculating distances between points on Earth.
3. **Database**: Functions for connecting to the database and upserting earthquake data.
4. **USGS Fetcher**: Functions for fetching earthquake data from the USGS API.
5. **Cluster Detection**: Functions for detecting clusters of earthquakes.
6. **Antipodal Detection**: Functions for finding antipodal pairs of earthquakes.
7. **Telegram Summary**: Functions for generating a summary of recent seismic activity.

#### Patterns
- **Singleton**: The `get_db` function can be considered a singleton pattern as it ensures a single database connection is used throughout the module.
- **Factory**: The `fetch_earthquakes` function acts as a factory for creating earthquake records from the USGS data.

#### Dependencies
- **Standard Libraries**: `json`, `logging`, `math`, `os`, `signal`, `sys`, `time`
- **External Libraries**: `psycopg2`, `psycopg2.extras`, `requests`

#### Interfaces
- **Public Functions**:
  - `haversine_km`: Calculates the great-circle distance between two points.
  - `get_db`: Returns a database connection.
  - `upsert_earthquakes`: Upserts earthquake events into the database.
  - `fetch_earthquakes`: Fetches earthquake data from the USGS API.
  - `detect_clusters`: Detects clusters of earthquakes.
  - `find_antipodal_pairs`: Finds antipodal pairs of earthquakes.
  - `get_seismic_summary`: Generates a summary of recent seismic activity.
  - `_shutdown`: Handles shutdown signals.
  - `run`: Main entry point for the module.

#### Database
- **Tables**:
  - `earthquakes`: Stores earthquake data.
  - `seismic_clusters`: Stores detected earthquake clusters.
  - `antipodal_pairs`: Stores antipodal pairs of earthquakes.

#### Configuration
- **Environment Variables**:
  - `MYTHOS_DB`: Database name.
  - `POSTGRES_USER`: Database user.
  - `POSTGRES_HOST`: Database host.
  - `MYTHOS_DB_PORT`: Database port.
- **Constants**:
  - `USGS_FEED_URL`: URL for the USGS earthquake feed.
  - `USGS_SIGNIFICANT_URL`: URL for significant earthquakes.
  - `POLL_INTERVAL`: Interval for polling the USGS feed.
  - `SIGNIFICANT_INTERVAL`: Interval for polling significant earthquakes.
  - `CLUSTER_DISTANCE_KM`: Distance threshold for cluster detection.
  - `CLUSTER_TIME_HOURS`: Time threshold for cluster detection.
  - `ANTIPODAL_RADIUS_KM`: Radius threshold for antipodal detection.
  - `ANTIPODAL_TIME_HOURS`: Time threshold for antipodal detection.

#### Key Logic
- **`haversine_km`**: Calculates the great-circle distance between two points using the Haversine formula.
- **`upsert_earthquakes`**: Inserts or updates earthquake data in the `earthquakes` table.
- **`fetch_earthquakes`**: Fetches earthquake data from the USGS API and processes it into a list of earthquake records.
- **`detect_clusters`**: Detects clusters of earthquakes based on proximity and time.
- **`find_antipodal_pairs`**: Finds pairs of earthquakes that are near the antipodal points of each other.
- **`get_seismic_summary`**: Generates a summary of recent seismic activity.

#### Integration Points
- **Database**: Connects to PostgreSQL to store and retrieve earthquake data.
- **USGS API**: Fetches earthquake data from the USGS GeoJSON feed.
- **Logging**: Logs events to a file and standard output.
- **Shutdown Handling**: Handles shutdown signals to ensure proper cleanup.

### Detailed Function Descriptions

1. **`haversine_km`**:
   - **Purpose**: Calculates the great-circle distance between two points on Earth.
   - **Parameters**: `lat1`, `lon1`, `lat2`, `lon2` (coordinates in degrees).
   - **Returns**: Distance in kilometers.

2. **`get_db`**:
   - **Purpose**: Returns a database connection.
   - **Parameters**: None.
   - **Returns**: A `psycopg2` database connection.

3. **`upsert_earthquakes`**:
   - **Purpose**: Inserts or updates earthquake data in the `earthquakes` table.
   - **Parameters**: `conn` (database connection), `quakes` (list of earthquake records).
   - **Returns**: Count of new inserts.

4. **`fetch_earthquakes`**:
   - **Purpose**: Fetches earthquake data from the USGS API and processes it into a list of earthquake records.
   - **Parameters**: `url` (optional, defaults to `USGS_FEED_URL`).
   - **Returns**: List of earthquake records.

5. **`detect_clusters`**:
   - **Purpose**: Detects clusters of earthquakes based on proximity and time.
   - **Parameters**: `conn` (database connection).
   - **Returns**: None.

6. **`find_antipodal_pairs`**:
   - **Purpose**: Finds pairs of earthquakes that are near the antipodal points of each other.
   - **Parameters**: `conn` (database connection).
   - **Returns**: None.

7. **`get_seismic_summary`**:
   - **Purpose**: Generates a summary of recent seismic activity.
   - **Parameters**: `conn` (database connection).
   - **Returns**: Formatted summary of recent seismic activity.

8. **`_shutdown`**:
   - **Purpose**: Handles shutdown signals.
   - **Parameters**: `signum`, `frame` (signal and frame).
   - **Returns**: None.

9. **`run`**:
   - **Purpose**: Main entry point for the module.
   - **Parameters**: None.
   - **Returns**: None.
