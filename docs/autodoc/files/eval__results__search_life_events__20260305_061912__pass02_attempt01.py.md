# eval/results/search_life_events/20260305_061912/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 166

---

### Documentation for `eval/results/search_life_events/20260305_061912/pass02_attempt01.py`

#### Purpose
This file contains the implementation of a skill (`SearchLifeEventsSkill`) for the Mythos system that allows users to search for life events based on keywords, domain, or person. The skill processes user requests, extracts relevant search terms, applies filters, searches the database, formats the results, and builds a summary.

#### Architecture
The file contains a single class `SearchLifeEventsSkill` that inherits from `SkillBase`. The class includes methods for executing the skill, extracting search terms, detecting filters, searching events, formatting results, and building a summary. Additionally, there are top-level functions for getting a database connection and executing the skill.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a form of singleton as it ensures a single database connection is created.
- **Factory Method Pattern**: The `_search_events` method can be seen as a factory method that creates and returns a list of event results based on the provided parameters.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`

#### Interfaces
- **Public Methods**: `execute`
- **Internal Methods**: `_extract_search_terms`, `_detect_filters`, `_search_events`, `_format_results`, `_build_summary`
- **Top-level Functions**: `_get_conn`, `execute`

#### Database
- **Tables/Labels**: `life_events` (PostgreSQL table)

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables using `dotenv`.

#### Key Logic
1. **Extract Search Terms**: `_extract_search_terms` removes trigger phrases and normalizes the input message.
2. **Detect Filters**: `_detect_filters` checks for domain and person filters in the message.
3. **Search Events**: `_search_events` performs an ILIKE search on the `description` field with optional filters for `domain` and `person`.
4. **Format Results**: `_format_results` formats the search results to include truncated descriptions.
5. **Build Summary**: `_build_summary` generates a summary of the search results.

#### Integration Points
- **SkillBase**: The class extends `SkillBase` and integrates with the Mythos system's skill framework.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database.
- **Request/Response**: Utilizes `SkillRequest` and `SkillResponse` for handling requests and responses within the Mythos system.

### Detailed Breakdown

#### Classes
- **SearchLifeEventsSkill**
  - **Inherits**: `SkillBase`
  - **Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`
  - **Methods**:
    - `execute`: Main entry point for the skill, orchestrates the search process.
    - `_extract_search_terms`: Removes trigger phrases and normalizes the input message.
    - `_detect_filters`: Identifies domain and person filters in the message.
    - `_search_events`: Executes the database query to search for life events.
    - `_format_results`: Formats the raw query results into a more readable form.
    - `_build_summary`: Generates a summary of the search results.

#### Top-level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database.
- **execute**: Asynchronous function to execute the skill.

#### Key Methods
- **_extract_search_terms**: Processes the input message to extract meaningful search terms.
- **_detect_filters**: Identifies domain and person filters from the input message.
- **_search_events**: Performs the actual database query to find matching life events.
- **_format_results**: Formats the raw query results into a more readable form.
- **_build_summary**: Generates a summary of the search results for user feedback.

This file is a critical component of the Mythos system, enabling users to search and retrieve life events based on various criteria.
