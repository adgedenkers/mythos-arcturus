# api/routes/ontology.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 344

---

### File: `api/routes/ontology.py`

#### Purpose
This file contains the FastAPI routes for managing ontology terms and their relationships in the Mythos system. It provides endpoints for listing, creating, updating, and deleting ontology terms, as well as managing relationships between terms.

#### Architecture
The file is structured around FastAPI routes and Pydantic models. It includes:
- **Pydantic Models**: `TermCreate`, `TermUpdate`, and `RelationshipCreate` for request validation.
- **Functions**: Various asynchronous functions that handle different HTTP methods (GET, POST, PATCH, DELETE) for ontology terms and relationships.
- **Database Interaction**: Uses Neo4j to manage ontology terms and relationships.

#### Patterns
- **Factory Method**: The `get_driver` function acts as a factory method to create a Neo4j driver instance.
- **Singleton**: The `get_driver` function ensures a single instance of the Neo4j driver is used throughout the file.

#### Dependencies
- **Imports**: `os`, `fastapi`, `pydantic`, `typing`, `datetime`, `neo4j`, `dotenv`.
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.

#### Interfaces
- **Endpoints**:
  - `GET /terms`: List ontology terms.
  - `GET /terms/{name}`: Get a specific term.
  - `POST /terms`: Create a new term.
  - `PATCH /terms/{name}`: Update an existing term.
  - `DELETE /terms/{name}`: Delete a term.
  - `GET /categories`: List all categories with term counts.
  - `GET /graph`: Get full relationship graph data.
  - `POST /relationships`: Create a relationship between two terms.
  - `DELETE /relationships`: Delete a relationship between two terms.

#### Database
- **Neo4j Labels**: `OntologyTerm`, `RELATED_TO`.
- **Neo4j Queries**: Various Cypher queries to manage ontology terms and relationships.

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` are loaded from `.env` file.

#### Key Logic
- **Term Management**:
  - **Listing Terms**: Filters terms by category and search terms.
  - **Creating Terms**: Ensures no duplicate terms are created.
  - **Updating Terms**: Updates term attributes and handles partial updates.
  - **Deleting Terms**: Deletes a term and all its relationships.
- **Relationship Management**:
  - **Creating Relationships**: Ensures both source and target terms exist before creating a relationship.
  - **Deleting Relationships**: Deletes a specific relationship between two terms.

#### Integration Points
- **Neo4j**: All term and relationship operations are performed using Neo4j.
- **FastAPI**: The file integrates with FastAPI to handle HTTP requests and responses.

### Detailed Analysis of Functions

1. **`get_driver`**:
   - **Purpose**: Returns a Neo4j driver instance.
   - **Dependencies**: `neo4j`, `os` (for environment variables).

2. **`list_terms`**:
   - **Purpose**: Lists ontology terms, optionally filtered by category and search terms.
   - **Logic**: Uses Cypher queries to filter and retrieve terms based on provided parameters.

3. **`get_term`**:
   - **Purpose**: Retrieves a single term with all its relationships.
   - **Logic**: Uses Cypher queries to fetch the term and its relationships.

4. **`create_term`**:
   - **Purpose**: Creates a new ontology term.
   - **Logic**: Checks for duplicates and creates a new term if it doesn't exist.

5. **`update_term`**:
   - **Purpose**: Updates an existing ontology term.
   - **Logic**: Updates the term's attributes and ensures the term exists before updating.

6. **`delete_term`**:
   - **Purpose**: Deletes an ontology term and its relationships.
   - **Logic**: Deletes the term and all its relationships using Cypher queries.

7. **`list_categories`**:
   - **Purpose**: Lists all categories with term counts.
   - **Logic**: Uses Cypher queries to count terms in each category.

8. **`get_graph`**:
   - **Purpose**: Retrieves full relationship graph data for visualization.
   - **Logic**: Fetches nodes and edges using Cypher queries.

9. **`create_relationship`**:
   - **Purpose**: Creates a relationship between two terms.
   - **Logic**: Ensures both source and target terms exist before creating the relationship.

10. **`delete_relationship`**:
    - **Purpose**: Deletes a specific relationship between two terms.
    - **Logic**: Deletes the relationship using Cypher queries.

### Summary
The `ontology.py` file provides comprehensive management of ontology terms and their relationships using FastAPI and Neo4j. It includes robust validation, error handling, and efficient database interactions to ensure the integrity and consistency of the ontology data.
