# skills/data/memory_router.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 149

---

### Documentation for `skills/data/memory_router.py`

#### Purpose
The `MemoryRouterSkill` class in `memory_router.py` is responsible for analyzing incoming messages to determine which memory stores should be searched based on the content of the message. It extracts relevant search terms and scores different memory stores to identify the most relevant ones.

#### Architecture
The file contains a single class `MemoryRouterSkill` that inherits from `SkillBase`. The class has three methods: `execute`, `_extract_search_terms`, and `_score_stores`. The `execute` method is the main entry point, which orchestrates the extraction of search terms and scoring of memory stores. The `_extract_search_terms` method cleans and processes the message to extract meaningful search terms, while `_score_stores` evaluates the message against predefined keywords to score each memory store.

#### Patterns
- **Factory Method**: The `MemoryRouterSkill` class can be seen as a factory method for processing messages and determining memory store targets.
- **Singleton**: The class does not enforce singleton behavior, but it could be used as a singleton in the system.

#### Dependencies
- **Imports**: The file imports `logging` for logging errors and `re` for regular expression operations.
- **From `engine.base`**: It imports `SkillBase`, `SkillRequest`, and `SkillResponse` which are likely part of the Mythos system's core infrastructure.

#### Interfaces
- **`execute` Method**: This method is the primary interface for the `MemoryRouterSkill` class. It takes a `SkillRequest` object and returns a `SkillResponse` object containing the targets, scores, and search terms.
- **`_extract_search_terms` Method**: This method is used internally to clean and extract search terms from the message.
- **`_score_stores` Method**: This method is used internally to score each memory store based on the message content.

#### Database
- **PostgreSQL Table**: The file references the `engine` table in PostgreSQL, which is likely used for storing configurations or metadata related to the skill.

#### Configuration
- **Environment Variables**: The file does not explicitly use any environment variables.
- **Configuration Files**: The file does not explicitly reference any configuration files.

#### Key Logic
1. **Message Analysis**:
   - The `execute` method first calls `_extract_search_terms` to clean and extract meaningful search terms from the message.
   - It then calls `_score_stores` to determine which memory stores are most relevant based on the message content.

2. **Search Term Extraction**:
   - The `_extract_search_terms` method removes predefined trigger phrases and cleans the message to extract meaningful search terms.

3. **Store Scoring**:
   - The `_score_stores` method scores each memory store based on the presence of predefined keywords in the message. It normalizes the scores so that the highest score is 1.0.

#### Integration Points
- **SkillBase**: The `MemoryRouterSkill` class inherits from `SkillBase`, indicating that it integrates with the broader Mythos system's skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, indicating integration with the Mythos system's request-response model.
- **PostgreSQL**: The file references the `engine` table in PostgreSQL, suggesting integration with the system's database for configuration or metadata storage.

### Summary
The `MemoryRouterSkill` class in `memory_router.py` is a critical component of the Mythos system, responsible for analyzing messages and determining which memory stores to search. It uses a combination of message cleaning, keyword matching, and scoring to provide relevant search targets and terms. The class integrates with the Mythos system's skill framework and database, making it a versatile and essential part of the system's memory management capabilities.
