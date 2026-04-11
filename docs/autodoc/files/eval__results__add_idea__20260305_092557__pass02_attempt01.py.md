# eval/results/add_idea/20260305_092557/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 132

---

### Purpose
The `AddIdeaSkill` class is designed to capture new ideas from user input, detect the domain of the idea, and store it in a PostgreSQL database table named `idea_inbox`. The class processes user messages to extract the idea text and determine its domain before inserting it into the database.

### Architecture
The `AddIdeaSkill` class extends the `SkillBase` class and includes the following methods:
- `execute`: The main entry point for the skill, which orchestrates the idea extraction, domain detection, and database insertion.
- `_extract_idea`: Extracts the idea text from the user message by removing predefined triggers and normalizing the text.
- `_detect_domain`: Determines the domain of the idea based on predefined keywords.
- `_insert_idea`: Inserts the idea into the `idea_inbox` table in the PostgreSQL database and returns the idea ID.

### Patterns
- **Singleton**: The `AddIdeaSkill` class is designed to be a singleton, as it is intended to be instantiated once and reused.
- **Factory**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object.

### Dependencies
- **Imports**: `os`, `logging`, `json`, `psycopg2`, `re`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` are loaded from `.env` file using `dotenv`.

### Interfaces
- **Public Methods**: `execute` is the public method that takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Private Methods**: `_extract_idea`, `_detect_domain`, and `_insert_idea` are private methods used internally by the class.

### Database
- **Tables**: The class interacts with the `idea_inbox` table in the PostgreSQL database.
- **Operations**: Inserts new ideas into the `idea_inbox` table.

### Configuration
- **Environment Variables**: The class relies on environment variables for database connection details (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`).
- **Triggers**: The class uses predefined triggers to detect when a user is providing a new idea.

### Key Logic
1. **Idea Extraction**: The `_extract_idea` method removes predefined triggers from the user message and normalizes the text.
2. **Domain Detection**: The `_detect_domain` method determines the domain of the idea based on predefined keywords.
3. **Database Insertion**: The `_insert_idea` method inserts the idea into the `idea_inbox` table and returns the idea ID.

### Integration Points
- **SkillBase**: The class extends `SkillBase`, which likely provides a framework for handling skill requests and responses.
- **Database Connection**: The class uses `psycopg2` to connect to the PostgreSQL database and perform insert operations.
- **Environment Configuration**: The class uses `dotenv` to load environment variables from a `.env` file, which is likely used to configure the database connection and other settings.

### Summary
The `AddIdeaSkill` class is a crucial component of the Mythos system, responsible for capturing and storing new ideas from user input. It leverages PostgreSQL for data storage and uses environment variables for configuration. The class is designed to be reusable and integrates seamlessly with the broader Mythos infrastructure.
