# eval/results/query_shopping_lists/20260305_103302/pass04_attempt03.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 168

---

### Purpose
The `pass04_attempt03.py` file contains a class `QueryShoppingListsSkill` that handles the querying and formatting of shopping lists and their items from a PostgreSQL database. It is designed to respond to user requests for shopping list information, providing both detailed and summarized results.

### Architecture
The file is structured around a single class `QueryShoppingListsSkill` which inherits from `SkillBase`. This class contains several methods for executing the query, fetching lists and items, formatting results, and building summaries. Additionally, there are top-level functions for establishing a database connection and executing the skill.

### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures that a database connection is established only once per execution.
- **Factory Method**: The `execute` method acts as a factory method, coordinating the execution of various sub-methods to produce a `SkillResponse`.

### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `engine.base`
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

### Interfaces
- **Public Methods**: 
  - `execute(request: SkillRequest) -> SkillResponse`: Executes the skill and returns a formatted response.
- **Private Methods**:
  - `_query_lists(conn)`: Queries active shopping lists.
  - `_query_items(conn, list_ids)`: Queries items for given list IDs.
  - `_format_results(lists, items)`: Formats the lists and items into a readable string.
  - `_build_summary(lists, items)`: Builds a summary of the lists and items.

### Database
- **Tables**:
  - `shopping_lists`: Stores shopping list information.
  - `shopping_list_items`: Stores items within each shopping list.
  - `shopping_items`: Stores individual item details.

### Configuration
- **Environment Variables**: The database connection details are loaded from environment variables using `dotenv`.

### Key Logic
- **Query Execution**: The `execute` method orchestrates the querying of lists and items, formatting the results, and building a summary.
- **Database Interaction**: The `_query_lists` and `_query_items` methods handle the SQL queries to fetch shopping lists and their items.
- **Result Formatting**: The `_format_results` method groups items by list and formats them into a readable string.
- **Summary Building**: The `_build_summary` method provides a concise summary of the lists and items, including the number of active lists and the items in the most recent list.

### Integration Points
- **SkillBase**: The class inherits from `SkillBase` and integrates with the Mythos skill system, using `SkillRequest` and `SkillResponse` objects.
- **Database Connection**: The `_get_conn` function establishes a connection to the PostgreSQL database, which is used by the `_query_lists` and `_query_items` methods.
- **Logging**: Errors are logged using the `logging` module to ensure issues are tracked and can be debugged.

### Detailed Analysis

#### Class: `QueryShoppingListsSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: Name of the skill.
  - `triggers`: List of trigger phrases.
  - `cache_ttl`: Time-to-live for caching results.
- **Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: Main method that handles the execution of the skill. It queries the database, formats the results, and builds a summary.
  - `_query_lists(conn)`: Queries the `shopping_lists` table for active lists.
  - `_query_items(conn, list_ids)`: Queries the `shopping_list_items` and `shopping_items` tables for items in the specified lists.
  - `_format_results(lists, items)`: Formats the lists and items into a readable string.
  - `_build_summary(lists, items)`: Builds a summary of the lists and items.

#### Top-Level Functions
- `_get_conn()`: Establishes a connection to the PostgreSQL database using environment variables.
- `execute(request)`: A top-level function that delegates to the `QueryShoppingListsSkill.execute` method.

### Conclusion
This file is a crucial component of the Mythos system, handling the retrieval and formatting of shopping list data from a PostgreSQL database. It integrates with the Mythos skill system and ensures that user requests for shopping list information are handled efficiently and accurately.
