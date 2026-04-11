# eval/results/search_voice_memos/20260304_185923/pass01_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 77

---

### Documentation for `pass01_attempt01.py`

#### Purpose
This file implements the `SearchVoiceMemoSkill` class, which provides full-text search capabilities across voice memo transcripts stored in a PostgreSQL database. The skill processes user queries, extracts search terms, performs a full-text search, formats the results, and builds a summary of the findings.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class has several methods to handle different stages of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_search_transcripts`: Executes the full-text search query on the database.
- `_format_results`: Formats the raw query results into a more readable form.
- `_build_summary`: Builds a human-readable summary of the search results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database using environment variables.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single connection is established and reused.
- **Factory**: The `execute` method acts as a factory method, orchestrating the creation and processing of search results.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `typing`
- **Database**: PostgreSQL
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute`
- **Internal Methods**: `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary`
- **Top-Level Functions**: `_get_conn`

#### Database
- **Tables/Labels**: The file interacts with a PostgreSQL table named `voice_memos` (assumed from context, though not explicitly mentioned in the code).
- **Operations**: The `_search_transcripts` method performs a full-text search using `ts_rank` for relevance scoring.

#### Configuration
- **Environment Variables**: The `_get_conn` function uses environment variables to configure the database connection.
- **Config Files**: `.env` file is loaded using `dotenv` to set environment variables.

#### Key Logic
1. **Extract Search Terms**: The `_extract_search_terms` method removes trigger phrases and returns a cleaned search string.
2. **Full-Text Search**: The `_search_transcripts` method uses `to_tsquery` and `plainto_tsquery` for safe full-text search, ordering results by relevance (`ts_rank`) and creation date.
3. **Result Formatting**: The `_format_results` method converts raw query results into a more readable format, truncating transcript previews and formatting durations.
4. **Summary Building**: The `_build_summary` method creates a human-readable summary of the search results, including a brief transcript snippet from the top result.

#### Integration Points
- **SkillBase**: The `SearchVoiceMemoSkill` class inherits from `SkillBase`, indicating integration with the Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, indicating integration with the Mythos request/response pipeline.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, enabling integration with the Mythos data storage layer.

### Summary
This file implements a full-text search skill for voice memo transcripts, leveraging PostgreSQL's text search capabilities. It integrates with the Mythos skill framework, handles database connections, and processes user queries to provide relevant search results and summaries.
