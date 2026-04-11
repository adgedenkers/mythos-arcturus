# assistants/db_manager.backup.2026-01-06-2.py

**Language:** python
**Stream:** LOG
**Module:** Chat Assistants
**Lines:** 221

---

### File: `assistants/db_manager.backup.2026-01-06-2.py`

#### Purpose
This file contains the `DatabaseManager` class, which serves as a natural language interface to both Neo4j and PostgreSQL databases. It handles query routing, query generation, execution, and result formatting.

#### Architecture
The `DatabaseManager` class is the primary component of this file. It contains methods for initializing database connections, setting user context, routing queries, generating and executing queries, and formatting results. The class follows a straightforward procedural design with no inheritance or complex patterns.

#### Patterns
- **Singleton Pattern**: The `DatabaseManager` class can be designed as a singleton to ensure only one instance manages the database connections.
- **Factory Method**: The `generate_cypher` and `generate_sql` methods can be seen as factory methods for generating queries based on natural language input.

#### Dependencies
- **Imports**: `os`, `json`, `psycopg2`, `dotenv`, `neo4j`, `ollama`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `OLLAMA_HOST`, `OLLAMA_MODEL`

#### Interfaces
- **Public Methods**:
  - `set_user(user_info)`: Sets the current user context.
  - `route_query(natural_language_query)`: Determines which database to use based on the query content.
  - `generate_cypher(natural_language_query)`: Generates a Cypher query from natural language.
  - `format_neo4j_result(result, cypher)`: Formats Neo4j results for readable display.
  - `execute_neo4j(cypher_query)`: Executes a Cypher query against Neo4j.
  - `execute_postgres(sql_query)`: Executes an SQL query against PostgreSQL.
  - `query(natural_language_query)`: Main query interface that returns a formatted string for Telegram.
  - `generate_sql(natural_language_query)`: Generates an SQL query from natural language.
  - `close()`: Cleans up database connections.

#### Database
- **PostgreSQL Tables**: `users`, `chat_messages`
- **Neo4j Labels**: `Person`, `Soul`, `Lifetime`

#### Configuration
- **Environment Variables**: Configured in `/opt/mythos/.env`
- **System Prompt**: Loaded from `~/main-vault/systems/arcturus/prompts/db_mode_prompt.md`

#### Key Logic
- **Query Routing**: Determines whether to use Neo4j or PostgreSQL based on keywords in the natural language query.
- **Query Generation**: Uses the Ollama client to generate Cypher and SQL queries from natural language.
- **Result Formatting**: Formats Neo4j results for Telegram display, handling different node types and properties.

#### Integration Points
- **Ollama Client**: Used for generating Cypher and SQL queries from natural language.
- **Neo4j Driver**: Manages connections and query execution for Neo4j.
- **PostgreSQL Connection**: Manages connections and query execution for PostgreSQL.
- **Telegram Interface**: The `query` method returns a formatted string suitable for Telegram display.

### Detailed Method Descriptions

1. **`__init__`**:
   - Initializes the `DatabaseManager` class by setting up connections to Neo4j and PostgreSQL, loading the system prompt, and initializing the Ollama client.

2. **`set_user(user_info)`**:
   - Sets the current user context for the database manager.

3. **`route_query(natural_language_query)`**:
   - Determines the appropriate database (Neo4j or PostgreSQL) to use based on keywords in the natural language query.

4. **`generate_cypher(natural_language_query)`**:
   - Generates a Cypher query from natural language using the Ollama client and the system prompt.

5. **`format_neo4j_result(result, cypher)`**:
   - Formats Neo4j results for readable display, handling different node types and properties.

6. **`execute_neo4j(cypher_query)`**:
   - Executes a Cypher query against Neo4j and returns the results.

7. **`execute_postgres(sql_query)`**:
   - Executes an SQL query against PostgreSQL and returns the results.

8. **`query(natural_language_query)`**:
   - Main query interface that routes the query to the appropriate database, generates the query, executes it, and formats the results for Telegram display.

9. **`generate_sql(natural_language_query)`**:
   - Generates an SQL query from natural language using the Ollama client and a predefined prompt.

10. **`close()`**:
    - Cleans up database connections by closing the Neo4j driver and PostgreSQL connection.

This file serves as a central hub for managing database interactions in the Mythos system, providing a unified interface for querying both Neo4j and PostgreSQL databases.
