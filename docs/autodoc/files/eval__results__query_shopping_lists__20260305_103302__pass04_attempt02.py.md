# eval/results/query_shopping_lists/20260305_103302/pass04_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 168

---

### Documentation for `20260305_103302/pass04_attempt02.py`

#### Purpose
This file contains the implementation of the `QueryShoppingListsSkill` class, which is responsible for querying active shopping lists and their items from a PostgreSQL database and formatting the results for a user-friendly response.

#### Architecture
The file is structured around a single class `QueryShoppingListsSkill` that inherits from `SkillBase`. The class contains several methods for executing the query, fetching lists and items, formatting results, and building a summary. Additionally, there are top-level functions for database connection and execution.

- **Classes:**
  - `QueryShoppingListsSkill`: Inherits from `SkillBase` and implements methods for querying and formatting shopping lists and items.

- **Methods:**
  - `execute`: Main method that orchestrates the querying and formatting process.
  - `_query_lists`: Fetches active shopping lists from the database.
  - `_query_items`: Fetches items associated with the given list IDs.
  - `_format_results`: Formats the lists and items into a user-readable string.
  - `_build_summary`: Builds a summary of the lists and items.

- **Top-level Functions:**
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: A top-level function that might be used for testing or direct execution.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single connection is established and reused.
- **Factory Method**: The `execute` method acts as a factory method, creating and returning a `SkillResponse` object.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` is the primary method exposed to other parts of the system.
- **Data Structures**: `SkillRequest` and `SkillResponse` are used to pass and return data.

#### Database
- **Tables**: `shopping_lists`, `shopping_list_items`, `shopping_items`.
- **Queries**:
  - `_query_lists`: Queries `shopping_lists` for active lists.
  - `_query_items`: Queries `shopping_list_items` and `shopping_items` for items associated with the given list IDs.

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables using `dotenv`.
- **Class Variables**: `name`, `triggers`, `cache_ttl` are class variables used to configure the skill.

#### Key Logic
- **Query Execution**: The `execute` method fetches lists and items, formats the results, and builds a summary.
- **Result Formatting**: `_format_results` groups items by list and formats them into a readable string.
- **Summary Building**: `_build_summary` provides a concise summary of the lists and items.

#### Integration Points
- **SkillBase**: The class inherits from `SkillBase` and integrates with the Mythos skill system.
- **Database Connection**: Uses `psycopg2` to connect to and query the PostgreSQL database.
- **Response Handling**: Returns `SkillResponse` objects to the Mythos system for further processing.

### Detailed Breakdown

1. **Class `QueryShoppingListsSkill`**:
   - **Attributes**:
     - `name`: Name of the skill.
     - `triggers`: List of keywords that trigger this skill.
     - `cache_ttl`: Time to live for caching results.
   - **Methods**:
     - `execute`: Main method that handles the entire process of querying and formatting.
     - `_query_lists`: Fetches active shopping lists.
     - `_query_items`: Fetches items for the given list IDs.
     - `_format_results`: Formats the lists and items into a user-readable string.
     - `_build_summary`: Builds a summary of the lists and items.

2. **Top-level Functions**:
   - `_get_conn`: Establishes a connection to the PostgreSQL database.
   - `execute`: A top-level function that might be used for testing or direct execution.

3. **Database Interaction**:
   - Uses `psycopg2` to connect to the PostgreSQL database.
   - Queries `shopping_lists` and `shopping_list_items` tables to fetch lists and items.

4. **Result Formatting**:
   - `_format_results` groups items by list and formats them into a readable string.
   - `_build_summary` provides a concise summary of the lists and items.

5. **Error Handling**:
   - Uses `try-except` blocks to handle exceptions and log errors.

This file is a critical component of the Mythos system, providing a robust and user-friendly way to query and present shopping lists and items.
