# eval/results/search_voice_memos/20260304_184607/pass06_attempt03.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 213

---

### Documentation for `eval/results/search_voice_memos/20260304_184607/pass06_attempt03.py`

#### Purpose
This file implements a skill for searching voice memo transcripts using full-text search capabilities in PostgreSQL. It defines a class `SearchVoiceMemoSkill` that handles the extraction of search terms, execution of the search, formatting of results, and building of a summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class has several methods:
- `execute`: The main method for executing the search.
- `_extract_search_terms`: Extracts search terms from the input message.
- `_search_transcripts`: Executes the full-text search query.
- `_format_results`: Formats the search results.
- `_build_summary`: Builds a summary of the search results.

Additionally, there are several top-level functions:
- `_get_conn`: Establishes a database connection.
- `execute`: A top-level function that is likely a duplicate or placeholder for the class method.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is established.
- **Factory Method Pattern**: The `execute` method acts as a factory method for creating `SkillResponse` objects.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `re`: For regular expression operations.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- `execute`: Exposes the main functionality to other parts of the system, taking a `SkillRequest` and returning a `SkillResponse`.
- `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary`: Internal methods used by `execute` to process the request.

#### Database
- **Tables/Labels**: 
  - `voice_memos`: Table used for storing voice memo records.
  - `dotenv`: Configuration table or reference for environment variables.

#### Configuration
- **Environment Variables**: 
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Database connection details.
  - `.env` file: Loaded using `dotenv.load_dotenv`.

#### Key Logic
1. **Search Term Extraction**: The `_extract_search_terms` method removes trigger phrases and cleans the input message to extract meaningful search terms.
2. **Full-Text Search**: The `_search_transcripts` method uses PostgreSQL's full-text search capabilities to find matching voice memos.
3. **Result Formatting**: The `_format_results` method formats the search results into a more readable form.
4. **Summary Building**: The `_build_summary` method creates a human-readable summary of the search results.

#### Integration Points
- **SkillBase Class**: The `SearchVoiceMemoSkill` class integrates with the broader Mythos system through the `SkillBase` class, which likely handles the orchestration and routing of skill requests.
- **Database Connection**: The `_get_conn` function integrates with the PostgreSQL database to execute queries and retrieve results.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object, which is likely used by other parts of the system to process the search results.

### Summary
This file provides a comprehensive implementation for searching voice memo transcripts within the Mythos system. It leverages PostgreSQL's full-text search capabilities and integrates seamlessly with the system's skill architecture, ensuring that search requests are processed efficiently and results are presented in a user-friendly manner.
