# eval/results/search_voice_memos/20260304_184607/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 180

---

### Documentation for `pass04_attempt01.py`

#### Purpose
This file implements the `SearchVoiceMemoSkill` class, which provides a full-text search capability across voice memo transcripts stored in a PostgreSQL database. The skill extracts search terms from user input, queries the database for matching voice memos, formats the results, and builds a human-readable summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class includes methods for executing the search, extracting search terms, searching transcripts, formatting results, and building a summary. Additionally, there are top-level functions for getting the database connection and handling the search logic.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create a database connection.
- **Singleton**: The `_get_conn` function ensures a single database connection is created and reused.
- **Observer**: The class observes user input and triggers the search based on specific phrases.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute`, `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary`
- **Top-Level Functions**: `_get_conn`, `execute`

#### Database
- **Tables/Labels**: `voice_memos` (PostgreSQL)
- **Operations**: Reads from `voice_memos` table to retrieve voice memo transcripts and metadata.

#### Configuration
- **Environment Variables**: Database connection details (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`) are loaded from the `.env` file using `dotenv`.

#### Key Logic
1. **Extract Search Terms**: `_extract_search_terms` removes trigger phrases and cleans the input message to generate a search query.
2. **Search Transcripts**: `_search_transcripts` uses PostgreSQL's full-text search capabilities to find matching voice memos based on the cleaned search terms.
3. **Format Results**: `_format_results` converts the raw database rows into a clean, human-readable format.
4. **Build Summary**: `_build_summary` creates a summary string that includes the number of matches, file names, durations, and a snippet from the top result.

#### Integration Points
- **SkillBase**: The `SearchVoiceMemoSkill` class extends `SkillBase` and integrates with the Mythos system's skill execution framework.
- **Database**: The skill interacts with the PostgreSQL database to retrieve and process voice memo data.
- **Logging**: Uses the `logging` module to log errors and other information.

### Detailed Breakdown

#### Class: `SearchVoiceMemoSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.
- **Methods**:
  - `execute`: Asynchronous method that orchestrates the search process.
  - `_extract_search_terms`: Cleans and extracts search terms from the input message.
  - `_search_transcripts`: Queries the PostgreSQL database to find matching voice memos.
  - `_format_results`: Formats the raw query results into a clean list of dictionaries.
  - `_build_summary`: Builds a human-readable summary of the search results.

#### Top-Level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database using environment variables.
- **execute**: Placeholder for asynchronous execution logic (not implemented in the provided code).

#### Database Operations
- **_search_transcripts**: Uses PostgreSQL's full-text search capabilities (`to_tsvector`, `plainto_tsquery`, `ts_rank`) to query the `voice_memos` table and retrieve relevant results.

#### Configuration and Environment
- **dotenv**: Loads environment variables from `.env` file to configure the database connection.

This documentation provides a comprehensive overview of the `pass04_attempt01.py` file, detailing its purpose, architecture, dependencies, interfaces, database interactions, configuration, key logic, and integration points within the Mythos system.
