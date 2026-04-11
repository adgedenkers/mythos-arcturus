# eval/results/search_ideas/20260305_062733/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 221

---

### File: `eval/results/search_ideas/20260305_062733/pass06_attempt01.py`

#### Purpose
This file contains the implementation of the `SearchIdeasSkill` class, which is responsible for searching ideas stored in the `idea_inbox` table in PostgreSQL. It processes user requests to extract search terms and filters, performs the search, formats the results, and builds a summary.

#### Architecture
The file contains a single class `SearchIdeasSkill` that inherits from `SkillBase`. The class has several methods to handle different stages of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_filters`: Detects filters (disposition and domain) from the user message.
- `_search_ideas`: Executes the search query on the `idea_inbox` table.
- `_format_results`: Formats the search results.
- `_build_summary`: Builds a summary of the search results.
- `execute`: The main method that orchestrates the entire search process.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it provides a single connection to the PostgreSQL database.
- **Factory**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object.

#### Dependencies
- **Imports**: `os`, `logging`, `json`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async) which takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**: `_extract_search_terms`, `_detect_filters`, `_search_ideas`, `_format_results`, `_build_summary`.

#### Database
- **Tables**: `idea_inbox` (PostgreSQL).
- **Operations**: 
  - **Read**: Queries the `idea_inbox` table to retrieve ideas based on search terms and filters.
  - **Count**: Retrieves the count of pending ideas.

#### Configuration
- **Environment Variables**: Configured using `dotenv` to load PostgreSQL connection details.
- **Configuration File**: `.env` located at `/opt/mythos/.env`.

#### Key Logic
1. **Extract Search Terms**: The `_extract_search_terms` method removes trigger phrases and strips punctuation from the user message to extract meaningful search terms.
2. **Detect Filters**: The `_detect_filters` method identifies disposition and domain filters from the user message.
3. **Search Execution**: The `_search_ideas` method constructs and executes a PostgreSQL query to search the `idea_inbox` table based on the extracted terms and filters.
4. **Result Formatting**: The `_format_results` method formats the search results to a more readable form.
5. **Summary Building**: The `_build_summary` method generates a summary of the search results.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos system's skill framework.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` to handle input and output.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database, which is part of the Mythos infrastructure.

### Summary
This file implements the `SearchIdeasSkill` class, which is designed to search ideas in the PostgreSQL `idea_inbox` table based on user requests. It handles the extraction of search terms and filters, performs the search, formats the results, and builds a summary, all while integrating with the Mythos system's skill framework.
