# skills/engine/base.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 175

---

### File: skills/engine/base.py

#### Purpose
This file defines the foundational classes and methods for all skills in the Mythos system. It includes the `SkillRequest` and `SkillResponse` data classes, and the `SkillBase` abstract base class that all skills must inherit from.

#### Architecture
- **SkillRequest**: A data class representing the input to a skill, containing the user message, context, parameters, and metadata.
- **SkillResponse**: A data class representing the output of a skill, containing the skill name, structured data, summary, confidence, sources, execution time, and error information.
- **SkillBase**: An abstract base class that defines the structure and behavior of all skills. It includes methods for relevance scoring, execution, caching, and running the skill.

#### Patterns
- **Abstract Base Class (ABC)**: `SkillBase` is an abstract base class that enforces the implementation of the `execute` method in subclasses.
- **Data Classes**: `SkillRequest` and `SkillResponse` use Python's `dataclasses` to simplify the definition of classes with attributes and methods.

#### Dependencies
- **Imports**: `logging`, `time`, `abc`, `dataclasses`, `datetime`, `typing`
- **Database References**: None (the file references `abc`, `dataclasses`, `datetime`, `typing`, `router`, and `Iris`, but these are not database tables or Neo4j labels).

#### Interfaces
- **SkillRequest**: Exposes attributes for message, context, parameters, calling skill, and timestamp.
- **SkillResponse**: Exposes attributes for skill name, data, summary, confidence, sources, execution time, error, and suggested skills. Also provides a `ok` property to check if the response is valid.
- **SkillBase**: Exposes methods for relevance scoring (`relevance`), execution (`execute`), caching (`_cache_key`, `_check_cache`, `_set_cache`), and running the skill (`run`). It also requires subclasses to set metadata attributes like `name`, `version`, `category`, `description`, `triggers`, and `cache_ttl`.

#### Database
- **References**: None (the file does not interact with any database tables or Neo4j labels).

#### Configuration
- **Configuration**: None (the file does not use any config files or environment variables).

#### Key Logic
- **Relevance Scoring**: The `relevance` method scores how relevant a skill is to a given message based on keyword matching against predefined triggers.
- **Execution**: The `execute` method is an abstract method that must be implemented by subclasses to perform the skill's specific functionality and return a `SkillResponse`.
- **Caching**: Methods `_cache_key`, `_check_cache`, and `_set_cache` manage caching of responses to improve performance.
- **Running the Skill**: The `run` method orchestrates the execution of the skill, including checking the cache, timing the execution, and logging the results.

#### Integration Points
- **SkillRequest**: This class is used to pass input data to skills.
- **SkillResponse**: This class is used to return output data from skills.
- **SkillBase**: This class is inherited by all skills, ensuring a consistent interface and behavior across the system. It integrates with the routing and execution logic of the Mythos system.

### Summary
This file provides the foundational classes and methods for all skills in the Mythos system. It defines the structure of requests and responses, enforces a consistent interface for skills through the `SkillBase` abstract base class, and includes logic for relevance scoring, execution, caching, and logging.
