# eval/results/search_voice_memos/20260304_185923/pass06_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 202

---

### Documentation for `pass06_attempt02.py`

#### Purpose
This file implements a skill for searching voice memo transcripts using PostgreSQL's full-text search capabilities. It processes user requests to extract search terms, performs the search, formats the results, and builds a summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class has several methods to handle different aspects of the search process:
- `execute`: Main method to handle the search request.
- `_extract_search_terms`: Extracts search terms from the user message.
- `_search_transcripts`: Executes the full-text search query.
- `_format_results`: Formats the search results into a more readable form.
- `_build_summary`: Builds a human-readable summary of the search results.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: An asynchronous function to handle the skill execution.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern as it ensures a single connection object is returned.
- **Factory Method Pattern**: The `execute` method acts as a factory method, orchestrating the creation and processing of search results.

#### Dependencies
- `os`: For environment variable handling.
- `logging`: For logging errors.
- `psycopg2`: For PostgreSQL database operations.
- `typing`: For type hints.
- `dotenv`: For loading environment variables from `.env` files.
- `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Public Methods**: 
  - `execute`: Asynchronous method to handle the skill execution.
- **Private Methods**: 
  - `_extract_search_terms`: Extracts search terms from the user message.
  - `_search_transcripts`: Executes the full-text search query.
  - `_format_results`: Formats the search results.
  - `_build_summary`: Builds a summary of the search results.
- **Top-level Functions**: 
  - `_get_conn`: Establishes a database connection.

#### Database
- **Tables**: 
  - `voice_memos`: Table containing voice memo data.
  - `top`: Potentially used for top-level queries or summaries.

#### Configuration
- **Environment Variables**: 
  - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Database connection details loaded from `.env` file.

#### Key Logic
- **Search Execution**: 
  - Extracts search terms from the user message.
  - Executes a full-text search query using PostgreSQL's `ts_rank` and `plainto_tsquery`.
  - Formats the results and builds a summary.
- **Error Handling**: 
  - Logs errors and returns a `SkillResponse` with an error message if an exception occurs.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill execution framework.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database.
- **SkillResponse**: Returns a `SkillResponse` object containing the search results and summary.

### Detailed Breakdown

#### Class: `SearchVoiceMemoSkill`
- **Attributes**:
  - `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`: Metadata for the skill.
- **Methods**:
  - `execute`: Main method to handle the search request. It extracts search terms, performs the search, formats results, and builds a summary.
  - `_extract_search_terms`: Removes trigger phrases and cleans the search terms.
  - `_search_transcripts`: Executes the full-text search query using PostgreSQL's text search capabilities.
  - `_format_results`: Formats the search results into a more readable form.
  - `_build_summary`: Builds a human-readable summary of the search results.

#### Top-level Functions
- `_get_conn`: Establishes a connection to the PostgreSQL database using environment variables for configuration.

### Example Usage
```python
# Example usage of SearchVoiceMemoSkill
skill = SearchVoiceMemoSkill()
request = SkillRequest(message="search voice memos about project updates")
response = await skill.execute(request)
print(response.summary)
```

This file is a crucial component of the Mythos system, enabling users to search through voice memo transcripts efficiently using PostgreSQL's powerful text search features.
