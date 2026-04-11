# skills/data/grocery_skill.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 441

---

### Documentation for `skills/data/grocery_skill.py`

#### Purpose
This file implements the grocery list management functionality for the Mythos system, specifically handling commands related to adding, listing, checking, and removing items from a grocery list stored in a PostgreSQL database.

#### Architecture
The file consists of several helper functions and a main handler function (`handle`). Each helper function is responsible for a specific task such as connecting to the database, guessing the department of an item, sorting departments, fetching active lists, adding items, and handling various commands like listing items, checking items, and clearing the list.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it returns a database connection that can be reused.
- **Factory**: Functions like `_find_or_create_item` act as factories by creating or retrieving items from the database.

#### Dependencies
- **Imports**: `re`, `os`, `psycopg2`, `RealDictCursor` from `psycopg2.extras`, and `load_dotenv` from `dotenv`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Public Interface**: The `handle` function is the main entry point for processing grocery list commands.
- **Helper Functions**: Functions like `_get_conn`, `_guess_dept`, `_dept_sort`, `_dept_icon`, `_get_active_list`, `_find_or_create_item`, `_get_list_items`, `_handle_add`, `_handle_list`, `_handle_aisle`, `_handle_check`, `_handle_remove`, `_handle_clear`, `_handle_reset`, `_handle_summary`.

#### Database
- **Tables**: `shopping_lists`, `shopping_items`, `shopping_list_items`.
- **Operations**: The file performs various operations such as fetching active lists, inserting new items, updating item quantities, and retrieving list items.

#### Configuration
- **Environment Variables**: The file uses environment variables to configure the PostgreSQL database connection.
- **Constants**: `DEPT_ORDER`, `DEPT_ICONS`, `DEPT_KEYWORDS` are used to define department order, icons, and keywords for department guessing.

#### Key Logic
- **Department Guessing**: `_guess_dept` function matches item names with predefined keywords to guess the department.
- **Item Management**: Functions like `_find_or_create_item` and `_handle_add` manage the creation and addition of items to the list.
- **List Operations**: Functions like `_handle_list`, `_handle_aisle`, `_handle_check`, `_handle_remove`, `_handle_clear`, `_handle_reset`, and `_handle_summary` handle various operations on the grocery list.

#### Integration Points
- **Database Integration**: The file integrates with the PostgreSQL database to manage grocery lists and items.
- **Command Handling**: The `handle` function integrates with the command processing system to handle `/grocery` commands.
- **Environment Configuration**: The file integrates with the environment configuration system to load database connection details.

### Detailed Function Descriptions

1. **_get_conn**
   - **Purpose**: Establishes a connection to the PostgreSQL database.
   - **Logic**: Uses environment variables to configure the connection.

2. **_guess_dept**
   - **Purpose**: Guesses the department of an item based on predefined keywords.
   - **Logic**: Matches the item name with keywords in `DEPT_KEYWORDS`.

3. **_dept_sort**
   - **Purpose**: Returns the sort order of a department based on `DEPT_ORDER`.
   - **Logic**: Uses the index of the department in `DEPT_ORDER`.

4. **_dept_icon**
   - **Purpose**: Returns an icon for a department.
   - **Logic**: Uses `DEPT_ICONS` to map department names to icons.

5. **_get_active_list**
   - **Purpose**: Retrieves the active shopping list or creates a new one if none exists.
   - **Logic**: Queries the `shopping_lists` table and creates a new list if necessary.

6. **_find_or_create_item**
   - **Purpose**: Finds or creates a new item in the `shopping_items` table.
   - **Logic**: Queries the `shopping_items` table and inserts a new item if not found.

7. **_get_list_items**
   - **Purpose**: Retrieves items from a shopping list.
   - **Logic**: Queries the `shopping_list_items` and `shopping_items` tables.

8. **_handle_add**
   - **Purpose**: Handles the addition of items to the shopping list.
   - **Logic**: Parses the input, guesses the department, and inserts the item into the list.

9. **_handle_list**
   - **Purpose**: Handles the listing of items in the shopping list.
   - **Logic**: Retrieves and formats the list items, sorting by department.

10. **_handle_aisle**
    - **Purpose**: Handles the display of the current aisle items.
    - **Logic**: Retrieves and formats the items for the current aisle.

11. **_handle_check**
    - **Purpose**: Handles checking or unchecking items in the list.
    - **Logic**: Updates the `completed` status of items in the `shopping_list_items` table.

12. **_handle_remove**
    - **Purpose**: Handles the removal of items from the list.
    - **Logic**: Deletes items from the `shopping_list_items` table.

13. **_handle_clear**
    - **Purpose**: Handles the clearing of checked items from the list.
    - **Logic**: Deletes checked items from the `shopping_list_items` table.

14. **_handle_reset**
    - **Purpose**: Handles the resetting of the list.
    - **Logic**: Archives the current list and creates a new one.

15. **_handle_summary**
    - **Purpose**: Handles the summary of the list.
    - **Logic**: Retrieves and formats a summary of the list items.

16. **handle**
    - **Purpose**: Main handler function for processing `/grocery` commands.
    - **Logic**: Dispatches the command to the appropriate handler function based on the command type.
