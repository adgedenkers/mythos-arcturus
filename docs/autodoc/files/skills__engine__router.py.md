# skills/engine/router.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 111

---

### Documentation for `skills/engine/router.py`

#### Purpose
This file contains the `SkillRouter` and `AlwaysOnRouter` classes, which are responsible for routing user messages to the appropriate skills based on heuristic keyword matching. The `AlwaysOnRouter` is a variant that ensures certain skills are always activated, regardless of the message content.

#### Architecture
- **SkillRouter**: The base class for routing messages to skills. It contains methods for initialization (`__init__`) and routing (`route`).
- **AlwaysOnRouter**: A subclass of `SkillRouter` that extends the routing logic to include always-on skills.

#### Patterns
- **Decorator Pattern**: The `AlwaysOnRouter` can be seen as a decorator around the `SkillRouter`, adding additional behavior (always-on skills) without changing the interface.
- **Factory Pattern**: The `SkillRouter` and `AlwaysOnRouter` can be instantiated based on different configurations, acting as factories for different routing strategies.

#### Dependencies
- **Imports**: 
  - `logging`: For logging messages.
  - `typing`: For type hints.
  - `SkillBase` from `skills.base`: Base class for skills.

#### Interfaces
- **SkillRouter**:
  - `__init__(self, threshold: float = DEFAULT_THRESHOLD, max_skills: int = DEFAULT_MAX_SKILLS)`: Initializes the router with a relevance threshold and maximum number of skills to activate.
  - `route(self, message: str, skills: Dict[str, SkillBase], context: Dict[str, Any] = None) -> List[Tuple[str, float]]`: Determines which skills should be activated for a given message and returns a list of (skill_name, relevance_score) tuples.
- **AlwaysOnRouter**:
  - `__init__(self, always_on: List[str] = None, **kwargs)`: Initializes the router with a list of always-on skills and other parameters.
  - `route(self, message: str, skills: Dict[str, SkillBase], context: Dict[str, Any] = None) -> List[Tuple[str, float]]`: Extends the routing logic to include always-on skills.

#### Database
- **PostgreSQL Tables**:
  - `REGISTRY`: Used to store skill triggers and other metadata.
  - `registered`: Used to store registered skills.
  - `typing`: Used for type hints, not a database table.

#### Configuration
- **Environment Variables**: None.
- **Configuration Files**: 
  - `REGISTRY.yaml`: Contains skill triggers and other metadata.

#### Key Logic
- **SkillRouter**:
  - Heuristic keyword matching to determine relevance scores.
  - Filtering and sorting skills based on relevance scores.
  - Logging activation decisions.
- **AlwaysOnRouter**:
  - Ensures certain skills are always activated.
  - Combines always-on skills with heuristic routing results.

#### Integration Points
- **Mythos Subsystems**:
  - **SkillBase**: Each skill must implement the `relevance` method.
  - **Skill Registry**: The router interacts with the skill registry to get the list of available skills.
  - **Context Manager**: The router can optionally use context information to refine relevance scores.
  - **Logging**: The router logs activation decisions and errors.

### Detailed Analysis

#### SkillRouter Class
- **Initialization**:
  - `__init__(self, threshold: float = DEFAULT_THRESHOLD, max_skills: int = DEFAULT_MAX_SKILLS)`: Initializes the router with a relevance threshold and maximum number of skills to activate.
- **Routing Logic**:
  - `route(self, message: str, skills: Dict[str, SkillBase], context: Dict[str, Any] = None) -> List[Tuple[str, float]]`: 
    - Iterates over all registered skills and calculates their relevance scores.
    - Filters out skills with scores below the threshold.
    - Sorts the remaining skills by relevance score in descending order.
    - Caps the number of activated skills to `max_skills`.
    - Logs the activation decisions.

#### AlwaysOnRouter Class
- **Initialization**:
  - `__init__(self, always_on: List[str] = None, **kwargs)`: Initializes the router with a list of always-on skills and other parameters.
- **Routing Logic**:
  - `route(self, message: str, skills: Dict[str, SkillBase], context: Dict[str, Any] = None) -> List[Tuple[str, float]]`: 
    - Calls the `route` method of the base `SkillRouter` to get heuristic results.
    - Adds always-on skills to the results if they were not already activated.
    - Sorts and caps the final list of activated skills.

### Conclusion
The `SkillRouter` and `AlwaysOnRouter` classes provide a flexible and extensible mechanism for routing user messages to the appropriate skills based on heuristic keyword matching. The design allows for easy integration with other subsystems and future enhancements, such as replacing the heuristic matching with a more sophisticated LLM-based classification.
