# eval/results/add_idea/20260305_092557/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 151

---

### Documentation for `test_skill.py`

#### Purpose
The `test_skill.py` file contains the implementation of the `AddIdeaSkill` class, which is responsible for capturing new ideas from user input, detecting the domain of the idea, and storing it in a PostgreSQL database table named `idea_inbox`.

#### Architecture
The file defines a single class `AddIdeaSkill` that inherits from `SkillBase`. The class contains four methods:
- `execute`: The main entry point for the skill, which processes the user request.
- `_extract_idea`: Extracts the idea text from the user message.
- `_detect_domain`: Detects the domain of the idea based on keywords in the message.
- `_insert_idea`: Inserts the idea into the `idea_inbox` table in the PostgreSQL database.

#### Patterns
- **Factory Method**: The `execute` method acts as a factory method, orchestrating the extraction, domain detection, and insertion of ideas.
- **Singleton**: The `AddIdeaSkill` class can be considered a singleton in the context of the skill system, as it is instantiated once and reused.

#### Dependencies
- **Imports**: 
  - `os`: For accessing environment variables.
  - `logging`: For logging errors.
  - `json`: For JSON serialization.
  - `psycopg2`: For PostgreSQL database operations.
  - `re`: For regular expression operations.
- **Environment Variables**: 
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: For database connection.

#### Interfaces
- **Exposed Methods**: 
  - `execute`: Asynchronous method that takes a `SkillRequest` object and returns a `SkillResponse` object.
- **Classes**: 
  - `AddIdeaSkill`: Inherits from `SkillBase` and implements the required methods.

#### Database
- **Tables/Labels**: 
  - `idea_inbox`: PostgreSQL table where ideas are inserted with fields such as `conversation_context`, `items`, `item_count`, `disposition`, `domain`, and `tags`.

#### Configuration
- **Environment Variables**: 
  - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: Configured in the `.env` file.
- **Configuration File**: 
  - `.env`: Loaded using `load_dotenv()` to set up database connection parameters.

#### Key Logic
- **Extract Idea**: The `_extract_idea` method removes predefined triggers from the message and normalizes the text.
- **Detect Domain**: The `_detect_domain` method checks for keywords in the message to determine the domain of the idea.
- **Insert Idea**: The `_insert_idea` method inserts the idea into the `idea_inbox` table with appropriate fields and returns the `idea_id`.

#### Integration Points
- **SkillBase**: The `AddIdeaSkill` class integrates with the `SkillBase` class, which likely provides a framework for handling skill requests and responses.
- **Database**: The skill interacts with the PostgreSQL database to store ideas in the `idea_inbox` table.
- **Environment Variables**: The skill relies on environment variables for database connection details, which are loaded from the `.env` file.

### Summary
The `test_skill.py` file implements the `AddIdeaSkill` class, which captures ideas from user input, detects their domain, and stores them in a PostgreSQL database. It integrates with the `SkillBase` framework and uses environment variables for configuration. The key logic involves text extraction, domain detection, and database insertion.
