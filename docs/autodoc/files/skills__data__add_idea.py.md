# skills/data/add_idea.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 156

---

### File: skills/data/add_idea.py

#### Purpose
This file defines the `AddIdeaSkill` class, which is responsible for capturing new ideas from user messages, extracting the idea text, detecting the domain, and inserting the idea into the `idea_inbox` table in PostgreSQL.

#### Architecture
The file contains a single class `AddIdeaSkill` that inherits from `SkillBase`. It includes several methods for executing the skill, extracting the idea text, detecting the domain, and inserting the idea into the database. Additionally, there are top-level functions for database connection and idea extraction.

- **Class**: `AddIdeaSkill`
  - **Methods**:
    - `execute`: Main method to process the request, extract idea, detect domain, and insert into the database.
    - `_extract_idea`: Extracts the idea text from the user message.
    - `_detect_domain`: Detects the domain of the idea based on keywords.
    - `_insert_idea`: Inserts the idea into the `idea_inbox` table.
- **Top-level Functions**:
  - `_get_conn`: Establishes a connection to the PostgreSQL database.
  - `execute`: A top-level function that mirrors the class method for potential standalone execution.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern as it ensures a single database connection is used.
- **Factory Method Pattern**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `json`: For JSON serialization.
  - `psycopg2`: For PostgreSQL database operations.
  - `re`: For regular expression operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For the `SkillBase` class and related types.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Processes the request and returns a `SkillResponse` object.
- **Exposed Functions**:
  - `_get_conn`: Establishes a database connection.
  - `execute`: A top-level function that processes the request and returns a `SkillResponse` object.

#### Database
- **Tables/Labels**:
  - `idea_inbox`: Table in PostgreSQL where ideas are inserted.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configuration for the PostgreSQL database connection.

#### Key Logic
- **Idea Extraction**:
  - The `_extract_idea` method removes predefined triggers from the user message and normalizes the text.
- **Domain Detection**:
  - The `_detect_domain` method checks for keywords in predefined domains and returns the matching domain.
- **Database Insertion**:
  - The `_insert_idea` method inserts the idea into the `idea_inbox` table with relevant details and returns the idea ID.

#### Integration Points
- **Mythos Subsystems**:
  - **Database**: Interacts with the PostgreSQL database to insert ideas into the `idea_inbox` table.
  - **SkillBase**: Inherits from `SkillBase` to integrate with the skill execution framework.
  - **Environment Configuration**: Uses environment variables and `.env` file for configuration.

### Summary
The `AddIdeaSkill` class in `add_idea.py` is designed to process user messages, extract ideas, detect their domain, and store them in a PostgreSQL database. It leverages PostgreSQL for data persistence and uses environment variables for configuration. The class integrates with the Mythos skill execution framework by inheriting from `SkillBase` and exposing methods for skill execution and response generation.
