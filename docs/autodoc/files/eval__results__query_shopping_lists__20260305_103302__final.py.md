# eval/results/query_shopping_lists/20260305_103302/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 161

---

### File: eval/results/query_shopping_lists/20260305_103302/final.py

#### Purpose
This file contains a class `QueryShoppingListsSkill` that handles the retrieval and formatting of shopping lists and their items from a PostgreSQL database. It is designed to respond to queries related to shopping lists and provide a summary of the lists and items.

#### Architecture
- **Class**: `QueryShoppingListsSkill` extends `SkillBase` and contains methods for executing the query, retrieving lists and items, formatting results, and building a summary.
- **Functions**: `_get_conn`, `execute`, `_query_lists`, `_query_items`, `_format_results`, `_build_summary`.

#### Patterns
- **Singleton**: The connection to the PostgreSQL database is managed through the `_get_conn` function, which can be considered a singleton pattern for database connections.
- **Facade**: The `execute` method acts as a facade, coordinating the retrieval and formatting of data.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Public Methods**: `execute` (part of the `SkillBase` interface).
- **Private Methods**: `_query_lists`, `_query_items`, `_format_results`, `_build_summary`.

#### Database
- **Tables**: `shopping_lists`, `shopping_list_items`, `shopping_items`.
- **Queries**: 
  - `SELECT` from `shopping_lists` to get active lists.
  - `JOIN` between `shopping_list_items` and `shopping_items` to get detailed items for each list.

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables using `dotenv`.

#### Key Logic
- **_query_lists**: Retrieves active shopping lists from the `shopping_lists` table.
- **_query_items**: Retrieves items for the given list IDs from `shopping_list_items` and `shopping_items` tables.
- **_format_results**: Formats the retrieved lists and items into a human-readable string.
- **_build_summary**: Builds a summary of the lists and items, including counts and details of the most recent list.

#### Integration Points
- **SkillBase Interface**: The class extends `SkillBase` and implements the `execute` method to integrate with the Mythos system.
- **Database Connection**: Uses `psycopg2` to connect to the PostgreSQL database.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` to handle input and output within the Mythos system.

### Detailed Documentation

#### Class: `QueryShoppingListsSkill`
- **Inheritance**: `SkillBase`
- **Attributes**:
  - `name`: 'query_shopping_lists'
  - `triggers`: List of phrases that trigger this skill.
  - `cache_ttl`: Time-to-live for caching results (300 seconds).

- **Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: Main method that handles the request, queries the database, formats the results, and returns a `SkillResponse`.
  - `_query_lists(conn)`: Queries the `shopping_lists` table for active lists.
  - `_query_items(conn, list_ids)`: Queries the `shopping_list_items` and `shopping_items` tables for items related to the given list IDs.
  - `_format_results(lists, items)`: Formats the lists and items into a human-readable string.
  - `_build_summary(lists, items)`: Builds a summary of the lists and items.

#### Top-level Functions
- **_get_conn()**: Establishes a connection to the PostgreSQL database using environment variables.
- **execute(request)**: This function is not part of the class but is defined at the top level. It seems redundant as the class method `execute` already exists.

#### Database References
- **Tables**: `shopping_lists`, `shopping_list_items`, `shopping_items`.
- **Queries**:
  - `SELECT id, name, status, created_at FROM shopping_lists WHERE is_active = true ORDER BY created_at DESC`
  - `SELECT sli.id, si.name as item_name, si.department, sli.quantity, sli.priority, sli.completed, sli.notes FROM shopping_list_items sli JOIN shopping_items si ON si.id = sli.item_id WHERE sli.list_id IN (...) ORDER BY sli.completed, si.department, si.name`

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables using `dotenv`.

#### Key Logic
- **_query_lists**: Retrieves active shopping lists from the `shopping_lists` table.
- **_query_items**: Retrieves items for the given list IDs from `shopping_list_items` and `shopping_items` tables.
- **_format_results**: Formats the retrieved lists and items into a human-readable string.
- **_build_summary**: Builds a summary of the lists and items, including counts and details of the most recent list.

#### Integration Points
- **SkillBase Interface**: The class extends `SkillBase` and implements the `execute` method to integrate with the Mythos system.
- **Database Connection**: Uses `psycopg2` to connect to the PostgreSQL database.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` to handle input and output within the Mythos system.
