# skills/data/query_shopping_lists.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 161

---

### File: skills/data/query_shopping_lists.py

#### Purpose
This file contains the `QueryShoppingListsSkill` class, which is responsible for querying and formatting active shopping lists and their items from a PostgreSQL database. It handles requests to retrieve and summarize shopping list data.

#### Architecture
The file is structured around the `QueryShoppingListsSkill` class, which inherits from `SkillBase`. The class contains methods for executing the skill, querying lists and items, formatting results, and building summaries. The file also includes a top-level function `_get_conn` for establishing a database connection.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern for database connections, ensuring a consistent connection setup.
- **Facade**: The `QueryShoppingListsSkill` class acts as a facade, abstracting the complexities of database queries and result formatting.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Public Methods**: `execute`, `_query_lists`, `_query_items`, `_format_results`, `_build_summary`.
- **Exposed Interfaces**: The `execute` method is the primary interface, which takes a `SkillRequest` and returns a `SkillResponse`.

#### Database
- **Tables**: `shopping_lists`, `shopping_list_items`, `shopping_items`.
- **Queries**: 
  - `SELECT id, name, status, created_at FROM shopping_lists WHERE is_active = true ORDER BY created_at DESC`
  - `SELECT sli.id, si.name as item_name, si.department, sli.quantity, sli.priority, sli.completed, sli.notes FROM shopping_list_items sli JOIN shopping_items si ON si.id = sli.item_id WHERE sli.list_id IN (...) ORDER BY sli.completed, si.department, si.name`

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables using `dotenv`.

#### Key Logic
- **Query Execution**: The `execute` method orchestrates the querying of shopping lists and items, formatting the results, and building a summary.
- **Result Formatting**: The `_format_results` method groups items by list and formats them into a readable string.
- **Summary Building**: The `_build_summary` method provides a concise summary of the shopping lists and their items, highlighting the most recent list and its uncompleted items.

#### Integration Points
- **SkillBase**: The `QueryShoppingListsSkill` class inherits from `SkillBase`, integrating with the Mythos skill system.
- **Database Connection**: The `_get_conn` function provides a consistent way to connect to the PostgreSQL database, ensuring that the skill can interact with the database seamlessly.
- **SkillRequest/SkillResponse**: The `execute` method processes incoming requests and returns responses, integrating with the Mythos request-response framework.

### Detailed Breakdown

#### `_get_conn`
- **Purpose**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **Dependencies**: `os`, `psycopg2`.
- **Configuration**: Uses environment variables for database connection details.

#### `QueryShoppingListsSkill`
- **Purpose**: Manages the querying and formatting of shopping lists and items.
- **Methods**:
  - `execute`: Main method that handles the request, queries the database, formats results, and builds a summary.
  - `_query_lists`: Queries active shopping lists from the `shopping_lists` table.
  - `_query_items`: Queries items for given list IDs from the `shopping_list_items` and `shopping_items` tables.
  - `_format_results`: Formats the queried lists and items into a readable string.
  - `_build_summary`: Builds a summary of the queried lists and items.

#### Integration with Mythos
- **SkillBase**: The class inherits from `SkillBase`, integrating with the Mythos skill system.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, integrating with the Mythos request-response framework.

This file is a crucial component of the Mythos system, providing a robust and efficient way to query and present shopping list data.
