# eval/results/search_voice_memos/20260304_185923/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 181

---

### File: `eval/results/search_voice_memos/20260304_185923/pass04_attempt01.py`

#### Purpose
This file implements a skill (`SearchVoiceMemoSkill`) that enables full-text search across voice memo transcripts using PostgreSQL's text search capabilities. It processes user requests, extracts search terms, performs database queries, formats results, and builds a human-readable summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class has several methods:
- `execute`: The main method that orchestrates the search process.
- `_extract_search_terms`: Extracts and cleans search terms from the user message.
- `_search_transcripts`: Executes a full-text search query on the `voice_memos` table.
- `_format_results`: Formats the raw query results into a more readable form.
- `_build_summary`: Builds a human-readable summary of the search results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a database connection using environment variables.
- `execute`: A top-level function that is not used within the class.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is established.
- **Factory**: The `_build_summary` method can be seen as a factory method that constructs a summary based on the search results.

#### Dependencies
- `os`: Used for environment variable handling.
- `logging`: For logging errors.
- `psycopg2`: PostgreSQL database adapter.
- `dotenv`: For loading environment variables from `.env` files.
- `SkillBase`, `SkillRequest`, `SkillResponse`: Base classes and types from the `engine.base` module.

#### Interfaces
- `execute`: The main entry point for the skill, which takes a `SkillRequest` and returns a `SkillResponse`.
- `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary`: Helper methods that are called within `execute`.

#### Database
- **Tables**: `voice_memos`
- **Operations**: 
  - Full-text search using `to_tsvector` and `plainto_tsquery`.
  - Retrieval of `id`, `filename`, `duration_seconds`, `transcript_full`, and `created_at` fields.
  - Filtering by `status` and ordering by relevance (`ts_rank`) and creation time (`created_at`).

#### Configuration
- Environment variables: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.
- `.env` file: Loaded using `dotenv.load_dotenv`.

#### Key Logic
1. **Extract Search Terms**: `_extract_search_terms` removes trigger phrases and cleans the message.
2. **Full-Text Search**: `_search_transcripts` performs a full-text search on the `voice_memos` table.
3. **Result Formatting**: `_format_results` formats the raw query results into a more readable form.
4. **Summary Building**: `_build_summary` constructs a human-readable summary of the search results.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase`, which provides a base structure for skills.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` for request and response handling.
- **Database**: Connects to PostgreSQL using `psycopg2` and interacts with the `voice_memos` table.
- **Environment Variables**: Uses environment variables for database connection details.

### Summary
This file implements a skill for searching voice memo transcripts using PostgreSQL's full-text search capabilities. It processes user requests, extracts search terms, performs database queries, formats results, and builds a human-readable summary. The skill integrates with the Mythos system through the `SkillBase` class and uses PostgreSQL for data storage and retrieval.
