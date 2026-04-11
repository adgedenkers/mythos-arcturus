# api/routes/rolodex.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 785

---

### File: api/routes/rolodex.py

#### Purpose
This file contains the API routes for the Mythos Rolodex, which manages identity and directory information using Neo4j and PostgreSQL. It provides endpoints for browsing, creating, updating, and deleting nodes and relationships.

#### Architecture
The file is structured around FastAPI routes and Pydantic models. It includes several classes for request models (`NodeCreate`, `NodeUpdate`, `RelCreate`, `RelDelete`, `ResolveEntity`) and top-level functions for database connections and utility operations. The main logic is organized into asynchronous functions that handle different HTTP methods and paths.

#### Patterns
- **Factory Pattern**: The `get_neo4j` and `get_pg` functions act as factory methods to create connections to Neo4j and PostgreSQL, respectively.
- **Singleton Pattern**: The `router` object is a singleton instance of `APIRouter` that defines all the routes.

#### Dependencies
- **Imports**: `os`, `datetime`, `fastapi`, `pydantic`, `typing`, `neo4j`, `psycopg2`, `psycopg2.extras`, `dotenv`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

#### Interfaces
- **FastAPI Routes**: 
  - `GET /stats`: Dashboard stats
  - `GET /`: Browse directory
  - `GET /unresolved`: Unresolved entities
  - `GET /graph`: Graph data for visualization
  - `GET /node/{cid}`: Node detail by canonical_id
  - `GET /node/{cid}/graph`: Ego graph for a node
  - `POST /resolve`: Resolve entity → person
  - `POST /node`: Create a node
  - `PATCH /node/{cid}`: Update a node
  - `POST /node/{cid}/rel`: Create a relationship
  - `DELETE /node/{cid}/rel`: Delete a relationship
  - `GET /search`: Search all Rolodex nodes

#### Database
- **PostgreSQL**: 
  - Tables: `a`, `datetime`, `fastapi`, `pydantic`, `typing`, `neo4j`, `dotenv`, `its`, `rolodex`, `node`, `this`
- **Neo4j**: 
  - Labels: `Entity`, `Person`, `REFERS_TO`

#### Configuration
- **Environment Variables**: 
  - `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

#### Key Logic
- **Node Classification**: `classify_node` function classifies nodes based on their labels and canonical IDs.
- **Node Conversion**: `node_to_dict` converts Neo4j records to serializable dictionaries.
- **Database Operations**: 
  - `rolodex_stats`: Fetches dashboard stats from Neo4j.
  - `browse_directory`: Browses the directory with filtering and sorting.
  - `unresolved_entities`: Lists unresolved entities.
  - `rolodex_graph`: Fetches graph data for visualization.
  - `get_node`: Retrieves full node detail by canonical_id.
  - `node_ego_graph`: Fetches ego-centric graph for a specific node.
  - `resolve_entity`: Links an entity mention to a canonical person.
  - `create_node`: Creates a new node in the Rolodex.
  - `update_node`: Updates node properties.
  - `create_relationship`: Creates a relationship from one node to another.
  - `delete_relationship`: Deletes a relationship.
  - `search_nodes`: Searches all Rolodex nodes for relationship target picker.

#### Integration Points
- **Neo4j**: The file interacts with Neo4j to manage nodes and relationships.
- **PostgreSQL**: The file uses PostgreSQL for additional data storage and retrieval.
- **FastAPI**: The file integrates with FastAPI to expose RESTful API endpoints.
- **Pydantic Models**: The file uses Pydantic models to validate and serialize request and response data.

This file is a critical component of the Mythos system, providing comprehensive API endpoints for managing the Rolodex, which is the identity and directory layer of the system.
