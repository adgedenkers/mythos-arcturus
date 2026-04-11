# eval/challenges/log_checkin/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 75

---

### File: eval/challenges/log_checkin/build_plan.json

#### Purpose
This JSON file serves as a detailed build plan and specification for the `LogCheckinSkill` class, which is responsible for recording mood or status check-ins in the Mythos system. It includes instructions for implementing the class, its methods, and the necessary database interactions.

#### Architecture
The file is structured as a JSON object with several key sections:
- **plan_id**: Identifies the plan.
- **version**: Specifies the version of the plan.
- **description**: Describes the purpose of the skill.
- **pattern**: Indicates the type of skill.
- **model_hint**: Suggests the model to use.
- **context**: Contains detailed information about the class structure, database schema, and mandatory patterns.
- **build_plan**: A step-by-step guide for implementing the skill.
- **test_cases**: Provides test cases to validate the implementation.

#### Patterns
- **Factory Pattern**: The `LogCheckinSkill` class is a factory for creating instances that handle check-in requests.
- **Singleton Pattern**: The `_get_conn` function ensures a single connection to the PostgreSQL database.
- **Observer Pattern**: The `execute` method observes the input message and triggers the appropriate actions.

#### Dependencies
- **Imports**: 
  - `os`, `logging`, `psycopg2`, `RealDictCursor`, `dotenv`, `engine.base`
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`

#### Interfaces
- **Class**: `LogCheckinSkill` inherits from `SkillBase` and implements the following methods:
  - `execute`: Main method to process the check-in request.
  - `_extract_mood`: Extracts the mood/status from the message.
  - `_insert_checkin`: Inserts the check-in into the database.
- **SkillResponse**: The class returns instances of `SkillResponse` with specific attributes.

#### Database
- **Table**: `checkin_log`
  - **Columns**:
    - `id`: Primary key, auto-incremented.
    - `checkin_date`: Date of the check-in.
    - `checkin_time`: Timestamp of the check-in.
    - `checkin_type`: Type of check-in (e.g., 'morning', 'evening', 'midday', 'mood').
    - `summary`: The mood or status text.
    - `user_response`: The original message.
    - `created_at`: Timestamp when the record was created.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`
- **Database Connection**: Configured using `psycopg2.connect` with environment variables.

#### Key Logic
- **_extract_mood**: 
  - Converts the message to lowercase.
  - Removes specific triggers from the message.
  - Normalizes whitespace and returns the remaining text as the mood/status.
- **_insert_checkin**: 
  - Connects to the PostgreSQL database using `_get_conn`.
  - Inserts a new record into `checkin_log` with the extracted mood and original message.
  - Returns the ID of the newly inserted record.
- **execute**: 
  - Extracts the mood from the message.
  - If the mood is not valid, returns a `SkillResponse` asking for the mood.
  - Inserts the check-in into the database and returns a `SkillResponse` confirming the check-in.

#### Integration Points
- **Database Integration**: Uses PostgreSQL to store check-in records.
- **SkillBase Integration**: Inherits from `SkillBase` and integrates with the Mythos skill framework.
- **Environment Variables**: Uses environment variables for database connection details.

### Detailed Breakdown of Build Plan Steps
1. **Pass 1**: Write the file skeleton with necessary imports and class structure.
2. **Pass 2**: Implement the `_extract_mood` method to process the input message.
3. **Pass 3**: Implement the `_insert_checkin` method to insert the check-in into the database.
4. **Pass 4**: Implement the `execute` method to handle the check-in request and return a response.
5. **Pass 5**: Review the implementation to ensure it meets all requirements and is production-ready.

### Test Cases
- **Test Case 1**: Validates a message with a clear mood.
- **Test Case 2**: Validates a message with a detailed mood.
- **Test Case 3**: Validates a message without a specified mood, expecting a follow-up request.

This JSON file provides a comprehensive guide for implementing the `LogCheckinSkill` class, ensuring that all aspects of the skill, from database interactions to user responses, are thoroughly documented and tested.
