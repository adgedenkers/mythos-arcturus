# integrity/function_extractor.py

**Language:** python
**Stream:** SYS
**Module:** Integrity Scanner
**Lines:** 262

---

### Documentation for `integrity/function_extractor.py`

#### Purpose
This file is responsible for parsing Python files using the `ast` module to extract function definitions, imports, and call relationships. It then merges these extracted elements into Neo4j with appropriate relationships.

#### Architecture
The file consists of several top-level functions:
- `extract_functions`: The main function that orchestrates the extraction process.
- `_process_file_ast`: Processes the AST of a single file and returns local statistics.
- `_merge_function`: Merges a function node into Neo4j and links it to its file.
- `_extract_imports`: Extracts import statements from an AST.
- `_merge_import`: Records an import relationship and attempts to resolve it to a local file.
- `_resolve_import_path`: Converts a Python module path to possible file paths.

#### Patterns
- **Helper Functions**: The use of helper functions like `_process_file_ast`, `_merge_function`, `_extract_imports`, `_merge_import`, and `_resolve_import_path` to modularize the logic.
- **Singleton Pattern**: The `driver` argument in functions like `extract_functions` allows for reusing a single Neo4j driver instance, which can be considered a form of singleton pattern.

#### Dependencies
- **Imports**: `ast`, `logging`, `os`, `datetime`, `integrity.graph` (for `get_driver`, `run_write`, `run_query`).
- **External Libraries**: `neo4j` (for database operations).

#### Interfaces
- **Public Functions**:
  - `extract_functions(driver=None) -> dict`: Main function that returns extraction statistics.
- **Private Functions**:
  - `_process_file_ast(driver, filepath, tree, scan_timestamp) -> dict`: Processes the AST of a single file.
  - `_merge_function(driver, filepath, node, scan_timestamp)`: Merges a function node into Neo4j.
  - `_extract_imports(tree) -> list`: Extracts import statements from an AST.
  - `_merge_import(driver, filepath, imp, scan_timestamp)`: Records an import relationship.
  - `_resolve_import_path(module) -> list`: Resolves a module path to possible file paths.

#### Database
- **Neo4j Labels**:
  - `IntegrityFile`: Represents a Python file.
  - `IntegrityFunction`: Represents a function definition within a file.
- **Neo4j Relationships**:
  - `CONTAINS`: Links a file to its functions.
  - `IMPORTS`: Links a file to its imported files.

#### Configuration
- **Environment Variables**:
  - `MYTHOS_ROOT`: Specifies the root directory of the Mythos system (default is `/opt/mythos`).

#### Key Logic
- **Function Extraction**: The `extract_functions` function retrieves all active Python files from Neo4j, parses each file using the `ast` module, and extracts function definitions and imports.
- **AST Processing**: The `_process_file_ast` function walks through the AST to find function definitions and imports.
- **Neo4j Operations**: Functions like `_merge_function` and `_merge_import` use Cypher queries to merge nodes and relationships into Neo4j.
- **Import Resolution**: The `_resolve_import_path` function converts module paths to possible file paths and checks if they exist in the Neo4j graph.

#### Integration Points
- **Neo4j Integration**: The file interacts with Neo4j to retrieve files, merge function nodes, and record import relationships.
- **Integrity Scanner**: This module is part of the Integrity Scanner subsystem, which aims to maintain a self-knowledge graph of the Mythos system.

This file is a critical component of the Mythos system, ensuring that the graph database is up-to-date with the latest function definitions and import relationships within Python files.
