# eval/results/query_transactions/20260305_090947/pass01_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 63

---

### File: `eval/results/query_transactions/20260305_090947/pass01_attempt01.py`

#### Purpose
This file contains the `QueryTransactionsSkill` class, which is designed to handle user requests to query transaction data from a PostgreSQL database. It extracts search terms from user messages, detects account identifiers, queries the database, formats the results, and builds a summary.

#### Architecture
- **Class**: `QueryTransactionsSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: The main method that processes the request and orchestrates the extraction of search terms, account detection, querying, and result formatting.
  - `_extract_search_terms`: Extracts search terms from the user message.
  - `_detect_account`: Detects account identifiers from the user message.
  - `_query`: Queries the database based on search terms and account identifiers.
  - `_format_results`: Formats the query results.
  - `_build_summary`: Builds a summary of the query results.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: A top-level function that mirrors the class method for potential direct use.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern for database connection management.
- **Factory**: The `_query` method can be seen as a factory method that produces a list of transaction results based on input parameters.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging purposes.
  - `psycopg2`: For PostgreSQL database interaction.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Public Methods**:
  - `execute`: Processes the request and returns a `SkillResponse` object.
- **Private Methods**:
  - `_extract_search_terms`: Extracts search terms from the message.
  - `_detect_account`: Detects account identifiers from the message.
  - `_query`: Queries the database based on search terms and account identifiers.
  - `_format_results`: Formats the query results.
  - `_build_summary`: Builds a summary of the query results.

#### Database
- **Tables/Labels**:
  - `accounts`: Used to join account information with transaction data.
  - `transactions`: The primary table containing transaction data.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Used to configure the PostgreSQL database connection.

#### Key Logic
- **Execution Flow**:
  1. Extract search terms and detect account identifiers from the user message.
  2. If no terms or filters are provided, return the most recent 10 transactions.
  3. Query the database using `ILIKE` on description or merchant name, with optional account filters.
  4. Format the results to include amount, merchant, date, and account.
  5. Build a summary of the total amount spent and the count of transactions.

#### Integration Points
- **Mythos Subsystems**:
  - **Skill Engine**: The `QueryTransactionsSkill` class is part of the skill engine and integrates with the skill execution framework.
  - **Database Layer**: Uses `psycopg2` to interact with the PostgreSQL database.
  - **Logging**: Uses the `logging` module to log relevant information during execution.
  - **Environment Configuration**: Loads environment variables using `dotenv` for database connection details.

This file is a critical component of the Mythos system, enabling users to query transaction data based on various search terms and account identifiers, and providing formatted results and summaries.
