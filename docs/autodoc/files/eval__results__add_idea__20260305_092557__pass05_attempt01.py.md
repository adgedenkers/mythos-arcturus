# eval/results/add_idea/20260305_092557/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 156

---

### Documentation for `eval/results/add_idea/20260305_092557/pass05_attempt01.py`

#### Purpose
This file defines a skill (`AddIdeaSkill`) that captures new ideas from user messages, detects the domain of the idea, and inserts it into a PostgreSQL database table named `idea_inbox`.

#### Architecture
- **Classes**: 
  - `AddIdeaSkill`: Inherits from `SkillBase` and implements the `execute` method to process the idea capture workflow.
- **Methods**:
  - `execute`: The main entry point that orchestrates the idea extraction, domain detection, and database insertion.
  - `_extract_idea`: Extracts the idea text from the user message by removing triggers and normalizing the text.
  - `_detect_domain`: Detects the domain of the idea based on keywords in the message.
  - `_insert_idea`: Inserts the idea into the `idea_inbox` table in the PostgreSQL database.
- **Data Flow**: 
  - The `execute` method receives a `SkillRequest` object, processes it through `_extract_idea` and `_detect_domain`, and then inserts the idea into the database using `_insert_idea`. The result is returned as a `SkillResponse` object.

#### Patterns
- **Singleton**: Not explicitly used.
- **Factory**: Not explicitly used.
- **Observer**: Not explicitly used.
- **Strategy**: The `_extract_idea` and `_detect_domain` methods could be seen as different strategies for processing the user message.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `json`: For JSON serialization.
  - `psycopg2`: For PostgreSQL database operations.
  - `re`: For regular expressions.
  - `unicodedata`: For Unicode normalization.
  - `dotenv`: For loading environment variables from `.env` files.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response objects for the skill.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Asynchronous method that processes the idea capture workflow and returns a `SkillResponse` object.
- **Exposed Classes**:
  - `AddIdeaSkill`: A class that inherits from `SkillBase` and implements the idea capture logic.

#### Database
- **Tables**:
  - `idea_inbox`: The table where new ideas are inserted. The table has columns for `conversation_context`, `items`, `item_count`, `disposition`, `domain`, and `tags`.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: Host for the PostgreSQL database.
  - `DB_NAME`: Name of the PostgreSQL database.
  - `DB_USER`: Username for the PostgreSQL database.
  - `DB_PASSWORD`: Password for the PostgreSQL database.
  - `DB_PORT`: Port for the PostgreSQL database.

#### Key Logic
- **_extract_idea**:
  - Converts the message to lowercase.
  - Removes predefined triggers.
  - Normalizes whitespace and punctuation.
  - Normalizes to ASCII.
- **_detect_domain**:
  - Converts the message to lowercase.
  - Matches keywords to predefined domains (`technical`, `spiritual`, `personal`, `financial`, `mythos`).
- **_insert_idea**:
  - Connects to the PostgreSQL database.
  - Inserts the idea into the `idea_inbox` table.
  - Returns the `id` of the newly inserted idea.

#### Integration Points
- **Mythos System**:
  - The `AddIdeaSkill` class integrates with the Mythos system through the `SkillBase` class and its methods.
  - The `execute` method is called by the Mythos system when a user message matches the skill's triggers.
  - The `SkillResponse` object is returned to the Mythos system to provide feedback on the idea capture process.

This file is a critical component of the Mythos system, enabling the capture and categorization of user-generated ideas, which can then be further processed or analyzed within the system.
