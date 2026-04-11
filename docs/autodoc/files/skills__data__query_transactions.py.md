# skills/data/query_transactions.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 207

---

### File: skills/data/query_transactions.py

#### Purpose
This file implements the `QueryTransactionsSkill` class, which handles the querying of transaction data from a PostgreSQL database based on user input. It extracts search terms and account filters from the user's message, queries the database, formats the results, and builds a summary.

#### Architecture
- **Class**: `QueryTransactionsSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: Main method that processes the request, extracts search terms, detects account, queries the database, formats results, and builds a summary.
  - `_extract_search_terms`: Extracts and cleans search terms from the user's message.
  - `_detect_account`: Detects the account ID based on abbreviations in the user's message.
  - `_query`: Executes the database query to fetch transactions based on search terms and account ID.
  - `_format_results`: Formats the raw query results into a more readable form.
  - `_build_summary`: Builds a summary of the query results.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: An additional top-level `execute` function, likely a typo or leftover from development.

#### Patterns
- **Singleton**: The `_get_conn` function could be considered a singleton pattern for database connection management, though it is not explicitly enforced.
- **Factory**: The `SkillResponse` object creation can be seen as a factory method for creating response objects.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Exposed Methods**: `execute` is the primary method exposed to other parts of the system for executing the skill.
- **SkillBase Inheritance**: Inherits from `SkillBase`, which likely defines a common interface for skills in the Mythos system.

#### Database
- **Tables**: `transactions`, `accounts`.
- **Queries**: Uses `ILIKE` for case-insensitive searches on `description` and `merchant_name` in the `transactions` table. Joins with `accounts` table to get account details.

#### Configuration
- **Environment Variables**: Uses `dotenv` to load environment variables for database connection details.
- **Class Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl` are defined in the `QueryTransactionsSkill` class.

#### Key Logic
- **Search Term Extraction**: Cleans and normalizes the user's message to extract meaningful search terms.
- **Account Detection**: Detects account IDs based on predefined abbreviations in the user's message.
- **Database Query**: Constructs and executes a PostgreSQL query to fetch transactions based on search terms and account ID.
- **Result Formatting**: Converts raw query results into a more readable format.
- **Summary Building**: Generates a summary of the query results, including a total amount and top 3 transactions.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase`, integrating with the Mythos skill system.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database.
- **SkillResponse**: Uses `SkillResponse` to return results to the calling system.
- **Environment Variables**: Uses environment variables for database configuration, integrating with the system's configuration management.

This file is a critical component of the Mythos system, enabling users to query transaction data based on various filters and providing a structured response with a summary.
