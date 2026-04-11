# assistants/db_manager.backup.2026-01-06-1.py

**Language:** python
**Stream:** LOG
**Module:** Chat Assistants
**Lines:** 254

---

### File: `assistants/db_manager.backup.2026-01-06-1.py`

#### Purpose
This file contains the `DatabaseManager` class, which serves as a natural language interface to both Neo4j and PostgreSQL databases. It handles query routing, query generation, execution, and result formatting for Telegram display.

#### Architecture
The `DatabaseManager` class is designed to manage connections to Neo4j and PostgreSQL databases, generate queries from natural language, execute these queries, and format the results for display. The class contains methods for setting user context, routing queries, generating Cypher and SQL queries, executing queries, and formatting results.

#### Patterns
- **Singleton Pattern**: The `DatabaseManager` class can be designed as a singleton to ensure a single instance manages database connections throughout the application.
- **Factory Pattern**: The `generate_cypher` and `generate_sql` methods can be seen as factory methods that produce queries based on natural language input.

#### Dependencies
- **Imports**: `os`, `json`, `psycopg2`, `dotenv`, `neo4j`, `ollama`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `OLLAMA_HOST`, `OLLAMA_MODEL`

#### Interfaces
- **Public Methods**:
  - `set_user(user_info)`: Sets the current user context.
  - `query(natural_language_query)`: Main interface to execute a natural language query and return formatted results.
  - `close()`: Closes database connections.

#### Database
- **PostgreSQL Tables**: `dotenv`, `neo4j`, `ollama`, `natural`, `valid`
- **Neo4j Labels**: `Soul`, `Person`

#### Configuration
- **Environment Variables**: Loaded from `.env` file using `dotenv` for database connection details and Ollama client configuration.

#### Key Logic
1. **Query Routing**: Determines whether to use Neo4j or PostgreSQL based on keywords in the natural language query.
2. **Query Generation**:
   - `generate_cypher`: Converts natural language to Cypher using Ollama.
   - `generate_sql`: Converts natural language to SQL using Ollama.
3. **Query Execution**:
   - `execute_neo4j`: Executes Cypher queries against Neo4j.
   - `execute_postgres`: Executes SQL queries against PostgreSQL.
4. **Result Formatting**: Formats Neo4j results for Telegram display, including handling count queries and extracting key properties from nodes.

#### Integration Points
- **Ollama Client**: Used for generating Cypher and SQL queries from natural language.
- **Neo4j and PostgreSQL Databases**: Directly interacts with these databases for query execution.
- **Telegram**: Results are formatted for display in Telegram.

### Detailed Method Descriptions

1. **`__init__`**:
   - Initializes Neo4j and PostgreSQL connections.
   - Initializes Ollama client for query generation.
   - Loads database schema for Ollama context.

2. **`set_user(user_info)`**:
   - Sets the current user context for the database manager.

3. **`route_query(natural_language_query)`**:
   - Determines the appropriate database (Neo4j or PostgreSQL) based on keywords in the query.

4. **`generate_cypher(natural_language_query)`**:
   - Converts natural language to Cypher using Ollama, following specific rules and patterns.

5. **`format_neo4j_result(result, cypher)`**:
   - Formats Neo4j results for readable Telegram display, handling count queries and extracting key properties.

6. **`execute_neo4j(cypher_query)`**:
   - Executes Cypher queries against Neo4j and returns results as dictionaries.

7. **`execute_postgres(sql_query)`**:
   - Executes SQL queries against PostgreSQL and returns results as dictionaries.

8. **`query(natural_language_query)`**:
   - Main interface to execute a natural language query, route it to the appropriate database, generate and execute the query, and format the results.

9. **`generate_sql(natural_language_query)`**:
   - Converts natural language to SQL using Ollama.

10. **`close()`**:
    - Closes Neo4j and PostgreSQL connections.

This class serves as a central hub for database interactions, ensuring that natural language queries are correctly translated and executed, and results are formatted for user-friendly display.
