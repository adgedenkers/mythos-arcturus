# eval/results/search_life_events/20260305_061912/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 224

---

### Documentation for `final.py` in the Mythos System

#### Purpose
This file implements the `SearchLifeEventsSkill` class, which is responsible for searching life events in the Mythos database based on keywords, domains, or persons. It processes user requests, extracts search terms, applies filters, searches the database, formats results, and builds summaries.

#### Architecture
- **Class Structure**: 
  - `SearchLifeEventsSkill` inherits from `SkillBase`.
  - Contains methods for executing the skill, extracting search terms, detecting filters, searching events, formatting results, and building summaries.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: Asynchronous function to handle the execution of the skill.
  - `_extract_search_terms`: Extracts search terms from the user message.
  - `_detect_filters`: Detects domain and person filters from the user message.
  - `_search_events`: Performs the database search based on search terms and filters.
  - `_format_results`: Formats the search results.
  - `_build_summary`: Builds a summary of the search results.

#### Patterns
- **Singleton Pattern**: `_get_conn` function ensures a single connection to the database.
- **Factory Method Pattern**: `_search_events` constructs and executes the SQL query based on the provided parameters.

#### Dependencies
- **Imports**:
  - `os`: For environment variables.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database operations.
  - `string`: For string manipulation.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From `engine.base`.

#### Interfaces
- **Public Methods**:
  - `execute`: Asynchronous method to process user requests and return `SkillResponse`.
- **Private Methods**:
  - `_extract_search_terms`: Extracts search terms from the user message.
  - `_detect_filters`: Detects domain and person filters from the user message.
  - `_search_events`: Searches the database for life events.
  - `_format_results`: Formats the search results.
  - `_build_summary`: Builds a summary of the search results.

#### Database
- **Tables/Labels**:
  - `life_events`: PostgreSQL table where life events are stored.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured in `/opt/mythos/.env`.

#### Key Logic
1. **Extract Search Terms**: Removes trigger phrases and normalizes the user message to extract meaningful search terms.
2. **Detect Filters**: Identifies domain and person filters from the user message.
3. **Database Search**: Constructs and executes a SQL query to search for life events based on the extracted terms and filters.
4. **Result Formatting**: Formats the search results to include only relevant fields and truncate descriptions.
5. **Summary Building**: Constructs a summary of the search results, including a brief description of the first few events.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill framework.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` to handle input and output within the Mythos system.

### Summary
The `final.py` file implements a skill for searching life events in the Mythos system. It processes user requests, extracts search terms, applies filters, searches the PostgreSQL database, formats results, and builds summaries. The skill integrates with the Mythos framework and uses environment variables for database configuration.
