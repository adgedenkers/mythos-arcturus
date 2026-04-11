# eval/results/search_voice_memos/20260304_184607/pass06_attempt05.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 197

---

### Documentation for `pass06_attempt05.py`

#### Purpose
This file implements a skill for performing full-text search across voice memo transcripts stored in a PostgreSQL database. It extracts search terms from user input, queries the database for matching voice memos, formats the results, and builds a summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. It includes methods for executing the skill, extracting search terms, searching transcripts, formatting results, and building a summary. Additionally, there are top-level functions for getting a database connection and executing the skill.

#### Patterns
- **Singleton**: The `_get_conn` function ensures a single database connection is established per execution.
- **Factory**: The `SkillBase` class is used as a base class to create specific skill instances.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` are used to configure the database connection.

#### Interfaces
- **Public Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: Executes the skill by extracting search terms, searching transcripts, formatting results, and building a summary.
  - `_extract_search_terms(message: str) -> str`: Extracts search terms from the user message.
  - `_search_transcripts(search_terms: str, limit: int = 10) -> list`: Searches for matching voice memos in the database.
  - `_format_results(rows: list) -> list`: Formats the search results into a clean list of dictionaries.
  - `_build_summary(results: list, search_terms: str) -> str`: Builds a summary of the search results.

#### Database
- **Tables/Labels**:
  - `voice_memos`: Used to store voice memos with fields like `id`, `filename`, `transcript_full`, `created_at`, `status`, and `duration_seconds`.
  - `dotenv`: Used to load environment variables for database configuration.

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` are used to configure the database connection.
- **Configuration File**: `.env` file located at `/opt/mythos/.env` is loaded to retrieve environment variables.

#### Key Logic
- **Search Logic**:
  - Extracts search terms from the user message using `_extract_search_terms`.
  - Queries the `voice_memos` table using full-text search (`ts_rank` and `plainto_tsquery`).
  - Formats the results to include only relevant fields and summaries.
  - Builds a summary of the search results.

- **Database Connection**:
  - Establishes a connection to the PostgreSQL database using environment variables.
  - Uses `RealDictCursor` to return rows as dictionaries.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill system.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes to handle input and output.
- **Database**: Connects to the PostgreSQL database to query voice memos.
- **Logging**: Uses Python's `logging` module to log errors and other information.

### Detailed Class and Function Descriptions

#### Class: `SearchVoiceMemoSkill`
- **Inherits from**: `SkillBase`
- **Attributes**:
  - `name`: 'search_voice_memos'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Full-text search across voice memo transcripts'
  - `triggers`: List of phrases that trigger the skill
  - `cache_ttl`: 300 seconds

- **Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: Executes the skill by extracting search terms, searching transcripts, formatting results, and building a summary.
  - `_extract_search_terms(message: str) -> str`: Extracts search terms from the user message by removing trigger phrases and cleaning the input.
  - `_search_transcripts(search_terms: str, limit: int = 10) -> list`: Searches for matching voice memos in the `voice_memos` table using full-text search.
  - `_format_results(rows: list) -> list`: Formats the search results into a clean list of dictionaries, truncating transcript previews and formatting durations.
  - `_build_summary(results: list, search_terms: str) -> str`: Builds a summary of the search results, including the number of matches and brief transcript snippets.

#### Top-Level Functions
- **`_get_conn()`**: Establishes a connection to the PostgreSQL database using environment variables.
- **`execute(request)`**: Asynchronous function to execute the skill, handling the entire process from extracting search terms to building the summary.

### Summary
This file implements a skill for searching voice memos based on user input. It leverages PostgreSQL for full-text search and provides a structured response with formatted results and a summary. The skill integrates with the Mythos system through the `SkillBase` class and uses environment variables for configuration.
