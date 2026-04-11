# eval/challenges/log_life_event/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 34

---

### Documentation for `eval/challenges/log_life_event/build_plan.json`

#### Purpose
This JSON file serves as a blueprint for building a skill in the Mythos system that logs life events into a PostgreSQL database. It outlines the structure, logic, and testing requirements for the `LogLifeEventSkill` class.

#### Architecture
The file is structured as a JSON object containing several key sections:
- **plan_id**: Identifies the skill.
- **version**: Version of the skill.
- **description**: Brief description of the skill's purpose.
- **pattern**: Indicates the type of skill (action_skill).
- **model_hint**: Specifies the AI model to use.
- **context**: Contains detailed information about the skill's implementation, including database schema, class structure, and mandatory patterns.
- **build_plan**: A step-by-step guide for implementing the skill.
- **test_cases**: Example test cases to validate the skill.

#### Patterns
- **Factory Pattern**: The `LogLifeEventSkill` class can be seen as a factory for creating instances that log life events.
- **Singleton Pattern**: The `_get_conn` function ensures a single connection to the database.
- **Observer Pattern**: The `SkillResponse` class can be seen as an observer that collects and reports the outcome of the skill execution.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `RealDictCursor`, `dotenv`, `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Class**: `LogLifeEventSkill` extends `SkillBase`.
- **Methods**: `execute`, `_extract_description`, `_detect_domain`, `_detect_person`, `_insert_event`.
- **Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.

#### Database
- **Table**: `life_events`
- **Columns**: `id`, `description`, `domain`, `person`, `mood`, `source`, `source_message`, `created_at`.

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.
- **Database Connection**: Configured using `psycopg2.connect`.

#### Key Logic
1. **Extract Description**: Remove trigger phrases and normalize the message.
2. **Detect Domain**: Identify the domain of the event based on keywords.
3. **Detect Person**: Identify the person involved based on names.
4. **Insert Event**: Insert the event into the `life_events` table and return the new ID.
5. **Execute**: Combine the above steps to log the event and return a `SkillResponse`.

#### Integration Points
- **Database**: Connects to PostgreSQL to insert life events.
- **SkillBase**: Inherits from `SkillBase` to leverage common skill functionality.
- **SkillResponse**: Uses `SkillResponse` to return the outcome of the skill execution.
- **Environment**: Uses environment variables to configure the database connection.

### Detailed Breakdown of Key Sections

#### Context
- **System Context**: Specifies the database connection details and imports required.
- **Table Schema**: Defines the `life_events` table structure.
- **Scaffold**: Provides a template for the `LogLifeEventSkill` class with placeholders for methods.
- **Mandatory Patterns**: Includes specific patterns for database connection, connection cleanup, and `SkillResponse` usage.

#### Build Plan
- **Pass 1**: Write the file skeleton with imports and class structure.
- **Pass 2**: Implement `_extract_description`, `_detect_domain`, and `_detect_person` methods.
- **Pass 3**: Implement `_insert_event` method to insert events into the database.
- **Pass 4**: Implement the `execute` method to orchestrate the logging process.
- **Pass 5**: Review and ensure production readiness.

#### Test Cases
- **Test Case 1**: Logs a conversation about astrology.
- **Test Case 2**: Logs a good day at school for Fitz.
- **Test Case 3**: Logs an event with a message that is too short to determine the event.

This JSON file provides a comprehensive guide for implementing and testing the `LogLifeEventSkill` in the Mythos system, ensuring that all aspects of the skill are well-defined and thoroughly tested.
