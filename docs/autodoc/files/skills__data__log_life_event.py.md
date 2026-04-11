# skills/data/log_life_event.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 124

---

### File: skills/data/log_life_event.py

#### Purpose
This file defines the `LogLifeEventSkill` class, which is responsible for logging life events into a PostgreSQL database. The skill processes user messages to extract event descriptions, detect domains and persons, and insert these events into the `life_events` table.

#### Architecture
The file contains a single class `LogLifeEventSkill` that inherits from `SkillBase`. The class has several methods to handle the extraction of event details and the insertion of these events into the database. Additionally, there are top-level functions for extracting descriptions, detecting domains and persons, and inserting events into the database.

#### Patterns
- **Factory Method**: The `_get_conn` function acts as a factory method to create a database connection.
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it provides a single point of connection creation.

#### Dependencies
- **Imports**: `os`, `logging`, `psycopg2`, `re`, `dotenv`, `SkillBase` from `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Public Methods**:
  - `execute`: Asynchronous method to process the user request and log the event.
- **Private Methods**:
  - `_extract_description`: Extracts the event description from the message.
  - `_detect_domain`: Detects the domain of the event.
  - `_detect_person`: Detects the person associated with the event.
  - `_insert_event`: Inserts the event into the `life_events` table.
- **Top-level Functions**:
  - `_get_conn`: Returns a PostgreSQL database connection.

#### Database
- **Tables/Labels**: The file interacts with the `life_events` table in PostgreSQL to insert new life events.

#### Configuration
- **Environment Variables**: The file uses environment variables to configure the PostgreSQL connection.
- **Dotenv**: The `dotenv` library is used to load environment variables from a `.env` file.

#### Key Logic
1. **Message Processing**: The `execute` method processes the user message to extract the event description, domain, and person.
2. **Event Insertion**: The `_insert_event` method inserts the extracted details into the `life_events` table.
3. **Error Handling**: The method handles exceptions and logs errors appropriately.

#### Integration Points
- **SkillBase**: The `LogLifeEventSkill` class inherits from `SkillBase`, integrating with the broader Mythos skill system.
- **Database Connection**: The `_get_conn` function provides a connection to the PostgreSQL database, integrating with the database subsystem.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object, integrating with the Mythos response handling system.

### Detailed Breakdown

#### Class: `LogLifeEventSkill`
- **Attributes**:
  - `name`: 'log_life_event'
  - `version`: '1.0'
  - `category`: 'action'
  - `description`: 'Log a new life event'
  - `triggers`: List of trigger phrases for the skill
  - `cache_ttl`: Cache time-to-live (0 for no caching)
- **Methods**:
  - `execute`: Asynchronous method to process the user request and log the event.
  - `_extract_description`: Extracts the event description from the message.
  - `_detect_domain`: Detects the domain of the event.
  - `_detect_person`: Detects the person associated with the event.
  - `_insert_event`: Inserts the event into the `life_events` table.

#### Top-level Functions
- **_get_conn**: Returns a PostgreSQL database connection using environment variables for configuration.

#### Key Logic in `execute` Method
1. **Extract Description**: Uses `_extract_description` to clean and extract the event description from the message.
2. **Validate Description**: Checks if the description is valid and returns an error response if not.
3. **Detect Domain and Person**: Uses `_detect_domain` and `_detect_person` to determine the domain and person associated with the event.
4. **Insert Event**: Uses `_insert_event` to insert the event into the `life_events` table.
5. **Return Response**: Returns a `SkillResponse` object with the event details and a confirmation message.

#### Key Logic in `_insert_event` Method
1. **Database Connection**: Uses `_get_conn` to establish a connection to the PostgreSQL database.
2. **Insert Query**: Executes an `INSERT` query to add the event to the `life_events` table.
3. **Transaction Management**: Manages transactions by committing or rolling back based on the success of the insertion.
4. **Error Handling**: Logs and raises exceptions if an error occurs during the insertion.

This file is a critical component of the Mythos system, enabling the logging of life events with structured data and integration with the PostgreSQL database.
