# Integrity Scanner

**Stream:** SYS
**Files:** 7

## Files in this Module

- `integrity/__init__.py` (19L)
- `integrity/__main__.py` (202L)
- `integrity/file_scanner.py` (286L)
- `integrity/function_extractor.py` (262L)
- `integrity/graph.py` (70L)
- `integrity/service_scanner.py` (228L)
- `integrity/table_scanner.py` (213L)

---

# Mythos Integrity Scanner Module Documentation

---

## **1. Module Purpose**
The **Integrity Scanner** module is a core component of the Mythos system responsible for ensuring data consistency and system health by:
- **Cataloging** files, functions, PostgreSQL tables, and systemd services into a Neo4j graph database.
- **Performing health checks** by comparing the actual system state (file system, PostgreSQL, systemd) with the Neo4j graph representation.
- **Detecting anomalies** such as orphan files (present on disk but missing in the graph), ghost nodes (present in the graph but missing in the system), and outdated relationships.
- **Generating reports** and statistics to monitor system integrity and relationships between components.

---

## **2. Architecture Overview**
The module follows a **modular, pipeline-based architecture** with the following data flow:

```
[CLI Command] → [Main Dispatcher] → [Scanners] → [Neo4j Graph DB]
```

### **Key Components**
- **CLI Entry Point (`__main__.py`)**: Parses commands (`scan`, `stats`) and dispatches to submodules.
- **Scanners**:
  - **File Scanner**: Walks the file system, computes hashes, and updates Neo4j nodes.
  - **Function Extractor**: Parses Python files via AST to extract functions and imports.
  - **Table Scanner**: Queries PostgreSQL for schema and foreign keys, updates Neo4j.
  - **Service Scanner**: Scans systemd services and links them to entry point files.
- **Graph Utilities (`graph.py`)**: Manages Neo4j driver, constraints, and query execution.
- **Report Generation**: Writes JSON reports to `docs/live` and displays graph statistics.

### **Data Flow**
1. **Scan Command**:
   - Triggers individual scanners (files, functions, tables, services).
   - Each scanner queries the system (file system, PostgreSQL, systemd) and updates Neo4j.
2. **Stats Command**:
   - Queries Neo4j to generate node/relationship counts and system health metrics.
3. **Health Check**:
   - Compares Neo4j graph with actual system state to detect discrepancies.

---

## **3. Key Components**
### **CLI Commands**
- `scan`: Full system scan (files, functions, tables, services).
- `scan --files`: File system scan only.
- `scan --funcs`: Function/dependency scan only.
- `scan --tables`: PostgreSQL table scan only.
- `scan --services`: Systemd service scan only.
- `stats`: Displays graph statistics (node counts, orphan files, etc.).

### **Core Functions**
| Component               | Key Functions                                                                 |
|-------------------------|-------------------------------------------------------------------------------|
| **File Scanner**        | `scan_files`, `compute_sha256`, `_merge_directory`, `_merge_file`           |
| **Function Extractor**  | `extract_functions`, `_process_file_ast`, `_merge_function`, `_merge_import`|
| **Table Scanner**       | `scan_tables`, `_merge_table`, `_merge_column`, `_merge_fk_relationship`    |
| **Service Scanner**     | `scan_services`, `_find_unit_files`, `_merge_service`, `_link_to_entry_point`|
| **Graph Utilities**     | `get_driver`, `ensure_constraints`, `run_query`, `run_write`                |

---

## **4. Design Patterns**
- **Command Pattern**: CLI commands (`scan`, `stats`) are dispatched via `__main__.py`.
- **Singleton Pattern**: Neo4j driver (`get_driver`) and PostgreSQL connection (`get_pg_connection`) are reused as singletons.
- **Factory Method Pattern**: `run_query`/`run_write` in `graph.py` abstract Cypher execution.
- **Helper Functions**: Modularized logic (e.g., `_merge_table`, `_link_file_to_directory`) for reusability.
- **Visitor Pattern**: AST traversal in `function_extractor.py` to extract functions and imports.

---

## **5. Data Model**
### **Neo4j Graph Schema**
| Node Labels            | Properties                                                                 |
|------------------------|----------------------------------------------------------------------------|
| `IntegrityFile`        | `path`, `sha256`, `status`, `extension`                                   |
| `IntegrityDirectory`   | `path`, `last_modified`                                                   |
| `IntegrityFunction`    | `name`, `file_path`, `docstring`                                          |
| `IntegrityTable`       | `name`, `schema`, `database`                                              |
| `IntegrityColumn`      | `name`, `data_type`, `table_name`                                         |
| `IntegrityService`     | `name`, `status`, `entry_point`                                           |

### **Relationships**
| Relationship Types     | Description                                                              |
|------------------------|----------------------------------------------------------------------------|
| `CONTAINS`             | File/Directory containment (e.g., `Directory` → `File`).                 |
| `IMPORTS`              | File-to-file import relationships.                                       |
| `HAS_TABLE`            | Database → Table.                                                        |
| `HAS_COLUMN`           | Table → Column.                                                          |
| `REFERENCES`           | Foreign key relationships between tables.                                |
| `ENTRY_POINT`          | Service → Entry point file.                                              |

### **Constraints & Indexes**
- **Constraints**:
  - Unique constraints on `path` for `IntegrityFile`/`IntegrityDirectory`.
  - Unique constraints on `name` for `IntegrityFunction`/`IntegrityTable`.
- **Indexes**:
  - Indexes on `status`, `extension` for `IntegrityFile`.
  - Indexes on `name` for `IntegrityFunction`.

---

## **6. API Surface**
### **CLI Endpoints**
- `mythos-integrity scan [options]`: Triggers system scans.
- `mythos-integrity stats`: Displays graph statistics.

### **Internal APIs**
- **File Scanner**:
  - `scan_files(root: str = None, driver=None) → dict`: Returns file scan statistics.
- **Function Extractor**:
  - `extract_functions(driver=None) → dict`: Returns function extraction stats.
- **Table Scanner**:
  - `scan_tables(driver=None) → dict`: Returns table/column scan stats.
- **Service Scanner**:
  - `scan_services(driver=None) → dict`: Returns service scan stats.

---

## **7. Dependencies**
### **External Systems**
- **Neo4j**: Graph database for storing cataloged entities and relationships.
- **PostgreSQL**: Schema introspection for table/column/foreign key data.
- **Systemd**: Service status and unit file parsing.

### **Internal Modules**
- `integrity.graph`: Neo4j driver and query utilities.
- `integrity.file_scanner`: File system scanning.
- `integrity.function_extractor`: AST-based function parsing.
- `integrity.table_scanner`: PostgreSQL schema scanning.
- `integrity.service_scanner`: Systemd service scanning.

---

## **8. Configuration**
### **Environment Variables**
| Variable               | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `MYTHOS_ROOT`          | Root directory for Mythos (default: `/opt/mythos`).                         |
| `NEO4J_URI`            | Neo4j connection URI (e.g., `neo4j://localhost:7687`).                      |
| `NEO4J_USER`/`PASSWORD`| Neo4j authentication credentials.                                         |
| `POSTGRES_*`           | PostgreSQL connection parameters (host, port, user, password, database).    |

### **Configuration Files**
- `.env`: Loaded via `dotenv` to provide database credentials and Neo4j settings.

---

## **Summary**
The **Integrity Scanner** module ensures Mythos system health by maintaining a synchronized Neo4j graph of files, functions, tables, and services. It leverages modular scanners, a centralized Neo4j driver, and robust CLI tools to detect discrepancies and generate actionable insights. The module is designed for extensibility, allowing new scanners or data sources to be integrated with minimal changes.
