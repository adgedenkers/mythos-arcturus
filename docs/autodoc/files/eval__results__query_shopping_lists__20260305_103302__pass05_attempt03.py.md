# eval/results/query_shopping_lists/20260305_103302/pass05_attempt03.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 178

---

### Purpose
The `QueryShoppingListsSkill` class in `pass05_attempt03.py` is designed to query and format shopping lists and their associated items from a PostgreSQL database. It is part of the Mythos system and is triggered by specific keywords related to shopping lists.

### Architecture
The file contains a single class `QueryShoppingListsSkill` that inherits from `SkillBase`. This class contains several methods to handle the querying, formatting, and summarizing of shopping lists and items. Additionally, there are utility functions for database connection and result formatting.

- **Class**: `QueryShoppingListsSkill`
  - **Methods**:
    - `execute`: Main method to handle the execution of the skill.
    - `_query_lists`: Queries active shopping lists from the database.
    - `_query_items`: Queries items associated with specific shopping lists.
    - `_format_results`: Formats the queried lists and items into a readable string.
    - `_build_summary`: Builds a summary of the queried lists and items.

- **Top-level functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: A top-level function that mirrors the class method for potential external use.

### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is established and returned.
- **Factory Method**: The `execute` method acts as a factory method to create and return a `SkillResponse` object.

### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

### Interfaces
- **Exposed Methods**:
  - `execute`: Exposed to other parts of the system to execute the skill and return a `SkillResponse` object.

### Database
- **Tables/Labels**:
  - `shopping_lists`: Stores shopping list information.
  - `shopping_list_items`: Stores items associated with each shopping list.
  - `shopping_items`: Stores item details.

### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: Host of the PostgreSQL database.
  - `DB_NAME`: Name of the PostgreSQL database.
  - `DB_USER`: Username for the PostgreSQL database.
  - `DB_PASSWORD`: Password for the PostgreSQL database.
  - `DB_PORT`: Port for the PostgreSQL database.

### Key Logic
- **_query_lists**: Queries active shopping lists from the `shopping_lists` table.
- **_query_items**: Queries items from the `shopping_list_items` and `shopping_items` tables based on list IDs.
- **_format_results**: Formats the queried lists and items into a human-readable string.
- **_build_summary**: Builds a summary of the queried lists and items, highlighting the most recent list and its items.

### Integration Points
- **Mythos System**:
  - The `QueryShoppingListsSkill` class integrates with the Mythos system through the `SkillBase` class, which likely handles the overall skill execution framework.
  - The `execute` method is designed to be called by the Mythos system when specific triggers (like "shopping list" or "groceries") are detected in user queries.

### Detailed Breakdown

#### `_get_conn`
- Establishes a connection to the PostgreSQL database using environment variables for configuration.
- Uses `psycopg2` with `RealDictCursor` to return rows as dictionaries.

#### `QueryShoppingListsSkill`
- **Attributes**:
  - `name`: The name of the skill.
  - `triggers`: List of keywords that trigger this skill.
  - `cache_ttl`: Time-to-live for caching results.

- **Methods**:
  - `execute`: Main method to execute the skill, connecting to the database, querying lists and items, formatting results, and building a summary.
  - `_query_lists`: Queries active shopping lists from the `shopping_lists` table.
  - `_query_items`: Queries items from the `shopping_list_items` and `shopping_items` tables based on list IDs.
  - `_format_results`: Formats the queried lists and items into a human-readable string.
  - `_build_summary`: Builds a summary of the queried lists and items, highlighting the most recent list and its items.

### Summary
This file provides a comprehensive skill for querying and summarizing shopping lists and their items from a PostgreSQL database. It integrates seamlessly with the Mythos system, handling database connections, querying, formatting, and summarizing results based on user triggers.
