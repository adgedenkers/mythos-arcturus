# eval/results/format_person_summary/20260305_094735/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 96

---

### File: `eval/results/format_person_summary/20260305_094735/pass03_attempt01.py`

#### Purpose
This file contains the `FormatPersonSummarySkill` class, which is responsible for formatting person data into a standard readable summary. It processes input data from a request, formats it according to predefined rules, and returns a formatted summary.

#### Architecture
- **Class**: `FormatPersonSummarySkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: Asynchronously processes the request and formats the person data.
  - `_format`: Formats the person data into a readable summary string.
- **Data Flow**: The `execute` method receives a request, extracts person data, formats it using `_format`, and returns a `SkillResponse` object.

#### Patterns
- **Singleton**: Not explicitly used.
- **Factory**: Not explicitly used.
- **Observer**: Not explicitly used.

#### Dependencies
- **Imports**: `logging` for logging errors.
- **Base Class**: `SkillBase` from `engine.base`.
- **Request/Response Classes**: `SkillRequest` and `SkillResponse` from `engine.base`.

#### Interfaces
- **Public Methods**:
  - `execute`: Exposed to handle incoming requests and format person data.
  - `_format`: Internal method to format person data into a summary string.

#### Database
- **PostgreSQL Tables**: References `engine`, `a`, `fields`, and `parts` tables, though these are not directly accessed in the provided code.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
- **Main Logic**: The `execute` method processes the request, checks for the presence of person data, and formats it using the `_format` method.
- **Formatting Logic**: The `_format` method constructs a summary string by combining various fields from the person data, such as name, date of birth, birth location, date of death, and notes.

#### Integration Points
- **Skill System**: Integrates with the broader Mythos skill system, where `SkillBase` and `SkillResponse` are part of a larger framework for handling skills.
- **Data Source**: Expects person data to be provided in the request, which could be sourced from the PostgreSQL database or other parts of the Mythos system.

### Detailed Breakdown

#### Class: `FormatPersonSummarySkill`
- **Attributes**:
  - `name`: 'format_person_summary'
  - `version`: '1.0'
  - `category`: 'meta'
  - `description`: 'Format person data into a standard readable summary'
  - `triggers`: ['format person', 'person summary', 'who is']
  - `cache_ttl`: 0

- **Methods**:
  - **`execute`**:
    - **Purpose**: Processes the incoming request, formats the person data, and returns a `SkillResponse`.
    - **Parameters**: `request` (expected to contain `parameters` with a `person` key).
    - **Logic**:
      - Extracts `person` data from the request.
      - If no `person` data is found, returns a `SkillResponse` with a low confidence and a summary indicating no data.
      - Calls `_format` to format the person data.
      - Constructs and returns a `SkillResponse` with the formatted summary and relevant metadata.
    - **Error Handling**: Logs errors and returns a `SkillResponse` with an error message and zero confidence.

  - **`_format`**:
    - **Purpose**: Formats the person data into a readable summary string.
    - **Parameters**: `person` (a dictionary containing person data).
    - **Logic**:
      - Constructs the name from various name parts (prefix, first_name, middle_name, last_name, suffix).
      - Adds known aliases.
      - Includes date of birth and birth location.
      - Adds date of death if available.
      - Includes notes if they are less than 100 characters.
      - Joins all parts into a single summary string.

#### Top-level Functions
- **`execute`**: This function is not used in the provided code and seems to be a duplicate of the method within the class.
- **`_format`**: This function is also not used in the provided code and seems to be a duplicate of the method within the class.

### Conclusion
The `FormatPersonSummarySkill` class is designed to handle requests for formatting person data into a readable summary. It integrates with the Mythos skill system and processes data according to predefined rules, ensuring that the summary is both informative and concise.
