# skills/meta/introspection_skill.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 57

---

### File: skills/meta/introspection_skill.py

#### 1. Purpose
This file defines the `IntrospectionSkill` class, which is responsible for triggering self-introspection within the Mythos system. The skill evaluates the relevance of a user request and, if relevant, executes an introspection process to scan and analyze the Mythos codebase, updating the manifest and graph accordingly.

#### 2. Architecture
- **Class**: `IntrospectionSkill` extends `SkillBase` and implements two methods: `relevance` and `execute`.
- **Methods**:
  - `relevance(request: SkillRequest) -> float`: Scores the relevance of the skill to the given request.
  - `execute(request: SkillRequest) -> SkillResponse`: Executes the introspection process and returns a report.

#### 3. Patterns
- **Factory Pattern**: The `IntrospectionSkill` class can be seen as a factory for introspection tasks, as it creates and returns a `SkillResponse` object based on the request.
- **Singleton Pattern**: While not explicitly implemented, the skill could be used as a singleton if only one instance is needed throughout the system.

#### 4. Dependencies
- **Imports**: `logging` for logging purposes.
- **Internal Modules**: 
  - `skills.base` for `SkillBase`, `SkillRequest`, and `SkillResponse`.
  - `iris.introspection.run` for `run_introspection`.
  - `iris.introspection.report` for `format_report_text`.

#### 5. Interfaces
- **Exposed Methods**:
  - `relevance(request: SkillRequest) -> float`: Exposes a method to score the relevance of the skill to a given request.
  - `execute(request: SkillRequest) -> SkillResponse`: Exposes a method to execute the introspection process and return a report.

#### 6. Database
- **PostgreSQL Tables**: 
  - `skills`: Likely used to store skill metadata.
  - `manifest`: Likely used to store the manifest of the system.
  - `iris`: Likely used to store introspection-related data.
  - `request`: Likely used to store request data.

#### 7. Configuration
- **Environment Variables**: No specific environment variables are used in this file.
- **Config Files**: No specific configuration files are used in this file.

#### 8. Key Logic
- **Relevance Scoring**: The `relevance` method checks if the request text contains any of the predefined trigger phrases and returns a relevance score.
- **Introspection Execution**: The `execute` method parses options from the request, runs the introspection process, and formats the report. It handles exceptions and logs errors.

#### 9. Integration Points
- **SkillBase**: The `IntrospectionSkill` class extends `SkillBase`, integrating with the broader skills framework.
- **Iris Introspection**: The `execute` method integrates with the `iris.introspection.run` module to perform the introspection process.
- **Logging**: Uses the `logging` module to log errors and other relevant information.
- **PostgreSQL**: Interacts with PostgreSQL tables to store and retrieve data related to skills, manifest, and requests.

### Summary
The `IntrospectionSkill` class in `skills/meta/introspection_skill.py` is a critical component of the Mythos system, enabling self-introspection and analysis of the codebase. It integrates with the broader skills framework, leverages PostgreSQL for data storage, and uses logging for error handling and tracking. The class is designed to be modular and reusable, fitting well into the Mythos architecture.
