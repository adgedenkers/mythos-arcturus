# eval/results/search_life_events/20260305_061912/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 174

---

### File: `eval/results/search_life_events/20260305_061912/pass03_attempt01.py`

#### Purpose
This file contains the implementation of a skill (`SearchLifeEventsSkill`) for the Mythos system that allows users to search life events based on keywords, domain, or person. It processes user requests, extracts search terms, applies filters, queries the PostgreSQL database, formats the results, and builds a summary.

#### Architecture
The file is structured around a single class `SearchLifeEventsSkill` that inherits from `SkillBase`. The class contains methods for executing the skill, extracting search terms, detecting filters, searching events, formatting results, and building summaries. There are also top-level functions for getting database connections and executing the skill.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it returns a database connection that can be reused.
- **Factory**: The `_search_events` method acts as a factory for generating query results based on input parameters.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `engine.base`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`

#### Interfaces
- **Public Methods**: `execute`
- **Private Methods**: `_extract_search_terms`, `_detect_filters`, `_search_events`, `_format_results`, `_build_summary`
- **Top-level Functions**: `_get_conn`, `execute`

#### Database
- **Tables**: `life_events`
- **Operations**: The `_search_events` method performs `SELECT` operations on the `life_events` table.

#### Configuration
- **Environment Variables**: The `_get_conn` function uses environment variables to configure the PostgreSQL connection.
- **Configuration File**: The `dotenv` library loads environment variables from `/opt/mythos/.env`.

#### Key Logic
1. **Extract Search Terms**: `_extract_search_terms` removes trigger phrases and normalizes the message.
2. **Detect Filters**: `_detect_filters` identifies domain and person filters from the message.
3. **Search Events**: `_search_events` constructs and executes a PostgreSQL query to find life events based on search terms, domain, and person.
4. **Format Results**: `_format_results` cleans and formats the query results.
5. **Build Summary**: `_build_summary` generates a summary of the search results.

#### Integration Points
- **SkillBase Class**: The `SearchLifeEventsSkill` class inherits from `SkillBase`, indicating integration with the Mythos skill framework.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, which is used by `_search_events`.
- **SkillRequest and SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, indicating integration with the Mythos request-response model.

### Detailed Documentation

#### Class: `SearchLifeEventsSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: 'search_life_events'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Search life events by keyword, domain, or person'
  - `triggers`: List of trigger phrases
  - `cache_ttl`: 300 seconds
- **Methods**:
  - `execute`: Main method to process user requests.
  - `_extract_search_terms`: Removes trigger phrases and normalizes the message.
  - `_detect_filters`: Identifies domain and person filters from the message.
  - `_search_events`: Constructs and executes a PostgreSQL query to find life events.
  - `_format_results`: Cleans and formats the query results.
  - `_build_summary`: Generates a summary of the search results.

#### Top-level Functions
- **`_get_conn`**: Returns a PostgreSQL database connection.
- **`execute`**: Processes a `SkillRequest` and returns a `SkillResponse`.

#### Database Operations
- **Table**: `life_events`
- **Query**: The `_search_events` method constructs a query to search for life events based on search terms, domain, and person.

#### Configuration
- **Environment Variables**: Used to configure the PostgreSQL connection.
- **Dotenv**: Loads environment variables from `/opt/mythos/.env`.

#### Key Logic
- **Extract Search Terms**: Normalizes the message by removing trigger phrases.
- **Detect Filters**: Identifies domain and person filters from the message.
- **Search Events**: Constructs and executes a PostgreSQL query to find life events.
- **Format Results**: Cleans and formats the query results.
- **Build Summary**: Generates a summary of the search results.

#### Integration Points
- **SkillBase Class**: Integrates with the Mythos skill framework.
- **Database Connection**: Provides a connection to the PostgreSQL database.
- **SkillRequest and SkillResponse**: Processes requests and returns responses in the Mythos request-response model.
