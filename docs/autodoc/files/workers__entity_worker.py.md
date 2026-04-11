# workers/entity_worker.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 176

---

### Documentation for `workers/entity_worker.py`

#### Purpose
This file is responsible for resolving entities mentioned in messages to their canonical forms, creating or updating these entities in Neo4j, and storing mentions of these entities in TimescaleDB.

#### Architecture
The file consists of several functions that handle different aspects of entity resolution and storage:
- `get_db`: Establishes a connection to the PostgreSQL database.
- `get_neo4j`: Establishes a connection to the Neo4j graph database.
- `resolve_entity`: Resolves an entity name to its canonical form using a predefined mapping.
- `create_or_update_entity`: Creates or updates an entity in Neo4j.
- `store_entity_mention`: Stores an entity mention in TimescaleDB.
- `process_entity`: The main entry point that orchestrates the resolution and storage process.

#### Patterns
- **Singleton Pattern**: The `get_db` and `get_neo4j` functions can be considered as providing singleton instances of database connections.
- **Factory Method Pattern**: The `resolve_entity` function acts as a factory method to produce canonical entity forms.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `neo4j`, `dotenv`, `typing`, `datetime`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

#### Interfaces
- **Exposed Functions**: `process_entity`, which is the main entry point for entity resolution and storage.
- **Input**: `payload` (a dictionary containing message details and entities).
- **Output**: A dictionary indicating the status of the entity resolution process.

#### Database
- **PostgreSQL Tables**: `entity_mention_timeseries`
- **Neo4j Labels**: `Person`, `Place`, `Concept`, `Symbol`, `Entity`

#### Configuration
- **Environment Variables**: Loaded from `/opt/mythos/.env` for database and Neo4j connection details.
- **Known Aliases**: Defined in `KNOWN_ALIASES` dictionary for entity name resolution.

#### Key Logic
- **Entity Resolution**: Uses a predefined mapping (`KNOWN_ALIASES`) to resolve entity names to canonical forms.
- **Entity Creation/Update**: Uses Cypher queries to create or update entities in Neo4j, incrementing mention counts and updating timestamps.
- **Entity Mention Storage**: Inserts entity mentions into `entity_mention_timeseries` table in TimescaleDB.

#### Integration Points
- **Message Processing**: Integrates with the message processing pipeline to receive entity mentions.
- **Database Connections**: Connects to PostgreSQL and Neo4j databases to store and retrieve entity information.
- **Logging**: Uses the `logging` module to log the resolution process and any errors encountered.

### Detailed Function Descriptions

1. **`get_db`**
   - **Purpose**: Establishes a connection to the PostgreSQL database.
   - **Dependencies**: `os`, `psycopg2`
   - **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

2. **`get_neo4j`**
   - **Purpose**: Establishes a connection to the Neo4j graph database.
   - **Dependencies**: `os`, `neo4j`
   - **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

3. **`resolve_entity`**
   - **Purpose**: Resolves an entity name to its canonical form using a predefined mapping.
   - **Parameters**: `name` (entity name), `entity_type` (entity type)
   - **Returns**: Canonical form of the entity name.

4. **`create_or_update_entity`**
   - **Purpose**: Creates or updates an entity in Neo4j.
   - **Parameters**: `driver` (Neo4j driver), `canonical_id` (canonical ID of the entity), `name` (entity name), `entity_type` (entity type)
   - **Returns**: Canonical ID of the entity.

5. **`store_entity_mention`**
   - **Purpose**: Stores an entity mention in TimescaleDB.
   - **Parameters**: `user_uuid`, `conversation_id`, `message_id`, `canonical_id`, `name`, `entity_type`
   - **Returns**: None

6. **`process_entity`**
   - **Purpose**: Main entry point for entity resolution and storage.
   - **Parameters**: `payload` (dictionary containing message details and entities)
   - **Returns**: Dictionary indicating the status of the entity resolution process.

### Example Usage
```python
payload = {
    "message_id": 12345,
    "user_uuid": "user-123",
    "conversation_id": "conv-456",
    "entities": {
        "person": ["Rebecca", "Ka"],
        "concept": ["Merovingian"]
    }
}

result = process_entity(payload)
print(result)
```

This example demonstrates how the `process_entity` function processes a message payload containing entities, resolving them to canonical forms, updating Neo4j, and storing mentions in TimescaleDB.
