# eval/results/add_idea/20260305_092557/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 134

---

### Documentation for `eval/results/add_idea/20260305_092557/pass03_attempt01.py`

#### Purpose
This file defines the `AddIdeaSkill` class, which is responsible for capturing new ideas from user messages, detecting the domain of the idea, and storing it in a PostgreSQL database.

#### Architecture
- **Class Structure**: The `AddIdeaSkill` class inherits from `SkillBase` and contains methods for extracting the idea text, detecting the domain, and inserting the idea into the database.
- **Methods**:
  - `execute`: The main method that orchestrates the extraction, domain detection, and insertion of the idea.
  - `_extract_idea`: Extracts the idea text from the user message by removing specific triggers and normalizing the text.
  - `_detect_domain`: Determines the domain of the idea based on keywords in the message.
  - `_insert_idea`: Inserts the idea into the `idea_inbox` table in the PostgreSQL database and returns the new idea ID.

#### Patterns
- **Factory Pattern**: Not explicitly used, but the class can be seen as a factory for processing and storing ideas.
- **Singleton Pattern**: Not used.
- **Observer Pattern**: Not used.

#### Dependencies
- **Imports**:
  - `os`: For accessing environment variables.
  - `logging`: For logging errors.
  - `json`: For JSON serialization.
  - `psycopg2`: For PostgreSQL database operations.
  - `re`: For regular expression operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Asynchronous method that takes a `SkillRequest` object and returns a `SkillResponse` object.
  - `_extract_idea`: Synchronous method that takes a message string and returns the extracted idea text.
  - `_detect_domain`: Synchronous method that takes a message string and returns the detected domain.
  - `_insert_idea`: Synchronous method that takes the idea text, domain, and source message, and returns the new idea ID.

#### Database
- **Tables/Labels**:
  - `idea_inbox`: Table in the PostgreSQL database where ideas are stored. The `execute` method inserts new ideas into this table.

#### Configuration
- **Environment Variables**:
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Used to connect to the PostgreSQL database.

#### Key Logic
- **Extracting Idea Text**: The `_extract_idea` method removes specific triggers from the message and normalizes the text.
- **Detecting Domain**: The `_detect_domain` method checks for keywords in the message to determine the domain of the idea.
- **Inserting Idea**: The `_insert_idea` method inserts the idea into the `idea_inbox` table, including the conversation context, idea text, domain, and tags.

#### Integration Points
- **Mythos Subsystems**:
  - **SkillBase**: The `AddIdeaSkill` class inherits from `SkillBase`, which likely provides a framework for handling skills in the Mythos system.
  - **Database**: The `_insert_idea` method interacts with the PostgreSQL database to store ideas.
  - **Logging**: Errors are logged using the `logging` module, which may be integrated with the Mythos logging system.

### Summary
This file implements the `AddIdeaSkill` class, which captures new ideas from user messages, detects their domain, and stores them in a PostgreSQL database. The class is designed to be part of a larger Mythos system, integrating with the database and logging subsystems.
