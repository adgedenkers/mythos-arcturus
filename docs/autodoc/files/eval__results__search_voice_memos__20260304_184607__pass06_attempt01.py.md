# eval/results/search_voice_memos/20260304_184607/pass06_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 195

---

### File: eval/results/search_voice_memos/20260304_184607/pass06_attempt01.py

#### Purpose
This file implements a skill (`SearchVoiceMemoSkill`) that performs full-text search across voice memo transcripts stored in a PostgreSQL database. The skill processes user queries, extracts search terms, searches for matching transcripts, formats the results, and builds a summary.

#### Architecture
The file contains a single class, `SearchVoiceMemoSkill`, which inherits from `SkillBase`. The class has several methods:
- `execute`: The main method that orchestrates the search process.
- `_extract_search_terms`: Extracts and cleans search terms from the user message.
- `_search_transcripts`: Executes the full-text search query on the database.
- `_format_results`: Formats the search results into a more readable form.
- `_build_summary`: Builds a human-readable summary of the search results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a database connection using environment variables.
- `execute`: A top-level function that wraps the class method for external calls.

#### Patterns
- **Singleton**: The `_get_conn` function ensures a single database connection per execution.
- **Factory**: The `execute` method acts as a factory for creating `SkillResponse` objects based on the search results.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` (class method), `execute` (top-level function).
- **Exposed Interfaces**: The `execute` method accepts a `SkillRequest` object and returns a `SkillResponse` object.

#### Database
- **Tables**: `voice_memos` (PostgreSQL).
- **Operations**: 
  - Reads from `voice_memos` to count completed memos.
  - Executes full-text search queries on `voice_memos` using `ts_rank` and `to_tsvector`.

#### Configuration
- **Config Files**: `.env` file loaded using `dotenv`.
- **Environment Variables**: Database connection details (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`).

#### Key Logic
- **Search Terms Extraction**: The `_extract_search_terms` method removes trigger phrases and cleans the message to extract meaningful search terms.
- **Full-Text Search**: The `_search_transcripts` method constructs and executes a PostgreSQL full-text search query using `ts_rank` for relevance scoring.
- **Result Formatting**: The `_format_results` method formats the raw query results into a more user-friendly form, including duration formatting and transcript preview truncation.
- **Summary Building**: The `_build_summary` method generates a human-readable summary of the search results.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill framework.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` to interface with the Mythos system for request handling and response generation.
- **Database Connection**: Uses `_get_conn` to establish a database connection, integrating with the PostgreSQL database for data retrieval and manipulation.

This file is a critical component of the Mythos system, enabling users to search through voice memo transcripts efficiently and effectively.
