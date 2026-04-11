# eval/results/search_voice_memos/20260304_184607/pass06_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 213

---

### Documentation for `pass06_attempt02.py`

#### Purpose
This file implements a voice memo search skill (`SearchVoiceMemoSkill`) that performs full-text search on voice memo transcripts stored in a PostgreSQL database. It extracts search terms from user input, queries the database for matching transcripts, formats the results, and builds a human-readable summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class defines several methods for handling the search process, including extracting search terms, querying the database, formatting results, and building a summary. Additionally, there are several top-level functions for database connection and utility operations.

#### Patterns
- **Singleton**: The `_get_conn` function ensures a single database connection is created per call.
- **Factory**: The `SkillResponse` object is created based on the search results and error handling.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

#### Interfaces
- **Public Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: Main entry point for executing the skill.
- **Private Methods**:
  - `_extract_search_terms(message: str) -> str`: Extracts search terms from the user message.
  - `_search_transcripts(search_terms: str, limit: int = 10) -> list`: Queries the database for matching transcripts.
  - `_format_results(rows: list) -> list`: Formats the raw query results into a clean list of dictionaries.
  - `_build_summary(results: list, search_terms: str) -> str`: Builds a human-readable summary of the search results.

#### Database
- **Tables**: `voice_memos`
- **Operations**:
  - **Read**: `voice_memos` table is queried to retrieve transcripts and metadata.
  - **Write**: No write operations are performed in this file.

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` are used to configure the database connection.
- **Dotenv**: `.env` file is loaded to provide environment variables.

#### Key Logic
1. **Extract Search Terms**: The `_extract_search_terms` method removes trigger phrases and cleans the message to extract meaningful search terms.
2. **Database Query**: The `_search_transcripts` method constructs a full-text search query using `ts_rank` and `plainto_tsquery` to retrieve relevant transcripts.
3. **Result Formatting**: The `_format_results` method formats the raw query results into a clean list of dictionaries with truncated transcript previews and formatted durations.
4. **Summary Building**: The `_build_summary` method constructs a human-readable summary of the search results, including snippets from the top results.

#### Integration Points
- **SkillBase**: The `SearchVoiceMemoSkill` class inherits from `SkillBase`, integrating with the Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos request-response cycle.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, integrating with the Mythos database layer.

### Summary
This file implements a voice memo search skill that integrates with the Mythos system to perform full-text searches on voice memo transcripts. It handles user input, database queries, result formatting, and summary generation, providing a comprehensive search functionality within the Mythos platform.
