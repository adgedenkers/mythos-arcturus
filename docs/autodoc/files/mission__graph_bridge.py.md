# mission/graph_bridge.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 404

---

### File: mission/graph_bridge.py

#### Purpose
The `GraphBridge` class provides a high-level interface for querying the Neo4j graph database used by the Mythos system. It encapsulates various functions to retrieve information about files, directories, tables, and services within the Mythos codebase. Additionally, it supports exporting a comprehensive snapshot of the codebase structure.

#### Architecture
The `GraphBridge` class is designed to interact with the Neo4j database through the `neo4j.GraphDatabase.driver` interface. It includes methods for executing Cypher queries and retrieving results in a structured format. The class supports context management (`__enter__` and `__exit__`) to ensure proper resource management.

#### Patterns
- **Singleton Pattern**: Although not explicitly implemented, the `GraphBridge` class can be used as a singleton to manage a single connection to the Neo4j database throughout the application.
- **Context Manager**: The class implements the `__enter__` and `__exit__` methods to allow the use of the `with` statement for managing the database connection.

#### Dependencies
- **Standard Libraries**: `json`, `os`, `subprocess`, `sys`
- **Third-party Libraries**: `neo4j`, `pathlib`, `typing`
- **Internal Functions**: `_load_credentials`

#### Interfaces
- **Public Methods**: 
  - `__init__`: Initialize the `GraphBridge` instance and establish a connection to the Neo4j database.
  - `close`: Close the database connection.
  - `query`: Execute a Cypher query and return results as a list of dictionaries.
  - `functions_in_file`: Retrieve all function names defined in a specific file.
  - `file_dependencies`: Retrieve all files that a given file imports.
  - `file_dependents`: Retrieve all files that import a given file.
  - `files_in_directory`: Retrieve all files in a directory with their metadata.
  - `file_info`: Retrieve full metadata for a specific file.
  - `files_calling_function`: Find files that contain a specific function.
  - `recently_modified_files`: Retrieve the most recently modified files.
  - `table_columns`: Retrieve columns for a specific Postgres table from the graph.
  - `all_tables`: Retrieve all table names.
  - `tables_for_service`: Find which tables a service touches.
  - `all_services`: Retrieve all registered services.
  - `service_files`: Retrieve files associated with a service.
  - `search_functions`: Search for functions by name pattern.
  - `search_files`: Search for files by path pattern.
  - `directory_tree`: Retrieve directory tree starting from a root.
  - `export_snapshot`: Export a structural snapshot for Claude to consume.

#### Database
- **Neo4j Labels**: `IntegrityFile`, `IntegrityFunction`, `IntegrityDirectory`, `IntegrityTable`, `IntegrityColumn`, `IntegrityService`
- **Neo4j Relationships**: `CONTAINS`, `IMPORTS`, `HAS_COLUMN`, `RUNS`, `REFERENCES`

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` loaded from `/opt/mythos/.env`

#### Key Logic
- **Query Execution**: The `query` method executes Cypher queries and processes the results into a list of dictionaries.
- **File Metadata Retrieval**: Methods like `functions_in_file`, `file_dependencies`, `file_dependents`, `file_info`, and `files_calling_function` retrieve metadata about files and their relationships.
- **Table and Service Queries**: Methods like `table_columns`, `all_tables`, `tables_for_service`, `all_services`, and `service_files` retrieve information about tables and services.
- **Search and Snapshot**: Methods like `search_functions`, `search_files`, `directory_tree`, and `export_snapshot` provide search capabilities and export a comprehensive snapshot of the codebase.

#### Integration Points
- **Mission Executor**: The `GraphBridge` class is used by the mission executor to gather structural context about the Mythos codebase.
- **CLI Usage**: The file can be used as a CLI tool to perform various graph queries.
- **Mythos Codebase**: The class interacts with the Neo4j graph database to retrieve and manipulate metadata about the Mythos codebase.

### Example Usage
```python
from graph_bridge import GraphBridge

gb = GraphBridge()
funcs = gb.functions_in_file('/opt/mythos/assistants/chat_assistant.py')
print(funcs)
```

This example initializes the `GraphBridge` instance and retrieves all function names defined in the specified file.
