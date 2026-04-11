# telegram_bot/handlers/shopping_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 510

---

### File: `telegram_bot/handlers/shopping_handler.py`

#### Purpose
This file contains functions to handle various commands related to shopping lists and stores for a Telegram bot. It interacts with a PostgreSQL database to manage items, lists, and stores.

#### Architecture
The file consists of several functions that handle different commands and operations related to shopping lists. The main entry point is the `handle_shop` function, which parses the command text and delegates to other functions based on the command. Each function is responsible for a specific operation such as adding items, marking items as completed, or showing items at a specific store.

#### Patterns
- **Single Responsibility Principle**: Each function is designed to handle a specific task, ensuring that the code is modular and maintainable.
- **Database Connection Management**: The `get_conn` function is used to establish a database connection, which is then used across multiple functions.

#### Dependencies
- **Imports**: `os`, `logging`, `typing`, `psycopg2`, `dotenv`
- **Environment Variables**: Uses `os.getenv` to load PostgreSQL connection details from environment variables.

#### Interfaces
- **Public Functions**:
  - `handle_shop(text: str) -> str`: Main function to handle `/shop` commands.
  - `_show_usage() -> str`: Returns usage information for the `/shop` commands.
  - `_show_stats() -> str`: Returns statistics about the shopping lists and items.
  - `_add_item(text: str) -> str`: Adds an item to a shopping list.
  - `_at_store(store_name: str) -> str`: Shows items at a specific store, grouped by department.
  - `_done_item(item_name: str) -> str`: Marks an item as completed across all active lists.
  - `_show_list(name: str) -> str`: Shows items in a specific list.
  - `_show_lists() -> str`: Shows all shopping lists.
  - `_show_stores() -> str`: Shows all stores.
  - `_store_command(text: str) -> str`: Handles commands related to stores.
  - `_search_items(query: str) -> str`: Searches for items.
  - `_new_list(name: str) -> str`: Creates a new shopping list.

#### Database
- **Tables**:
  - `shopping_lists`: Stores information about shopping lists.
  - `shopping_items`: Stores information about individual items.
  - `shopping_list_items`: Stores the relationship between items and lists.
  - `stores`: Stores information about stores.
  - `item_stores`: Stores the relationship between items and stores.
  - `visit`: Tracks store visits.
  - `purchase`: Tracks item purchases.

#### Configuration
- **Environment Variables**: Uses `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` to configure the PostgreSQL connection.
- **Dotenv**: Loads environment variables from `.env` file.

#### Key Logic
- **Item Addition**: `_add_item` function parses the command text to determine the item name, list name, and store name. It then adds the item to the specified list and associates it with the store if provided.
- **Store Items Display**: `_at_store` function retrieves items associated with a specific store and groups them by department. It also updates the store's visit frequency.
- **Item Completion**: `_done_item` function marks an item as completed across all active lists where it is pending.

#### Integration Points
- **Telegram Bot**: This file is part of the Telegram bot system and is likely integrated with the bot's command handling mechanism.
- **Database**: Integrates with the PostgreSQL database to manage shopping lists, items, and stores.
- **Logging**: Uses the `logging` module to log errors and other information.

### Example Usage
```python
# Example command handling
response = handle_shop("/shop add milk --store Walmart")
print(response)  # Output: "✅ Added: milk [Master List] → Walmart"
```

This file is crucial for the shopping list functionality of the Mythos Telegram bot, providing a comprehensive set of operations to manage items, lists, and stores.
