# skills/data/idea_backlog_manager.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 80

---

### Purpose
The `idea_backlog_manager.py` file implements the `IdeaBacklogManagerSkill` class, which is responsible for managing and providing information about the idea backlog and pending ideas in the Mythos system. This skill retrieves data from PostgreSQL tables `idea_inbox` and `idea_backlog` to generate a summary of the idea pipeline status.

### Architecture
The file contains:
- A top-level function `_get_conn()` for establishing a PostgreSQL database connection.
- A top-level asynchronous function `execute()` that is the entry point for the skill execution.
- A class `IdeaBacklogManagerSkill` that inherits from `SkillBase` and implements the `execute` method to handle the skill's logic.

### Patterns
- **Singleton Pattern**: The `_get_conn()` function can be considered a singleton pattern as it provides a single point of connection to the PostgreSQL database.
- **Factory Method Pattern**: The `execute` method can be seen as a factory method that constructs and returns a `SkillResponse` object.

### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `RealDictCursor` from `psycopg2.extras`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

### Interfaces
- **Public Methods**: `execute` method in `IdeaBacklogManagerSkill` class.
- **Exposed Objects**: `SkillResponse` object returned by the `execute` method.

### Database
- **Tables**: `idea_inbox`, `idea_backlog`.
- **Operations**: 
  - `SELECT COUNT(*) as cnt FROM idea_inbox WHERE disposition = 'pending'`
  - `SELECT stream, COUNT(*) as total, SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as done, SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress, SUM(CASE WHEN status = 'backlog' THEN 1 ELSE 0 END) as backlog_count FROM idea_backlog GROUP BY stream ORDER BY stream`

### Configuration
- **Config Files**: `.env` file loaded using `load_dotenv('/opt/mythos/.env')`.
- **Environment Variables**: PostgreSQL connection details (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`).

### Key Logic
- **Pending Count**: Retrieves the count of ideas in the `idea_inbox` table with a `disposition` of 'pending'.
- **Backlog by Stream**: Aggregates the status of ideas in the `idea_backlog` table by stream, categorizing them into 'done', 'in_progress', and 'backlog'.
- **Summary Construction**: Constructs a summary string that includes the pending count and the breakdown of backlog items by stream.

### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill system.
- **Database Connection**: Uses `_get_conn()` to connect to the PostgreSQL database.
- **SkillRequest and SkillResponse**: Utilizes `SkillRequest` and `SkillResponse` objects for request handling and response construction.

### Detailed Analysis

#### `_get_conn()` Function
- **Purpose**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **Implementation**: Uses `psycopg2.connect()` with `RealDictCursor` to return a dictionary cursor.

#### `IdeaBacklogManagerSkill` Class
- **Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.
- **Methods**: `execute` method that handles the skill's logic.

#### `execute` Method
- **Purpose**: Executes the skill logic to retrieve and summarize the idea pipeline status.
- **Implementation**:
  - Establishes a database connection using `_get_conn()`.
  - Executes SQL queries to get the pending count and backlog status by stream.
  - Constructs a summary string and a `SkillResponse` object with the retrieved data.
  - Handles exceptions and ensures the database connection is closed.

This file is a critical component of the Mythos system, providing insights into the idea pipeline and managing the backlog efficiently.
