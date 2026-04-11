# eval/results/search_ideas/20260305_062733/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 221

---

### Documentation for `test_skill.py`

#### Purpose
The `test_skill.py` file implements the `SearchIdeasSkill` class, which is responsible for searching ideas stored in the `idea_inbox` table of the PostgreSQL database. It processes user requests to extract search terms and filters, performs the search, and formats the results.

#### Architecture
The file contains a single class `SearchIdeasSkill` that inherits from `SkillBase`. The class has several methods to handle different stages of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_filters`: Detects filters (disposition and domain) from the user message.
- `_search_ideas`: Executes the search query on the `idea_inbox` table.
- `_format_results`: Formats the search results.
- `_build_summary`: Builds a summary of the search results.

The file also includes a top-level function `_get_conn` to establish a connection to the PostgreSQL database.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton as it provides a single connection to the PostgreSQL database.
- **Factory Method Pattern**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object based on the search results.

#### Dependencies
- **Imports**: `os`, `logging`, `json`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async) - Processes the user request and returns a `SkillResponse` object.
- **Private Methods**: `_extract_search_terms`, `_detect_filters`, `_search_ideas`, `_format_results`, `_build_summary`.

#### Database
- **Tables**: `idea_inbox` - The table where ideas are stored.
- **Operations**: 
  - **Read**: `SELECT COUNT(*) as total FROM idea_inbox WHERE disposition = 'pending'`
  - **Read**: `SELECT id, conversation_context, items, item_count, chosen_text, disposition, domain, tags, created_at FROM idea_inbox WHERE 1=1` (with dynamic conditions based on search terms and filters).

#### Configuration
- **Environment Variables**: The file uses environment variables to configure the PostgreSQL connection details.
- **Dotenv**: Loads environment variables from `.env` file located at `/opt/mythos/.env`.

#### Key Logic
1. **Extract Search Terms**: The `_extract_search_terms` method removes trigger phrases and strips punctuation from the user message to extract meaningful search terms.
2. **Detect Filters**: The `_detect_filters` method identifies disposition and domain filters from the user message.
3. **Search Ideas**: The `_search_ideas` method constructs and executes a dynamic SQL query to search the `idea_inbox` table based on the extracted terms and filters.
4. **Format Results**: The `_format_results` method formats the raw search results into a more readable form.
5. **Build Summary**: The `_build_summary` method generates a summary of the search results.

#### Integration Points
- **SkillBase**: The `SearchIdeasSkill` class inherits from `SkillBase`, which likely provides a framework for handling user requests and responses.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the broader Mythos system for request handling and response generation.
- **PostgreSQL**: The `_get_conn` function and methods that interact with the `idea_inbox` table integrate with the PostgreSQL database to perform searches and retrieve results.

This file is a crucial component of the Mythos system, enabling users to search and retrieve ideas based on various criteria, and it integrates seamlessly with the PostgreSQL database and the broader Mythos framework.
