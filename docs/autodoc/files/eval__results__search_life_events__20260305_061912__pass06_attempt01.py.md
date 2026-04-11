# eval/results/search_life_events/20260305_061912/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 224

---

### Documentation for `eval/results/search_life_events/20260305_061912/pass06_attempt01.py`

#### Purpose
This file contains the implementation of the `SearchLifeEventsSkill` class, which is designed to search and retrieve life events from a PostgreSQL database based on user input, including search terms, domain filters, and person filters.

#### Architecture
The file is structured around the `SearchLifeEventsSkill` class, which inherits from `SkillBase`. The class contains several methods that handle different stages of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_filters`: Detects domain and person filters from the user message.
- `_search_events`: Performs the actual search in the database.
- `_format_results`: Formats the search results.
- `_build_summary`: Builds a summary of the search results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: The main entry point for executing the skill, which orchestrates the search process.

#### Patterns
- **Factory Pattern**: Not explicitly used, but the `_get_conn` function can be seen as a factory method for database connections.
- **Singleton Pattern**: Not used.
- **Observer Pattern**: Not used.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async), which takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Private Methods**: `_extract_search_terms`, `_detect_filters`, `_search_events`, `_format_results`, `_build_summary`.

#### Database
- **Tables/Labels**: `life_events` (PostgreSQL table).

#### Configuration
- **Environment Variables**: Database connection details (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`) are loaded from a `.env` file located at `/opt/mythos/.env`.

#### Key Logic
1. **Extract Search Terms**: The `_extract_search_terms` method removes trigger phrases and normalizes the user message to extract meaningful search terms.
2. **Detect Filters**: The `_detect_filters` method identifies domain and person filters from the user message.
3. **Search Events**: The `_search_events` method constructs and executes a SQL query to search the `life_events` table based on the extracted search terms and filters.
4. **Format Results**: The `_format_results` method formats the search results into a more readable form.
5. **Build Summary**: The `_build_summary` method generates a summary of the search results.

#### Integration Points
- **SkillBase**: The `SearchLifeEventsSkill` class inherits from `SkillBase`, integrating with the broader Mythos system's skill framework.
- **SkillRequest/SkillResponse**: The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object, allowing seamless integration with the Mythos request-response pipeline.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, which is used throughout the search process.

### Summary
This file implements a skill to search and retrieve life events from a PostgreSQL database based on user input. It handles the extraction of search terms and filters, performs the database query, formats the results, and builds a summary. The skill is designed to integrate seamlessly with the Mythos system's skill framework and database infrastructure.
