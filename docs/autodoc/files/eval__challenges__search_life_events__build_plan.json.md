# eval/challenges/search_life_events/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 78

---

### Documentation for `eval/challenges/search_life_events/build_plan.json`

#### Purpose
This JSON file serves as a blueprint for developing a Mythos skill named `SearchLifeEventsSkill`. The skill aims to search life events by keyword, domain, or person from a PostgreSQL database table named `life_events`.

#### Architecture
The file is structured as a JSON object containing several key sections:
- **plan_id**: Identifies the plan.
- **version**: Version of the plan.
- **description**: Brief description of the skill.
- **context**: Contains detailed information about the system context, table schema, scaffold code, and mandatory patterns.
- **build_plan**: A step-by-step guide to implement the skill, divided into multiple passes.
- **test_cases**: Example test cases to validate the skill's functionality.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function is designed to be a singleton pattern to ensure a single database connection instance.
- **Factory Method**: The `execute` method acts as a factory method to construct and return a `SkillResponse` object based on the input request.

#### Dependencies
- **Imports**: The skill relies on `os`, `logging`, `psycopg2`, `psycopg2.extras.RealDictCursor`, `dotenv`, and `engine.base`.
- **Environment Variables**: The connection to PostgreSQL is configured using environment variables (`POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`).

#### Interfaces
- **SkillBase Class**: The `SearchLifeEventsSkill` class inherits from `SkillBase` and implements methods like `execute`, `_extract_search_terms`, `_detect_filters`, `_search_events`, `_format_results`, and `_build_summary`.
- **SkillRequest and SkillResponse**: The `execute` method takes a `SkillRequest` object and returns a `SkillResponse` object.

#### Database
- **Table**: `life_events` with columns including `id`, `description`, `domain`, `person`, `mood`, `source`, `source_message`, `extraction_data`, `actions_taken`, and `created_at`.
- **Indexes**: Indexes on `id`, `created_at`, `domain`, and `person`.

#### Configuration
- **Environment Variables**: Connection details are loaded from environment variables.
- **Config Files**: The `.env` file in `/opt/mythos/` is used to load PostgreSQL connection details.

#### Key Logic
1. **_extract_search_terms**: Removes trigger phrases and normalizes whitespace.
2. **_detect_filters**: Identifies domain and person filters from the message.
3. **_search_events**: Constructs and executes a dynamic SQL query to search the `life_events` table.
4. **_format_results**: Formats the search results into a list of dictionaries.
5. **_build_summary**: Constructs a summary string based on the search results.
6. **execute**: Orchestrates the search process, handling both the case with and without search terms or filters.

#### Integration Points
- **Database Connection**: The skill integrates with the PostgreSQL database using the `_get_conn` function.
- **SkillBase Class**: The skill integrates with the Mythos skill framework through the `SkillBase` class and its methods.
- **Environment Configuration**: The skill relies on environment variables for database connection details.

### Detailed Breakdown of Build Plan Passes

1. **Pass 1**: Write the complete file skeleton with necessary imports and class structure.
2. **Pass 2**: Implement `_extract_search_terms` and `_detect_filters` methods.
3. **Pass 3**: Implement `_search_events` method to dynamically construct and execute SQL queries.
4. **Pass 4**: Implement `_format_results` and `_build_summary` methods to format and summarize search results.
5. **Pass 5**: Implement the `execute` method to orchestrate the search process and return responses.
6. **Pass 6**: Review and finalize the complete file, ensuring all connections are properly closed and no unicode characters are used in comments.

### Test Cases
- **Test Case 1**: Search for "spiritual" domain.
- **Test Case 2**: Search for recent events.
- **Test Case 3**: No terms or filters - should return the total count of life events.

This JSON file provides a comprehensive guide for developing the `SearchLifeEventsSkill` skill within the Mythos system, ensuring proper integration with the PostgreSQL database and adherence to best coding practices.
