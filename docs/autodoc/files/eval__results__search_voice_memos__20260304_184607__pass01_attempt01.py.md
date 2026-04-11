# eval/results/search_voice_memos/20260304_184607/pass01_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 71

---

### Documentation for `eval/results/search_voice_memos/20260304_184607/pass01_attempt01.py`

#### Purpose
This file implements the `SearchVoiceMemoSkill` class, which provides a full-text search capability across voice memo transcripts stored in a PostgreSQL database. The class processes user requests, extracts search terms, performs the search, formats the results, and builds a summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class includes methods for executing the skill, extracting search terms, searching transcripts, formatting results, and building a summary. Additionally, there are top-level functions for getting the database connection and executing the skill.

#### Patterns
- **Singleton**: The `_get_conn` function ensures a single database connection is established.
- **Factory**: The `execute` method acts as a factory method to orchestrate the search process.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async), `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary`.
- **Class Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.

#### Database
- **Tables/Labels**: The file interacts with PostgreSQL tables (not explicitly named but implied through the use of `psycopg2` and `RealDictCursor`).

#### Configuration
- **Config Files**: `.env` file located at `/opt/mythos/.env`.
- **Environment Variables**: Used for database connection parameters (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`).

#### Key Logic
1. **_get_conn**: Establishes a database connection using environment variables.
2. **execute**: Orchestrates the search process by extracting search terms, performing the search, formatting results, and building a summary.
3. **_extract_search_terms**: Cleans the user message to extract meaningful search terms.
4. **_search_transcripts**: Executes a full-text search query on the transcripts using `ts_rank` for relevance scoring.
5. **_format_results**: Converts raw query results into a clean, human-readable format.
6. **_build_summary**: Constructs a summary of the search results.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` to integrate with the broader Mythos skill system.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` objects to handle input and output.
- **Database**: Connects to the PostgreSQL database to retrieve and process voice memo transcripts.
- **Logging**: Uses `logging` to log relevant information during the execution of the skill.

### Detailed Breakdown

#### Class: `SearchVoiceMemoSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: 'search_voice_memos'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Full-text search across voice memo transcripts'
  - `triggers`: List of trigger phrases for the skill.
  - `cache_ttl`: 300 seconds for caching results.
- **Methods**:
  - `execute`: Asynchronous method to execute the skill, orchestrating the search process.
  - `_extract_search_terms`: Extracts meaningful search terms from the user message.
  - `_search_transcripts`: Performs the full-text search on the transcripts.
  - `_format_results`: Formats the search results into a clean, human-readable format.
  - `_build_summary`: Builds a summary of the search results.

#### Top-Level Functions
- **_get_conn**: Establishes a database connection using environment variables.
- **execute**: Asynchronous function to execute the skill, similar to the class method but operates at the top level.

#### Database Interaction
- **Connection**: Uses `psycopg2` to connect to the PostgreSQL database.
- **Cursor**: Uses `RealDictCursor` to return query results as dictionaries.

#### Configuration and Environment
- **.env**: Loads environment variables from `/opt/mythos/.env` for database connection parameters.

This file is a critical component of the Mythos system, enabling users to perform full-text searches on voice memo transcripts, thus providing a powerful tool for data retrieval and analysis.
