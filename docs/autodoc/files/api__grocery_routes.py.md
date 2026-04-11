# api/grocery_routes.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 179

---

### File: api/grocery_routes.py

#### Purpose
This file contains the FastAPI routes for managing grocery lists, including adding, checking, removing, and resetting items. It serves both the Command Center React frontend and the Telegram skill.

#### Architecture
- **Classes**: 
  - `AddItemsRequest`: A Pydantic model representing the request to add items to the grocery list.
  - `CheckRequest`: A Pydantic model representing the request to check/uncheck an item.
- **Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `_get_active_list_id`: Retrieves the active grocery list ID for a given Telegram user ID.
  - `get_list`: Retrieves the current grocery list.
  - `add_items`: Adds items to the grocery list.
  - `check_item`: Checks or unchecks an item in the grocery list.
  - `remove_item`: Removes an item from the grocery list.
  - `clear_checked`: Clears all checked items from the grocery list.
  - `reset_list`: Resets the grocery list by marking the current list as completed and creating a new one.
- **Data Flow**: 
  - The file interacts with the PostgreSQL database to retrieve and modify grocery list data.
  - It uses Pydantic models to validate incoming requests.

#### Patterns
- **Factory**: The `_get_conn` function acts as a factory method to create a database connection.
- **Singleton**: The database connection is managed within each function to ensure it is properly closed after use.

#### Dependencies
- **Imports**: 
  - `psycopg2`: For database connection and operations.
  - `sys`: For modifying the Python path.
  - `re`: For regular expression operations.
  - `fastapi`: For defining API routes.
  - `pydantic`: For data validation.
  - `HTTPException`: For raising HTTP exceptions.

#### Interfaces
- **FastAPI Routes**:
  - `GET /list`: Retrieves the current grocery list.
  - `POST /add`: Adds items to the grocery list.
  - `POST /check/{item_id}`: Checks or unchecks an item.
  - `DELETE /remove/{item_id}`: Removes an item from the grocery list.
  - `POST /clear`: Clears all checked items from the grocery list.
  - `POST /reset`: Resets the grocery list.

#### Database
- **Tables and Labels**:
  - `grocery_lists`: Stores grocery lists.
  - `grocery_items`: Stores individual items in a grocery list.
  - `grocery_aisles`: Stores aisles for categorizing grocery items.

#### Configuration
- **Environment Variables**: 
  - The database connection details are hardcoded in `_get_conn`.
- **Config Files**: 
  - No explicit configuration files are used.

#### Key Logic
- **_get_conn**: Establishes a connection to the PostgreSQL database.
- **_get_active_list_id**: Retrieves the active grocery list ID for a given Telegram user ID. If no active list exists, it creates a new one.
- **get_list**: Retrieves the current grocery list, including items and aisles.
- **add_items**: Adds items to the grocery list, inferring the aisle for each item.
- **check_item**: Updates the checked status of an item.
- **remove_item**: Deletes an item from the grocery list.
- **clear_checked**: Deletes all checked items from the grocery list.
- **reset_list**: Marks the current list as completed and creates a new one.

#### Integration Points
- **Mythos Subsystems**:
  - **Command Center React frontend**: This file serves as the backend API for the frontend to interact with the grocery list.
  - **Telegram skill**: The `grocery_skill` module is imported to guess the aisle for new items.
  - **Database**: The file interacts with the PostgreSQL database to manage grocery list data.

This file is a critical component of the Mythos system, providing the necessary API endpoints to manage grocery lists effectively.
