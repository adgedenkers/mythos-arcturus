# eval/results/search_ideas/20260305_062733/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 182

---

### Documentation for `eval/results/search_ideas/20260305_062733/pass04_attempt01.py`

#### Purpose
This file contains the `SearchIdeasSkill` class, which is responsible for searching ideas stored in a PostgreSQL database based on user-provided search terms and filters. It processes user requests, extracts relevant information, and formats the results for display.

#### Architecture
The file is structured around the `SearchIdeasSkill` class, which inherits from `SkillBase`. The class contains several methods to handle different stages of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_filters`: Detects filters like disposition and domain from the user message.
- `_search_ideas`: Executes the database query to search for ideas.
- `_format_results`: Formats the raw query results into a more readable form.
- `_build_summary`: Builds a summary of the search results.

Additionally, there are top-level functions like `_get_conn` for database connection and `execute` for the main execution logic.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function could be considered a singleton as it provides a single connection to the database.
- **Factory Method Pattern**: The `execute` method can be seen as a factory method that orchestrates the creation and processing of search results.

#### Dependencies
- **Imports**: `os`, `logging`, `json`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` from `.env` file.

#### Interfaces
- **Public Methods**: `execute` (async) is the main entry point for executing the skill.
- **Private Methods**: `_extract_search_terms`, `_detect_filters`, `_search_ideas`, `_format_results`, `_build_summary` are used internally to process the search logic.

#### Database
- **Tables/Labels**: The `idea_inbox` table in PostgreSQL is queried to retrieve ideas based on search terms and filters.

#### Configuration
- **Environment Variables**: The PostgreSQL connection details are loaded from environment variables using `dotenv`.
- **Class Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl` are defined in the `SearchIdeasSkill` class.

#### Key Logic
1. **Extract Search Terms**: Removes trigger phrases and strips punctuation from the user message to extract meaningful search terms.
2. **Detect Filters**: Identifies disposition and domain filters from the user message.
3. **Search Ideas**: Constructs and executes a PostgreSQL query to search the `idea_inbox` table based on the extracted terms and filters.
4. **Format Results**: Converts the raw query results into a more readable format.
5. **Build Summary**: Generates a summary of the search results, highlighting the top three results.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the broader Mythos system through the `execute` method.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database, which is a common integration point for database operations in the Mythos system.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes for handling input and output, integrating with the Mythos skill execution framework.

This file is a critical component of the Mythos system, enabling users to search and retrieve ideas from the database based on various criteria.
