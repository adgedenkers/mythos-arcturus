# NEU-0001_perception_router/opt/mythos/neuro/perception_router.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 76

---

### Documentation for `perception_router.py`

#### Purpose
The `perception_router.py` file contains the `PerceptionRouter` class, which is responsible for logging perception events to both a PostgreSQL database and a Redis stream. This class ensures that events are stored persistently and made available for real-time processing.

#### Architecture
- **Classes**: 
  - `PerceptionRouter`: The main class that handles event logging and storage.
- **Methods**:
  - `__init__`: Initializes the `PerceptionRouter` with PostgreSQL and Redis connections.
  - `log_event`: Logs a perception event to the database and Redis stream.
  - `_store_event`: Stores the event in the PostgreSQL database and returns the event ID.

#### Patterns
- **Singleton**: The `PerceptionRouter` class is not explicitly designed as a singleton, but it can be used as one by ensuring only one instance is created.
- **Facade**: The `PerceptionRouter` class acts as a facade, abstracting the complexities of database and Redis interactions.

#### Dependencies
- **Imports**:
  - `json`: For JSON serialization and deserialization.
  - `redis`: For interacting with the Redis stream.
  - `psycopg2`: For interacting with the PostgreSQL database.
  - `datetime`: For generating timestamps.
  - `perception_event_types`: For event type validation.

#### Interfaces
- **Public Methods**:
  - `log_event(event_type, content, source=None, metadata=None)`: Logs a perception event to the database and Redis stream.
- **Private Methods**:
  - `_store_event(payload)`: Stores the event in the PostgreSQL database and returns the event ID.

#### Database
- **PostgreSQL Tables**:
  - `perception_log`: Stores perception events with columns `event_type`, `content`, `source`, `metadata`, `created_at`, and `id`.
  - `perception_event_types`: Contains valid event types for validation.
- **Redis**:
  - `mythos:perception`: Redis stream where perception events are published.

#### Configuration
- **Environment Variables/Config Files**:
  - `pg_conn_string`: PostgreSQL connection string.
  - `redis_host`: Redis host (default: `localhost`).
  - `redis_port`: Redis port (default: `6379`).

#### Key Logic
- **Event Logging**:
  - Validates the event type against `perception_event_types`.
  - Serializes the event payload and stores it in the PostgreSQL database.
  - Publishes the event to the Redis stream for real-time processing.
- **Database Storage**:
  - Inserts the event into the `perception_log` table.
  - Uses `json.dumps` to serialize the metadata field.

#### Integration Points
- **PostgreSQL**:
  - Connects to the PostgreSQL database to store perception events.
- **Redis**:
  - Publishes perception events to a Redis stream for real-time processing.
- **Event Types**:
  - Validates event types against a predefined list (`perception_event_types`).

### Summary
The `PerceptionRouter` class in `perception_router.py` is a critical component of the Mythos system, responsible for logging perception events to both a PostgreSQL database and a Redis stream. It ensures that events are stored persistently and made available for real-time processing, abstracting the complexities of database and Redis interactions.
