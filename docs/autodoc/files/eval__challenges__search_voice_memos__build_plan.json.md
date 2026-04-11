# eval/challenges/search_voice_memos/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 73

---

### Documentation for `eval/challenges/search_voice_memos/build_plan.json`

#### Purpose
This JSON file serves as a comprehensive build plan for developing a Mythos skill named `search_voice_memos`. The skill is designed to perform full-text searches on voice memo transcripts stored in a PostgreSQL database.

#### Architecture
The file is structured into several key sections:
- **Meta Information**: Includes `plan_id`, `version`, `description`, `pattern`, and `model_hint`.
- **Context**: Provides details about the system context, table schema, and a scaffold for the skill class.
- **Build Plan**: A step-by-step guide to implement the skill, divided into multiple passes.
- **Test Cases**: Example test cases to validate the skill's functionality.

#### Patterns
- **Singleton**: The skill class `SearchVoiceMemoSkill` can be considered a singleton as it represents a single instance of the skill.
- **Factory**: The skill class is a factory for creating responses based on user input.

#### Dependencies
- **Python Libraries**: `os`, `logging`, `psycopg2`, `psycopg2.extras.RealDictCursor`, `dotenv`, `engine.base`.
- **Database**: PostgreSQL with specific table and index configurations.
- **Environment Variables**: Loaded from `/opt/mythos/.env` via `dotenv`.

#### Interfaces
- **SkillBase Class**: The skill class `SearchVoiceMemoSkill` inherits from `SkillBase` and implements methods like `execute`, `_extract_search_terms`, `_search_transcripts`, `_format_results`, and `_build_summary`.
- **SkillRequest and SkillResponse**: The `execute` method takes a `SkillRequest` and returns a `SkillResponse`.

#### Database
- **Tables**: `voice_memos` and `voice_memo_segments`.
- **Indexes**: `idx_voice_memos_transcript_fts` (GIN index for full-text search) and `idx_voice_memos_created` (btree index for creation date).

#### Configuration
- **Environment Variables**: Database connection details are loaded from `/opt/mythos/.env`.
- **Skill Directory**: `/opt/mythos/skills/data/`.

#### Key Logic
1. **_extract_search_terms**: Cleans and extracts search terms from the user message.
2. **_search_transcripts**: Executes a full-text search query on the `voice_memos` table using `ts_rank` for relevance scoring.
3. **_format_results**: Formats the search results into a clean dictionary format.
4. **_build_summary**: Constructs a human-readable summary of the search results.
5. **execute**: Orchestrates the extraction, search, formatting, and summary building processes.

#### Integration Points
- **Database Connection**: Uses `_get_conn()` to establish a connection to the PostgreSQL database.
- **SkillBase**: Inherits from `SkillBase` to integrate with the Mythos skill framework.
- **Environment**: Loads configuration from `.env` and uses `dotenv` for environment variable management.

### Detailed Breakdown of Key Sections

#### Context
- **System Context**: Specifies the database connection details, skill directory, and virtual environment Python path.
- **Table Schema**: Describes the `voice_memos` table and its columns, along with related indexes and the `voice_memo_segments` table.
- **Scaffold**: Provides a template for the `SearchVoiceMemoSkill` class with placeholders for methods.

#### Build Plan
- **Pass 1**: Writes the file skeleton, including shebang, docstring, imports, and class definition.
- **Pass 2**: Implements `_extract_search_terms` to clean and extract search terms.
- **Pass 3**: Implements `_search_transcripts` to execute the full-text search query.
- **Pass 4**: Implements `_format_results` and `_build_summary` to format and summarize results.
- **Pass 5**: Implements the `execute` method to orchestrate the search process.
- **Pass 6**: Reviews and finalizes the complete file for production readiness.

#### Test Cases
- **Test Case 1**: Validates the skill with a search term "love".
- **Test Case 2**: Validates the skill with a search term "relationship".
- **Test Case 3**: Validates the skill with a message that does not contain search terms, expecting a count or guidance message.

This comprehensive build plan ensures that the `search_voice_memos` skill is developed systematically, tested thoroughly, and integrated seamlessly into the Mythos system.
