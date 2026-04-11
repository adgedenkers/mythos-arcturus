# iris/introspection/graph_enricher.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 49

---

### File: `iris/introspection/graph_enricher.py`

#### Purpose
This file contains the `enrich_graph` function, which updates Neo4j with nodes and relationships representing system components, files, and dependencies based on introspection data.

#### Architecture
The file consists of a single top-level function `enrich_graph`. The function takes a Neo4j driver, a run ID, a list of files, and a dictionary of component groups. It uses the Neo4j driver to create or update nodes and relationships in the Neo4j graph database.

#### Patterns
- **Singleton**: The `logging` module is used to log messages, which is a singleton pattern.
- **Data Access Object (DAO)**: The function acts as a DAO by directly interacting with the Neo4j database to persist data.

#### Dependencies
- **Imports**: `logging`
- **External Dependencies**: `driver` (Neo4j driver), `run_id`, `file_list`, `component_groups`

#### Interfaces
- **Function Interface**: `enrich_graph(driver, run_id, file_list, component_groups)`
  - **Parameters**:
    - `driver`: Neo4j driver instance.
    - `run_id`: Unique identifier for the introspection run.
    - `file_list`: List of files to be processed.
    - `component_groups`: Dictionary mapping component names to lists of files.
  - **Returns**: The number of relationships created or updated.

#### Database
- **Neo4j Labels**:
  - `SystemComponent`
  - `SystemFile`
  - `IntrospectionRun`
  - `SystemDependency`
- **Neo4j Relationships**:
  - `CONTAINS`
  - `SCANNED`
  - `DEPENDS_ON`

#### Configuration
- **Environment Variables**: None
- **Config Files**: None

#### Key Logic
1. **Introspection Run Node**: Creates or updates an `IntrospectionRun` node with the given `run_id`.
2. **SystemComponent Nodes**: Creates or updates `SystemComponent` nodes for each component in `component_groups`.
3. **SystemFile Nodes**: Creates or updates `SystemFile` nodes for each file in `file_list`, setting properties like `path`, `component`, `file_type`, etc.
4. **Relationships**:
   - `CONTAINS`: Links `SystemComponent` nodes to `SystemFile` nodes.
   - `SCANNED`: Links `IntrospectionRun` node to `SystemFile` nodes.
   - `DEPENDS_ON`: Links `SystemFile` nodes to `SystemDependency` nodes based on dependencies.

#### Integration Points
- **Mythos Subsystems**:
  - **Introspection Service**: The function is likely called by the introspection service after it has gathered data about system components and files.
  - **Neo4j Database**: The function directly interacts with the Neo4j database to persist the gathered data.

### Summary
The `graph_enricher.py` file provides a function to enrich the Neo4j graph database with nodes and relationships representing system components, files, and dependencies. It uses the Neo4j driver to execute Cypher queries, ensuring that the graph is updated with the latest introspection data. The function is designed to be called by the introspection service and integrates with the Neo4j database to maintain the system's graph representation.
