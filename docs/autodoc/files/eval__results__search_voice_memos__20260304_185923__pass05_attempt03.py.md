# eval/results/search_voice_memos/20260304_185923/pass05_attempt03.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 224

---

### Documentation for `pass05_attempt03.py`

#### Purpose
This Python file implements a skill (`SearchVoiceMemoSkill`) for the Mythos system that enables full-text search across voice memo transcripts using PostgreSQL's text search capabilities.

#### Architecture
The file defines a class `SearchVoiceMemoSkill` that inherits from `SkillBase`. It contains several methods to handle the search logic:
- `execute`: Main method that orchestrates the search process.
- `_extract_search_terms`: Extracts search terms from the user message.
- `_search_transcripts`: Executes the full-text search query on the `voice_memos` table.
- `_format_results`: Formats the search results into a more readable form.
- `_build_summary`: Builds a human-readable summary of the search results.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern as it provides a single point of access to the database connection.
- **Factory Method**: The `execute` method acts as a factory method, orchestrating the creation and processing of search results.

#### Dependencies
- `os`: For environment variable handling.
- `logging`: For logging errors.
- `psycopg2`: For PostgreSQL database operations.
- `psycopg2.extras`: For using `RealDictCursor`.
- `dotenv`: For loading environment variables from `.env` files.
- `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse`.

#### Interfaces
- **Public Methods**:
  - `execute`: Takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**:
  - `_extract_search_terms`: Extracts search terms from the user message.
  - `_search_transcripts`: Executes the full-text search query.
  - `_format_results`: Formats the search results.
  - `_build_summary`: Builds a human-readable summary of the search results.

#### Database
- **Tables/Labels**:
  - `voice_memos`: The table containing voice memo records.
  - `voice_memo_segments`: Related table containing segments of voice memos.
- **Operations**:
  - Reads from `voice_memos` table to retrieve voice memo records.
  - Uses full-text search (`to_tsvector`, `plainto_tsquery`, `ts_rank`) to find relevant records.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Database connection details.
- **Configuration Files**:
  - `.env`: Environment variables are loaded from this file.

#### Key Logic
1. **Search Term Extraction**:
   - The `_extract_search_terms` method removes trigger phrases from the user message and returns a cleaned search string.
2. **Full-Text Search**:
   - The `_search_transcripts` method constructs and executes a PostgreSQL full-text search query using `to_tsvector` and `plainto_tsquery`.
3. **Result Formatting**:
   - The `_format_results` method formats the search results, truncating transcript previews and formatting durations.
4. **Summary Building**:
   - The `_build_summary` method creates a human-readable summary of the search results.

#### Integration Points
- **Mythos Engine**:
  - The `SearchVoiceMemoSkill` class integrates with the Mythos engine via the `SkillBase` class, which provides the `execute` method interface.
- **Database**:
  - The `_get_conn` function provides a connection to the PostgreSQL database, which is used by the `_search_transcripts` method to execute queries.
- **Environment Variables**:
  - The `load_dotenv` function loads environment variables from the `.env` file, which are used to configure the database connection.

This file is a critical component of the Mythos system, enabling efficient and user-friendly full-text search across voice memo transcripts.
