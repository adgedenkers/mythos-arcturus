# eval/results/search_voice_memos/20260304_184607/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 200

---

### Documentation for `test_skill.py`

#### Purpose
The `test_skill.py` file implements a skill named `SearchVoiceMemoSkill` that performs full-text search across voice memo transcripts stored in a PostgreSQL database. It processes user queries to extract search terms, searches the transcripts, formats the results, and builds a summary for the user.

#### Architecture
The file is structured around a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class contains several methods to handle different parts of the search process:
- `_extract_search_terms`: Extracts search terms from the user message.
- `_search_transcripts`: Executes the full-text search query on the database.
- `_format_results`: Formats the search results into a user-friendly format.
- `_build_summary`: Builds a summary of the search results.
- `execute`: The main method that orchestrates the search process and returns the response.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a database connection using environment variables.
- `execute`: A top-level function that mirrors the class method for testing purposes.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton as it ensures a single database connection is established per call.
- **Factory Method Pattern**: The `execute` method acts as a factory method, creating and returning a `SkillResponse` object.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async) is the primary method that processes the user request and returns a `SkillResponse`.
- **Internal Methods**: `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary` are used internally to handle specific parts of the search process.

#### Database
- **Tables**: `voice_memos` (PostgreSQL) is queried for full-text search and to retrieve voice memo details.
- **Queries**: Uses `to_tsvector` and `plainto_tsquery` for full-text search, and `ts_rank` for relevance scoring.

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables.
- **Dotenv File**: `.env` file located at `/opt/mythos/.env` is used to load environment variables.

#### Key Logic
- **Search Terms Extraction**: The `_extract_search_terms` method removes trigger phrases and cleans the message to extract search terms.
- **Full-Text Search**: The `_search_transcripts` method performs a full-text search using PostgreSQL's `to_tsvector` and `plainto_tsquery` functions.
- **Result Formatting**: The `_format_results` method formats the search results to include duration in minutes and seconds, truncated transcript previews, and creation timestamps.
- **Summary Building**: The `_build_summary` method constructs a summary of the search results, including the number of matches and the top filenames.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill framework.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` objects to handle input and output.
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database, integrating with the Mythos database infrastructure.

This file is a crucial component of the Mythos system, enabling users to search through their voice memo transcripts efficiently and retrieve relevant information.
