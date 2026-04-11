# api/routes/quotes.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 428

---

### File: api/routes/quotes.py

#### Purpose
This file defines the API routes for managing quotes in the Mythos system, including listing, creating, updating, and deleting quotes and their relationships in both PostgreSQL and Neo4j.

#### Architecture
The file is structured around FastAPI routes and Pydantic models. It includes:
- **Pydantic Models**: `QuoteCreate`, `QuoteUpdate`, and `RelationshipCreate` for request validation.
- **Top-level Functions**: `get_driver`, `list_quotes`, `list_tags`, `list_speakers`, `get_graph`, `get_quote`, `create_quote`, `update_quote`, `delete_quote`, `create_relationship`, and `delete_relationship`.
- **Neo4j Driver Initialization**: `get_driver` function initializes the Neo4j driver.
- **Database Interactions**: Each endpoint interacts with Neo4j to perform CRUD operations on quotes and relationships.

#### Patterns
- **Factory Pattern**: `get_driver` acts as a factory method to initialize the Neo4j driver.
- **Singleton Pattern**: The Neo4j driver is initialized once and reused across multiple functions.

#### Dependencies
- **Imports**: `os`, `uuid`, `datetime`, `fastapi`, `pydantic`, `neo4j`, `dotenv`.
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` from `.env` file.

#### Interfaces
- **FastAPI Routes**:
  - `GET /`: List all quotes.
  - `GET /tags`: List all tags with counts.
  - `GET /speakers`: List all speakers with counts.
  - `GET /graph`: Get full relationship graph data.
  - `GET /{qid}`: Get a single quote with relationships.
  - `POST /`: Create a new quote.
  - `PATCH /{qid}`: Update an existing quote.
  - `DELETE /{qid}`: Delete a quote.
  - `POST /relationships`: Create a relationship.
  - `DELETE /relationships`: Delete a relationship.

#### Database
- **Neo4j Labels**: `Quote`, `OntologyTerm`.
- **Neo4j Relationships**: `TAGGED_WITH`, `RELATES_TO`.

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` are loaded from `.env` file.

#### Key Logic
- **List Quotes**: Filters and retrieves quotes based on speaker, tag, and search text.
- **Create Quote**: Creates a new quote node in Neo4j and auto-links to `OntologyTerm` nodes based on tags.
- **Update Quote**: Updates an existing quote node.
- **Delete Quote**: Deletes a quote node and its relationships.
- **Create Relationship**: Creates a relationship between a quote and another node.
- **Delete Relationship**: Deletes a specific relationship from a quote.

#### Integration Points
- **Neo4j**: All database interactions are performed using the Neo4j driver.
- **FastAPI**: Routes are defined using FastAPI decorators and integrated into the main application.
- **Pydantic Models**: Used for request validation and data transfer.

### Detailed Documentation

#### Classes
- **QuoteCreate**: Pydantic model for creating a new quote.
- **QuoteUpdate**: Pydantic model for updating an existing quote.
- **RelationshipCreate**: Pydantic model for creating a relationship.

#### Top-level Functions
- **get_driver**: Initializes and returns the Neo4j driver.
- **list_quotes**: Lists all quotes with optional filtering by speaker, tag, and search text.
- **list_tags**: Lists all tags with their counts.
- **list_speakers**: Lists all speakers with their counts.
- **get_graph**: Retrieves the full relationship graph data for visualization.
- **get_quote**: Retrieves a single quote with all its relationships.
- **create_quote**: Creates a new quote and auto-links to `OntologyTerm` nodes based on tags.
- **update_quote**: Updates an existing quote.
- **delete_quote**: Deletes a quote and its relationships.
- **create_relationship**: Creates a relationship between a quote and another node.
- **delete_relationship**: Deletes a specific relationship from a quote.

### Example Usage

```python
# Example of creating a new quote
from api.routes.quotes import create_quote

quote_data = {
    "text": "The quick brown fox jumps over the lazy dog.",
    "speaker": "Seraphe",
    "tags": ["example", "test"]
}

response = create_quote(QuoteCreate(**quote_data))
print(response)
```

This file serves as the primary interface for managing quotes and their relationships within the Mythos system, providing a robust set of endpoints for CRUD operations and data retrieval.
