# eval/results/query_shopping_lists/20260305_103302/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 178

---

### Documentation for `test_skill.py`

#### Purpose
The `test_skill.py` file defines a `QueryShoppingListsSkill` class that handles the retrieval and formatting of shopping lists and their items from a PostgreSQL database. This skill is triggered by specific keywords and provides a summary of active shopping lists along with detailed item information.

#### Architecture
The file contains a single class `QueryShoppingListsSkill` that inherits from `SkillBase`. The class has several methods to handle the execution of the skill, querying the database, formatting results, and building summaries. Additionally, there are top-level functions for establishing a database connection and executing queries.

- **Class**: `QueryShoppingListsSkill`
  - **Methods**: `execute`, `_query_lists`, `_query_items`, `_format_results`, `_build_summary`
- **Top-level Functions**: `_get_conn`, `execute`, `_query_lists`, `_query_items`, `_format_results`, `_build_summary`

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is established and closed properly.
- **Factory Method Pattern**: The `execute` method acts as a factory method to create and return a `SkillResponse` object.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute`
- **Private Methods**: `_query_lists`, `_query_items`, `_format_results`, `_build_summary`
- **Top-level Functions**: `_get_conn`

#### Database
- **Tables**: `shopping_lists`, `shopping_list_items`, `shopping_items`
- **Queries**:
  - `SELECT id, name, status, created_at FROM shopping_lists WHERE is_active = true ORDER BY created_at DESC`
  - `SELECT sli.id, si.name as item_name, si.department, sli.quantity, sli.priority, sli.completed, sli.notes FROM shopping_list_items sli JOIN shopping_items si ON si.id = sli.item_id WHERE sli.list_id IN (...) ORDER BY sli.completed, si.department, si.name`

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`
- **Configuration File**: `.env` (loaded using `dotenv`)

#### Key Logic
- **Database Connection**: Establishes a connection to the PostgreSQL database using `psycopg2`.
- **Query Execution**: Queries active shopping lists and their items, formats the results, and builds a summary.
- **Result Formatting**: Groups items by list and formats them into a readable string.
- **Summary Building**: Constructs a summary of active lists and their items, highlighting uncompleted items.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill system.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` for input and output.
- **Database**: Connects to the PostgreSQL database to retrieve shopping lists and items.
- **Logging**: Uses `logging` to log errors and information.

### Detailed Breakdown

#### `_get_conn` Function
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Dependencies**: `psycopg2`, `os`, `dotenv`
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`
- **Returns**: Database connection object

#### `QueryShoppingListsSkill` Class
- **Attributes**:
  - `name`: Name of the skill (`'query_shopping_lists'`)
  - `triggers`: List of keywords that trigger the skill
  - `cache_ttl`: Time-to-live for caching results (300 seconds)
- **Methods**:
  - `execute`: Main method that handles the execution of the skill, querying the database, formatting results, and building a summary.
  - `_query_lists`: Queries active shopping lists from the `shopping_lists` table.
  - `_query_items`: Queries items for the given list IDs from the `shopping_list_items` and `shopping_items` tables.
  - `_format_results`: Formats the queried lists and items into a readable string.
  - `_build_summary`: Builds a summary of active lists and their items.

#### Top-level Functions
- **Purpose**: These functions are not part of the class and are used for specific tasks.
- **Dependencies**: `psycopg2`, `logging`, `os`, `dotenv`
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

### Conclusion
The `test_skill.py` file is a crucial component of the Mythos system, responsible for querying and formatting shopping lists and their items from a PostgreSQL database. It integrates with the skill system, uses environment variables for configuration, and provides detailed summaries and formatted results.
