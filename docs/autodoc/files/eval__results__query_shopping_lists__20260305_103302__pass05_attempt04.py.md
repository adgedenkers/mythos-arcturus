# eval/results/query_shopping_lists/20260305_103302/pass05_attempt04.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 176

---

### Purpose
The `pass05_attempt04.py` file contains the `QueryShoppingListsSkill` class, which is responsible for querying active shopping lists and their associated items from a PostgreSQL database. It formats the results and builds a summary for the user.

### Architecture
The file is structured around the `QueryShoppingListsSkill` class, which inherits from `SkillBase`. The class contains several methods to handle different aspects of the query and result formatting:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `_query_lists`: Queries active shopping lists.
- `_query_items`: Queries items associated with specific shopping lists.
- `_format_results`: Formats the query results into a readable string.
- `_build_summary`: Builds a summary of the shopping lists and items.

### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is established.
- **Factory Method**: The `execute` method acts as a factory method, orchestrating the query and formatting processes.

### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `engine.base`
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

### Interfaces
- **Exposed Methods**: `execute` method of `QueryShoppingListsSkill` class.
- **Exposed Classes**: `QueryShoppingListsSkill` class.

### Database
- **Tables**: `shopping_lists`, `shopping_list_items`, `shopping_items`
- **Queries**:
  - `shopping_lists`: Queries active shopping lists.
  - `shopping_list_items`: Queries items associated with specific shopping lists.

### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` are used to configure the database connection.

### Key Logic
- **Database Connection**: Establishes a connection to the PostgreSQL database using `psycopg2` and `dotenv` for configuration.
- **Query Execution**: Executes SQL queries to fetch active shopping lists and associated items.
- **Result Formatting**: Formats the query results into a readable string and builds a summary.
- **Error Handling**: Logs errors and ensures the database connection is closed in the `finally` block.

### Integration Points
- **SkillBase**: The `QueryShoppingListsSkill` class inherits from `SkillBase`, indicating it integrates with the Mythos skill system.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes for request handling and response formatting.
- **Database**: Connects to the PostgreSQL database to fetch shopping lists and items.

### Detailed Breakdown

#### `_get_conn`
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Dependencies**: `os`, `psycopg2`, `dotenv`
- **Configuration**: Uses environment variables for database configuration.

#### `QueryShoppingListsSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**: `name`, `triggers`, `cache_ttl`.
- **Methods**:
  - `execute`: Main method to execute the skill, handling database connection, querying, formatting, and building summary.
  - `_query_lists`: Queries active shopping lists from the `shopping_lists` table.
  - `_query_items`: Queries items associated with specific shopping lists from the `shopping_list_items` and `shopping_items` tables.
  - `_format_results`: Formats the query results into a readable string.
  - `_build_summary`: Builds a summary of the shopping lists and items.

#### `_query_lists`
- **Purpose**: Queries active shopping lists from the `shopping_lists` table.
- **SQL Query**: Selects `id`, `name`, `status`, and `created_at` from `shopping_lists` where `is_active` is `true`.

#### `_query_items`
- **Purpose**: Queries items associated with specific shopping lists from the `shopping_list_items` and `shopping_items` tables.
- **SQL Query**: Joins `shopping_list_items` and `shopping_items` tables to fetch item details.

#### `_format_results`
- **Purpose**: Formats the query results into a readable string.
- **Logic**: Groups items by list and formats them into a human-readable string.

#### `_build_summary`
- **Purpose**: Builds a summary of the shopping lists and items.
- **Logic**: Counts active lists, items, and remaining items, and formats them into a summary string.

This file is a crucial component of the Mythos system, handling the querying and formatting of shopping lists and items, providing a user-friendly summary of the user's shopping needs.
