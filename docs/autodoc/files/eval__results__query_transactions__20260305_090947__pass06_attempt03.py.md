# eval/results/query_transactions/20260305_090947/pass06_attempt03.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 220

---

### Documentation for `eval/results/query_transactions/20260305_090947/pass06_attempt03.py`

#### Purpose
This file defines a skill (`QueryTransactionsSkill`) for the Mythos system that allows users to query transaction data from a PostgreSQL database based on search terms and account filters. It processes user requests, extracts relevant information, queries the database, formats results, and builds a summary.

#### Architecture
The file contains a single class `QueryTransactionsSkill` that inherits from `SkillBase`. The class includes several methods for processing requests, extracting search terms, detecting account IDs, querying the database, formatting results, and building summaries. Additionally, there are several top-level functions for utility purposes.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create and return a database connection.
- **Singleton**: The `_get_conn` function could be considered a singleton pattern if the connection is intended to be reused throughout the application.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async), `_extract_search_terms`, `_detect_account`, `_query`, `_format_results`, `_build_summary`.
- **Top-Level Functions**: `_get_conn`, `execute`.

#### Database
- **Tables**: `transactions`, `accounts`.
- **Labels**: None (since Neo4j is not used in this file).

#### Configuration
- **Environment Variables**: Used to configure the PostgreSQL connection.
- **Config Files**: `.env` file is loaded using `dotenv`.

#### Key Logic
1. **Extract Search Terms**: `_extract_search_terms` removes common triggers and normalizes the input message to extract meaningful search terms.
2. **Detect Account**: `_detect_account` identifies account IDs based on abbreviations in the input message.
3. **Query Database**: `_query` constructs and executes a PostgreSQL query to fetch transactions based on search terms and account filters.
4. **Format Results**: `_format_results` converts raw query results into a structured format.
5. **Build Summary**: `_build_summary` generates a summary of the query results, including a count and total amount.

#### Integration Points
- **SkillBase**: The `QueryTransactionsSkill` class inherits from `SkillBase`, indicating integration with the Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, indicating integration with the Mythos request/response handling system.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, integrating with the Mythos data storage layer.

### Detailed Breakdown

#### Class: `QueryTransactionsSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: 'query_transactions'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Search transactions by description, merchant, date, amount, or account'
  - `triggers`: List of keywords that trigger this skill.
  - `cache_ttl`: 300 seconds for caching results.
- **Methods**:
  - `execute`: Main method to process the request, extract search terms, detect accounts, query the database, format results, and build a summary.
  - `_extract_search_terms`: Extracts meaningful search terms from the input message.
  - `_detect_account`: Detects account IDs based on abbreviations in the input message.
  - `_query`: Queries the PostgreSQL database for transactions based on search terms and account filters.
  - `_format_results`: Formats the raw query results into a structured format.
  - `_build_summary`: Builds a summary of the query results.

#### Top-Level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **execute**: A top-level function that mirrors the class method `execute` for potential external use.

### Conclusion
This file is a crucial component of the Mythos system, enabling users to query transaction data efficiently. It integrates with the Mythos skill framework, PostgreSQL database, and environment configuration to provide a robust and flexible transaction querying capability.
