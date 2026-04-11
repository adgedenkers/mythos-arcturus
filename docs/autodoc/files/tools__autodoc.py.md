# tools/autodoc.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 1612

---

### File: tools/autodoc.py

#### Purpose
This file contains the core logic for the Mythos Autodoc Engine, which crawls the Mythos codebase, analyzes files using AST parsing and Ollama LLM calls, builds a Neo4j knowledge graph, and generates comprehensive markdown documentation.

#### Architecture
The file is structured into several classes and utility functions:
- **PythonAnalyzer**: Extracts structural information from Python files using AST parsing.
- **SystemScanner**: Scans for systemd services, PostgreSQL tables, and Neo4j labels.
- **GraphBuilder**: Builds the Neo4j knowledge graph with Autodoc labels.
- **OllamaClient**: Interface to the Ollama LLM for code analysis.
- **StateManager**: Tracks autodoc progress for resumability.
- **AutodocEngine**: Main engine orchestrating the autodoc process.

#### Patterns
- **Factory**: The `AutodocEngine` class uses factory methods to create instances of other classes.
- **Singleton**: The `StateManager` class ensures that only one instance tracks the autodoc progress.
- **Observer**: The `AutodocEngine` class observes the state changes and updates the progress accordingly.

#### Dependencies
- **Imports**: `ast`, `hashlib`, `json`, `os`, `re`, `subprocess`, `sys`, `time`, `traceback`, `requests`, `argparse`, `shutil`
- **External Services**: Ollama LLM (`requests`), PostgreSQL (`psycopg2`), Neo4j (`neo4j`)

#### Interfaces
- **Public Methods**: `AutodocEngine.run`, `AutodocEngine.run_reindex`, `AutodocEngine.run_synthesize`, `AutodocEngine.run_clean`, `AutodocEngine.run_status`
- **Utility Functions**: `file_hash`, `relative_path`, `should_skip_dir`, `should_skip_file`, `is_documentable`, `guess_stream`, `guess_module`, `guess_language`

#### Database
- **Neo4j Labels**: `Autodoc`, `AutodocFile`, `AutodocStream`, `AutodocModule`, `AutodocFunction`, `AutodocClass`, `AutodocEndpoint`, `AutodocDBTable`
- **Neo4j Relationships**: `BELONGS_TO_STREAM`, `OWNED_BY`, `BELONGS_TO`, `DEFINED_IN`, `IMPORTS`, `HANDLED_BY`
- **PostgreSQL Tables**: `datetime`, `pathlib`, `typing`, `Python`, `references`, `information_schema`, `neo4j`, `node`, `Ollama`, `the`, `individual`, `other`, `module`, `files`

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- **Config Files**: `.env` for loading Neo4j credentials if not set in environment variables

#### Key Logic
- **AST Parsing**: `PythonAnalyzer` class parses Python files to extract imports, classes, functions, and database references.
- **LLM Analysis**: `OllamaClient` class sends files to Ollama for semantic analysis.
- **Graph Construction**: `GraphBuilder` class constructs the Neo4j graph with nodes and relationships.
- **Progress Tracking**: `StateManager` class tracks the progress of the autodoc process to allow resumability.

#### Integration Points
- **Ollama**: `OllamaClient` class interacts with the Ollama LLM for code analysis.
- **Neo4j**: `GraphBuilder` class interacts with Neo4j to build the knowledge graph.
- **PostgreSQL**: `SystemScanner` class queries PostgreSQL for Mythos-related tables.
- **File System**: Various utility functions handle file operations and directory traversal.
- **Command Line Interface**: `main` function handles command-line arguments for different autodoc operations.

### Detailed Class Descriptions

#### PythonAnalyzer
- **Purpose**: Extracts structural information from Python files via AST.
- **Methods**: `__init__`, `analyze`, `_walk`, `_find_db_refs`, `_find_fastapi_routes`
- **Key Logic**: Parses Python files to extract imports, classes, functions, and database references.

#### SystemScanner
- **Purpose**: Scans for systemd services, PostgreSQL tables, and Neo4j labels.
- **Methods**: `find_systemd_services`, `find_postgres_tables`, `find_neo4j_labels`
- **Key Logic**: Queries PostgreSQL and Neo4j to find relevant tables and labels.

#### GraphBuilder
- **Purpose**: Builds the Neo4j knowledge graph with Autodoc labels.
- **Methods**: `__init__`, `close`, `clean`, `create_constraints`, `create_streams`, `create_file_node`, `create_module_node`, `link_file_to_module`, `create_function_node`, `create_class_node`, `create_import_relationship`, `_resolve_module_path`, `create_endpoint_node`, `create_service_node`, `create_db_table_node`, `link_file_to_table`, `create_config_node`, `get_stats`
- **Key Logic**: Constructs Neo4j nodes and relationships for files, modules, functions, classes, and database tables.

#### OllamaClient
- **Purpose**: Interface to Ollama for code analysis.
- **Methods**: `__init__`, `generate`, `analyze_file`, `synthesize_module`, `synthesize_stream`, `synthesize_system`
- **Key Logic**: Sends files to Ollama for semantic analysis and synthesizes module, stream, and system-level overviews.

#### StateManager
- **Purpose**: Tracks autodoc progress for resumability.
- **Methods**: `__init__`, `_load`, `save`, `needs_analysis`, `mark_done`, `mark_failed`, `get_progress`
- **Key Logic**: Manages state to allow resuming interrupted autodoc runs.

#### AutodocEngine
- **Purpose**: Main engine orchestrating the autodoc process.
- **Methods**: `__init__`, `_init_graph`, `_ensure_dirs`, `inventory`, `build_graph`, `analyze_files`, `synthesize_modules`, `synthesize_streams`, `synthesize_system`, `generate_index`, `run`, `run_reindex`, `run_synthesize`, `run_clean`, `run_status`
- **Key Logic**: Coordinates the entire autodoc pipeline, including inventory, graph construction, LLM analysis, and documentation generation.

### Utility Functions
- **file_hash**: Computes the SHA-256 hash of a file.
- **relative_path**: Computes the path relative to `MYTHOS_ROOT`.
- **should_skip_dir**: Determines if a directory should be skipped.
- **should_skip_file**: Determines if a file should be skipped.
- **is_documentable**: Determines if a file should be documented.
- **guess_stream**: Guesses which stream a file belongs to based on its path.
- **guess_module**: Guesses which module a file belongs to.
- **guess_language**: Determines the language/type of a file.
