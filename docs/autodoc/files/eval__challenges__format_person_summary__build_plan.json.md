# eval/challenges/format_person_summary/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 28

---

### File: eval/challenges/format_person_summary/build_plan.json

#### Purpose
This JSON file serves as a build plan for the `FormatPersonSummarySkill` class, detailing the steps and requirements for implementing a skill that formats person data into a standard human-readable summary.

#### Architecture
The file is structured as a JSON object with several key sections:
- **plan_id**: Identifies the plan.
- **version**: Specifies the version of the plan.
- **description**: Describes the purpose of the skill.
- **pattern**: Indicates the pattern to follow.
- **model_hint**: Suggests a model to use.
- **context**: Contains system context and scaffold code.
- **build_plan**: Lists the steps to implement the skill.
- **test_cases**: Provides test cases to validate the implementation.

#### Patterns
- **Factory Pattern**: The scaffold code suggests a factory-like approach to creating the `FormatPersonSummarySkill` class.
- **Singleton Pattern**: The class is designed to be a singleton with a unique name and version.

#### Dependencies
- **Imports**: The scaffold code imports `SkillBase`, `SkillRequest`, and `SkillResponse` from `engine.base`.
- **No Database Imports**: The plan explicitly states that no database imports are allowed.

#### Interfaces
- **SkillBase Class**: The `FormatPersonSummarySkill` class extends `SkillBase` and implements the `execute` method.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object.

#### Database
- **No Database Access**: The plan explicitly states that no database access is required.

#### Configuration
- **Environment Variables**: No specific environment variables are mentioned.
- **Configuration Files**: No specific configuration files are mentioned.

#### Key Logic
- **_format Method**: This method takes a person dictionary and formats it into a human-readable string. It handles various fields like `prefix`, `first_name`, `middle_name`, `last_name`, `suffix`, `known_as`, `date_of_birth`, `birth_city`, `birth_state`, `date_of_death`, and `notes`.
- **execute Method**: This method processes the request, extracts the person data, calls the `_format` method, and returns a `SkillResponse` object with the formatted summary.

#### Integration Points
- **SkillBase Integration**: The `FormatPersonSummarySkill` class integrates with the `SkillBase` class, which is part of the Mythos system's skill framework.
- **SkillResponse Integration**: The `execute` method returns a `SkillResponse` object, which is used throughout the Mythos system to communicate results.

### Detailed Breakdown of Build Plan Steps

1. **Pass 1**: Write the file skeleton with necessary imports and class attributes. The methods should have `pass` placeholders.
2. **Pass 2**: Implement the `_format` method to build the display name from the person dictionary. Handle various fields and conditions as specified.
3. **Pass 3**: Implement the `execute` method to process the request, extract person data, call `_format`, and return a `SkillResponse` object. Handle exceptions and missing fields gracefully.
4. **Pass 4**: Review the implementation to ensure no database imports, graceful handling of missing fields, and ASCII-only output. Ensure the summary is never empty.

### Test Cases
- **Test Case 1**: Message: "format person", Expectation: Successful response with `formatted` data.
- **Test Case 2**: Message: "who is this person", Expectation: Successful response.

This build plan ensures a structured and thorough implementation of the `FormatPersonSummarySkill` class, adhering to the specified patterns and constraints.
