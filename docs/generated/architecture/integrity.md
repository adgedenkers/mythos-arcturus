## integrity
The integrity component validates structural and referential consistency across codebases, services, and database schemas by scanning for anomalies, enforcing constraints, and building dependency graphs. It ensures all system elements adhere to defined rules before deployment.

**Key files and structure**  
- `file_scanner.py`: Scans source files for syntax errors and structural issues.  
- `function_extractor.py`: Extracts function signatures and dependencies from code.  
- `graph.py`: Constructs and validates dependency graphs (code/services/tables).  
- `service_scanner.py`: Validates service definitions and inter-service dependencies.  
- `table_scanner.py`: Checks database table schemas for referential integrity.  
- `__init__.py`/`__main__.py`: Module initialization and CLI entrypoint.  

**Data flow**  
Input (source files, service configs, DB schemas) → Scanners extract structural data → Extractors build dependency graphs → Graph module validates against integrity rules → Results output via CLI or integrated system hooks.  

**Dependencies and integration points**  
- **Dependencies**: `ast` (code parsing), `sqlalchemy` (DB schema analysis), `mythos.core` (system-wide rule engine).  
- **Integration**: Hooked into build pipelines via `mythos.core` for automated checks; CLI (`__main__.py`) enables manual execution.  

**Known issues**  
- Graph validation has O(n²) complexity for large codebases (performance bottleneck).  
- `table_scanner.py` assumes PostgreSQL-specific schema patterns (limited DB support).  
- `service_scanner.py` lacks coverage for non-REST service types (e.g., gRPC).
