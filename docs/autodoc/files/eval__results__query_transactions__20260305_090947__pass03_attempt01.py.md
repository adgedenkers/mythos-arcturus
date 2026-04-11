# eval/results/query_transactions/20260305_090947/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 145

---

### Documentation for `eval/results/query_transactions/20260305_090947/pass03_attempt01.py`

#### Purpose
This file contains the `QueryTransactionsSkill` class, which is designed to query transaction data from a PostgreSQL database based on user input. It processes user messages to extract search terms and account filters, queries the database, formats the results, and builds a summary.

#### Architecture
The file consists of a single class `QueryTransactionsSkill` that inherits from `SkillBase`. The class contains several methods for different stages of processing user requests:
- `_extract_search_terms`: Extracts and cleans search terms from the user message.
- `_detect_account`: Detects account abbreviations in the user message.
- `_query`: Executes the database query based on search terms and account filters.
- `_format_results`: Formats the raw query results.
- `_build_summary`: Builds a summary of the query results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: The main entry point for processing user requests.

#### Patterns
- **Factory Method**: `_get_conn` can be seen as a factory method for creating database connections.
- **Singleton**: The database connection is managed within `_get_conn`, ensuring a consistent connection setup.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging purposes.
- `psycopg2`: For PostgreSQL database interactions.
- `string`: For string manipulation.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase` class and related types.

#### Interfaces
- **Public Methods**:
  - `execute`: Asynchronous method that processes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**:
  - `_extract_search_terms`: Extracts and cleans search terms from the user message.
  - `_detect_account`: Detects account abbreviations in the user message.
  - `_query`: Executes the database query.
  - `_format_results`: Formats the raw query results.
  - `_build_summary`: Builds a summary of the query results.

#### Database
- **Tables/Labels**:
  - `transactions`: Table containing transaction data.
  - `accounts`: Table containing account data.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`: Host of the PostgreSQL database.
  - `DB_NAME`: Name of the PostgreSQL database.
  - `DB_USER`: Username for the PostgreSQL database.
  - `DB_PASSWORD`: Password for the PostgreSQL database.
  - `DB_PORT`: Port of the PostgreSQL database.

#### Key Logic
1. **Extract Search Terms**: The `_extract_search_terms` method removes predefined triggers and normalizes the user message to extract meaningful search terms.
2. **Detect Account**: The `_detect_account` method checks for account abbreviations in the user message.
3. **Query Execution**: The `_query` method constructs and executes a PostgreSQL query based on the extracted search terms and detected account filters.
4. **Result Formatting**: The `_format_results` method formats the raw query results into a more user-friendly format.
5. **Summary Building**: The `_build_summary` method generates a summary of the query results, including total amount spent and count.

#### Integration Points
- **SkillBase Integration**: The `QueryTransactionsSkill` class inherits from `SkillBase`, integrating with the broader Mythos system's skill framework.
- **Database Integration**: The `_query` method interacts with the PostgreSQL database to fetch transaction data.
- **Environment Variables**: The `_get_conn` function uses environment variables to establish a database connection, ensuring seamless integration with the system's configuration.

This file is a crucial component of the Mythos system, enabling users to query and analyze transaction data based on various filters and search terms.
