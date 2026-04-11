# neuro/perception_router.py

**Language:** python
**Stream:** NEU
**Module:** NEURO / Consciousness Processing
**Lines:** 76

---

### File: `neuro/perception_router.py`

#### Purpose
The `PerceptionRouter` class in `perception_router.py` is responsible for logging perception events to both a PostgreSQL database and a Redis stream. It validates the event type, stores the event in the database, and then pushes the event to a Redis stream for further processing.

#### Architecture
- **Classes**: 
  - `PerceptionRouter`: The main class that handles event logging and storage.
- **Methods**:
  - `__init__`: Initializes the `PerceptionRouter` with PostgreSQL and Redis connections.
  - `log_event`: Logs a perception event by validating the event type, storing it in the database, and pushing it to a Redis stream.
  - `_store_event`: Stores the event in the PostgreSQL database and returns the event ID.
- **Data Flow**:
  1. The `log_event` method is called with event details.
  2. The event type is validated against predefined types.
  3. The event is stored in the PostgreSQL database via `_store_event`.
  4. The event is pushed to a Redis stream.

#### Patterns
- **Singleton**: The `PerceptionRouter` class does not enforce a singleton pattern, but it could be used as a singleton in the application to ensure a single instance manages event logging.
- **Facade**: The `log_event` method acts as a facade, abstracting the complexities of database and Redis operations.

#### Dependencies
- **Imports**:
  - `json`: For JSON serialization.
  - `redis`: For Redis operations.
  - `psycopg2`: For PostgreSQL operations.
  - `datetime`: For timestamp generation.
  - `perception_event_types`: For event type validation.

#### Interfaces
- **Public Methods**:
  - `log_event(event_type, content, source=None, metadata=None)`: Logs a perception event and returns the event ID.
- **Private Methods**:
  - `_store_event(payload)`: Stores the event in the PostgreSQL database and returns the event ID.

#### Database
- **PostgreSQL Tables**:
  - `perception_log`: Stores perception events with columns `source`, `source_platform`, `content`, `raw_data`, and `timestamp`.
  - `perception_event_types`: Contains valid event types for validation.
  - `datetime`: Used for timestamp generation.

#### Configuration
- **Environment Variables**:
  - `pg_conn_string`: PostgreSQL connection string.
  - `redis_host`: Redis host (default is "localhost").
  - `redis_port`: Redis port (default is 6379).

#### Key Logic
- **Event Validation**: The `log_event` method validates the event type against predefined types in `perception_event_types`.
- **Event Storage**: The `_store_event` method inserts the event into the `perception_log` table and returns the event ID.
- **Redis Stream**: The `log_event` method pushes the event payload to a Redis stream for further processing.

#### Integration Points
- **PostgreSQL**: The `PerceptionRouter` class interacts with the PostgreSQL database to store perception events.
- **Redis**: The `PerceptionRouter` class pushes perception events to a Redis stream for real-time processing or further analysis.
- **Event Types**: The `log_event` method relies on the `perception_event_types` module to validate event types.

### Summary
The `PerceptionRouter` class in `perception_router.py` is a crucial component of the Mythos system, responsible for logging perception events to both a PostgreSQL database and a Redis stream. It ensures that events are validated, stored, and pushed to a stream for real-time processing, integrating seamlessly with the Mythos infrastructure.
