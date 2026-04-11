# core/app_registry.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 411

---

### File: core/app_registry.py

#### Purpose
The `AppRegistry` class in `app_registry.py` manages and queries the Neo4j application registry, which tracks ownership of node labels and relationship types by different applications. It provides methods to audit, clean up, and manage the registry.

#### Architecture
The `AppRegistry` class is the primary component of this file. It is initialized with a Neo4j driver and contains methods to perform various operations on the application registry. The class maintains a reverse lookup dictionary (`_label_to_app`) for efficient label-to-app lookups.

#### Patterns
- **Singleton**: The `AppRegistry` class can be designed as a singleton to ensure a single instance manages the registry.
- **Factory**: The class could be extended to use a factory pattern for creating instances with different configurations.

#### Dependencies
- **Imports**: `os`, `logging`, `datetime`, `typing`
- **Neo4j Driver**: Required for database operations.

#### Interfaces
- **Initialization**: `__init__(neo4j_driver)`
- **Label Ownership**: `get_label_owner(label)`
- **App Labels**: `get_app_labels(app_id)`
- **App Relationships**: `get_app_relationships(app_id)`
- **Protected Status**: `is_protected(app_id)`
- **List Apps**: `list_apps()`
- **App Info**: `get_app_info(app_id)`
- **Orphan Labels**: `find_orphan_labels()`
- **Audit App**: `audit_app(app_id)`
- **Audit All**: `audit_all()`
- **Cleanup Query**: `get_cleanup_query(app_id, dry_run)`
- **Seed Neo4j**: `seed_neo4j()`
- **Audit Report**: `format_audit_report(include_orphans)`

#### Database
- **Neo4j Labels**: `GenPerson`, `AppRegistry`
- **Neo4j Nodes**: `AppRegistry` nodes are created/updated to mirror `APP_DEFINITIONS`.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Configuration Files**: None explicitly used.

#### Key Logic
- **Label Ownership**: Efficiently maps labels to their owning application using a reverse lookup dictionary.
- **Audit**: Counts nodes for each application by constructing and executing Cypher queries.
- **Cleanup**: Generates Cypher queries to either count or delete nodes for an application.
- **Seed Neo4j**: Ensures that the Neo4j database reflects the canonical `APP_DEFINITIONS` by creating or updating `AppRegistry` nodes.

#### Integration Points
- **Neo4j Driver**: The class interacts with Neo4j through the provided driver for auditing, finding orphan labels, and seeding the database.
- **APP_DEFINITIONS**: The class uses the `APP_DEFINITIONS` dictionary as the single source of truth for application definitions and ownership.

### Detailed Documentation

#### Class: `AppRegistry`
- **Purpose**: Manages and queries the Neo4j application registry.
- **Initialization**: `__init__(neo4j_driver=None)` initializes the class with a Neo4j driver and builds a reverse lookup dictionary for label-to-app mapping.
- **Methods**:
  - `get_label_owner(label: str) -> Optional[str]`: Returns the owning application ID for a given label.
  - `get_app_labels(app_id: str) -> list`: Returns all labels owned by a given application.
  - `get_app_relationships(app_id: str) -> list`: Returns all relationship types owned by a given application.
  - `is_protected(app_id: str) -> bool`: Checks if an application is marked as protected.
  - `list_apps() -> list`: Lists all registered application IDs.
  - `get_app_info(app_id: str) -> Optional[dict]`: Returns the full definition of an application.
  - `find_orphan_labels() -> list`: Finds labels in Neo4j that are not registered to any application.
  - `audit_app(app_id: str) -> Optional[dict]`: Counts all nodes belonging to a given application.
  - `audit_all() -> list`: Audits all registered applications.
  - `get_cleanup_query(app_id: str, dry_run: bool) -> str`: Generates a Cypher query to count or delete nodes for an application.
  - `seed_neo4j()`: Creates or updates `AppRegistry` nodes in Neo4j to mirror `APP_DEFINITIONS`.
  - `format_audit_report(include_orphans: bool) -> str`: Generates a formatted text report of the full registry audit.

#### Key Data Structures
- **APP_DEFINITIONS**: A dictionary containing canonical definitions for all applications, including their labels, relationships, and protected status.

#### Example Usage
```python
from core.app_registry import AppRegistry

registry = AppRegistry(neo4j_driver)

# Check who owns a label
owner = registry.get_label_owner('GenPerson')
# => 'genealogy'

# Get all apps and their node counts
audit = registry.audit_all()
# => [{'app_id': 'genealogy', 'labels': [...], 'node_count': 3872}, ...]

# Get cleanup query for an app
query = registry.get_cleanup_query('genealogy', dry_run=True)
# => 'MATCH (n) WHERE n:GenPerson OR n:GenPlace ... RETURN count(n)'
```

This file is crucial for maintaining the integrity and organization of the Neo4j database by ensuring that all node labels and relationship types are properly registered and managed by their respective applications.
