# eval/results/search_conversations/20260305_061549/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 197

---

### File: `eval/results/search_conversations/20260305_061549/temp_skill/test_skill.py`

#### Purpose
This file defines a skill named `SearchConversationsSkill` that allows users to search through conversation history based on keywords. It processes user requests, extracts search terms, searches the conversation turns in a PostgreSQL database, formats the results, and builds a summary.

#### Architecture
The file contains a single class `SearchConversationsSkill` that inherits from `SkillBase`. The class has several methods to handle different stages of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_search_turns`: Searches the conversation turns in the PostgreSQL database.
- `_format_results`: Formats the search results into a readable format.
- `_build_summary`: Builds a human-readable summary of the search results.
- `execute`: The main method that orchestrates the search process.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: An asynchronous function that handles the execution of the skill.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single connection to the PostgreSQL database.
- **Factory**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object based on the search results.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async) is the primary method exposed to other parts of the system.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object containing the search results and summary.

#### Database
- **Tables**: The file interacts with the `conversation_turns` table in the PostgreSQL database.
- **Operations**: It performs `SELECT` operations to retrieve conversation turns based on search terms.

#### Configuration
- **Environment Variables**: The file loads environment variables from `.env` using `dotenv` to configure the PostgreSQL connection.
- **Class Attributes**: The `SearchConversationsSkill` class has attributes like `name`, `version`, `category`, `description`, `triggers`, and `cache_ttl`.

#### Key Logic
1. **Extract Search Terms**: The `_extract_search_terms` method cleans the user message by removing trigger phrases and normalizing the remaining text.
2. **Search Turns**: The `_search_turns` method queries the `conversation_turns` table using the `ILIKE` operator to find matching conversation turns.
3. **Format Results**: The `_format_results` method formats the raw query results into a more readable format, truncating content previews and formatting dates.
4. **Build Summary**: The `_build_summary` method creates a summary of the search results, showing up to three previews.

#### Integration Points
- **SkillBase**: The `SearchConversationsSkill` class inherits from `SkillBase`, integrating with the broader Mythos skill system.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, integrating with the request-response model of the Mythos system.
- **Database Connection**: The `_get_conn` function establishes a connection to the PostgreSQL database, integrating with the Mythos data storage layer.

This file is a crucial component of the Mythos system, enabling users to query and retrieve conversation history based on specific keywords, thereby enhancing the system's conversational capabilities.
