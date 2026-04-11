# skills/data/search_voice_memos.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 204

---

### File: `skills/data/search_voice_memos.py`

#### Purpose
This file implements a skill for searching voice memo transcripts using PostgreSQL's full-text search capabilities. It processes user queries to extract search terms, performs the search, formats results, and builds a summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class contains methods for executing the search (`execute`), extracting search terms (`_extract_search_terms`), searching transcripts (`_search_transcripts`), formatting results (`_format_results`), and building a summary (`_build_summary`). Additionally, there are top-level functions for getting a database connection (`_get_conn`) and executing the skill (`execute`).

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern as it provides a single connection object.
- **Factory Method Pattern**: The `execute` method acts as a factory method, orchestrating the extraction, search, formatting, and summary building processes.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `typing`, `dotenv`, `engine.base`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`

#### Interfaces
- **Public Methods**: `execute` (asynchronous)
- **Private Methods**: `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary`
- **Top-level Functions**: `_get_conn`

#### Database
- **Tables**: `voice_memos`
- **Operations**: 
  - **Read**: `SELECT COUNT(*) FROM voice_memos WHERE status = 'complete'`
  - **Read**: `SELECT id, filename, duration_seconds, LEFT(transcript_full, 300) as transcript_preview, created_at, ts_rank(to_tsvector('english', COALESCE(transcript_full, '')), plainto_tsquery('english', %s)) as rank FROM voice_memos WHERE status = 'complete' AND to_tsvector('english', COALESCE(transcript_full, '')) @@ plainto_tsquery('english', %s) ORDER BY rank DESC, created_at DESC LIMIT %s`

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`
- **Dotenv File**: `/opt/mythos/.env`

#### Key Logic
1. **Extract Search Terms**: `_extract_search_terms` removes trigger phrases and cleans the message to extract meaningful search terms.
2. **Full-Text Search**: `_search_transcripts` uses PostgreSQL's full-text search capabilities to find matching voice memos.
3. **Result Formatting**: `_format_results` formats the search results into a more readable form, including duration and transcript previews.
4. **Summary Building**: `_build_summary` constructs a human-readable summary of the search results.

#### Integration Points
- **SkillBase Class**: The `SearchVoiceMemoSkill` class inherits from `SkillBase`, indicating integration with the broader Mythos skill system.
- **SkillRequest and SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, indicating interaction with the Mythos request/response framework.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, integrating with the Mythos database layer.

### Detailed Analysis

#### Class: `SearchVoiceMemoSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.
- **Methods**:
  - `execute`: Asynchronous method that orchestrates the search process.
  - `_extract_search_terms`: Extracts meaningful search terms from the user message.
  - `_search_transcripts`: Performs the full-text search on the `voice_memos` table.
  - `_format_results`: Formats the search results into a more readable form.
  - `_build_summary`: Constructs a human-readable summary of the search results.

#### Top-level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database using environment variables.
- **execute**: A top-level function that mirrors the class method `execute` for potential direct execution.

#### Database Operations
- **Count Query**: Counts the number of completed voice memos.
- **Full-Text Search Query**: Uses `ts_rank` and `plainto_tsquery` to rank and retrieve matching voice memos.

#### Configuration and Environment
- **Environment Variables**: Database connection details are loaded from environment variables.
- **Dotenv File**: Environment variables are loaded from `/opt/mythos/.env`.

This file is a critical component of the Mythos system, enabling users to search through voice memo transcripts efficiently and effectively.
