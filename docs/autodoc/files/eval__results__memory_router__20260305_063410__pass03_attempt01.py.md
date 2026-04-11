# eval/results/memory_router/20260305_063410/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 115

---

### Documentation for `pass03_attempt01.py`

#### Purpose
The `pass03_attempt01.py` file contains the `MemoryRouterSkill` class, which is responsible for analyzing user messages to determine which memory stores to search based on specific keywords and phrases. It extracts search terms from the message and scores different memory stores based on keyword matches.

#### Architecture
The file defines a single class `MemoryRouterSkill` that inherits from `SkillBase`. The class contains three methods:
- `execute`: The main method that processes the incoming request, extracts search terms, scores memory stores, and returns the results.
- `_extract_search_terms`: A helper method that cleans and processes the message to extract meaningful search terms.
- `_score_stores`: A helper method that scores different memory stores based on keyword matches within the extracted search terms.

#### Patterns
- **Strategy Pattern**: The `MemoryRouterSkill` class implements a strategy for analyzing messages and determining which memory stores to search, encapsulating the logic within the `execute` method.
- **Singleton Pattern**: Although not explicitly implemented, the class could be designed to act as a singleton if only one instance is needed across the system.

#### Dependencies
- **Imports**: The file imports `logging` and `re` for logging and regular expression operations, respectively.
- **External Classes**: It imports `SkillBase`, `SkillRequest`, and `SkillResponse` from the `engine.base` module.

#### Interfaces
- **Public Methods**: The `execute` method is the primary interface, accepting a `SkillRequest` object and returning a `SkillResponse` object.
- **Helper Methods**: `_extract_search_terms` and `_score_stores` are private methods used internally by `execute`.

#### Database
- **PostgreSQL Table**: The file references the `engine` table in PostgreSQL, though it does not perform any direct database operations within the provided code.

#### Configuration
- **Environment Variables**: No explicit environment variables are used.
- **Configuration Files**: No configuration files are referenced.

#### Key Logic
1. **Message Processing**: The `execute` method processes the incoming message by extracting search terms and scoring memory stores.
2. **Search Term Extraction**: The `_extract_search_terms` method cleans the message by removing trigger phrases and stripping punctuation, returning a cleaned string.
3. **Store Scoring**: The `_score_stores` method scores each memory store based on keyword matches within the extracted search terms. It normalizes the scores and returns a sorted list of stores with their scores.

#### Integration Points
- **SkillBase Integration**: The `MemoryRouterSkill` class integrates with the `SkillBase` class, inheriting its structure and methods.
- **SkillRequest/SkillResponse**: The `execute` method interacts with `SkillRequest` and `SkillResponse` objects, which are part of the broader Mythos system's request-response mechanism.
- **Trigger Phrases**: The class uses a predefined list of trigger phrases to determine when to analyze messages for memory store searches.

### Summary
The `pass03_attempt01.py` file implements the `MemoryRouterSkill` class, which processes user messages to determine which memory stores to search based on keyword matches. It integrates with the broader Mythos system through the `SkillBase` class and uses `SkillRequest` and `SkillResponse` for communication. The class employs a strategy pattern to encapsulate the logic for message analysis and store scoring.
