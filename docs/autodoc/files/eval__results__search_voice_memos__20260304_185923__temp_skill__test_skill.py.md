# eval/results/search_voice_memos/20260304_185923/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 202

---

### Documentation for `test_skill.py`

#### Purpose
The `test_skill.py` file implements a skill called `SearchVoiceMemoSkill` that enables full-text search across voice memo transcripts using PostgreSQL's text search capabilities. This skill is part of the Mythos system and is designed to process user requests for searching voice memos based on specific terms.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class has several methods:
- `execute`: The main method that processes the user request.
- `_extract_search_terms`: Extracts search terms from the user message.
- `_search_transcripts`: Executes the full-text search query on the `voice_memos` table.
- `_format_results`: Formats the search results into a more readable form.
- `_build_summary`: Builds a summary of the search results.

Additionally, there are several top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: A top-level function that mirrors the class method for testing purposes.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton as it ensures a single database connection is established.
- **Factory Method Pattern**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object based on the search results.

#### Dependencies
- `os`: For environment variable handling.
- `logging`: For logging errors.
- `psycopg2`: For PostgreSQL database interactions.
- `dotenv`: For loading environment variables from a `.env` file.
- `typing`: For type hints.
- `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- The `SearchVoiceMemoSkill` class implements the `execute` method, which is part of the `SkillBase` interface.
- The `execute` method returns a `SkillResponse` object containing the search results and a summary.

#### Database
- **Tables**: The `voice_memos` table is queried to retrieve voice memo transcripts.
- **Operations**: The file performs SELECT operations on the `voice_memos` table to extract and rank search results.

#### Configuration
- **Environment Variables**: The file uses environment variables for database connection details (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).
- **Dotenv**: The `.env` file located at `/opt/mythos/.env` is loaded to access these environment variables.

#### Key Logic
- **Search Terms Extraction**: The `_extract_search_terms` method removes predefined trigger phrases from the user message and returns a cleaned search string.
- **Full-Text Search**: The `_search_transcripts` method uses PostgreSQL's full-text search capabilities (`to_tsvector`, `plainto_tsquery`, `ts_rank`) to search and rank the voice memo transcripts.
- **Result Formatting**: The `_format_results` method formats the search results into a list of dictionaries, truncating transcript previews and formatting durations.
- **Summary Building**: The `_build_summary` method constructs a human-readable summary of the search results.

#### Integration Points
- **SkillBase**: The `SearchVoiceMemoSkill` class inherits from `SkillBase`, integrating with the Mythos skill framework.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, integrating with the Mythos data storage.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object, integrating with the Mythos response handling system.

This documentation provides a comprehensive overview of the `test_skill.py` file, detailing its purpose, architecture, dependencies, interfaces, database interactions, configuration, key logic, and integration points within the Mythos system.
