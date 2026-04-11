# eval/results/add_idea/20260305_092557/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 151

---

### File: eval/results/add_idea/20260305_092557/final.py

#### Purpose
This file defines a skill named `AddIdeaSkill` that captures new ideas from user messages and stores them in a PostgreSQL database table named `idea_inbox`.

#### Architecture
The file contains a single class `AddIdeaSkill` that inherits from `SkillBase`. The class has four methods:
- `execute`: The main method that processes the user request and orchestrates the idea extraction, domain detection, and database insertion.
- `_extract_idea`: A helper method to extract the idea text from the user message.
- `_detect_domain`: A helper method to detect the domain of the idea based on keywords in the message.
- `_insert_idea`: A helper method to insert the idea into the `idea_inbox` table in the PostgreSQL database.

#### Patterns
- **Factory Method**: The `execute` method acts as a factory method, coordinating the creation and processing of the idea.
- **Singleton**: The `AddIdeaSkill` class can be treated as a singleton since it is designed to be instantiated once and reused.

#### Dependencies
- **Imports**: `os`, `logging`, `json`, `psycopg2`, `re`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` are loaded from `.env` file using `dotenv`.

#### Interfaces
- **Public Methods**: `execute` is the primary method that processes the user request and returns a `SkillResponse` object.
- **Helper Methods**: `_extract_idea`, `_detect_domain`, and `_insert_idea` are private methods used internally by `execute`.

#### Database
- **Tables**: The file interacts with the `idea_inbox` table in the PostgreSQL database.
- **Operations**: Inserts new ideas into the `idea_inbox` table.

#### Configuration
- **Environment Variables**: The database connection details are loaded from environment variables.
- **Triggers**: The `triggers` list in the `AddIdeaSkill` class defines the keywords that trigger the skill.

#### Key Logic
1. **Idea Extraction**: The `_extract_idea` method removes predefined triggers and normalizes the message text.
2. **Domain Detection**: The `_detect_domain` method identifies the domain of the idea based on predefined keywords.
3. **Database Insertion**: The `_insert_idea` method inserts the idea into the `idea_inbox` table with details like `conversation_context`, `items`, `item_count`, `disposition`, `domain`, and `tags`.

#### Integration Points
- **SkillBase**: The `AddIdeaSkill` class inherits from `SkillBase` and integrates with the broader Mythos system.
- **Database Connection**: The `_insert_idea` method connects to the PostgreSQL database using `psycopg2` to insert the idea.
- **Response**: The `execute` method constructs and returns a `SkillResponse` object, which is used to communicate the result back to the system.

### Summary
This file implements a skill to capture and store new ideas from user messages into a PostgreSQL database. It processes the user input to extract the idea, detect its domain, and insert it into the `idea_inbox` table. The skill is designed to be part of a larger system and integrates with the database and other components through well-defined interfaces and methods.
