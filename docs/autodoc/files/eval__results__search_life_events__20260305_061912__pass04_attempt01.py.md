# eval/results/search_life_events/20260305_061912/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 174

---

### Documentation for `eval/results/search_life_events/20260305_061912/pass04_attempt01.py`

#### Purpose
This file implements a skill for the Mythos system that searches life events based on keywords, domain, or person. It processes user requests to extract search terms and filters, performs database queries, and formats the results.

#### Architecture
The file contains a single class `SearchLifeEventsSkill` that inherits from `SkillBase`. The class has several methods to handle different stages of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_detect_filters`: Detects domain and person filters from the user message.
- `_search_events`: Executes a PostgreSQL query to search life events based on the provided terms and filters.
- `_format_results`: Formats the raw query results into a more readable form.
- `_build_summary`: Builds a summary of the search results.

Additionally, there are top-level functions `_get_conn` and `execute` that handle database connection and the main execution flow, respectively.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single connection to the PostgreSQL database.
- **Factory Method Pattern**: The `execute` method acts as a factory method, orchestrating the extraction, filtering, searching, and formatting processes.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `string`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` loaded from `.env` file.

#### Interfaces
- **Public Methods**: `execute` is the main entry point for the skill, taking a `SkillRequest` and returning a `SkillResponse`.
- **Private Methods**: `_extract_search_terms`, `_detect_filters`, `_search_events`, `_format_results`, `_build_summary` are used internally to process the request.

#### Database
- **Tables**: The file interacts with the `life_events` table in the PostgreSQL database.
- **Operations**: Performs `SELECT` operations on the `life_events` table to retrieve life events based on search terms and filters.

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables.
- **Dotenv**: `.env` file located at `/opt/mythos/.env` is used to load environment variables.

#### Key Logic
- **Search Terms Extraction**: The `_extract_search_terms` method removes trigger phrases and normalizes the message to extract meaningful search terms.
- **Filter Detection**: The `_detect_filters` method identifies domain and person filters from the user message.
- **Database Query**: The `_search_events` method constructs and executes a PostgreSQL query to search life events based on the extracted terms and filters.
- **Result Formatting**: The `_format_results` method formats the raw query results into a more readable form, truncating descriptions and converting dates to ISO format.
- **Summary Building**: The `_build_summary` method generates a summary of the search results, showing up to three events and indicating if there are more.

#### Integration Points
- **SkillBase**: The `SearchLifeEventsSkill` class inherits from `SkillBase`, integrating with the Mythos system's skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos system's request/response model.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, integrating with the Mythos system's data storage.

This file is a critical component of the Mythos system, enabling users to search and retrieve life events based on various criteria, and it integrates seamlessly with the system's architecture and data storage.
