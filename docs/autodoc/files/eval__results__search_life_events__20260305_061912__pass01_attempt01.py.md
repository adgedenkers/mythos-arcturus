# eval/results/search_life_events/20260305_061912/pass01_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 64

---

### Documentation for `eval/results/search_life_events/20260305_061912/pass01_attempt01.py`

#### Purpose
This file defines the `SearchLifeEventsSkill` class, which is responsible for searching life events based on user-provided search terms, domain, and person filters. It interacts with a PostgreSQL database to retrieve and format the search results.

#### Architecture
The file contains a single class `SearchLifeEventsSkill` that inherits from `SkillBase`. The class has several methods to handle different stages of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_filters`: Detects domain and person filters from the user message.
- `_search_events`: Executes the search query on the PostgreSQL database.
- `_format_results`: Formats the raw database results into a more readable form.
- `_build_summary`: Builds a summary of the search results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: The main entry point for the skill, orchestrating the search process.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is returned.
- **Factory**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object based on the input request.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`

#### Interfaces
- **Public Methods**: `execute` (async)
- **Internal Methods**: `_extract_search_terms`, `_detect_filters`, `_search_events`, `_format_results`, `_build_summary`

#### Database
- **PostgreSQL Tables**: The file interacts with a PostgreSQL database using the `psycopg2` library. The specific table or schema is not explicitly named but is inferred to be part of the `mythos` database.

#### Configuration
- **Environment Variables**: The database connection details are loaded from environment variables using `dotenv`.
- **Configuration File**: `.env` file located at `/opt/mythos/.env`.

#### Key Logic
1. **Connection Establishment**: `_get_conn` establishes a connection to the PostgreSQL database using environment variables.
2. **Search Execution**: 
   - `_extract_search_terms` removes trigger phrases and normalizes the search terms.
   - `_detect_filters` identifies domain and person filters from the message.
   - `_search_events` performs the actual search using ILIKE and optional filters.
   - `_format_results` formats the raw database results into a more readable form.
   - `_build_summary` creates a summary of the search results.
3. **Response Construction**: The `execute` method orchestrates the above steps and constructs a `SkillResponse` object.

#### Integration Points
- **SkillBase Class**: Inherits from `SkillBase` and integrates with the Mythos system's skill framework.
- **Database Integration**: Uses `psycopg2` to interact with the PostgreSQL database.
- **Environment Configuration**: Loads configuration from `.env` using `dotenv`.

### Detailed Method Descriptions

#### `_get_conn`
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Dependencies**: `psycopg2`, `os.getenv`
- **Database**: Connects to the `mythos` database using environment variables.

#### `execute`
- **Purpose**: Main entry point for the skill, orchestrates the search process.
- **Parameters**: `request: SkillRequest`
- **Returns**: `SkillResponse`
- **Logic**: Extracts search terms, detects filters, searches events, formats results, and builds a summary.

#### `_extract_search_terms`
- **Purpose**: Extracts search terms from the user message.
- **Parameters**: `message: str`
- **Returns**: `str`
- **Logic**: Removes trigger phrases and normalizes whitespace.

#### `_detect_filters`
- **Purpose**: Detects domain and person filters from the user message.
- **Parameters**: `message: str`
- **Returns**: `dict`
- **Logic**: Checks for domain and person mentions in the message.

#### `_search_events`
- **Purpose**: Executes the search query on the PostgreSQL database.
- **Parameters**: `search_terms: str`, `domain: str`, `person: str`, `limit: int`
- **Returns**: `list`
- **Logic**: Performs an ILIKE search with optional filters and limits the results.

#### `_format_results`
- **Purpose**: Formats the raw database results into a more readable form.
- **Parameters**: `rows: list`
- **Returns**: `list`
- **Logic**: Cleans and formats the result dictionaries.

#### `_build_summary`
- **Purpose**: Builds a summary of the search results.
- **Parameters**: `results: list`, `search_terms: str`
- **Returns**: `str`
- **Logic**: Constructs a summary string based on the search results.

This documentation provides a comprehensive overview of the `SearchLifeEventsSkill` class and its methods, detailing how it integrates with the Mythos system and interacts with the PostgreSQL database.
