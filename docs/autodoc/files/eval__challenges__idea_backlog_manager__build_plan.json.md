# eval/challenges/idea_backlog_manager/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 36

---

### File: eval/challenges/idea_backlog_manager/build_plan.json

#### Purpose
This JSON file serves as a build plan for the `IdeaBacklogManagerSkill` class, detailing the step-by-step development process, including the required methods, database interactions, and testing cases.

#### Architecture
The file is structured into several sections:
- **plan_id**: Identifier for the build plan.
- **version**: Version of the build plan.
- **description**: Description of the skill's purpose.
- **pattern**: Design pattern or skill type.
- **model_hint**: Model hint for the AI model to use.
- **context**: Contains system context, table schema, and mandatory patterns.
- **build_plan**: Step-by-step instructions for implementing the skill.
- **test_cases**: Test cases to validate the implementation.

#### Patterns
- **Data Query Skill**: The skill is designed to query and manage data from the database.
- **Singleton**: The `_get_conn` function ensures a consistent connection setup.

#### Dependencies
- **Imports**: `os`, `logging`, `json`, `psycopg2`, `RealDictCursor`, `dotenv`, `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Class**: `IdeaBacklogManagerSkill` with methods `execute`, `_get_pending_count`, `_get_backlog_status`, `_get_stream_breakdown`, `_build_summary`.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object with attributes `skill_name`, `data`, `summary`, `confidence`, `sources`, `error`.

#### Database
- **Tables**:
  - `idea_inbox`: Contains pending ideas with fields like `id`, `conversation_context`, `items`, `item_count`, `chosen_text`, `disposition`, `domain`, `tags`, `created_at`.
  - `idea_backlog`: Manages the backlog with fields like `id`, `inbox_id`, `title`, `description`, `stream`, `priority`, `status`, `created_at`.

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.
- **System Context**: Database connection details and mandatory patterns for implementation.

#### Key Logic
- **_get_pending_count**: Queries the count of pending ideas from `idea_inbox`.
- **_get_backlog_status**: Retrieves the status of items in the backlog grouped by stream, priority, and status.
- **_get_stream_breakdown**: Provides a breakdown of items in the backlog by stream, including counts of done, in progress, and backlog items.
- **_build_summary**: Constructs a summary string based on the pending count and backlog status.
- **execute**: Orchestrates the execution of the above methods and returns a `SkillResponse` object.

#### Integration Points
- **Database Connection**: Uses `_get_conn` to connect to PostgreSQL.
- **Engine Base**: Imports `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Test Cases**: Validates the skill with predefined messages and expected outcomes.

### Detailed Breakdown of Build Plan Steps

1. **Pass 1**: Write the file skeleton with necessary imports and class structure.
2. **Pass 2**: Implement `_get_pending_count` and `_get_backlog_status` methods.
3. **Pass 3**: Implement `_get_stream_breakdown` method.
4. **Pass 4**: Implement `_build_summary` method to construct the summary string.
5. **Pass 5**: Implement `execute` method to orchestrate the queries and return `SkillResponse`.
6. **Pass 6**: Review and ensure production readiness, including connection setup and ASCII compliance.

### Test Cases
- **Test Case 1**: Message "show me the idea backlog" expects `pending_count` in the response.
- **Test Case 2**: Message "what ideas are pending" expects a successful response.
- **Test Case 3**: Message "backlog status" expects a successful response.

This build plan ensures a structured and thorough development process for the `IdeaBacklogManagerSkill`, covering all necessary aspects from database interactions to testing.
