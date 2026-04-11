# api/routes/doc_registry.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 401

---

### File: `api/routes/doc_registry.py`

#### Purpose
This file contains the API endpoints for managing and querying documents in the Mythos document registry. It includes functionalities for searching, listing, retrieving, registering, updating, and deprecating documents.

#### Architecture
The file is structured around FastAPI routes and Pydantic models. It defines several Pydantic models (`DocRegister`, `DocUpdate`, `DocDeprecate`) for request validation and several top-level functions for database operations and utility tasks. The main logic is encapsulated in asynchronous functions decorated with FastAPI route decorators (`@router.get`, `@router.post`, `@router.put`).

#### Patterns
- **Pydantic Models**: Used for request validation and data modeling (`DocRegister`, `DocUpdate`, `DocDeprecate`).
- **Dependency Injection**: The `get_db` function is used to inject a database connection into each route.
- **Singleton Pattern**: The `get_db` function ensures a single database connection is used per request.

#### Dependencies
- **Standard Libraries**: `os`, `json`, `hashlib`, `logging`, `datetime`, `typing`.
- **Third-party Libraries**: `fastapi`, `psycopg2`, `pydantic`, `dotenv`.

#### Interfaces
The file exposes several FastAPI routes for document management:
- `GET /search`: Search documents by query, domain, type, tags.
- `GET /registry`: List all active documents.
- `GET /{slug}`: Get full registry entry for a document.
- `GET /{slug}/content`: Get the actual file contents of a registered document.
- `POST /register`: Register a new document.
- `PUT /{slug}`: Update a document.
- `POST /{slug}/deprecate`: Mark a document as deprecated.

#### Database
The file interacts with the PostgreSQL database, specifically with the following tables:
- `document_registry`: Stores document metadata.
- `document_versions`: Stores version history of documents.

#### Configuration
The file uses environment variables loaded from `.env` for database connection details:
- `POSTGRES_HOST`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_PORT`

#### Key Logic
- **Search Documents**: Filters documents based on various criteria and optionally includes file contents.
- **List Registry**: Lists all documents in the registry, grouped by domain.
- **Get Document**: Retrieves a document's metadata and version history.
- **Get Document Content**: Retrieves the actual file contents of a document.
- **Register Document**: Registers a new document, ensuring uniqueness and hashing the file if provided.
- **Update Document**: Updates a document, versions the previous state, and updates file hash if necessary.
- **Deprecate Document**: Marks a document as deprecated and points to its replacement.

#### Integration Points
- **Database**: Connects to PostgreSQL to perform CRUD operations on `document_registry` and `document_versions`.
- **File System**: Reads file contents and computes file hashes.
- **Logging**: Logs important events such as document registration and updates.

### Detailed Breakdown of Functions

1. **`get_db`**: Returns a database connection using environment variables for configuration.
2. **`json_response`**: Converts data to a JSON response.
3. **`file_hash`**: Computes the SHA-256 hash of a file's contents.
4. **`search_docs`**: Implements document search functionality, filtering by various criteria and optionally including file contents.
5. **`list_registry`**: Lists all documents in the registry, grouped by domain.
6. **`get_doc`**: Retrieves a document's metadata and version history.
7. **`get_doc_content`**: Retrieves the actual file contents of a document.
8. **`register_doc`**: Registers a new document, ensuring uniqueness and hashing the file if provided.
9. **`update_doc`**: Updates a document, versions the previous state, and updates file hash if necessary.
10. **`deprecate_doc`**: Marks a document as deprecated and points to its replacement.

This file is crucial for managing the document registry in the Mythos system, providing a comprehensive set of APIs for document management and retrieval.
