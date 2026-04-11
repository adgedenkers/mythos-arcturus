# eval/results/search_ideas/20260305_062733/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 231

---

### Documentation for `pass05_attempt01.py`

#### Purpose
This file contains the `SearchIdeasSkill` class, which is responsible for searching the idea inbox in the Mythos system based on keywords, domain, or status. It processes user requests to extract search terms and filters, performs the search, formats the results, and builds a summary.

#### Architecture
The file is structured around a single class, `SearchIdeasSkill`, which inherits from `SkillBase`. The class contains several methods to handle different aspects of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_filters`: Detects filters (disposition and domain) from the user message.
- `_search_ideas`: Executes the database query to search for ideas based on the provided terms and filters.
- `_format_results`: Formats the raw search results into a more readable form.
- `_build_summary`: Builds a summary of the search results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: The main entry point for the skill, orchestrating the search process.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single connection is returned.
- **Factory**: The `execute` method acts as a factory, orchestrating the creation and processing of search terms, filters, and results.

#### Dependencies
- **Imports**: `os`, `logging`, `json`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`

#### Interfaces
- **Public Methods**: `execute` is the primary method exposed to other parts of the system, which takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**: `_extract_search_terms`, `_detect_filters`, `_search_ideas`, `_format_results`, `_build_summary` are used internally by `execute`.

#### Database
- **Tables**: `idea_inbox`
- **Operations**: Reads from `idea_inbox` to fetch ideas based on search terms and filters.

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables using `dotenv`.
- **Configuration File**: `.env` file located at `/opt/mythos/.env`.

#### Key Logic
1. **Extract Search Terms**: Removes trigger phrases and strips punctuation from the user message to extract meaningful search terms.
2. **Detect Filters**: Identifies disposition and domain filters from the user message.
3. **Search Ideas**: Constructs a PostgreSQL query to search the `idea_inbox` table based on the extracted terms and filters.
4. **Format Results**: Converts raw query results into a more readable format.
5. **Build Summary**: Generates a summary of the search results, including a count and top 3 matches.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase`, integrating with the Mythos skill framework.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database, integrating with the database subsystem.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` to communicate with the Mythos skill execution framework.

### Summary
The `SearchIdeasSkill` class in `pass05_attempt01.py` is designed to handle user requests for searching the idea inbox in the Mythos system. It processes the user message to extract search terms and filters, performs a database query to fetch relevant ideas, formats the results, and builds a summary. The class integrates with the Mythos skill framework and the PostgreSQL database subsystem.
