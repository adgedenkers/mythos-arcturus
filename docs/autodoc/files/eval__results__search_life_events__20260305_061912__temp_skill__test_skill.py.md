# eval/results/search_life_events/20260305_061912/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 224

---

### Documentation for `test_skill.py`

#### Purpose
This file defines the `SearchLifeEventsSkill` class, which is responsible for searching life events in the PostgreSQL database based on user-provided search terms and filters. It handles the extraction of search terms, detection of filters, execution of database queries, and formatting of results.

#### Architecture
The file contains a single class `SearchLifeEventsSkill` that inherits from `SkillBase`. The class has several methods to handle different aspects of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_filters`: Detects domain and person filters from the user message.
- `_search_events`: Executes the database query to search for life events.
- `_format_results`: Formats the raw database results into a more readable form.
- `_build_summary`: Builds a summary of the search results.

Additionally, there are utility functions such as `_get_conn` for database connection and `execute` for the main execution logic.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton as it provides a single connection to the database.
- **Factory Method**: The `execute` method acts as a factory method, coordinating the creation and processing of search results.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Public Methods**: `execute` is the primary method exposed to other parts of the system, which takes a `SkillRequest` and returns a `SkillResponse`.
- **Internal Methods**: `_extract_search_terms`, `_detect_filters`, `_search_events`, `_format_results`, `_build_summary`.

#### Database
- **Tables**: The file interacts with the `life_events` table in the PostgreSQL database.
- **Operations**: Performs `SELECT` operations to retrieve life events based on search terms and filters.

#### Configuration
- **Environment Variables**: Configuration is loaded from environment variables using `dotenv.load_dotenv` for database connection details.
- **Configuration File**: The `.env` file located at `/opt/mythos/.env` is used to load environment variables.

#### Key Logic
1. **Extract Search Terms**: The `_extract_search_terms` method removes trigger phrases and normalizes the message to extract meaningful search terms.
2. **Detect Filters**: The `_detect_filters` method identifies domain and person filters from the user message.
3. **Search Events**: The `_search_events` method constructs and executes a SQL query to search for life events based on the extracted terms and filters.
4. **Format Results**: The `_format_results` method formats the raw database results into a more readable form.
5. **Build Summary**: The `_build_summary` method generates a summary of the search results.

#### Integration Points
- **SkillBase**: The `SearchLifeEventsSkill` class inherits from `SkillBase`, integrating with the broader Mythos system's skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the system's request-response mechanism.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, integrating with the Mythos system's data storage layer.

### Summary
The `test_skill.py` file implements the `SearchLifeEventsSkill` class, which provides functionality to search life events in the PostgreSQL database based on user input. It integrates with the Mythos system's skill framework, handles database interactions, and formats results for user consumption.
