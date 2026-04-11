# eval/results/query_shopping_lists/20260305_103302/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 165

---

### Purpose
The `pass03_attempt01.py` file contains the `QueryShoppingListsSkill` class, which is responsible for querying active shopping lists and their associated items from a PostgreSQL database and formatting the results for display. This skill is triggered by specific keywords related to shopping lists.

### Architecture
The file is structured around a single class, `QueryShoppingListsSkill`, which inherits from `SkillBase`. The class contains several methods:
- `execute`: The main method that handles the request and orchestrates the query and formatting.
- `_query_lists`: Queries the active shopping lists.
- `_query_items`: Queries the items associated with the shopping lists.
- `_format_results`: Formats the queried lists and items into a readable string.
- `_build_summary`: Builds a summary of the queried lists and items.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: A top-level function that wraps the class method for external use.

### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is established and closed properly.
- **Factory Method**: The `execute` method acts as a factory method, creating and returning a `SkillResponse` object.

### Dependencies
The file imports the following modules:
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

### Interfaces
- **Public Methods**: 
  - `execute`: Takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Private Methods**: 
  - `_query_lists`: Queries active shopping lists.
  - `_query_items`: Queries items associated with the lists.
  - `_format_results`: Formats the results into a readable string.
  - `_build_summary`: Builds a summary of the results.

### Database
The file interacts with the following PostgreSQL tables:
- `shopping_lists`: Stores shopping list information.
- `shopping_list_items`: Stores items associated with each shopping list.
- `shopping_items`: Stores item details.

### Configuration
The file uses environment variables loaded via `dotenv` for database connection details:
- `DB_HOST`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_PORT`

### Key Logic
- **Querying Lists and Items**: The `_query_lists` and `_query_items` methods execute SQL queries to fetch active shopping lists and their associated items.
- **Formatting Results**: The `_format_results` method groups items by list and formats them into a readable string.
- **Building Summary**: The `_build_summary` method provides a summary of the lists and items, including the number of active lists and the number of remaining items in the most recent list.

### Integration Points
- **SkillBase**: The `QueryShoppingListsSkill` class inherits from `SkillBase`, integrating with the Mythos skill system.
- **SkillRequest and SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the request-response flow of the Mythos system.
- **Database Connection**: The `_get_conn` function ensures a consistent way to connect to the PostgreSQL database, integrating with the database layer of Mythos.

This file is a crucial component of the Mythos system, enabling users to query and view their shopping lists and items in a structured and readable format.
