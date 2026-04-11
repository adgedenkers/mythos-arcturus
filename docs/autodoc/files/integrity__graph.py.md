# integrity/graph.py

**Language:** python
**Stream:** SYS
**Module:** Integrity Scanner
**Lines:** 70

---

### File: integrity/graph.py

#### Purpose
This file provides utility functions for interacting with Neo4j, including obtaining a driver instance, ensuring database constraints and indexes, and running both read and write Cypher queries.

#### Architecture
The file consists of four top-level functions:
1. `get_driver`: Returns a Neo4j driver instance.
2. `ensure_constraints`: Ensures that necessary constraints and indexes are created for specific node types.
3. `run_query`: Executes a read Cypher query and returns the results.
4. `run_write`: Executes a write Cypher query.

The functions are designed to be stateless and rely on the Neo4j driver for session management.

#### Patterns
- **Singleton Pattern**: The `get_driver` function can be considered a singleton as it returns a single instance of the Neo4j driver.
- **Factory Method Pattern**: The `run_query` and `run_write` functions can be seen as factory methods that create and execute Cypher queries.

#### Dependencies
- **Imports**: 
  - `os`: Used to load environment variables.
  - `neo4j.GraphDatabase`: Used to create a Neo4j driver instance.
  - `dotenv.load_dotenv`: Used to load environment variables from a `.env` file.
- **Environment Variables**: 
  - `NEO4J_URI`: URI for the Neo4j server.
  - `NEO4J_USER`: Username for Neo4j.
  - `NEO4J_PASSWORD`: Password for Neo4j.

#### Interfaces
- **Public Functions**:
  - `get_driver()`: Returns a Neo4j driver instance.
  - `ensure_constraints(driver)`: Ensures constraints and indexes are created.
  - `run_query(driver, cypher, parameters=None, **kwargs)`: Executes a read Cypher query.
  - `run_write(driver, cypher, parameters=None, **kwargs)`: Executes a write Cypher query.

#### Database
- **Neo4j**:
  - **Constraints**: 
    - `file_path_unique` for `IntegrityFile` nodes.
    - `func_id_unique` for `IntegrityFunction` nodes.
    - `dir_path_unique` for `IntegrityDirectory` nodes.
    - `table_name_unique` for `IntegrityTable` nodes.
    - `column_id_unique` for `IntegrityColumn` nodes.
  - **Indexes**: 
    - `file_status_idx` for `IntegrityFile` nodes.
    - `file_extension_idx` for `IntegrityFile` nodes.
    - `func_name_idx` for `IntegrityFunction` nodes.
    - `dir_path_idx` for `IntegrityDirectory` nodes.

#### Configuration
- **Environment Variables**:
  - `.env` file located at `/opt/mythos/.env` is loaded to fetch Neo4j credentials.

#### Key Logic
- **Constraint Creation**: The `ensure_constraints` function ensures that necessary constraints and indexes are created for specific node types, using `CREATE ... IF NOT EXISTS` to avoid errors if they already exist.
- **Query Execution**: The `run_query` and `run_write` functions handle the execution of Cypher queries, with `run_query` returning results and `run_write` performing write operations.

#### Integration Points
- **Neo4j Driver**: The functions in this file interact directly with the Neo4j driver to manage sessions and execute queries.
- **Mythos System**: This file is part of the Mythos system and is likely used by other subsystems to interact with the Neo4j database for integrity checks and management.

This file serves as a crucial component for ensuring data integrity and efficient querying within the Neo4j database used by the Mythos system.
