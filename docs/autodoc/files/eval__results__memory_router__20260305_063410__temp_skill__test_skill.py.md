# eval/results/memory_router/20260305_063410/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 141

---

### Documentation for `test_skill.py`

#### Purpose
The `test_skill.py` file contains the `MemoryRouterSkill` class, which is responsible for analyzing incoming messages to determine which memory stores to search based on specific keywords and phrases. It extracts search terms from the message and scores each memory store based on relevance.

#### Architecture
- **Class**: `MemoryRouterSkill` extends `SkillBase`.
- **Methods**:
  - `execute`: Main method that processes the incoming request, extracts search terms, and scores memory stores.
  - `_extract_search_terms`: Helper method to clean and extract relevant search terms from the message.
  - `_score_stores`: Helper method to score each memory store based on the presence of specific keywords in the message.
- **Data Flow**:
  - The `execute` method receives a `SkillRequest` object, processes it using `_extract_search_terms` and `_score_stores`, and returns a `SkillResponse` object.

#### Patterns
- **Singleton**: The `MemoryRouterSkill` class can be considered a singleton since it is designed to be a single instance that processes requests.
- **Factory**: The `SkillBase` class might be part of a factory pattern to instantiate different skills.

#### Dependencies
- **Imports**:
  - `logging`: For logging errors.
  - `re`: For regular expression operations.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response objects.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Asynchronous method that processes a `SkillRequest` and returns a `SkillResponse`.
  - `_extract_search_terms`: Synchronous method that extracts search terms from a message.
  - `_score_stores`: Synchronous method that scores memory stores based on the message.

#### Database
- **PostgreSQL Table**: `engine` (likely used for storing skill definitions or configurations).

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
- **`execute` Method**:
  - Extracts search terms from the message using `_extract_search_terms`.
  - Scores each memory store using `_score_stores`.
  - Constructs a summary based on the extracted terms and scored stores.
  - Returns a `SkillResponse` object with the ranked list of stores to search, extracted terms, and a confidence score.
- **`_extract_search_terms` Method**:
  - Cleans the message by removing trigger phrases and punctuation.
  - Returns the cleaned message if it has at least two characters.
- **`_score_stores` Method**:
  - Scores each memory store based on the presence of specific keywords in the message.
  - Normalizes and sorts the scores in descending order.

#### Integration Points
- **Mythos Subsystems**:
  - **SkillBase**: Inherits from `SkillBase`, which likely provides a common interface for all skills.
  - **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` to communicate with the Mythos system.
  - **Memory Stores**: Integrates with various memory stores (`voice_memos`, `conversations`, `life_events`, `ideas`, `documents`) to determine which ones to search based on the message content.

This file is crucial for routing incoming messages to the appropriate memory stores, ensuring efficient and relevant search operations within the Mythos system.
