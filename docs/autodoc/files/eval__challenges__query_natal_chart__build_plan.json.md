# eval/challenges/query_natal_chart/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 35

---

### Documentation for `eval/challenges/query_natal_chart/build_plan.json`

#### Purpose
This JSON file serves as a blueprint for constructing a skill in the Mythos system that queries natal chart placements for a person from the astrology tables in a PostgreSQL database.

#### Architecture
The file is structured as a JSON object with several key sections:
- **plan_id**: Identifies the plan.
- **version**: Specifies the version of the plan.
- **description**: Provides a brief description of the plan's purpose.
- **pattern**: Indicates the type of skill (data_query_skill).
- **model_hint**: Suggests the AI model to use for generating the skill code.
- **context**: Contains detailed information about the database schema, mandatory patterns, and other context needed for the skill.
- **build_plan**: Outlines the step-by-step instructions for building the skill.
- **test_cases**: Lists test cases to validate the skill's functionality.

#### Patterns
- **Data Query Skill Pattern**: The skill is designed to query data from a database and return it in a structured format.
- **Mandatory Patterns**: Specific patterns like `_get_conn`, `connection_cleanup`, `no_unicode`, `skillresponse_signature`, and `fetchone_dict` are enforced to ensure consistency and proper handling of database connections and responses.

#### Dependencies
- **Imports**: The skill will import `os`, `logging`, `psycopg2`, `RealDictCursor`, `dotenv`, and `engine.base`.
- **Environment Variables**: The skill relies on environment variables such as `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_PORT`.

#### Interfaces
- **Class**: `QueryNatalChartSkill` with methods `execute`, `_resolve_name`, `_query_chart`, `_query_placements`, `_format`, and `_build_summary`.
- **SkillResponse**: The skill returns responses using the `SkillResponse` class, which includes fields like `skill_name`, `data`, `summary`, `confidence`, `sources`, and `error`.

#### Database
- **Tables**: The skill interacts with two PostgreSQL tables:
  - `astro_natal_charts`: Contains natal chart information.
  - `astro_chart_objects`: Contains placements of celestial objects in the natal chart.
- **Queries**: The skill performs SELECT queries on these tables to retrieve chart information and placements.

#### Configuration
- **Environment Variables**: The skill uses environment variables to configure the PostgreSQL connection.
- **Class-Level Constants**: The skill uses a class-level dictionary `NAME_MAP` to map aliases to actual names in the database.

#### Key Logic
- **_resolve_name**: Converts input names to their canonical form using `NAME_MAP`.
- **_query_chart**: Retrieves the natal chart information for a given name.
- **_query_placements**: Retrieves the placements of celestial objects for a given chart.
- **_format**: Formats the retrieved data into a structured dictionary.
- **_build_summary**: Constructs a summary string describing the chart placements.
- **execute**: Orchestrates the resolution of the name, querying the chart and placements, formatting the data, and building the summary.

#### Integration Points
- **Database Connection**: The skill integrates with the PostgreSQL database using the `_get_conn` function.
- **Skill Base**: The skill inherits from `SkillBase` and uses `SkillRequest` and `SkillResponse` from `engine.base`.
- **Environment Configuration**: The skill reads configuration from environment variables to connect to the database.

### Detailed Breakdown of Build Plan Steps

1. **Pass 1**: Write the file skeleton, including imports and class definition.
2. **Pass 2**: Implement `_resolve_name` and `_query_chart` methods.
3. **Pass 3**: Implement `_query_placements` method.
4. **Pass 4**: Implement `_format` and `_build_summary` methods.
5. **Pass 5**: Implement the `execute` method to orchestrate the skill's logic.
6. **Pass 6**: Review and ensure production readiness, including correct usage of environment variables and database schema.

### Test Cases
- **Test Case 1**: Query for "adge natal chart" should return placements and summary.
- **Test Case 2**: Query for "seraphe moon" should return the moon's placement.
- **Test Case 3**: Query for an unknown name should return a message indicating no chart is found.

This JSON file provides a comprehensive guide for developing a robust and well-integrated skill within the Mythos system.
