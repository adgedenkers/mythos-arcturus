# eval/results/search_voice_memos/20260304_184607/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 127

---

### File: `eval/results/search_voice_memos/20260304_184607/pass03_attempt01.py`

#### Purpose
This file implements a skill (`SearchVoiceMemoSkill`) that performs full-text search across voice memo transcripts stored in a PostgreSQL database. It processes user requests to extract search terms, query the database, format the results, and build a human-readable summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class includes methods for executing the skill, extracting search terms, searching transcripts, formatting results, and building a summary. Additionally, there are top-level functions for getting the database connection and executing the skill.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is established.
- **Factory Method Pattern**: The `execute` method acts as a factory method, orchestrating the execution of various sub-methods to produce a `SkillResponse`.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `psycopg2`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` (async), `_extract_search_terms`, `_search_transcripts`, `_format_results`, `_build_summary`.
- **Public Functions**: `_get_conn`.

#### Database
- **Tables**: `voice_memos` (for storing voice memo data), `dotenv` (for loading environment variables), `psycopg2` (for database connection), `engine` (for skill base).

#### Configuration
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.
- **Configuration File**: `.env` (loaded using `dotenv`).

#### Key Logic
- **_extract_search_terms**: Removes trigger phrases and cleans the search string.
- **_search_transcripts**: Executes a full-text search query on the `voice_memos` table using `ts_rank` for relevance scoring.
- **_format_results**: Converts query results into a clean dictionary format.
- **_build_summary**: Constructs a human-readable summary of the search results.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill execution framework.
- **Database Connection**: Uses `_get_conn` to connect to the PostgreSQL database.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes for request and response handling.

### Detailed Documentation

#### Classes
- **SearchVoiceMemoSkill**
  - **Inheritance**: `SkillBase`
  - **Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`
  - **Methods**:
    - `execute`: Main execution method that orchestrates the search process.
    - `_extract_search_terms`: Cleans and extracts search terms from the user message.
    - `_search_transcripts`: Executes the full-text search query on the `voice_memos` table.
    - `_format_results`: Formats the query results into a clean dictionary format.
    - `_build_summary`: Builds a human-readable summary of the search results.

#### Top-level Functions
- **_get_conn**: Establishes a database connection using environment variables.
- **execute**: Asynchronous function to execute the skill.
- **_extract_search_terms**: Cleans and extracts search terms from the user message.
- **_search_transcripts**: Executes the full-text search query on the `voice_memos` table.
- **_format_results**: Formats the query results into a clean dictionary format.
- **_build_summary**: Builds a human-readable summary of the search results.

#### Key Logic and Algorithms
- **_extract_search_terms**: Uses regular expressions to remove trigger phrases and clean the search string.
- **_search_transcripts**: Uses PostgreSQL's full-text search capabilities (`ts_rank`, `plainto_tsquery`) to rank and retrieve relevant voice memo transcripts.
- **_format_results**: Ensures the results are formatted in a consistent and readable manner.
- **_build_summary**: Constructs a summary that includes the number of matches and brief details of the top results.

#### Integration Points
- **SkillBase**: The class inherits from `SkillBase` to integrate with the Mythos skill execution framework.
- **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes for handling requests and responses within the Mythos system.
