# api/routes/sales.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 164

---

### File: api/routes/sales.py

#### Purpose
This file contains API routes for managing sales items, including fetching, updating, and deleting items, as well as retrieving item photos.

#### Architecture
The file is structured around FastAPI routes and includes a `BaseModel` subclass for request validation. It defines several asynchronous functions for handling HTTP requests, each corresponding to a specific route. The database connection is managed through a helper function `get_db`.

- **Classes**: 
  - `ItemUpdate`: A Pydantic model for validating item update requests.
  
- **Functions**: 
  - `get_db`: Establishes a connection to the PostgreSQL database.
  - `get_items`: Retrieves all items for sale by status.
  - `get_item`: Retrieves details of a single item.
  - `update_item`: Updates fields of a specific item.
  - `delete_item`: Deletes a specific item.
  - `get_item_photos`: Retrieves photos associated with a specific item.

#### Patterns
- **Factory Method**: `get_db` acts as a factory method for creating database connections.
- **Repository Pattern**: The database operations are encapsulated within the functions, acting as a repository for item data.

#### Dependencies
- **Imports**: 
  - `psycopg2`: For PostgreSQL database operations.
  - `os`: For accessing environment variables.
  - `fastapi`: For defining API routes.
  - `pydantic`: For data validation.
  - `datetime`: For handling date and time objects.

#### Interfaces
- **Exposed Routes**:
  - `GET /items/sale`: Retrieves all items for sale by status.
  - `GET /items/sale/{item_id}`: Retrieves details of a single item.
  - `PATCH /items/sale/{item_id}`: Updates fields of a specific item.
  - `DELETE /items/sale/{item_id}`: Deletes a specific item.
  - `GET /items/sale/{item_id}/photos`: Retrieves photos associated with a specific item.

#### Database
- **Tables and Labels**:
  - `items_for_sale`: Table for storing item details.
  - `item_images`: Table for storing item photos.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_DB`: Database name.
  - `POSTGRES_USER`: Database user.
  - `POSTGRES_PASSWORD`: Database password.
  - `POSTGRES_HOST`: Database host.

#### Key Logic
- **get_items**: Fetches items from the `items_for_sale` table based on the status and includes a count of associated photos.
- **get_item**: Fetches a single item from the `items_for_sale` table.
- **update_item**: Updates fields of a specific item in the `items_for_sale` table.
- **delete_item**: Deletes a specific item from the `items_for_sale` table.
- **get_item_photos**: Fetches photos associated with a specific item from the `item_images` table.

#### Integration Points
- **Database Integration**: Uses PostgreSQL for storing and retrieving item and photo data.
- **FastAPI Integration**: Uses FastAPI to define and handle HTTP routes.
- **Pydantic Integration**: Uses Pydantic for request validation and model definition.

### Detailed Documentation

#### Classes
- **ItemUpdate**: A Pydantic model used for validating item update requests. It includes optional fields for various item attributes.

#### Functions
- **get_db**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **get_items**: Retrieves all items for sale by status. It performs a SQL query to fetch items and associated photo counts, converting datetime and UUID objects to strings.
- **get_item**: Retrieves details of a single item by ID. It performs a SQL query to fetch the item, converting datetime and UUID objects to strings.
- **update_item**: Updates fields of a specific item. It builds an SQL `UPDATE` query based on the provided updates and executes it.
- **delete_item**: Deletes a specific item by ID. It performs a SQL `DELETE` query.
- **get_item_photos**: Retrieves photos associated with a specific item. It performs a SQL query to fetch photos, converting datetime and UUID objects to strings.

#### Dependencies
- **psycopg2**: Used for connecting to and querying the PostgreSQL database.
- **os**: Used to access environment variables for database configuration.
- **fastapi**: Used to define and handle HTTP routes.
- **pydantic**: Used for data validation and model definition.
- **datetime**: Used for handling date and time objects.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_DB`: Name of the PostgreSQL database.
  - `POSTGRES_USER`: Username for the PostgreSQL database.
  - `POSTGRES_PASSWORD`: Password for the PostgreSQL database.
  - `POSTGRES_HOST`: Host address for the PostgreSQL database.

#### Key Logic
- **get_items**: Fetches items from the `items_for_sale` table based on the provided status and includes a count of associated photos.
- **get_item**: Fetches a single item from the `items_for_sale` table based on the provided item ID.
- **update_item**: Updates fields of a specific item in the `items_for_sale` table based on the provided updates.
- **delete_item**: Deletes a specific item from the `items_for_sale` table based on the provided item ID.
- **get_item_photos**: Fetches photos associated with a specific item from the `item_images` table based on the provided item ID.

#### Integration Points
- **Database Integration**: Uses PostgreSQL for storing and retrieving item and photo data.
- **FastAPI Integration**: Uses FastAPI to define and handle HTTP routes.
- **Pydantic Integration**: Uses Pydantic for request validation and model definition.
