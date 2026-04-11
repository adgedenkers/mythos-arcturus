# eval/results/format_person_summary/20260305_094735/pass04_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 107

---

### Purpose
The `FormatPersonSummarySkill` class in `pass04_attempt02.py` is designed to format person data into a standard, readable summary string. It processes person data from a request, formats it according to specific rules, and returns a formatted summary.

### Architecture
- **Classes**: 
  - `FormatPersonSummarySkill` inherits from `SkillBase` and implements the `execute` method to process the request and `_format` method to format the person data.
- **Methods**:
  - `execute`: Asynchronous method that processes the request, calls `_format`, and returns a `SkillResponse`.
  - `_format`: Synchronous method that constructs a formatted summary string from the person data.

### Patterns
- **Factory Method**: The `execute` method acts as a factory method to create and return a `SkillResponse` object.
- **Decorator**: The `execute` method is decorated with `async` to handle asynchronous operations.

### Dependencies
- **Imports**:
  - `logging`: For error logging.
  - `unicodedata`: For normalizing Unicode strings to ASCII.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and response objects.

### Interfaces
- **Exposed Methods**:
  - `execute(request)`: Asynchronous method that takes a `SkillRequest` object and returns a `SkillResponse` object.
  - `_format(person)`: Synchronous method that takes a person dictionary and returns a formatted string.

### Database
- **References**:
  - `engine`, `a`, `fields`, `parts`: PostgreSQL tables used for data retrieval and storage, though the specific usage within this file is not detailed.

### Configuration
- **Environment Variables**: None explicitly used in this file.
- **Config Files**: None explicitly used in this file.

### Key Logic
- **Business Logic**:
  - **Data Processing**: The `execute` method processes the request parameters to extract person data and calls `_format` to generate a summary.
  - **String Formatting**: The `_format` method constructs a summary string by combining various fields from the person data (e.g., name, date of birth, birth location, date of death, notes).
  - **Normalization**: The summary string is normalized to ASCII using `unicodedata.normalize` to ensure compatibility and readability.

### Integration Points
- **Mythos Subsystems**:
  - **Engine**: The `FormatPersonSummarySkill` integrates with the Mythos engine through the `SkillBase` class and interacts with the `SkillRequest` and `SkillResponse` objects.
  - **Database**: The skill indirectly interacts with the PostgreSQL database through the `engine`, `a`, `fields`, and `parts` tables, though the specific interactions are not detailed in this file.
  - **Logging**: Uses the `logging` module to log errors, which may be integrated with a centralized logging system in Mythos.

### Summary
The `FormatPersonSummarySkill` class in `pass04_attempt02.py` is a skill that formats person data into a readable summary string. It processes incoming requests, formats the person data according to predefined rules, and returns a formatted summary. The class integrates with the Mythos engine and uses logging for error handling. The summary string is normalized to ASCII for compatibility and readability.
