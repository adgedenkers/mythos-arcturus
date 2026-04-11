# eval/results/search_voice_memos/20260304_185923/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 95

---

### File: eval/results/search_voice_memos/20260304_185923/pass02_attempt01.py

#### Purpose
This file implements the `SearchVoiceMemoSkill` class, which provides a full-text search capability across voice memo transcripts stored in a PostgreSQL database. The skill extracts search terms from user input, queries the database for matching transcripts, formats the results, and builds a human-readable summary.

#### Architecture
The file contains a single class `SearchVoiceMemoSkill` that inherits from `SkillBase`. The class includes methods for executing the search, extracting search terms, searching transcripts, formatting results, and building summaries. Additionally, there are top-level functions for database connection and executing the skill.

- **Classes**: 
  - `SearchVoiceMemoSkill`: Inherits from `SkillBase` and implements methods for handling the search process.
  
- **Methods**:
  - `execute`: Main method that orchestrates the search process.
  - `_extract_search_terms`: Cleans and extracts search terms from the user message.
  - `_search_transcripts`: Executes the full-text search query on the database.
  - `_format_results`: Formats the raw query results into a more readable form.
  - `_build_summary`: Constructs a human-readable summary of the search results.

- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database using environment variables.

#### Patterns
- **Factory Method**: The `_get_conn` function can be seen as a factory method for creating database connections.
- **Singleton**: The `_get_conn` function ensures a single connection is established per call, acting as a singleton for the connection process.

#### Dependencies
- **Imports**: 
  - `os`: For accessing environment variables.
  - `logging`: For logging purposes.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `typing`: For type hints.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse`.

#### Interfaces
- **Public Methods**:
  - `execute`: Exposed to other parts of the system for initiating the search process.
  - `_get_conn`: Exposed for establishing a database connection.

#### Database
- **Tables/Labels**:
  - The file references PostgreSQL tables, but specific table names are not explicitly mentioned in the code snippet. The `_search_transcripts` method is expected to query a table containing voice memo transcripts.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Used to configure the database connection.

- **Files**:
  - `.env`: Contains environment variables for database configuration.

#### Key Logic
- **_extract_search_terms**: Cleans the user message by removing trigger phrases and punctuation, ensuring the search terms are meaningful.
- **_search_transcripts**: Uses PostgreSQL's full-text search capabilities (`to_tsquery` and `plainto_tsquery`) to query the database for matching transcripts.
- **_format_results**: Converts raw query results into a more readable format, truncating transcript previews and formatting durations.
- **_build_summary**: Constructs a human-readable summary of the search results, including the number of matches and a brief snippet from the top result.

#### Integration Points
- **SkillBase**: The `SearchVoiceMemoSkill` class inherits from `SkillBase`, integrating with the broader Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos request-response model.
- **Database**: The `_get_conn` function integrates with the PostgreSQL database to execute full-text search queries.

This file is a critical component of the Mythos system, enabling users to search through voice memo transcripts efficiently and effectively.
