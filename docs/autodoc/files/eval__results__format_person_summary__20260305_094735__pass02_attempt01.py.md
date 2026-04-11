# eval/results/format_person_summary/20260305_094735/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 65

---

### File: `eval/results/format_person_summary/20260305_094735/pass02_attempt01.py`

#### Purpose
This file contains the `FormatPersonSummarySkill` class, which is responsible for formatting person data into a standard readable summary. It processes person data from a request and formats it into a structured summary string.

#### Architecture
- **Class**: `FormatPersonSummarySkill` extends `SkillBase` and includes methods `execute` and `_format`.
- **Methods**:
  - `execute`: An asynchronous method that processes the request and returns a `SkillResponse`.
  - `_format`: A synchronous method that formats the person data into a summary string.
- **Data Flow**: The `execute` method receives a request, processes it using the `_format` method, and returns a formatted summary.

#### Patterns
- **Decorator Pattern**: The `execute` method is decorated with `async` to handle asynchronous operations.
- **Template Method Pattern**: The `execute` method provides a template for processing the request, while `_format` is a concrete method for formatting the data.

#### Dependencies
- **Imports**: `logging` for logging purposes.
- **Base Class**: `SkillBase` from `engine.base` for inheritance.

#### Interfaces
- **Exposed Methods**: 
  - `execute`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
  - `_format`: Synchronous method that takes a `person` dictionary and returns a formatted summary string.

#### Database
- **PostgreSQL Tables**: The file references the following tables:
  - `engine`
  - `a`
  - `fields`
  - `parts`

#### Configuration
- **Environment Variables**: No specific environment variables are used in this file.
- **Config Files**: No specific configuration files are used in this file.

#### Key Logic
- **`execute` Method**:
  - Processes the request and expects `request.parameters['person']` to be a dictionary containing person data.
  - Calls `_format` to generate the summary string.
- **`_format` Method**:
  - Constructs a summary string from the person data.
  - Includes name, nickname, date of birth, birth location, date of death, and notes (if less than 100 characters).
  - Uses conditional checks to include only available data fields.

#### Integration Points
- **Mythos Subsystems**:
  - **Skill System**: Integrates with the Mythos skill system via `SkillBase` inheritance.
  - **Database**: Uses PostgreSQL tables to fetch or store person data.
  - **Request/Response Handling**: Uses `SkillRequest` and `SkillResponse` from `engine.base` for request and response handling.

### Detailed Breakdown of `_format` Method
- **Name Construction**:
  - Assembles the name from `prefix`, `first_name`, `middle_name`, `last_name`, and `suffix`.
  - Appends a nickname if available.
- **Date of Birth**:
  - Includes the date of birth if available.
- **Birth Location**:
  - Constructs the birth location from `birth_city` and `birth_state`.
- **Date of Death**:
  - Includes the date of death if available.
- **Notes**:
  - Appends notes if they are less than 100 characters long.

This file is a critical component of the Mythos system, responsible for formatting person data into a readable summary, which can be used for various downstream processes or user interfaces.
