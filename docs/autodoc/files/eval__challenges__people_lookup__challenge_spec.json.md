# eval/challenges/people_lookup/challenge_spec.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 101

---

### File: eval/challenges/people_lookup/challenge_spec.json

#### Purpose
This JSON file specifies the requirements and validation criteria for the "people_lookup" challenge in the Mythos system. It outlines the expected behavior, database schema, and structural requirements for the `PeopleLookupSkill` class.

#### Architecture
The file is structured as a JSON object with several key sections:
- **Metadata**: Contains basic information about the challenge.
- **Requirement**: Specifies the natural language requirement, skill details, and triggers.
- **System Context**: Provides details about the database schema, connection pattern, and required imports.
- **Expected Behavior**: Lists test cases to validate the skill's behavior.
- **Validation Criteria**: Defines structural and behavioral validation criteria for the skill.

#### Patterns
- **Configuration Pattern**: The file serves as a configuration file that defines the expected structure and behavior of the skill.
- **Validation Pattern**: The validation criteria section outlines the expected structure and behavior, ensuring the skill meets the specified requirements.

#### Dependencies
- **Database**: PostgreSQL
- **Python Libraries**: `psycopg2`, `dotenv`
- **Mythos Engine**: `engine.base` for `SkillBase`, `SkillRequest`, `SkillResponse`

#### Interfaces
- **Skill Class**: The skill should be implemented as a class named `PeopleLookupSkill` that subclasses `SkillBase`.
- **Methods**: The class must implement `async def execute(self, request: SkillRequest) -> SkillResponse`.

#### Database
- **Table**: `people` in the `public` schema.
- **Columns**: `id`, `first_name`, `last_name`, `known_as`, `date_of_birth`, `birth_city`, `birth_state`, `birth_country`, `created_at`, `updated_at`.
- **Indexes**: `people_pkey (id)`, `idx_people_last_name (last_name)`, `idx_people_dob (date_of_birth)`.

#### Configuration
- **Environment Variables**: Database connection details loaded from `/opt/mythos/.env` via `dotenv`.
- **Python Environment**: `/opt/mythos/.venv/bin/python3`.
- **Skill Directory**: `/opt/mythos/skills/data/`.

#### Key Logic
- **Search Logic**: The skill should search the `people` table by `first_name`, `last_name`, or `known_as` using case-insensitive matching.
- **Response Handling**: The skill should return a `SkillResponse` with a human-readable summary and structured data. If no search term is found, it should return the total count of people in the registry.

#### Integration Points
- **Mythos Engine**: The skill integrates with the Mythos engine through the `SkillBase` class and the `execute` method.
- **Database**: The skill interacts with the PostgreSQL database to query the `people` table.
- **Skill Directory**: The skill file (`people_lookup.py`) should be placed in `/opt/mythos/skills/data/`.

### Detailed Analysis

#### Metadata
- **Challenge ID**: `people_lookup`
- **Version**: `1.0`
- **Created By**: `claude`
- **Created At**: `2026-03-04`
- **Description**: Build a skill that searches the people registry by name, nickname, or ID.
- **Difficulty**: `beginner`
- **Category**: `data`
- **Stream**: `SYS`

#### Requirement
- **Natural Language Requirement**: The skill should search the `people` table based on user messages like "who is Adge" or "find person Rebecca".
- **Skill Name**: `people_lookup`
- **Class Name**: `PeopleLookupSkill`
- **Filename**: `people_lookup.py`
- **Category**: `data`
- **Cache TTL**: `600`
- **Triggers**: `["who is", "find person", "people", "person", "lookup", "born", "birthday", "birth data"]`

#### System Context
- **Database**: PostgreSQL
- **Database Name**: `mythos`
- **Connection Pattern**: `psycopg2` with `RealDictCursor`, loaded from `/opt/mythos/.env` via `dotenv`.
- **Table**: `people` in the `public` schema.
- **Columns**: Detailed schema of the `people` table.
- **Indexes**: `people_pkey (id)`, `idx_people_last_name (last_name)`, `idx_people_dob (date_of_birth)`.
- **Engine Import**: `from engine.base import SkillBase, SkillRequest, SkillResponse`.
- **Python Environment**: `/opt/mythos/.venv/bin/python3`.
- **Skill Directory**: `/opt/mythos/skills/data/`.

#### Expected Behavior
- **Test Cases**: Three test cases are provided to validate the skill's behavior:
  - `who is Adge`: Should return a summary containing "Adge".
  - `find person Rebecca`: Should return a summary containing "Rebecca".
  - `hello how are you`: Should handle the case where no search term is extractable.

#### Validation Criteria
- **Structural**: 
  - File parses as valid Python.
  - Contains exactly one class that subclasses `SkillBase`.
  - Class has specific attributes and methods.
  - Uses `_get_conn()` pattern with `psycopg2` and `RealDictCursor`.
  - Closes database connections in `try/finally`.
  - Returns `SkillResponse` with non-empty summary on success.
  - Returns `SkillResponse` with error field on failure.
  - Import line: `from engine.base import SkillBase, SkillRequest, SkillResponse`.
- **Behavioral**: 
  - Searches by `first_name`, `last_name`, and `known_as`.
  - Case-insensitive matching.
  - Returns structured person data in `response.data`.
  - Summary includes person names and birth dates when available.
  - Handles no-match case gracefully with informative summary.
  - Handles no-search-term case without crashing.

#### Gold Path
- **Gold Path**: `challenges/people_lookup/gold/people_lookup.py` — a reference implementation for the skill.

This JSON file serves as a comprehensive specification for developing and validating the `people_lookup` skill within the Mythos system.
