# eval/results/search_ideas/20260305_062733/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 123

---

### File: eval/results/search_ideas/20260305_062733/pass02_attempt01.py

#### Purpose
This file defines a `SearchIdeasSkill` class that implements a skill for searching ideas within the Mythos system. The skill processes user requests to search the idea inbox based on keywords, domain, or status.

#### Architecture
The file contains a single class `SearchIdeasSkill` that inherits from `SkillBase`. The class has several methods to handle different stages of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_filters`: Detects filters (domain and disposition) from the user message.
- `_search_ideas`: Performs the actual search in the database.
- `_format_results`: Formats the search results.
- `_build_summary`: Builds a summary of the search results.

Additionally, there are top-level functions `_get_conn`, `execute`, `_extract_search_terms`, `_detect_filters`, `_search_ideas`, `_format_results`, and `_build_summary`.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create a database connection.
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it returns a single database connection object.

#### Dependencies
- **Imports**: `os`, `logging`, `json`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` are loaded from `.env` file.

#### Interfaces
- **Public Methods**: `execute` (async) is the main entry point for executing the skill.
- **Private Methods**: `_extract_search_terms`, `_detect_filters`, `_search_ideas`, `_format_results`, `_build_summary` are helper methods used internally by `execute`.

#### Database
- **PostgreSQL**: The file interacts with a PostgreSQL database using `psycopg2`. The connection is established using `_get_conn` function.
- **Tables**: The file references the PostgreSQL database but does not specify exact table names. The `_search_ideas` method likely queries a table containing ideas.

#### Configuration
- **Environment Variables**: Configuration is loaded from a `.env` file using `dotenv.load_dotenv('/opt/mythos/.env')`.

#### Key Logic
1. **Extract Search Terms**: `_extract_search_terms` removes trigger phrases and strips punctuation from the user message.
2. **Detect Filters**: `_detect_filters` identifies disposition and domain filters from the user message.
3. **Search Ideas**: `_search_ideas` performs the search using `ILIKE` on `conversation_context` and `chosen_text` fields, with optional filters for disposition and domain.
4. **Format Results**: `_format_results` formats the raw search results.
5. **Build Summary**: `_build_summary` creates a summary of the search results.

#### Integration Points
- **SkillBase**: The `SearchIdeasSkill` class inherits from `SkillBase`, indicating it integrates with the Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method takes `SkillRequest` and returns `SkillResponse`, indicating integration with the request-response model of the Mythos system.
- **Database**: The skill interacts with the PostgreSQL database to retrieve and process idea data.
- **Logging**: Uses `logging` to log information and errors, which can be integrated with the Mythos logging system.

### Summary
This file implements a skill for searching ideas within the Mythos system. It processes user requests to extract search terms and filters, performs the search in the PostgreSQL database, and formats the results. The skill is designed to integrate with the Mythos skill framework and uses environment variables for configuration.
