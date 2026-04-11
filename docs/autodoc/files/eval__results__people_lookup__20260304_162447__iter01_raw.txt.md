# eval/results/people_lookup/20260304_162447/iter01_raw.txt

**Language:** text
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 91

---

### Documentation for `eval/results/people_lookup/20260304_162447/iter01_raw.txt`

#### Purpose
This file contains the implementation of the `PeopleLookupSkill`, a skill within the Mythos system designed to search for people in the Mythos registry based on various criteria such as first name, last name, or known as.

#### Architecture
- **Classes**: 
  - `PeopleLookupSkill` inherits from `SkillBase` and implements the `execute` method to handle skill execution.
- **Functions**:
  - `_get_conn()`: A helper function to establish a connection to the PostgreSQL database.
- **Data Flow**:
  - The skill receives a `SkillRequest` object, processes the request to extract a search term, queries the database for matching records, and returns a `SkillResponse` object with the results.

#### Patterns
- **Singleton**: The database connection is established and closed within the `execute` method, but the connection logic is encapsulated in the `_get_conn` function.
- **Factory**: The `SkillBase` class acts as a factory for creating skill instances.

#### Dependencies
- **Imports**:
  - `os`: For environment variable handling.
  - `logging`: For logging.
  - `typing`: For type hints.
  - `psycopg2`: For PostgreSQL database operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse`.

#### Interfaces
- **Exposed Interfaces**:
  - `execute(self, request: SkillRequest) -> SkillResponse`: The main method that processes the skill request and returns a response.

#### Database
- **Tables/Labels**:
  - **PostgreSQL Table**: `public.people` with columns `id`, `first_name`, `last_name`, `known_as`, `date_of_birth`, `birth_city`, `birth_state`.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configuration for connecting to the PostgreSQL database.
- **Config Files**:
  - `.env`: Loaded from `/opt/mythos/.env` to set environment variables.

#### Key Logic
- **Search Term Extraction**:
  - The skill identifies a search term by checking if any of the predefined triggers are present in the request message.
- **Database Query**:
  - If a search term is found, the skill performs a case-insensitive search on the `people` table using `LIKE` conditions on `first_name`, `last_name`, and `known_as` columns.
  - If no search term is found, it returns the count of all people in the registry.
- **Result Compilation**:
  - The skill compiles the results into a summary string, including names and birth information if available.

#### Integration Points
- **Mythos Engine**:
  - The skill integrates with the Mythos engine through the `SkillBase` class, which provides the framework for skill execution.
- **Database Layer**:
  - The skill interacts with the PostgreSQL database to retrieve people data.
- **Logging**:
  - The skill uses the Python `logging` module to log errors and other information.

### Summary
The `PeopleLookupSkill` is a well-structured skill within the Mythos system that leverages PostgreSQL to search for people based on various criteria. It integrates seamlessly with the Mythos engine and handles database interactions efficiently, providing a robust and flexible solution for people lookup operations.
