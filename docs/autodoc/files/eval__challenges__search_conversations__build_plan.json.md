# eval/challenges/search_conversations/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 78

---

### Documentation for `build_plan.json`

#### Purpose
This JSON file serves as a comprehensive build plan for developing a Mythos skill named `SearchConversationsSkill`. The skill is designed to perform full-text searches on conversation transcripts stored in a PostgreSQL database.

#### Architecture
The file is structured into several key sections:
1. **Plan Metadata**: Contains metadata about the plan, such as `plan_id`, `version`, and `description`.
2. **Context**: Provides detailed context about the system, including database connection details, table schema, and class scaffolding.
3. **Mandatory Patterns**: Lists mandatory patterns and guidelines for implementation.
4. **Build Plan**: Outlines step-by-step instructions for building the skill, divided into multiple passes.
5. **Test Cases**: Defines test cases to validate the functionality of the skill.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function is designed to create a database connection, which can be considered a singleton pattern for database connections.
- **Observer Pattern**: The skill class `SearchConversationsSkill` observes incoming requests and triggers specific methods based on the request content.

#### Dependencies
- **Imports**: The skill relies on `os`, `logging`, `psycopg2`, `psycopg2.extras.RealDictCursor`, `dotenv`, and `engine.base` (for `SkillBase`, `SkillRequest`, `SkillResponse`).
- **Environment Variables**: Uses environment variables for database connection details (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`).

#### Interfaces
- **SkillBase Class**: The `SearchConversationsSkill` class extends `SkillBase` and implements the `execute` method.
- **SkillRequest/SkillResponse**: The skill processes `SkillRequest` objects and returns `SkillResponse` objects.

#### Database
- **Tables**: The skill interacts with the `conversation_turns` and `conversations` tables.
- **Columns**: The `conversation_turns` table has columns like `conversation_id`, `turn_idx`, `speaker_type`, `speaker_id`, `created_at`, `token_estimate`, `content`, and `content_json`.
- **Queries**: Uses `ILIKE` for searching within the `content` column.

#### Configuration
- **Environment Variables**: Database connection details are loaded from environment variables.
- **Configuration Files**: The `.env` file in `/opt/mythos/` is used to load environment variables.

#### Key Logic
- **_extract_search_terms**: Removes trigger phrases from the message and normalizes whitespace.
- **_search_turns**: Executes a PostgreSQL query to search for terms in the `content` column using `ILIKE`.
- **_format_results**: Formats the search results into a list of dictionaries.
- **_build_summary**: Builds a human-readable summary of the search results.
- **execute**: Coordinates the execution of the skill by calling the above methods and handling exceptions.

#### Integration Points
- **Database Connection**: The skill integrates with the PostgreSQL database via the `_get_conn` function.
- **Skill System**: The skill integrates with the Mythos skill system, extending `SkillBase` and using `SkillRequest` and `SkillResponse` objects.

### Detailed Breakdown of Key Sections

#### Plan Metadata
- **plan_id**: `search_conversations`
- **version**: `1.0`
- **description**: Describes the purpose of the skill.

#### Context
- **System Context**: Provides details about the PostgreSQL database connection, required imports, skill directory, and Python virtual environment.
- **Table Schema**: Describes the `conversation_turns` and `conversations` tables.
- **Scaffold**: Provides a class template for `SearchConversationsSkill`.

#### Mandatory Patterns
- **_get_conn**: Defines the pattern for creating a database connection.
- **extract_whitespace**: Ensures whitespace is normalized after removing trigger phrases.
- **connection_cleanup**: Ensures database connections are properly closed.

#### Build Plan
- **Pass 1**: Skeleton file creation.
- **Pass 2**: Implementation of `_extract_search_terms`.
- **Pass 3**: Implementation of `_search_turns`.
- **Pass 4**: Implementation of `_format_results` and `_build_summary`.
- **Pass 5**: Implementation of `execute`.
- **Pass 6**: Final review and validation.

#### Test Cases
- **Test Case 1**: Validates search functionality with a message containing search terms.
- **Test Case 2**: Validates search functionality with another message containing search terms.
- **Test Case 3**: Validates handling of messages without search terms.

This comprehensive build plan ensures that the `SearchConversationsSkill` is developed in a structured and testable manner, adhering to the specified patterns and guidelines.
