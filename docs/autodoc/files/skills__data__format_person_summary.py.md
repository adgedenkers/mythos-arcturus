# skills/data/format_person_summary.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 107

---

### Purpose
The `format_person_summary.py` file defines a skill (`FormatPersonSummarySkill`) that formats person data into a standard readable summary. This skill is triggered by specific commands and processes person data to generate a concise summary.

### Architecture
The file contains a single class `FormatPersonSummarySkill` that inherits from `SkillBase`. The class has two methods:
- `execute`: The main method that handles the execution of the skill, taking a `SkillRequest` object and returning a `SkillResponse` object.
- `_format`: A helper method that formats the person data into a readable string.

### Patterns
- **Factory Method**: The `execute` method acts as a factory method, creating and returning a `SkillResponse` object based on the input request.
- **Helper Method**: The `_format` method is a helper method used by `execute` to perform the actual formatting of the person data.

### Dependencies
- **Imports**: The file imports `logging` for error logging and `unicodedata` for text normalization.
- **From `engine.base`**: It imports `SkillBase`, `SkillRequest`, and `SkillResponse` for the skill base class and response/request objects.

### Interfaces
- **Public Methods**:
  - `execute`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
  - `_format`: Synchronous method that takes a `person` dictionary and returns a formatted string.

### Database
The file references the following PostgreSQL tables:
- `engine`
- `a`
- `fields`
- `parts`

### Configuration
The skill does not explicitly use any configuration files or environment variables but relies on the `SkillBase` class for configuration and settings.

### Key Logic
1. **Error Handling**: The `execute` method catches and logs any exceptions that occur during execution.
2. **Data Validation**: It checks if the `person` data is present in the request parameters.
3. **Formatting Logic**:
   - The `_format` method constructs a summary string from various fields of the `person` dictionary.
   - It normalizes the resulting string to ASCII using `unicodedata.normalize`.
4. **Response Construction**: The `execute` method constructs and returns a `SkillResponse` object with the formatted summary.

### Integration Points
- **SkillBase**: The skill integrates with the `SkillBase` class, inheriting its structure and methods.
- **SkillRequest/SkillResponse**: The skill processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos request/response system.
- **Database**: The skill indirectly interacts with the PostgreSQL database through the `SkillBase` class, which manages database connections and queries.

### Summary
The `FormatPersonSummarySkill` class in `format_person_summary.py` is designed to format person data into a readable summary. It handles requests, processes person data, and constructs responses using the `SkillBase` framework. The skill integrates with the Mythos system through the request/response mechanism and indirectly with the PostgreSQL database.
