# eval/results/memory_router/20260305_063410/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 71

---

### File: eval/results/memory_router/20260305_063410/pass02_attempt01.py

#### Purpose
This file defines the `MemoryRouterSkill` class, which is responsible for analyzing messages to determine which memory stores (e.g., voice memos, conversations) to search based on specific keywords and phrases.

#### Architecture
- **Class**: `MemoryRouterSkill` inherits from `SkillBase`.
- **Methods**: 
  - `execute`: Asynchronously processes a `SkillRequest` and returns a `SkillResponse`.
  - `_extract_search_terms`: Processes a message to extract relevant search terms by removing trigger phrases and cleaning the text.

#### Patterns
- **Singleton**: Not explicitly used.
- **Observer**: Not explicitly used.
- **Factory**: Not explicitly used.

#### Dependencies
- **Imports**: 
  - `logging`: For logging messages.
  - `re`: For regular expression operations.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response models for skills.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Processes a `SkillRequest` and returns a `SkillResponse`.
  - `_extract_search_terms`: Processes a message to extract relevant search terms.

#### Database
- **PostgreSQL Table**: `engine` is referenced, but the specific operations are not detailed in the provided code snippet.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
- **_extract_search_terms**:
  - Converts the message to lowercase.
  - Removes predefined trigger phrases.
  - Cleans up extra spaces and removes punctuation.
  - Returns the cleaned message if it is at least 2 characters long.

- **execute**:
  - Calls `_extract_search_terms` to process the message.
  - Scores each memory store based on the extracted terms (logic not detailed in the provided snippet).
  - Returns a ranked list of stores to search along with the extracted terms.

#### Integration Points
- **Mythos Subsystems**:
  - **SkillBase**: Inherits from `SkillBase`, indicating integration with the broader Mythos skill system.
  - **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` models to interact with the Mythos system.
  - **Database**: Likely integrates with the PostgreSQL `engine` table for storing or retrieving memory store information.

### Summary
The `MemoryRouterSkill` class is designed to analyze messages and determine which memory stores to search based on specific keywords and phrases. It processes messages to extract relevant search terms and scores memory stores accordingly. The class integrates with the Mythos skill system through inheritance from `SkillBase` and uses `SkillRequest` and `SkillResponse` models for communication. The file also references a PostgreSQL table named `engine`, though specific database operations are not detailed in the provided code snippet.
