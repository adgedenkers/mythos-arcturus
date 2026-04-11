# eval/results/extract_search_terms/20260305_094655/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 117

---

### File: `eval/results/extract_search_terms/20260305_094655/pass03_attempt01.py`

#### Purpose
This file defines a skill (`ExtractSearchTermsSkill`) that processes natural language input to extract meaningful search keywords by removing common filler words and trigger phrases. It also includes a top-level asynchronous `execute` function and a helper `_clean` function.

#### Architecture
- **Class**: `ExtractSearchTermsSkill` inherits from `SkillBase`.
  - **Attributes**:
    - `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`
    - `FILLER_WORDS`: Set of common filler words to strip.
    - `TRIGGER_PHRASES`: List of common phrases users might use to initiate a search query.
  - **Methods**:
    - `execute`: Asynchronous method to process the input message and return a `SkillResponse` object.
    - `_clean`: Synchronous method to clean the input message by removing filler words, trigger phrases, and normalizing the text.
- **Top-level Functions**:
  - `execute`: Asynchronous function to handle the execution logic.
  - `_clean`: Synchronous function to clean the message.

#### Patterns
- **Singleton**: The class `ExtractSearchTermsSkill` is designed to be a singleton-like skill, where a single instance handles the extraction logic.
- **Decorator**: The `execute` method is decorated with `async` to handle asynchronous operations.

#### Dependencies
- **Imports**:
  - `logging`: For logging errors.
  - `re`: For regular expression operations.
  - `SkillBase`, `SkillRequest`, `SkillResponse`: From `engine.base` for base skill functionality.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Exposed to other parts of the system for processing input messages.
  - `_clean`: Internal method used by `execute` to clean messages.

#### Database
- **PostgreSQL Tables**:
  - `engine`, `natural`, `words`, `message`: Referenced but not explicitly used in the provided code snippet.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
- **`execute` Method**:
  - Cleans the input message using `_clean`.
  - Constructs a `SkillResponse` object with the original message, cleaned message, and extracted keywords.
  - Sets the confidence level based on whether meaningful keywords were found.
- **`_clean` Method**:
  - Converts the message to lowercase.
  - Removes trigger phrases.
  - Normalizes whitespace.
  - Filters out filler words and short words.
  - Strips punctuation except hyphens.
  - Final normalization of whitespace.

#### Integration Points
- **Mythos Subsystems**:
  - **Skill System**: Integrates with the skill system via `SkillBase` inheritance, allowing it to be invoked as part of the skill pipeline.
  - **Logging**: Uses `logging` for error reporting.
  - **Database**: References PostgreSQL tables but does not directly interact with them in the provided code.

### Summary
This file implements a skill to extract meaningful search keywords from natural language input by removing common filler words and trigger phrases. It integrates with the Mythos skill system and provides a clean interface for processing messages and returning structured responses. The key logic involves cleaning the input message and extracting keywords, with error handling and logging for robustness.
