# eval/results/search_voice_memos/20260304_184607/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 200

---

### Documentation for `pass05_attempt01.py`

#### Purpose
This file implements a skill (`SearchVoiceMemoSkill`) for full-text search across voice memo transcripts stored in a PostgreSQL database. It processes user requests to find relevant voice memos based on search terms and provides formatted results and summaries.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class has several methods to handle different stages of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_search_transcripts`: Executes a full-text search query on the `voice_memos` table.
- `_format_results`: Formats the search results into a more readable form.
- `_build_summary`: Builds a human-readable summary of the search results.

There are also top-level functions:
- `_get_conn`: Establishes a database connection using environment variables.
- `execute`: The main entry point for the skill, coordinating the search process.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is created and reused.
- **Factory**: The `execute` method acts as a factory, coordinating the creation and processing of search terms, executing the search, and formatting the results.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `re`: For regular expression operations.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Public Methods**: `execute` (async) is the primary method exposed to other parts of the system.
- **Internal Methods**: `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary` are used internally within the class.

#### Database
- **Tables**: `voice_memos` (PostgreSQL)
- **Operations**: 
  - Querying the `voice_memos` table for full-text search using `ts_rank` and `plainto_tsquery`.
  - Retrieving the total count of completed voice memos.

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` are used to configure the database connection.
- **Config Files**: `.env` file is loaded using `dotenv`.

#### Key Logic
1. **Extract Search Terms**: The `_extract_search_terms` method removes trigger phrases and cleans the user message to extract meaningful search terms.
2. **Full-Text Search**: The `_search_transcripts` method performs a full-text search on the `voice_memos` table using `ts_rank` and `plainto_tsquery`.
3. **Result Formatting**: The `_format_results` method formats the search results to include duration, preview, and creation date.
4. **Summary Building**: The `_build_summary` method creates a human-readable summary of the search results.

#### Integration Points
- **SkillBase**: The `SearchVoiceMemoSkill` class inherits from `SkillBase`, integrating with the broader Mythos skill system.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos request-response framework.
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database, integrating with the Mythos database layer.

This file is a critical component of the Mythos system, enabling users to search through voice memos efficiently and providing well-formatted results and summaries.
