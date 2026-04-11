# core/node_executor.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 461

---

### File: core/node_executor.py

#### Purpose
The `NodeExecutor` class is responsible for executing research tasks for a single grid node within the Mythos system. It handles data retrieval from various sources including Neo4j, PostgreSQL, and potentially the web, based on the node's domain and specified query hints.

#### Architecture
The `NodeExecutor` class contains methods for establishing database connections, executing queries, and managing the execution of research tasks. The class is designed to be instantiated and used to execute research tasks for a specific node.

- **Classes**: `NodeExecutor`
  - **Methods**: 
    - `__init__`: Initializes the class instance.
    - `_get_pg`: Establishes a PostgreSQL connection.
    - `_get_neo4j`: Establishes a Neo4j connection.
    - `_query_neo4j`: Executes a Neo4j query based on a query hint.
    - `_query_postgres`: Executes PostgreSQL queries based on a query hint and specified sources.
    - `_build_pg_queries`: Builds specific PostgreSQL queries for a given node.
    - `_query_web`: Placeholder for web queries (not yet implemented).
    - `execute_node`: Executes research for a single node.
    - `execute_plan`: Executes research for a list of nodes.
    - `close`: Closes database connections.

#### Patterns
- **Singleton Pattern**: The `_get_pg` and `_get_neo4j` methods ensure that only one connection is established per database, adhering to the singleton pattern.
- **Factory Method Pattern**: The `_build_pg_queries` method acts as a factory method to generate specific queries based on the node name.

#### Dependencies
- **Imports**: `os`, `sys`, `json`, `logging`, `typing`, `datetime`, `dotenv`, `psycopg2`, `neo4j`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

#### Interfaces
- **Public Methods**:
  - `execute_node(node_spec)`: Executes research for a single node.
  - `execute_plan(research_plan)`: Executes research for a list of nodes.
  - `close()`: Closes database connections.

#### Database
- **PostgreSQL Tables**: `accounts`, `recurring_bills`, `transactions`, `routines`, `checkin_log`, `calendar_events`, `idea_backlog`, `life_events`, `chat_messages`, `emotional_state_timeseries`, `people`, `astro_natal_charts`
- **Neo4j Labels**: `Person`, `Soul`, `OntologyTerm`, `Memory`, `Knowledge`, `Entity`

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` for PostgreSQL connection.
  - `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` for Neo4j connection.

#### Key Logic
- **_query_neo4j**: Executes a Neo4j query to search for relevant nodes based on the query hint.
- **_query_postgres**: Executes PostgreSQL queries to retrieve data from relevant tables based on the node's domain and specified sources.
- **_build_pg_queries**: Constructs specific PostgreSQL queries for each node based on its domain.
- **execute_node**: Coordinates the execution of research tasks for a single node, querying Neo4j and PostgreSQL, and potentially the web.
- **execute_plan**: Coordinates the execution of research tasks for a list of nodes, calling `execute_node` for each node.

#### Integration Points
- **Research Router**: The `execute_plan` method receives a research plan from the `research_router.route_message()` function.
- **Web Search**: Placeholder for web search integration using SearXNG or similar (currently a stub).
- **Data Convergence**: The results from `execute_node` and `execute_plan` are structured and intended to be merged into a final context package by the convergence subsystem.

This file is a critical component of the Mythos system, enabling the retrieval and integration of data from various sources to support research tasks for each grid node.
