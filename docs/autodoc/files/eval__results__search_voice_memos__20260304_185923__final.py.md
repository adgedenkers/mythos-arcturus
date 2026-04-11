# eval/results/search_voice_memos/20260304_185923/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 202

---

### Documentation for `eval/results/search_voice_memos/20260304_185923/final.py`

#### Purpose
This file implements a skill for full-text search across voice memo transcripts using PostgreSQL's text search capabilities. It defines a class `SearchVoiceMemoSkill` that handles the extraction of search terms, execution of the search, formatting of results, and building of a summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class includes methods for executing the search, extracting search terms, searching transcripts, formatting results, and building a summary. Additionally, there are top-level functions for getting a database connection and executing the search.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is returned.
- **Factory Method**: The `execute` method acts as a factory method, orchestrating the execution of the search process by calling other methods.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `dotenv`, `typing`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Database**: PostgreSQL (`voice_memos` table)

#### Interfaces
- **Public Methods**: `execute`
- **Internal Methods**: `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary`
- **Top-Level Functions**: `_get_conn`

#### Database
- **Tables**: `voice_memos` (PostgreSQL)

#### Configuration
- **Environment Variables**: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` loaded from `.env` file

#### Key Logic
1. **Extract Search Terms**: `_extract_search_terms` removes trigger phrases from the input message and returns a cleaned search string.
2. **Search Transcripts**: `_search_transcripts` uses PostgreSQL's full-text search capabilities to find matching voice memos, ranking results by relevance.
3. **Format Results**: `_format_results` converts the raw database rows into a clean list of dictionaries, formatting durations and truncating transcript previews.
4. **Build Summary**: `_build_summary` creates a human-readable summary of the search results, including details of the top result.

#### Integration Points
- **SkillBase**: The `SearchVoiceMemoSkill` class inherits from `SkillBase`, integrating with the broader Mythos skill framework.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, integrating with the Mythos database infrastructure.
- **SkillRequest/SkillResponse**: The `execute` method uses `SkillRequest` and `SkillResponse` to handle input and output, integrating with the Mythos request/response model.

### Detailed Breakdown

#### Class `SearchVoiceMemoSkill`
- **Attributes**:
  - `name`: 'search_voice_memos'
  - `version`: '1.0'
  - `category`: 'data'
  - `description`: 'Full-text search across voice memo transcripts'
  - `triggers`: List of trigger phrases for the skill
  - `cache_ttl`: 300 seconds

- **Methods**:
  - `execute`: Main method to execute the search, extract terms, search transcripts, format results, and build a summary.
  - `_extract_search_terms`: Cleans the input message to extract valid search terms.
  - `_search_transcripts`: Executes the full-text search query on the `voice_memos` table.
  - `_format_results`: Formats the raw database rows into a clean list of dictionaries.
  - `_build_summary`: Builds a human-readable summary of the search results.

#### Top-Level Functions
- **_get_conn**: Establishes a connection to the PostgreSQL database using environment variables for configuration.

### Example Usage
```python
# Example usage of SearchVoiceMemoSkill
skill = SearchVoiceMemoSkill()
request = SkillRequest(message="search voice memos about project updates")
response = skill.execute(request)
print(response.summary)
```

This example demonstrates how the `SearchVoiceMemoSkill` can be instantiated and used to execute a search request, returning a summary of the results.
