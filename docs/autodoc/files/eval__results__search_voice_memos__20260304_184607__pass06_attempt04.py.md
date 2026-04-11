# eval/results/search_voice_memos/20260304_184607/pass06_attempt04.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 213

---

### Documentation for `pass06_attempt04.py`

#### Purpose
This file implements a skill (`SearchVoiceMemoSkill`) for the Mythos system that performs full-text search across voice memo transcripts. It extracts search terms from user input, queries the PostgreSQL database for matching voice memos, formats the results, and builds a human-readable summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class has several methods to handle different parts of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_search_transcripts`: Queries the PostgreSQL database for matching voice memos.
- `_format_results`: Formats the query results into a clean dictionary format.
- `_build_summary`: Builds a human-readable summary of the search results.
- `execute`: The main method that orchestrates the search process and returns a `SkillResponse`.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a database connection using environment variables.
- `execute`: A top-level function that seems to be redundant with the class method.

#### Patterns
- **Singleton**: The `_get_conn` function could be considered a singleton pattern as it ensures a single database connection is established.
- **Factory**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `RealDictCursor`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` (class method) and `execute` (top-level function).
- **Exposed Objects**: `SearchVoiceMemoSkill` class with attributes `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.

#### Database
- **Tables**: `voice_memos` (PostgreSQL).
- **Operations**: 
  - Query for total count of completed voice memos.
  - Full-text search using `ts_rank` and `plainto_tsquery` for matching voice memos.

#### Configuration
- **Environment Variables**: Database connection details (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`).
- **Dotenv File**: `.env` file located at `/opt/mythos/.env`.

#### Key Logic
1. **Extract Search Terms**: The `_extract_search_terms` method removes trigger phrases and cleans the message to extract meaningful search terms.
2. **Search Transcripts**: The `_search_transcripts` method performs a full-text search on the `voice_memos` table using `ts_rank` for relevance scoring.
3. **Format Results**: The `_format_results` method formats the query results into a clean dictionary format, including duration and transcript snippets.
4. **Build Summary**: The `_build_summary` method constructs a human-readable summary of the search results, including a snippet from the top result.

#### Integration Points
- **SkillBase**: The `SearchVoiceMemoSkill` class inherits from `SkillBase`, indicating it integrates with the broader Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, indicating integration with the skill execution pipeline.
- **Database**: The `_get_conn` function and database operations integrate with the PostgreSQL database to retrieve and process voice memo data.

### Summary
This file implements a full-text search skill for voice memos in the Mythos system. It handles extracting search terms, querying the PostgreSQL database, formatting results, and building summaries. The skill is designed to integrate seamlessly with the Mythos skill framework and the PostgreSQL database.
