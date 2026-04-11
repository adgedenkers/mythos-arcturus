# eval/results/search_voice_memos/20260304_184607/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 95

---

### File: `eval/results/search_voice_memos/20260304_184607/pass02_attempt01.py`

#### Purpose
This file contains the implementation of the `SearchVoiceMemoSkill` class, which provides a full-text search capability across voice memo transcripts stored in a PostgreSQL database. The skill processes user requests to extract search terms, query the database, format the results, and build a summary.

#### Architecture
The file consists of a single class `SearchVoiceMemoSkill` inheriting from `SkillBase`. The class includes methods for executing the skill, extracting search terms, searching transcripts, formatting results, and building a summary. Additionally, there is a top-level function `_get_conn` for establishing a database connection.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is returned.
- **Factory Method**: The `execute` method acts as a factory method, orchestrating the creation and processing of search results.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Database**: PostgreSQL (`psycopg2` for connection and querying)

#### Interfaces
- **Public Methods**:
  - `execute`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**:
  - `_extract_search_terms`: Extracts search terms from a message.
  - `_search_transcripts`: Searches transcripts based on search terms.
  - `_format_results`: Formats the search results.
  - `_build_summary`: Builds a summary of the search results.

#### Database
- **Tables/Labels**:
  - `dotenv`: Configuration table for environment variables.
  - `psycopg2`: PostgreSQL connection and query execution.
  - `engine`: Base class for skill execution.
  - `top`: Top-level results from the search.

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` are used to configure the database connection.
- **Dotenv File**: `/opt/mythos/.env` is loaded to provide environment variables.

#### Key Logic
1. **_extract_search_terms**: Cleans and extracts search terms from the user message by removing trigger phrases and punctuation.
2. **_search_transcripts**: Executes a full-text search query on the transcripts using `ts_rank` for relevance scoring.
3. **_format_results**: Formats the raw database rows into a clean dictionary format, truncating transcript previews and formatting durations.
4. **_build_summary**: Constructs a human-readable summary of the search results, including the top result's transcript snippet.

#### Integration Points
- **SkillBase**: The `SearchVoiceMemoSkill` class inherits from `SkillBase`, integrating with the broader Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the request-response cycle of the Mythos system.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, integrating with the Mythos data storage layer.

### Summary
This file implements a full-text search skill for voice memo transcripts, handling request processing, database querying, result formatting, and summary generation. It integrates with the Mythos skill framework and PostgreSQL database, using environment variables for configuration.
