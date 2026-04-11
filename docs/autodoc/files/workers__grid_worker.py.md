# workers/grid_worker.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 492

---

### File: workers/grid_worker.py

#### Purpose
This file contains functions to perform grid analysis on message exchanges using an LLM, store the results in PostgreSQL and Neo4j, and process the grid analysis worker tasks.

#### Architecture
The file consists of several top-level functions:
- `get_db`: Establishes a connection to the PostgreSQL database.
- `get_neo4j_driver`: Establishes a connection to the Neo4j database.
- `analyze_with_llm`: Analyzes a conversation exchange using an LLM to determine the activation of consciousness domains.
- `store_grid_results_postgres`: Stores the grid analysis results in PostgreSQL.
- `store_grid_results_neo4j`: Stores the grid analysis results in Neo4j.
- `process_grid_analysis`: Main entry point for processing grid analysis tasks.

#### Patterns
- **Singleton Pattern**: The `get_db` and `get_neo4j_driver` functions can be considered as implementing a singleton pattern to ensure a single connection to the database.
- **Factory Method Pattern**: The `analyze_with_llm` function can be seen as a factory method that generates the analysis results based on the input messages.

#### Dependencies
- `os`: For environment variable handling.
- `json`: For JSON parsing.
- `logging`: For logging.
- `requests`: For making HTTP requests to the LLM.
- `psycopg2`: For PostgreSQL database operations.
- `sys`: For system-related operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `neo4j`: For Neo4j database operations.
- `grid_manifest`: For manifest writing (optional).
- `perception.engine`: For perception engine operations (optional).

#### Interfaces
- `get_db()`: Returns a PostgreSQL database connection.
- `get_neo4j_driver()`: Returns a Neo4j driver connection.
- `analyze_with_llm(user_message: str, assistant_response: str) -> Optional[Dict[str, Any]]`: Analyzes the conversation exchange and returns the analysis results.
- `store_grid_results_postgres(exchange_id: str, user_uuid: str, conversation_id: str, results: Dict[str, Any]) -> None`: Stores the grid analysis results in PostgreSQL.
- `store_grid_results_neo4j(exchange_id: str, user_uuid: str, conversation_id: str, user_message: str, assistant_response: str, model_used: str, results: Dict[str, Any]) -> None`: Stores the grid analysis results in Neo4j.
- `process_grid_analysis(payload: Dict[str, Any]) -> None`: Processes the grid analysis tasks based on the provided payload.

#### Database
- **PostgreSQL Tables**: `grid_activation_timeseries`, `emotional_state_timeseries`, `Exchange`
- **Neo4j Labels**: `Exchange`, `GridNode`, `Entity`, `Theme`

#### Configuration
- Environment variables: `OLLAMA_HOST`, `OLLAMA_MODEL`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `.env` file: Loaded using `dotenv.load_dotenv`

#### Key Logic
1. **LLM Analysis**: The `analyze_with_llm` function constructs a prompt for the LLM to analyze the conversation exchange and returns the analysis results in JSON format.
2. **PostgreSQL Storage**: The `store_grid_results_postgres` function stores the grid analysis results in the `grid_activation_timeseries` and `emotional_state_timeseries` tables.
3. **Neo4j Storage**: The `store_grid_results_neo4j` function creates nodes and relationships in Neo4j to represent the grid analysis results, including `Exchange`, `GridNode`, `Entity`, and `Theme` nodes.

#### Integration Points
- **LLM Integration**: The `analyze_with_llm` function interacts with the LLM to perform the grid analysis.
- **PostgreSQL Integration**: The `store_grid_results_postgres` function integrates with PostgreSQL to store the analysis results.
- **Neo4j Integration**: The `store_grid_results_neo4j` function integrates with Neo4j to store the analysis results.
- **Worker Integration**: The `process_grid_analysis` function is the main entry point for the grid analysis worker, which processes the incoming payloads and calls the necessary functions to perform the analysis and store the results.
