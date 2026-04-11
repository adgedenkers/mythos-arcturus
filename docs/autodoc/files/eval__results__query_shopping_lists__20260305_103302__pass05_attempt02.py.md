# eval/results/query_shopping_lists/20260305_103302/pass05_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 177

---

### File: `eval/results/query_shopping_lists/20260305_103302/pass05_attempt02.py`

#### Purpose
This file contains the implementation of a skill (`QueryShoppingListsSkill`) that queries active shopping lists and their items from a PostgreSQL database and formats the results into a human-readable summary.

#### Architecture
The file consists of a single class `QueryShoppingListsSkill` that extends `SkillBase`. The class contains methods for executing the skill, querying lists and items, formatting results, and building a summary. Additionally, there are top-level functions for getting the database connection and executing the skill.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is created per execution.
- **Facade Pattern**: The `execute` method acts as a facade, abstracting the complex operations of querying lists, items, formatting results, and building a summary.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: Executes the skill and returns a formatted response.
- **Private Methods**:
  - `_query_lists(conn)`: Queries active shopping lists.
  - `_query_items(conn, list_ids)`: Queries items for given list IDs.
  - `_format_results(lists, items)`: Formats the lists and items into a human-readable string.
  - `_build_summary(lists, items)`: Builds a summary of the lists and items.

#### Database
- **Tables/Labels**:
  - `shopping_lists`: Stores shopping lists.
  - `shopping_list_items`: Stores items associated with each list.
  - `shopping_items`: Stores individual items.

#### Configuration
- **Environment Variables**: The database connection details are loaded from environment variables (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`).

#### Key Logic
- **Query Execution**: The `execute` method orchestrates the querying of lists and items, formatting the results, and building a summary.
- **Database Connection**: The `_get_conn` function establishes a connection to the PostgreSQL database using environment variables.
- **Result Formatting**: The `_format_results` method groups items by list and formats them into a string.
- **Summary Building**: The `_build_summary` method generates a summary of the lists and items, including counts and top items.

#### Integration Points
- **SkillBase**: The class extends `SkillBase` and integrates with the Mythos skill system.
- **Database**: The skill interacts with the PostgreSQL database to retrieve shopping lists and items.
- **Response**: The skill returns a `SkillResponse` object, which is used by the Mythos system to handle the response.

### Detailed Analysis

#### Classes
- **QueryShoppingListsSkill**
  - **Inheritance**: Extends `SkillBase`.
  - **Attributes**:
    - `name`: 'query_shopping_lists'.
    - `triggers`: List of trigger phrases.
    - `cache_ttl`: Time-to-live for caching results.
  - **Methods**:
    - `execute(request: SkillRequest) -> SkillResponse`: Main method to execute the skill.
    - `_query_lists(conn)`: Queries active shopping lists.
    - `_query_items(conn, list_ids)`: Queries items for given list IDs.
    - `_format_results(lists, items)`: Formats the lists and items into a human-readable string.
    - `_build_summary(lists, items)`: Builds a summary of the lists and items.

#### Top-level Functions
- **_get_conn()**: Establishes a connection to the PostgreSQL database.
- **execute(request: SkillRequest) -> SkillResponse**: Executes the skill and returns a formatted response.

#### Database Operations
- **_query_lists(conn)**: Queries active shopping lists from the `shopping_lists` table.
- **_query_items(conn, list_ids)**: Queries items from the `shopping_list_items` and `shopping_items` tables for given list IDs.

#### Result Formatting
- **_format_results(lists, items)**: Groups items by list and formats them into a string.
- **_build_summary(lists, items)**: Generates a summary of the lists and items, including counts and top items.

#### Logging and Error Handling
- **Logging**: Errors are logged using `logging.error`.
- **Error Handling**: Exceptions are caught and re-raised to ensure proper error handling and resource cleanup.

This file is a critical component of the Mythos system, providing a robust mechanism for querying and summarizing shopping lists and items from the PostgreSQL database.
