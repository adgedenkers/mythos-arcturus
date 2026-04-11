# observatory/graph/observatory_graph.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 516

---

### File: `observatory/graph/observatory_graph.py`

#### Purpose
This file contains functions to synchronize and maintain Neo4j nodes and relationships for various observatory events (solar, seismic, and planetary alignments) from a PostgreSQL database. It ensures the schema is up-to-date and performs periodic synchronization of events.

#### Architecture
The file consists of several top-level functions that handle different aspects of the synchronization process:
- `pg_connect`: Establishes a connection to the PostgreSQL database.
- `neo4j_connect`: Establishes a connection to the Neo4j database.
- `ensure_schema`: Ensures that the necessary constraints are in place in the Neo4j schema.
- `sync_solar_events`: Upserts SolarEvent nodes from PostgreSQL tables.
- `sync_seismic_events`: Upserts SeismicEvent nodes for M4+ earthquakes.
- `sync_seismic_clusters`: Upserts SeismicCluster nodes and HAS_MEMBER relationships to SeismicEvents.
- `sync_planetary_alignments`: Upserts PlanetaryAlignment nodes from PostgreSQL.
- `build_temporal_relationships`: Builds temporal relationships (PRECEDED_BY, CONCURRENT_WITH) between events.
- `run_sync`: Runs the synchronization process.
- `main`: Entry point for the script.

#### Patterns
- **Singleton Pattern**: The database connections (`pg_connect`, `neo4j_connect`) are not explicitly singletons but are designed to be reused.
- **Factory Pattern**: The `ensure_schema` function can be seen as a factory for ensuring the schema is correctly set up.

#### Dependencies
- `logging`: For logging information and warnings.
- `os`: For accessing environment variables.
- `time`: For time-related operations.
- `psycopg2`: For PostgreSQL database operations.
- `psycopg2.extras`: For additional PostgreSQL features.
- `neo4j`: For Neo4j database operations.

#### Interfaces
- `pg_connect`: Establishes a connection to the PostgreSQL database.
- `neo4j_connect`: Establishes a connection to the Neo4j database.
- `ensure_schema`: Ensures the Neo4j schema constraints are in place.
- `sync_solar_events`: Upserts SolarEvent nodes.
- `sync_seismic_events`: Upserts SeismicEvent nodes.
- `sync_seismic_clusters`: Upserts SeismicCluster nodes and relationships.
- `sync_planetary_alignments`: Upserts PlanetaryAlignment nodes.
- `build_temporal_relationships`: Builds temporal relationships between events.
- `run_sync`: Runs the synchronization process.
- `main`: Entry point for the script.

#### Database
- **PostgreSQL Tables**:
  - `solar_flares`
  - `solar_wind_readings`
  - `geomagnetic_indices`
  - `earthquakes`
  - `planetary_alignments`
- **Neo4j Labels**:
  - `SolarEvent`
  - `SeismicEvent`
  - `SeismicCluster`
  - `PlanetaryAlignment`
- **Neo4j Relationships**:
  - `HAS_MEMBER`
  - `CONCURRENT_WITH`

#### Configuration
- Environment variables:
  - `DATABASE_URL`: PostgreSQL connection string.
  - `NEO4J_URI`: Neo4j connection URI.
  - `NEO4J_USER`: Neo4j username.
  - `NEO4J_PASSWORD`: Neo4j password.
- Constants:
  - `BACKFILL_DAYS`: Number of days to backfill data initially (default 3).
  - `CONCURRENT_WINDOW_HOURS`: Time window for concurrent events (default 6 hours).
  - `SYNC_INTERVAL_SECONDS`: Synchronization interval (default 1 hour).

#### Key Logic
- **Sync Solar Events**: Upserts SolarEvent nodes from `solar_flares`, `solar_wind_readings`, and `geomagnetic_indices` tables.
- **Sync Seismic Events**: Upserts SeismicEvent nodes for M4+ earthquakes from the `earthquakes` table.
- **Sync Seismic Clusters**: Upserts SeismicCluster nodes and HAS_MEMBER relationships to SeismicEvents.
- **Sync Planetary Alignments**: Upserts PlanetaryAlignment nodes from the `planetary_alignments` table.
- **Build Temporal Relationships**: Builds PRECEDED_BY and CONCURRENT_WITH relationships between events based on their timestamps.

#### Integration Points
- **PostgreSQL**: Reads data from various tables (`solar_flares`, `solar_wind_readings`, `geomagnetic_indices`, `earthquakes`, `planetary_alignments`).
- **Neo4j**: Writes nodes and relationships for `SolarEvent`, `SeismicEvent`, `SeismicCluster`, and `PlanetaryAlignment` labels.
- **Main Function**: The `main` function orchestrates the synchronization process, connecting to both databases and calling the necessary sync functions.

This file is a critical component of the Mythos system, ensuring that the Neo4j graph database is kept up-to-date with the latest observatory events from the PostgreSQL database.
