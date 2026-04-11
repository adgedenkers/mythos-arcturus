# core/knowledge_map_builder.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 254

---

### File: core/knowledge_map_builder.py

#### Purpose
This file is responsible for rebuilding the dynamic sections of the `KNOWLEDGE_MAP.md` document from the PostgreSQL database. It also listens for database changes and triggers a rebuild when necessary.

#### Architecture
The file contains several functions that handle different aspects of the knowledge map rebuilding process:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `_build_accounts_section`, `_build_bills_section`, `_build_routines_section`: Generate specific sections of the knowledge map from the database.
- `rebuild_knowledge_map`: Combines static and dynamic sections to produce the full document and writes it to disk.
- `listen_and_rebuild`: Listens for `pg_notify` signals and triggers a rebuild of the knowledge map.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton as it ensures a single connection to the database.
- **Observer Pattern**: The `listen_and_rebuild` function acts as an observer, listening for database changes and triggering a rebuild.

#### Dependencies
- `os`: Used for environment variable access.
- `logging`: For logging messages.
- `psycopg2`: PostgreSQL database adapter for Python.
- `select`: For monitoring I/O readiness.
- `redis`: For Redis integration.
- `sys`: For command-line argument handling.
- `dotenv`: For loading environment variables from a `.env` file.

#### Interfaces
- `rebuild_knowledge_map`: Exposes a function to rebuild the knowledge map and return the full document text.
- `listen_and_rebuild`: Exposes a function to start a long-lived service that listens for database changes and triggers rebuilds.

#### Database
- **PostgreSQL Tables**: The file interacts with the following tables:
  - `accounts`: Used to generate the accounts section.
  - `recurring_bills`: Used to generate the bills section.
  - `routines`: Used to generate the routines section.
- **pg_notify**: Used to listen for database changes.

#### Configuration
- **Environment Variables**: The file uses environment variables for database connection details (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`).
- **Dotenv File**: The `.env` file located at `/opt/mythos/.env` is loaded to provide environment variables.

#### Key Logic
- **Rebuilding the Knowledge Map**: The `rebuild_knowledge_map` function combines static and dynamic sections to produce the full document. It fetches data from the database, formats it into Markdown, and writes the document to disk.
- **Listening for Changes**: The `listen_and_rebuild` function sets up a listener for `pg_notify` signals and triggers a rebuild when changes are detected. It also integrates with Redis to notify other services of the rebuild.

#### Integration Points
- **Redis**: The `listen_and_rebuild` function uses Redis to publish notifications when the knowledge map is rebuilt.
- **PostgreSQL**: The file interacts with PostgreSQL to fetch data and listen for changes.
- **File System**: The rebuilt knowledge map is written to the file system at `/opt/mythos/docs/KNOWLEDGE_MAP.md`.

### Detailed Analysis

#### `_get_conn`
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Dependencies**: `psycopg2`, `os` (for environment variables).

#### `_build_accounts_section`
- **Purpose**: Generates the accounts section of the knowledge map from the `accounts` table.
- **Dependencies**: `psycopg2` (cursor).

#### `_build_bills_section`
- **Purpose**: Generates the bills section of the knowledge map from the `recurring_bills` table.
- **Dependencies**: `psycopg2` (cursor).

#### `_build_routines_section`
- **Purpose**: Generates the routines section of the knowledge map from the `routines` table.
- **Dependencies**: `psycopg2` (cursor).

#### `rebuild_knowledge_map`
- **Purpose**: Combines static and dynamic sections to produce the full knowledge map document and writes it to disk.
- **Dependencies**: `psycopg2`, `datetime`, `os`.

#### `listen_and_rebuild`
- **Purpose**: Listens for `pg_notify` signals and triggers a rebuild of the knowledge map.
- **Dependencies**: `psycopg2`, `select`, `redis`, `logging`.

### Example Usage
To manually rebuild the knowledge map:
```bash
python3 core/knowledge_map_builder.py
```

To start the listener service:
```bash
python3 core/knowledge_map_builder.py listen
```

This file is crucial for maintaining the up-to-date state of the `KNOWLEDGE_MAP.md` document, ensuring that all dynamic sections are synchronized with the database.
