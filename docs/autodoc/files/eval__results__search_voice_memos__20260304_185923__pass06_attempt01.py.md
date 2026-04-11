# eval/results/search_voice_memos/20260304_185923/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 215

---

### Documentation for `eval/results/search_voice_memos/20260304_185923/pass06_attempt01.py`

#### Purpose
This file implements a skill (`SearchVoiceMemoSkill`) that enables full-text search across voice memo transcripts stored in a PostgreSQL database. The skill processes user queries, extracts search terms, performs full-text search, formats results, and builds a summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class has several methods for executing the search, extracting search terms, searching transcripts, formatting results, and building summaries. Additionally, there are top-level functions for getting a database connection and executing the skill.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is created and reused.
- **Factory**: The `SkillResponse` object creation can be seen as a factory pattern, where the response is constructed based on the search results.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `typing`, `dotenv`, `engine.base`
- **Environment Variables**: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute`
- **Internal Methods**: `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary`
- **Top-level Functions**: `_get_conn`

#### Database
- **Tables**: `voice_memos`
- **Operations**: 
  - `SELECT COUNT(*) FROM voice_memos WHERE status = 'completed'`
  - `SELECT id, filename, duration_seconds, LEFT(transcript_full, 300) as transcript_preview, created_at, ts_rank(to_tsvector('english', COALESCE(transcript_full, '')), plainto_tsquery('english', %s)) as rank FROM voice_memos WHERE status = 'completed' AND to_tsvector('english', COALESCE(transcript_full, '')) @@ plainto_tsquery('english', %s) ORDER BY rank DESC, created_at DESC LIMIT %s`

#### Configuration
- **Environment Variables**: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- **File**: `.env` (loaded using `dotenv.load_dotenv`)

#### Key Logic
1. **Extract Search Terms**: `_extract_search_terms` removes trigger phrases and cleans the message to extract meaningful search terms.
2. **Search Transcripts**: `_search_transcripts` uses PostgreSQL's full-text search capabilities to find matching voice memos.
3. **Format Results**: `_format_results` formats the search results into a clean dictionary format.
4. **Build Summary**: `_build_summary` creates a human-readable summary of the search results.

#### Integration Points
- **SkillBase**: The `SearchVoiceMemoSkill` class extends `SkillBase`, integrating with the broader Mythos skill system.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, integrating with the request-response cycle of the Mythos system.
- **Database Connection**: `_get_conn` provides a connection to the PostgreSQL database, integrating with the Mythos database infrastructure.

### Detailed Breakdown

#### Class: `SearchVoiceMemoSkill`
- **Attributes**:
  - `name`: 'search_voice_memos'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Full-text search across voice memo transcripts'
  - `triggers`: List of trigger phrases
  - `cache_ttl`: 300 seconds

- **Methods**:
  - `execute`: Main method that orchestrates the search process.
  - `_extract_search_terms`: Cleans and extracts search terms from the user message.
  - `_search_transcripts`: Performs full-text search on the `voice_memos` table.
  - `_format_results`: Formats the search results into a clean dictionary.
  - `_build_summary`: Builds a human-readable summary of the search results.

#### Top-level Functions
- `_get_conn`: Establishes a connection to the PostgreSQL database using environment variables.
- `execute`: Asynchronous function that processes the skill request and returns a response.

#### Database Operations
- **Count Query**: Counts the total number of completed voice memos.
- **Search Query**: Uses `ts_rank` and `plainto_tsquery` to rank and retrieve relevant voice memos based on the search terms.

#### Configuration and Environment Variables
- The file loads environment variables from `.env` using `dotenv.load_dotenv`.
- Database connection details are retrieved from environment variables.

This file is a critical component of the Mythos system, enabling efficient and user-friendly full-text search across voice memo transcripts.
