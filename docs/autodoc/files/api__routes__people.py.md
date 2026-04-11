# api/routes/people.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 671

---

### File: api/routes/people.py

#### Purpose
This file contains the FastAPI routes for managing `Person`-type nodes in Neo4j, including CRUD operations, relationship management, and graph visualization endpoints.

#### Architecture
The file is structured around several Pydantic models (`PersonCreate`, `PersonUpdate`, `RelCreate`, `RelDelete`) and FastAPI routes. It uses functions to interact with Neo4j and convert Neo4j records to Python dictionaries. The main logic is organized into asynchronous functions decorated with FastAPI's `router` to handle HTTP requests.

#### Patterns
- **Factory Pattern**: The `get_driver` function acts as a factory to create Neo4j driver instances.
- **Singleton Pattern**: The `get_driver` function ensures a single Neo4j driver instance is used throughout the file.
- **Observer Pattern**: The `node_to_dict` function observes Neo4j records and converts them to a serializable dictionary format.

#### Dependencies
- **Imports**: `os`, `datetime`, `fastapi`, `pydantic`, `typing`, `neo4j`, `dotenv`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

#### Interfaces
- **FastAPI Routes**: 
  - `GET /stats`: Returns summary statistics about people nodes.
  - `GET /rel-types`: Lists all relationship types in use.
  - `GET /search-nodes`: Searches nodes for relationship target picker.
  - `GET /graph`: Full graph data for visualization.
  - `GET /{eid}/graph`: Ego-centric graph for a specific person.
  - `GET /`: Lists people nodes.
  - `GET /{eid}`: Retrieves a specific person node.
  - `POST /`: Creates a new person node.
  - `PATCH /{eid}`: Updates a person node.
  - `DELETE /{eid}`: Deletes a person node.
  - `GET /{eid}/rels`: Retrieves relationships for a specific person.
  - `POST /{eid}/rels`: Creates a relationship.
  - `DELETE /{eid}/rels`: Deletes a relationship.

#### Database
- **Neo4j Labels**: `Person`, `Soul`, `Entity`, `GenPerson`, `Incarnation`, `Alias`, `Lineage`
- **Neo4j Queries**: Various Cypher queries for listing, searching, and managing nodes and relationships.

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` are loaded from `.env` file using `dotenv`.

#### Key Logic
- **get_driver**: Creates and returns a Neo4j driver instance.
- **node_to_dict**: Converts Neo4j records to a serializable dictionary format.
- **classify_labels**: Determines the type of a node based on its labels.
- **people_stats**: Retrieves summary statistics about people nodes.
- **relationship_types**: Lists all relationship types in use.
- **search_nodes**: Searches nodes based on query parameters.
- **full_graph**: Retrieves full graph data for visualization.
- **ego_graph**: Retrieves ego-centric graph for a specific person.
- **list_people**: Lists people nodes with filtering options.
- **get_person**: Retrieves a specific person node.
- **create_person**: Creates a new person node.
- **update_person**: Updates a person node.
- **delete_person**: Deletes a person node.
- **get_relationships**: Retrieves relationships for a specific person.
- **create_relationship**: Creates a relationship.
- **delete_relationship**: Deletes a relationship.

#### Integration Points
- **Neo4j**: The file integrates with Neo4j to manage `Person`-type nodes and their relationships.
- **FastAPI**: The file integrates with FastAPI to expose RESTful endpoints for managing `Person` nodes.
- **Pydantic**: The file uses Pydantic models for request validation and response shaping.
- **Environment Configuration**: The file uses environment variables to configure Neo4j connection details.

This file serves as a comprehensive API for managing `Person` nodes and their relationships in the Mythos system, providing both CRUD operations and graph visualization capabilities.
