# skills/data/extract_search_terms.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 120

---

### File: skills/data/extract_search_terms.py

#### Purpose
This file contains the `ExtractSearchTermsSkill` class, which is responsible for extracting meaningful search keywords from natural language input. It processes user messages to remove common filler words and phrases, returning a cleaned list of keywords.

#### Architecture
- **Class**: `ExtractSearchTermsSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: The main method that processes the input message and returns a `SkillResponse` object.
  - `_clean`: A helper method that cleans the input message by removing filler words and phrases, normalizing whitespace, and ensuring ASCII compatibility.

#### Patterns
- **Singleton**: The class does not exhibit singleton behavior.
- **Factory**: The class does not use a factory pattern.
- **Observer**: The class does not use an observer pattern.

#### Dependencies
- **Imports**:
  - `logging`: For logging errors.
  - `re`: For regular expression operations.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From the `engine.base` module.

#### Interfaces
- **Public Methods**:
  - `execute`: Accepts a `SkillRequest` object and returns a `SkillResponse` object.
  - `_clean`: Accepts a string message and returns a cleaned string.

#### Database
- **PostgreSQL Tables**:
  - `engine`: Not directly used in this file.
  - `natural`: Not directly used in this file.
  - `words`: Not directly used in this file.
  - `message`: Not directly used in this file.

#### Configuration
- **Environment Variables**: None.
- **Config Files**: None.

#### Key Logic
- **Cleaning Logic**:
  - Converts the input message to lowercase.
  - Removes predefined trigger phrases.
  - Normalizes whitespace.
  - Filters out filler words and short words.
  - Strips punctuation except hyphens.
  - Ensures ASCII compatibility.
- **Response Construction**:
  - Constructs a `SkillResponse` object with the original message, cleaned message, and extracted keywords.
  - Sets the confidence level based on whether meaningful keywords were found.

#### Integration Points
- **SkillBase**: This class inherits from `SkillBase`, which likely provides a framework for skill execution and response handling.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, indicating integration with the Mythos skill execution framework.
- **Logging**: Uses `logging` for error handling, which integrates with the system-wide logging infrastructure.

### Summary
The `ExtractSearchTermsSkill` class is designed to process natural language inputs, extracting meaningful search keywords by removing filler words and phrases. It integrates with the Mythos skill execution framework, providing a cleaned output suitable for further search or analysis within the system.
