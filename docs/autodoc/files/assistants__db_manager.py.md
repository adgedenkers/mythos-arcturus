# assistants/db_manager.py

**Language:** python
**Stream:** LOG
**Module:** Chat Assistants
**Lines:** 259

---

### Documentation for `assistants/db_manager.py`

#### Purpose
The `DatabaseManager` class in `assistants/db_manager.py` provides a natural language interface to interact with both Neo4j and PostgreSQL databases. It handles query routing, query generation, execution, and result formatting.

#### Architecture
The `DatabaseManager` class contains methods for initializing database connections, setting user context, routing queries, generating and executing queries, and formatting results. The class is designed to manage connections to Neo4j and PostgreSQL, and it uses the Ollama client to generate SQL and Cypher queries from natural language input.

#### Patterns
- **Singleton Pattern**: The `DatabaseManager` class can be designed as a singleton to ensure a single instance manages the database connections.
- **Factory Method**: The `generate_cypher` and `generate_sql` methods can be seen as factory methods that produce specific query types based on input.

#### Dependencies
- **Imports**: `os`, `json`, `psycopg2`, `dotenv`, `neo4j`, `ollama`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `OLLAMA_HOST`, `OLLAMA_MODEL`
- **Files**: `~/main-vault/systems/arcturus/prompts/db_mode_prompt.md`

#### Interfaces
- **Public Methods**:
  - `set_user(user_info)`: Sets the current user context.
  - `route_query(natural_language_query)`: Determines which database to use based on the query content.
  - `generate_cypher(natural_language_query, recent_context=None, historical_context=None)`: Generates a Cypher query from natural language input.
  - `format_neo4j_result(result, cypher)`: Formats Neo4j results for readable display.
  - `execute_neo4j(cypher_query)`: Executes a Cypher query against Neo4j.
  - `execute_postgres(sql_query)`: Executes an SQL query against PostgreSQL.
  - `query(natural_language_query, recent_context=None, historical_context=None)`: Main query interface with conversation context.
  - `generate_sql(natural_language_query, recent_context=None, historical_context=None)`: Generates an SQL query from natural language input.
  - `close()`: Cleans up database connections.

#### Database
- **PostgreSQL Tables**: `users`, `chat_messages`
- **Neo4j Labels**: `Person`, `Soul`, `Incarnation`

#### Configuration
- **Environment Variables**: Configured in `/opt/mythos/.env`
- **System Prompt**: Loaded from `~/main-vault/systems/arcturus/prompts/db_mode_prompt.md`

#### Key Logic
- **Query Routing**: Determines whether to use Neo4j or PostgreSQL based on keywords in the natural language query.
- **Query Generation**: Uses the Ollama client to generate SQL and Cypher queries from natural language input, incorporating context from recent and historical conversations.
- **Result Formatting**: Formats Neo4j results for readable display, especially for Telegram.

#### Integration Points
- **Ollama Client**: Used to generate SQL and Cypher queries from natural language input.
- **Neo4j Driver**: Manages connections and query execution for Neo4j.
- **PostgreSQL Connection**: Manages connections and query execution for PostgreSQL.
- **User Context**: Manages and uses user context for query generation and execution.

### Detailed Breakdown of Methods

- **`__init__`**: Initializes the `DatabaseManager` with connections to Neo4j and PostgreSQL, and sets up the Ollama client. Loads the system prompt from a file.
- **`set_user`**: Sets the current user context.
- **`route_query`**: Determines which database to use based on keywords in the natural language query.
- **`generate_cypher`**: Generates a Cypher query from natural language input, incorporating recent and historical context.
- **`format_neo4j_result`**: Formats Neo4j results for readable display, especially for Telegram.
- **`execute_neo4j`**: Executes a Cypher query against Neo4j and returns the results.
- **`execute_postgres`**: Executes an SQL query against PostgreSQL and returns the results.
- **`query`**: Main query interface that routes, generates, executes, and formats results based on the natural language query.
- **`generate_sql`**: Generates an SQL query from natural language input, incorporating recent and historical context.
- **`close`**: Cleans up database connections.
