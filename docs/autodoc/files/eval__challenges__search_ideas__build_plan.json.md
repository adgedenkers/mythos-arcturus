# eval/challenges/search_ideas/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 77

---

### File: eval/challenges/search_ideas/build_plan.json

#### Purpose
This JSON file serves as a detailed build plan for developing a Mythos skill named `SearchIdeasSkill`. The skill is designed to search the idea inbox by keyword, domain, or disposition using PostgreSQL.

#### Architecture
The file is structured into several sections:
- **plan_id**: Identifies the plan.
- **version**: Version of the plan.
- **description**: Describes the skill's purpose.
- **pattern**: Indicates the memory search pattern.
- **model_hint**: Specifies the AI model hint.
- **context**: Contains detailed information about the system context, table schema, class scaffold, and mandatory patterns.
- **build_plan**: A step-by-step guide for implementing the skill.
- **test_cases**: Example test cases to validate the skill.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single connection instance.
- **Factory Pattern**: The `SearchIdeasSkill` class acts as a factory for creating instances of the skill.
- **Observer Pattern**: The skill observes user input and triggers based on specific keywords.

#### Dependencies
- **Imports**: `os`, `logging`, `json`, `psycopg2`, `psycopg2.extras.RealDictCursor`, `dotenv`, `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **SkillBase Class**: The `SearchIdeasSkill` class inherits from `SkillBase` and implements methods like `execute`, `_extract_search_terms`, `_detect_filters`, `_search_ideas`, `_format_results`, and `_build_summary`.
- **SkillRequest/SkillResponse**: The `execute` method takes `SkillRequest` and returns `SkillResponse`.

#### Database
- **Table**: `idea_inbox`
- **Columns**: `id`, `created_at`, `conversation_context`, `list_type`, `items`, `item_count`, `chosen_item`, `chosen_text`, `reviewed`, `disposition`, `domain`, `tags`.
- **Indexes**: `idea_inbox_pkey`, `idx_inbox_created`, `idx_inbox_disposition`, `idx_inbox_domain`, `idx_inbox_pending`.

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.
- **Config File**: `.env` file in `/opt/mythos/`.

#### Key Logic
1. **_extract_search_terms**: Removes trigger phrases and normalizes whitespace.
2. **_detect_filters**: Detects disposition and domain filters from the message.
3. **_search_ideas**: Constructs and executes a PostgreSQL query to search the `idea_inbox` table.
4. **_format_results**: Formats the query results into a list of dictionaries.
5. **_build_summary**: Builds a summary string based on the search results.
6. **execute**: Orchestrates the search process and returns a `SkillResponse`.

#### Integration Points
- **Database Connection**: Uses `_get_conn` to connect to PostgreSQL.
- **Skill Execution**: Integrates with the Mythos skill execution framework via `SkillBase`.
- **Environment Configuration**: Loads configuration from `.env` using `dotenv`.

### Detailed Breakdown of Build Plan Steps

1. **Pass 1**: Write the file skeleton with the `_get_conn` function and the `SearchIdeasSkill` class.
2. **Pass 2**: Implement `_extract_search_terms` and `_detect_filters`.
3. **Pass 3**: Implement `_search_ideas` to query the `idea_inbox` table.
4. **Pass 4**: Implement `_format_results` and `_build_summary` to format and summarize the results.
5. **Pass 5**: Implement the `execute` method to orchestrate the search process.
6. **Pass 6**: Review the complete file for production readiness.

### Test Cases
- **Test Case 1**: Search ideas about consulting.
- **Test Case 2**: Check pending ideas.
- **Test Case 3**: No terms - should return pending count.

This JSON file provides a comprehensive guide for developing the `SearchIdeasSkill` skill within the Mythos system, ensuring all necessary components and logic are implemented correctly.
