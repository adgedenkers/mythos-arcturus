# eval/results/search_conversations/20260305_061549/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 197

---

### File: eval/results/search_conversations/20260305_061549/pass06_attempt01.py

#### Purpose
This file contains the implementation of a skill (`SearchConversationsSkill`) for the Mythos system that allows users to search through conversation history by keyword. It handles the extraction of search terms from user messages, querying the PostgreSQL database for matching conversation turns, formatting the results, and building a summary of the findings.

#### Architecture
The file is structured around a single class `SearchConversationsSkill` that inherits from `SkillBase`. The class contains several methods to handle different aspects of the search process:
- `_extract_search_terms`: Extracts and cleans search terms from the user message.
- `_search_turns`: Queries the PostgreSQL database for conversation turns that match the search terms.
- `_format_results`: Formats the raw query results into a more readable form.
- `_build_summary`: Constructs a summary of the search results.
- `execute`: The main method that orchestrates the search process and returns the final response.

#### Patterns
- **Singleton**: The `_get_conn` function is used to get a database connection, which can be considered a singleton pattern as it ensures a single connection is used throughout the operations.
- **Factory**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object based on the search results.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: Uses `os.getenv` to load configuration from environment variables (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`).

#### Interfaces
- **Public Methods**: The `execute` method is the primary interface for executing the search operation.
- **SkillResponse**: The class returns `SkillResponse` objects, which are used to communicate the results back to the system.

#### Database
- **Tables**: The file interacts with the `conversation_turns` table in PostgreSQL.
- **Operations**: Performs `SELECT` operations to retrieve conversation turns based on search terms.

#### Configuration
- **Environment Variables**: Configuration for the PostgreSQL connection is loaded from environment variables.
- **Dotenv**: Uses `load_dotenv` to load configuration from a `.env` file located at `/opt/mythos/.env`.

#### Key Logic
- **Search Term Extraction**: The `_extract_search_terms` method cleans the user message by removing trigger phrases and normalizing whitespace.
- **Database Query**: The `_search_turns` method constructs and executes a PostgreSQL query to find conversation turns that match the search terms.
- **Result Formatting**: The `_format_results` method formats the raw query results into a more readable form, truncating content previews and formatting dates.
- **Summary Construction**: The `_build_summary` method constructs a summary of the search results, showing up to three previews.

#### Integration Points
- **SkillBase**: The `SearchConversationsSkill` class inherits from `SkillBase`, integrating with the broader Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object, integrating with the Mythos request-response model.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database, integrating with the Mythos database infrastructure.

### Summary
This file implements a search skill for the Mythos system, allowing users to search through conversation history by keyword. It handles the extraction of search terms, querying the PostgreSQL database, formatting the results, and building a summary. The skill integrates with the Mythos framework through the `SkillBase` class and the `SkillRequest`/`SkillResponse` objects, and it connects to the PostgreSQL database using a singleton-like connection method.
