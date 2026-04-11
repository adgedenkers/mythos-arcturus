# eval/results/search_voice_memos/20260304_184607/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 200

---

### Documentation for `final.py`

#### Purpose
The `final.py` file implements a skill for full-text search across voice memo transcripts stored in a PostgreSQL database. It processes user requests to extract search terms, query the database for matching transcripts, format the results, and build a human-readable summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. This class includes methods for executing the search, extracting search terms, searching transcripts, formatting results, and building summaries. Additionally, there are several top-level functions for database connection and utility operations.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is established and reused.
- **Factory**: The `execute` method acts as a factory for creating `SkillResponse` objects based on the search results.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Database**: PostgreSQL (`voice_memos` table)
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute`
- **Internal Methods**: `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary`
- **Top-Level Functions**: `_get_conn`

#### Database
- **Tables**: `voice_memos`
- **Operations**: 
  - `SELECT COUNT(*)` to get the total number of completed voice memos.
  - Full-text search using `to_tsvector` and `plainto_tsquery` to find matching transcripts.
  - `SELECT` with `ts_rank` for relevance scoring.

#### Configuration
- **Environment Variables**: Database connection details (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`)
- **Dotenv**: `.env` file for loading environment variables

#### Key Logic
1. **Extract Search Terms**: `_extract_search_terms` removes trigger phrases and cleans the message to extract meaningful search terms.
2. **Search Transcripts**: `_search_transcripts` performs a full-text search on the `voice_memos` table using `to_tsvector` and `plainto_tsquery`.
3. **Format Results**: `_format_results` converts raw query results into a clean, human-readable format.
4. **Build Summary**: `_build_summary` generates a summary of the search results, including the number of matches and relevant details.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and implements the `execute` method to handle incoming requests.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` to process and return data.
- **Database Connection**: Uses `_get_conn` to establish a database connection, ensuring seamless integration with the PostgreSQL database.

### Detailed Breakdown

#### Classes
- **SearchVoiceMemoSkill**
  - **Inheritance**: `SkillBase`
  - **Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`
  - **Methods**:
    - `execute`: Main method to handle the search request.
    - `_extract_search_terms`: Extracts meaningful search terms from the user message.
    - `_search_transcripts`: Performs the full-text search on the `voice_memos` table.
    - `_format_results`: Formats the search results into a readable format.
    - `_build_summary`: Builds a summary of the search results.

#### Top-Level Functions
- **_get_conn**: Establishes a database connection using environment variables.
- **_extract_search_terms**: (redundant with class method, likely a typo or leftover)
- **_search_transcripts**: (redundant with class method, likely a typo or leftover)
- **_format_results**: (redundant with class method, likely a typo or leftover)
- **_build_summary**: (redundant with class method, likely a typo or leftover)

#### Key Logic Flow
1. **Extract Search Terms**: The `_extract_search_terms` method cleans the user message to extract meaningful search terms.
2. **Search Transcripts**: The `_search_transcripts` method performs a full-text search on the `voice_memos` table using PostgreSQL's full-text search capabilities.
3. **Format Results**: The `_format_results` method formats the raw query results into a clean, human-readable format.
4. **Build Summary**: The `_build_summary` method generates a summary of the search results, including the number of matches and relevant details.
5. **Return Response**: The `execute` method constructs and returns a `SkillResponse` object with the search results and summary.

This file is a critical component of the Mythos system, enabling users to search through voice memo transcripts efficiently and effectively.
