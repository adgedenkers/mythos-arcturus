# api/routes/shopping.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 535

---

### File: api/routes/shopping.py

#### Purpose
This file contains the FastAPI routes and logic for managing shopping-related entities such as stores, items, and shopping lists. It provides endpoints for creating, updating, deleting, and querying these entities from a PostgreSQL database.

#### Architecture
The file is structured into several sections:
1. **Models**: Pydantic models for request and response schemas.
2. **Stats**: Endpoint for retrieving summary statistics.
3. **Stores**: CRUD operations for managing stores.
4. **Items**: CRUD operations for managing items.
5. **Lists**: CRUD operations for managing shopping lists.

Each section contains functions decorated with FastAPI's `@router.get`, `@router.post`, `@router.patch`, and `@router.delete` decorators to define the HTTP methods and paths for the API endpoints.

#### Patterns
- **Factory Method**: The `get_conn` function acts as a factory method to create and return a database connection.
- **Singleton**: The `get_conn` function could be considered a singleton pattern if the connection is reused across multiple requests (though it's not explicitly implemented as such here).

#### Dependencies
- **Imports**: 
  - `os`: For environment variable access.
  - `datetime`: For handling date and time.
  - `fastapi`: For defining API routes.
  - `pydantic`: For defining data models.
  - `typing`: For type hints.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.

#### Interfaces
The file exposes several FastAPI routes for managing shopping-related entities:
- **Stores**: 
  - `GET /api/shopping/stores`: List stores.
  - `POST /api/shopping/stores`: Create a store.
  - `PATCH /api/shopping/stores/{store_id}`: Update a store.
  - `DELETE /api/shopping/stores/{store_id}`: Delete a store.
- **Items**: 
  - `GET /api/shopping/items`: List items.
  - `POST /api/shopping/items`: Create an item.
  - `PATCH /api/shopping/items/{item_id}`: Update an item.
  - `DELETE /api/shopping/items/{item_id}`: Delete an item.
  - `POST /api/shopping/items/{item_id}/store`: Associate an item with a store.
- **Lists**: 
  - `GET /api/shopping/lists`: List shopping lists.
  - `POST /api/shopping/lists`: Create a shopping list.
  - `PATCH /api/shopping/lists/{list_id}`: Update a shopping list.
  - `DELETE /api/shopping/lists/{list_id}`: Delete a shopping list.
  - `POST /api/shopping/lists/{list_id}/add`: Add an item to a list.
  - `POST /api/shopping/lists/{list_id}/done`: Mark an item as done.
  - `GET /api/shopping/lists/{list_id}/items`: Get items in a list.
- **Stats**: 
  - `GET /api/shopping/stats`: Get summary statistics.

#### Database
The file interacts with the following PostgreSQL tables:
- `stores`: Stores information.
- `shopping_items`: Items information.
- `shopping_lists`: Shopping lists information.
- `shopping_list_items`: Items within shopping lists.
- `item_stores`: Associations between items and stores.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Database connection details.
  - `.env` file is loaded using `dotenv`.

#### Key Logic
- **Store Management**: 
  - `list_stores`: Lists stores with optional search and category filters.
  - `create_store`: Creates a new store.
  - `update_store`: Updates an existing store.
  - `delete_store`: Deactivates a store.
- **Item Management**: 
  - `list_items`: Lists items with optional search and department filters.
  - `create_item`: Creates a new item.
  - `update_item`: Updates an existing item.
  - `delete_item`: Deactivates an item.
  - `associate_item_store`: Associates an item with a store.
- **List Management**: 
  - `list_lists`: Lists shopping lists with an option to include completed lists.
  - `create_list`: Creates a new shopping list.
  - `update_list`: Updates an existing shopping list.
  - `delete_list`: Deactivates a shopping list.
  - `add_item_to_list`: Adds an item to a shopping list.
  - `mark_done`: Marks an item as done in a shopping list.
- **Stats**: 
  - `shopping_stats`: Retrieves summary statistics on stores, items, and lists.

#### Integration Points
- **Database**: The file integrates with the PostgreSQL database to perform CRUD operations on the `stores`, `shopping_items`, `shopping_lists`, and `shopping_list_items` tables.
- **Environment**: The file uses environment variables for database connection details.
- **FastAPI**: The file integrates with FastAPI to define and handle HTTP requests for the shopping-related endpoints.

This file is a critical component of the Mythos system, providing the backend logic for managing shopping-related entities and exposing them via a RESTful API.
