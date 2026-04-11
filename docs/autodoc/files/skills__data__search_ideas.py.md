# skills/data/search_ideas.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 221

---

### Documentation for `skills/data/search_ideas.py`

#### Purpose
This file implements the `SearchIdeasSkill` class, which is responsible for searching the idea inbox in the Mythos system based on user-provided search terms and filters. It handles extraction of search terms, detection of filters, execution of the search query, formatting of results, and building a summary of the search.

#### Architecture
The file contains a single class `SearchIdeasSkill` that inherits from `SkillBase`. The class has several methods for different stages of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_filters`: Detects filters such as disposition and domain from the user message.
- `_search_ideas`: Executes the search query on the PostgreSQL database.
- `_format_results`: Formats the search results for display.
- `_build_summary`: Builds a summary of the search results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: The main method that orchestrates the search process.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create database connections.
- **Singleton**: The `_get_conn` function ensures a consistent way to get a database connection, which can be considered a singleton pattern for database connections.

#### Dependencies
- `os`: For environment variable access.
- `logging`: For logging errors.
- `json`: For JSON handling.
- `psycopg2`: For PostgreSQL database interactions.
- `dotenv`: For loading environment variables from a `.env` file.
- `string`: For string manipulation.

#### Interfaces
- **Public Methods**: 
  - `execute`: The main entry point for the skill, which takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**:
  - `_extract_search_terms`: Extracts search terms from the message.
  - `_detect_filters`: Detects filters from the message.
  - `_search_ideas`: Executes the search query.
  - `_format_results`: Formats the search results.
  - `_build_summary`: Builds a summary of the search results.

#### Database
- **Tables/Labels**: 
  - `idea_inbox`: The table in the PostgreSQL database where ideas are stored. The skill reads from this table to retrieve ideas based on search terms and filters.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configuration for the PostgreSQL database connection.
- **Config Files**: 
  - `.env`: Loaded using `dotenv` to provide environment variables.

#### Key Logic
1. **Search Term Extraction**: The `_extract_search_terms` method removes trigger phrases and strips punctuation from the message to extract meaningful search terms.
2. **Filter Detection**: The `_detect_filters` method identifies disposition and domain filters from the message.
3. **Database Query**: The `_search_ideas` method constructs and executes a PostgreSQL query to search the `idea_inbox` table based on the extracted terms and detected filters.
4. **Result Formatting**: The `_format_results` method formats the raw query results into a more readable form.
5. **Summary Building**: The `_build_summary` method creates a summary of the search results.

#### Integration Points
- **SkillBase**: The `SearchIdeasSkill` class inherits from `SkillBase`, integrating with the broader Mythos skill system.
- **SkillRequest/SkillResponse**: The `execute` method uses `SkillRequest` and `SkillResponse` classes to interact with the Mythos system.
- **Database Connection**: The `_get_conn` function integrates with the PostgreSQL database to execute queries.

This file is a critical component of the Mythos system, enabling users to search and filter ideas stored in the `idea_inbox` table, providing a structured and formatted response.
