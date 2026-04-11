# eval/results/memory_router/20260305_063410/pass01_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 40

---

### Documentation for `pass01_attempt01.py`

#### 1. Purpose
This file defines the `MemoryRouterSkill` class, which is responsible for analyzing incoming messages to determine which memory stores to search based on the content of the message.

#### 2. Architecture
- **Class**: `MemoryRouterSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: The main method that processes the incoming request and returns a response.
  - `_extract_search_terms`: Helper method to extract the actual search content from the message.
  - `_score_stores`: Helper method to score each memory store based on the message content.
- **Data Flow**: The `execute` method orchestrates the process by first extracting search terms from the message and then scoring each memory store to determine the most relevant ones.

#### 3. Patterns
- **Singleton**: Not explicitly used.
- **Factory**: Not explicitly used.
- **Observer**: Not explicitly used.
- **Strategy**: The scoring logic can be seen as a strategy pattern where different methods could be used to score stores.

#### 4. Dependencies
- **Imports**: `logging` for logging purposes.
- **From `engine.base`**: `SkillBase`, `SkillRequest`, `SkillResponse` for the base class and request/response objects.

#### 5. Interfaces
- **Exposed Methods**:
  - `execute`: Public method that takes a `SkillRequest` and returns a `SkillResponse`.
  - `_extract_search_terms`: Private method that takes a message string and returns the extracted search terms.
  - `_score_stores`: Private method that takes a message string and returns a list of (store_name, score) tuples.

#### 6. Database
- **PostgreSQL Table**: `engine` (used indirectly through `SkillBase` or other dependencies).

#### 7. Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### 8. Key Logic
- **Extracting Search Terms**: The `_extract_search_terms` method removes routing trigger phrases and returns the actual search content.
- **Scoring Stores**: The `_score_stores` method scores each memory store based on keyword matches in the message. If no specific store keywords are found, it returns all stores for a broad search.
- **Execution Flow**: The `execute` method orchestrates the process by calling `_extract_search_terms` and `_score_stores`, and returns a ranked list of stores to search along with the extracted terms.

#### 9. Integration Points
- **Mythos Subsystems**: Integrates with the `SkillBase` class and the `engine` module to handle requests and responses.
- **Memory Stores**: The logic is designed to interact with various memory stores (`voice_memos`, `conversations`, `life_events`, `ideas`, `documents`) based on the message content.

### Summary
The `MemoryRouterSkill` class in `pass01_attempt01.py` is a crucial component of the Mythos system, responsible for analyzing messages and determining which memory stores to search. It leverages helper methods to extract search terms and score memory stores, ensuring that the most relevant stores are selected for a given query.
