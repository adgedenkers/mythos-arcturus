# skills/data/person_research.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 209

---

### File: skills/data/person_research.py

#### Purpose
This file implements the `PersonResearchSkill` class, which is responsible for researching information about a person when Iris encounters a query about an unknown individual. It checks a local registry first, falls back to web research if necessary, and stores the results in the database.

#### Architecture
The file contains a single class, `PersonResearchSkill`, which inherits from `SkillBase`. The class has three methods: `relevance`, `execute`, and `_extract_person_name`. Additionally, there are three top-level functions with the same names, which are likely intended to be methods of the `PersonResearchSkill` class but are currently defined outside of it.

- **Class Methods:**
  - `relevance`: Scores the relevance of a message to determine if the skill should be activated.
  - `execute`: Executes the person research pipeline.
  - `_extract_person_name`: Extracts a person's name from the message.

#### Patterns
- **Singleton Pattern**: The `logger` instance is a singleton, ensuring a single instance of the logger is used throughout the module.
- **Factory Pattern**: The `research_person` function can be seen as a factory method that creates and returns a `PersonRecord` object.

#### Dependencies
- **Imports**: 
  - `logging` for logging purposes.
  - `os` and `sys` for system-related operations.
  - `typing` for type hints.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
  - `research_person`, `PersonRecord` from `src.person_researcher`.

#### Interfaces
- **Exposed Methods**:
  - `relevance`: Determines the relevance of a message to the skill.
  - `execute`: Executes the research pipeline.
  - `_extract_person_name`: Extracts a person's name from the message.

#### Database
- **PostgreSQL Tables**: 
  - `first`, `typing`, `engine`, `src`, `the` (likely placeholders or misidentified table names).

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` for database configuration.

#### Key Logic
- **Relevance Scoring**:
  - The `relevance` method scores the relevance of a message based on specific patterns and keywords. It returns a score between 0 and 1, with higher scores indicating a higher likelihood that the message is a factual person question.

- **Person Research Pipeline**:
  - The `execute` method handles the main logic of the skill. It extracts the person's name from the message, checks the local registry, performs web research if necessary, and stores the results in the database. It also queues deep research for background processing.

- **Name Extraction**:
  - The `_extract_person_name` method removes common question prefixes and suffixes to isolate the person's name from the message.

#### Integration Points
- **SkillBase**: The `PersonResearchSkill` class inherits from `SkillBase`, which likely provides common functionality and interfaces for skills in the Mythos system.
- **Database Integration**: The skill interacts with PostgreSQL and Neo4j to store and retrieve person data.
- **Web Research**: The skill integrates with external web research tools (Wikipedia/Wikidata) to gather information about the person.
- **Deep Research Queue**: The skill queues deep research tasks (astrology, numerology, resonance) for background processing.

### Summary
The `PersonResearchSkill` class in `person_research.py` is designed to handle person research queries in the Mythos system. It checks a local registry first, performs web research if needed, and stores the results in the database. The class is structured to integrate with the Mythos infrastructure, including database interactions and background task queuing.
