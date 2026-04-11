# skills/data/search_life_events.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 224

---

### Documentation for `skills/data/search_life_events.py`

#### Purpose
This file implements the `SearchLifeEventsSkill` class, which provides functionality to search life events stored in a PostgreSQL database based on keywords, domains, or persons. It processes user requests, extracts relevant search terms, applies filters, and formats the results for presentation.

#### Architecture
The file contains a single class `SearchLifeEventsSkill` that inherits from `SkillBase`. It includes several methods to handle different aspects of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_filters`: Detects domain and person filters from the user message.
- `_search_events`: Executes the database query to search for life events.
- `_format_results`: Formats the raw query results for presentation.
- `_build_summary`: Builds a summary of the search results.

The file also contains a top-level function `_get_conn` to establish a database connection.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton as it provides a single connection instance.
- **Factory Method**: The `execute` method acts as a factory method, orchestrating the creation and processing of search results.

#### Dependencies
- `os`: For environment variable access.
- `logging`: For logging errors.
- `psycopg2`: For PostgreSQL database connection and operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `string`: For string manipulation.
- `SkillBase`, `SkillRequest`, `SkillResponse`: From `engine.base` module.

#### Interfaces
- **Public Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: Main method to process the request and return a response.
- **Private Methods**:
  - `_extract_search_terms(message: str) -> str`: Extracts search terms from the message.
  - `_detect_filters(message: str) -> dict`: Detects domain and person filters from the message.
  - `_search_events(search_terms: str, domain: str = None, person: str = None, limit: int = 15) -> list`: Executes the database query to search for life events.
  - `_format_results(rows: list) -> list`: Formats the raw query results.
  - `_build_summary(results: list, search_terms: str) -> str`: Builds a summary of the search results.

#### Database
- **Tables/Labels**:
  - `life_events`: Table in the PostgreSQL database where life events are stored.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Database connection details loaded from `/opt/mythos/.env`.

#### Key Logic
1. **Extract Search Terms**: Removes trigger phrases and normalizes the message to extract meaningful search terms.
2. **Detect Filters**: Identifies domain and person filters from the message.
3. **Search Events**: Constructs and executes a PostgreSQL query to search for life events based on the extracted terms and filters.
4. **Format Results**: Truncates and formats the query results for better readability.
5. **Build Summary**: Constructs a summary of the search results, including a brief description of the top events.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos system's skill framework.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes to handle request and response objects.

This file is crucial for enabling the Mythos system to provide intelligent and context-aware responses to user queries about life events, leveraging the structured data stored in the PostgreSQL database.
