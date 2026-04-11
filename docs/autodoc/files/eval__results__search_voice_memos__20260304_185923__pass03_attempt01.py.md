# eval/results/search_voice_memos/20260304_185923/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 130

---

### File: `eval/results/search_voice_memos/20260304_185923/pass03_attempt01.py`

#### Purpose
This file implements a skill (`SearchVoiceMemoSkill`) that enables full-text search across voice memo transcripts using PostgreSQL's text search capabilities. The skill processes user requests, extracts search terms, queries the database, formats results, and builds a summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` which inherits from `SkillBase`. The class includes methods for executing the skill (`execute`), extracting search terms (`_extract_search_terms`), searching transcripts (`_search_transcripts`), formatting results (`_format_results`), and building a summary (`_build_summary`). There is also a top-level function `_get_conn` for establishing a database connection.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton as it provides a single point of access to the database connection.
- **Factory Method Pattern**: The `_get_conn` function acts as a factory method for creating database connections.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `typing`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async), `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary`.
- **Top-Level Functions**: `_get_conn`.

#### Database
- **Tables**: `voice_memos` (PostgreSQL).
- **Operations**: 
  - `SELECT` with `ts_rank` for relevance scoring.
  - `to_tsvector` and `plainto_tsquery` for text search.

#### Configuration
- **Environment Variables**: Used to configure the database connection (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`).

#### Key Logic
1. **_extract_search_terms**: Cleans the input message by removing trigger phrases and punctuation, returning a cleaned search string.
2. **_search_transcripts**: Executes a PostgreSQL full-text search query using `ts_rank` for relevance scoring and returns the top results.
3. **_format_results**: Converts the raw query results into a clean, formatted list of dictionaries.
4. **_build_summary**: Constructs a human-readable summary of the search results.

#### Integration Points
- **SkillBase**: The class `SearchVoiceMemoSkill` inherits from `SkillBase`, indicating it integrates with the Mythos skill framework.
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database.
- **Environment Variables**: Loads environment variables using `dotenv` to configure the database connection.

### Detailed Breakdown

#### Class: `SearchVoiceMemoSkill`
- **Attributes**:
  - `name`: 'search_voice_memos'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Full-text search across voice memo transcripts'
  - `triggers`: List of trigger phrases for the skill.
  - `cache_ttl`: 300 seconds (cache time-to-live).

- **Methods**:
  - **execute**: Asynchronous method that orchestrates the search process. It extracts search terms, runs the search query, formats the results, and builds a summary.
  - **_extract_search_terms**: Cleans the input message by removing trigger phrases and punctuation, returning a cleaned search string.
  - **_search_transcripts**: Executes a PostgreSQL full-text search query using `ts_rank` for relevance scoring and returns the top results.
  - **_format_results**: Converts the raw query results into a clean, formatted list of dictionaries.
  - **_build_summary**: Constructs a human-readable summary of the search results.

#### Top-Level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database using environment variables for configuration.

#### Database Operations
- **_search_transcripts**: Uses a PostgreSQL query with `ts_rank` and `to_tsvector` to perform full-text search on the `voice_memos` table, returning results ordered by relevance and timestamp.

#### Configuration
- **dotenv**: Loads environment variables from `.env` file to configure the database connection.

This file is a critical component of the Mythos system, enabling efficient and user-friendly full-text search capabilities across voice memo transcripts.
