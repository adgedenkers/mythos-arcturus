# skills/data/people_lookup.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 187

---

### File: skills/data/people_lookup.py

#### Purpose
This file contains the `PeopleLookupSkill` class, which is responsible for searching the people registry in PostgreSQL by name, nickname, or ID. It returns matching person records with birth data and notes, and is used when Iris needs to identify someone, check birth details for astrology, or answer "who is X?" questions.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill`: Inherits from `SkillBase` and implements the `execute` method to handle the search logic.
- **Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `_extract_search_term`: Extracts the search term from the input message.
  - `_format_name`: Constructs a display name from the name parts.
  - `_format_birth_location`: Constructs a birth location string from the birth data.
- **Data Flow**: The class receives a `SkillRequest` object, processes it to extract a search term, queries the PostgreSQL database for matching records, formats the results, and returns a `SkillResponse` object.

#### Patterns
- **Singleton**: The `_get_conn` function is used to establish a database connection, which could be considered a singleton pattern if the connection is reused.
- **Factory**: The `PeopleLookupSkill` class can be seen as a factory that produces `SkillResponse` objects based on the input request.

#### Dependencies
- **Imports**:
  - `os`: For accessing environment variables.
  - `logging`: For logging errors and information.
  - `psycopg2`: For connecting to and querying the PostgreSQL database.
  - `typing`: For type hints.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Asynchronous method that processes the request and returns a `SkillResponse` object.
- **Exposed Functions**:
  - `_get_conn`: Returns a database connection.
  - `_extract_search_term`: Extracts the search term from a message.
  - `_format_name`: Formats a person's name.
  - `_format_birth_location`: Formats a person's birth location.

#### Database
- **Tables/Labels**:
  - `people`: The PostgreSQL table that stores person records, including fields like `first_name`, `last_name`, `known_as`, `date_of_birth`, `time_of_birth`, `birth_city`, `birth_state`, `birth_country`, `date_of_death`, `notes`, and `canonical_id`.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: Host for the PostgreSQL database.
  - `POSTGRES_DB`: Database name.
  - `POSTGRES_USER`: Username for the PostgreSQL database.
  - `POSTGRES_PASSWORD`: Password for the PostgreSQL database.
  - `POSTGRES_PORT`: Port for the PostgreSQL database.
- **Config Files**:
  - `.env`: Loaded using `dotenv.load_dotenv('/opt/mythos/.env')` to provide environment variables.

#### Key Logic
- **Search Logic**:
  - The `execute` method processes the input message to extract a search term.
  - It queries the `people` table in PostgreSQL to find matching records based on the search term.
  - It formats the results into a structured format and constructs a summary string.
- **Error Handling**:
  - The method logs any exceptions and returns an error response.

#### Integration Points
- **Mythos Subsystems**:
  - **SkillBase**: The `PeopleLookupSkill` class inherits from `SkillBase`, which likely provides a common interface for skill execution.
  - **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the broader Mythos skill execution framework.
  - **Database**: The skill interacts with the PostgreSQL database to retrieve and format person records, integrating with the Mythos data storage subsystem.

This file is a critical component of the Mythos system, enabling efficient and accurate person data retrieval and formatting for various use cases.
