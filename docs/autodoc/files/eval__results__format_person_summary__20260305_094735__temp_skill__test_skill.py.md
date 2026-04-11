# eval/results/format_person_summary/20260305_094735/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 107

---

### File: `eval/results/format_person_summary/20260305_094735/temp_skill/test_skill.py`

#### Purpose
This file defines a skill (`FormatPersonSummarySkill`) that formats person data into a standard readable summary. It processes input person data and generates a formatted summary string.

#### Architecture
The file contains a single class `FormatPersonSummarySkill` that inherits from `SkillBase`. The class has two methods:
- `execute`: The main method that handles the execution of the skill, taking a `SkillRequest` object as input and returning a `SkillResponse` object.
- `_format`: A helper method that constructs the formatted summary string from the person data.

#### Patterns
- **Decorator Pattern**: The `execute` method is marked as `async`, indicating it can be used in an asynchronous context.
- **Facade Pattern**: The `execute` method acts as a facade, handling the overall logic and calling the `_format` method to format the person data.

#### Dependencies
- **Imports**: `logging`, `unicodedata`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Database**: References PostgreSQL tables `engine`, `a`, `fields`, and `parts`.

#### Interfaces
- **Exposed Methods**:
  - `execute`: An asynchronous method that processes the request and returns a formatted summary.
  - `_format`: A private method that constructs the formatted summary string.

#### Database
- **PostgreSQL Tables**:
  - `engine`
  - `a`
  - `fields`
  - `parts`

#### Configuration
- **Environment Variables**: None explicitly used.
- **Configuration Files**: None explicitly used.

#### Key Logic
- **`execute` Method**:
  - Validates the input `request.parameters['person']` and ensures it is not empty.
  - Calls the `_format` method to generate the formatted summary.
  - Constructs and returns a `SkillResponse` object with the formatted summary and metadata.
- **`_format` Method**:
  - Constructs a summary string by combining various fields from the person data (e.g., name, date of birth, birth location, date of death, notes).
  - Normalizes the summary string to ASCII using `unicodedata.normalize`.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase`, which likely provides common functionality for skills in the Mythos system.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes to handle input and output, integrating with the Mythos request-response framework.
- **Logging**: Uses the `logging` module to log errors, integrating with the system's logging infrastructure.

### Summary
This file implements a skill that formats person data into a readable summary. It processes input data, constructs a formatted summary, and returns it in a standardized response format. The skill integrates with the Mythos system's request-response framework and logging infrastructure.
