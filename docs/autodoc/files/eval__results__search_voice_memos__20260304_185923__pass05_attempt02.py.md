# eval/results/search_voice_memos/20260304_185923/pass05_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 228

---

### Documentation for `pass05_attempt02.py`

#### Purpose
This Python file implements a skill named `SearchVoiceMemoSkill` that enables full-text search across voice memo transcripts using PostgreSQL's text search capabilities.

#### Architecture
The file defines a class `SearchVoiceMemoSkill` that inherits from `SkillBase`. It includes several methods:
- `execute`: The main method that handles the skill execution, including extracting search terms, querying the database, and formatting the results.
- `_extract_search_terms`: Extracts and cleans the search terms from the user's message.
- `_search_transcripts`: Queries the PostgreSQL database to find matching voice memos based on the search terms.
- `_format_results`: Formats the raw query results into a more user-friendly format.
- `_build_summary`: Builds a human-readable summary of the search results.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern as it provides a single point of access to the database connection.
- **Factory Method**: The `execute` method acts as a factory method, orchestrating the creation and processing of search results.

#### Dependencies
- **Imports**:
  - `os` and `logging` for environment and logging operations.
  - `psycopg2` and `psycopg2.extras` for PostgreSQL database operations.
  - `dotenv` for loading environment variables.
  - `SkillBase`, `SkillRequest`, and `SkillResponse` from `engine.base`.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Public method that takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Internal Methods**:
  - `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary`: Private methods used internally by the `execute` method.

#### Database
- **Tables and Labels**:
  - **voice_memos**: The primary table containing voice memo records.
    - Columns: `id`, `filename`, `duration_seconds`, `transcript_full`, `transcript_diarized`, `speaker_count`, `speaker_stats`, `status`, `created_at`.
    - Indexes: `idx_voice_memos_transcript_fts` (GIN index on `transcript_full` for full-text search), `idx_voice_memos_created` (btree index on `created_at`).
  - **voice_memo_segments**: Related table containing segments of voice memos.
    - Columns: `memo_id`, `segment_index`, `speaker_label`, `start_time`, `end_time`, `text`.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Configuration for the PostgreSQL database connection loaded via `dotenv`.

#### Key Logic
1. **Search Term Extraction**: The `_extract_search_terms` method removes trigger phrases and cleans the user's message to extract meaningful search terms.
2. **Full-Text Search**: The `_search_transcripts` method uses PostgreSQL's full-text search capabilities with `ts_rank` to retrieve relevant voice memos.
3. **Result Formatting**: The `_format_results` method formats the raw query results into a user-friendly list of dictionaries.
4. **Summary Building**: The `_build_summary` method constructs a human-readable summary of the search results.

#### Integration Points
- **SkillBase Integration**: The `SearchVoiceMemoSkill` class inherits from `SkillBase`, integrating with the Mythos skill execution framework.
- **Database Integration**: The `_get_conn` function provides a connection to the PostgreSQL database, enabling the skill to query and retrieve voice memo data.
- **SkillRequest and SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos skill execution pipeline.
