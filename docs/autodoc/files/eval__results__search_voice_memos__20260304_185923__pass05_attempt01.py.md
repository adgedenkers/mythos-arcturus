# eval/results/search_voice_memos/20260304_185923/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 240

---

### Documentation for `pass05_attempt01.py`

#### Purpose
This file implements a skill for full-text search across voice memo transcripts using PostgreSQL's text search capabilities. It processes search requests, extracts search terms, queries the database, formats results, and builds a human-readable summary.

#### Architecture
The file defines a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class contains several methods:
- `execute`: Main method that handles the search request, extracts search terms, queries the database, formats results, and builds a summary.
- `_extract_search_terms`: Cleans and extracts search terms from the input message.
- `_search_transcripts`: Executes the full-text search query on the `voice_memos` table.
- `_format_results`: Formats the raw query results into a clean list of dictionaries.
- `_build_summary`: Constructs a human-readable summary of the search results.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern as it provides a single point of access to the database connection.
- **Factory Method**: The `_get_conn` function acts as a factory method for creating database connections.

#### Dependencies
- `os`: For environment variable handling.
- `logging`: For logging errors.
- `psycopg2`: For PostgreSQL database operations.
- `psycopg2.extras`: For using `RealDictCursor`.
- `dotenv`: For loading environment variables from `.env` files.
- `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Public Methods**:
  - `execute`: Processes the search request and returns a `SkillResponse` object.
- **Private Methods**:
  - `_extract_search_terms`: Cleans and extracts search terms.
  - `_search_transcripts`: Executes the full-text search query.
  - `_format_results`: Formats the query results.
  - `_build_summary`: Builds a human-readable summary of the results.

#### Database
- **Tables and Labels**:
  - `voice_memos`: The table containing voice memo records.
    - Columns: `id`, `filename`, `duration_seconds`, `transcript_full`, `transcript_diarized`, `speaker_count`, `speaker_stats`, `status`, `created_at`.
    - Indexes: `idx_voice_memos_transcript_fts` (GIN index on `transcript_full`), `idx_voice_memos_created` (btree on `created_at`).

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Database connection details loaded via `dotenv`.

#### Key Logic
1. **Search Term Extraction**: The `_extract_search_terms` method cleans the input message by removing trigger phrases and punctuation, ensuring the search terms are at least two characters long.
2. **Full-Text Search**: The `_search_transcripts` method constructs a PostgreSQL query using `to_tsvector` and `plainto_tsquery` for full-text search, ordering results by relevance (`ts_rank`) and creation time.
3. **Result Formatting**: The `_format_results` method formats the raw query results into a clean list of dictionaries, truncating transcript previews and formatting durations.
4. **Summary Construction**: The `_build_summary` method constructs a human-readable summary of the search results, including a snippet from the top result.

#### Integration Points
- **SkillBase Interface**: The `execute` method integrates with the `SkillBase` interface, handling incoming `SkillRequest` objects and returning `SkillResponse` objects.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, which is used by the `_search_transcripts` method to execute queries.
- **Environment Configuration**: The `load_dotenv` function loads environment variables from `/opt/mythos/.env`, which are used to configure the database connection.

This file is a critical component of the Mythos system, enabling efficient and user-friendly full-text search across voice memo transcripts.
