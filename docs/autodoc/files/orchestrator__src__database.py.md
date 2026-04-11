# orchestrator/src/database.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 290

---

### File: orchestrator/src/database.py

#### Purpose
This file provides a database connection manager with connection pooling using `asyncpg` for PostgreSQL operations. It includes methods for executing queries, fetching data, and managing transactions.

#### Architecture
The file contains a single class `Database` that manages database connections and operations. The class provides methods for connecting, disconnecting, and executing various database operations like `execute`, `fetch`, `fetchrow`, `fetchval`, and `transaction`. The class also includes a global instance `db` that can be imported and used across the application.

#### Patterns
- **Singleton Pattern**: The `Database` class is designed to be a singleton, with a global instance `db` that is used throughout the application.
- **Context Manager**: The `connection` and `get_db` methods use the `asynccontextmanager` to manage asynchronous database connections and transactions.

#### Dependencies
- `asyncpg`: For asynchronous PostgreSQL operations.
- `logging`: For logging database operations and errors.
- `sys`, `os`: For managing the import path and system operations.
- `config`: For accessing application settings.

#### Interfaces
- `init_db()`: Initialize the database connection.
- `close_db()`: Close the database connection.
- `get_db()`: Get the database instance for dependency injection in FastAPI.

#### Database
- **Tables**: `orch_models`
- **Operations**: 
  - `execute`: Executes INSERT/UPDATE/DELETE queries.
  - `fetch`: Fetches multiple rows.
  - `fetchrow`: Fetches a single row.
  - `fetchval`: Fetches a single value.
  - `transaction`: Manages transactions.

#### Configuration
- `settings.DATABASE_URL`: URL for the PostgreSQL database.
- `settings.DATABASE_POOL_SIZE`: Size of the connection pool.

#### Key Logic
- **Connection Pooling**: The `Database` class uses `asyncpg.create_pool` to create a connection pool, which is reused for all database operations.
- **Connection Management**: The `connect` and `disconnect` methods manage the lifecycle of the connection pool.
- **Query Execution**: Methods like `execute`, `fetch`, `fetchrow`, and `fetchval` handle different types of database operations, ensuring the connection is properly managed using the `connection` context manager.

#### Integration Points
- **FastAPI**: The `get_db` function is used for dependency injection in FastAPI routes, allowing database access within route handlers.
- **Application Startup/Shutdown**: The `init_db` and `close_db` functions are called during application startup and shutdown to manage the database connection lifecycle.

### Example Usage

```python
from fastapi import Depends
from database import get_db, Database

@app.get("/models")
async def list_models(db: Database = Depends(get_db)):
    models = await db.fetch("SELECT * FROM orch_models")
    return models
```

### Summary
The `database.py` file provides a robust and efficient way to manage database connections and operations in an asynchronous environment. It leverages connection pooling and context managers to ensure optimal performance and resource management. The file integrates seamlessly with FastAPI for dependency injection and manages the database lifecycle during application startup and shutdown.
