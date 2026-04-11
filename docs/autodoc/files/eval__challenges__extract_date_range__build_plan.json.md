# eval/challenges/extract_date_range/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 29

---

### File: eval/challenges/extract_date_range/build_plan.json

#### Purpose
This JSON file contains a build plan for a skill named `ExtractDateRangeSkill` that parses natural language date references into SQL-ready date ranges. It outlines the steps to implement the skill, including class structure, method implementations, and testing cases.

#### Architecture
The file is structured as a JSON object with several key sections:
- `plan_id`: Identifies the skill.
- `version`: Specifies the version of the plan.
- `description`: Describes the purpose of the skill.
- `pattern`: Indicates the pattern or category of the skill.
- `model_hint`: Suggests a model to use.
- `context`: Contains system context, scaffold code, and mandatory patterns.
- `build_plan`: A step-by-step guide to implement the skill.
- `test_cases`: Provides test cases to validate the skill.

#### Patterns
- **Template Method Pattern**: The scaffold code provides a template method (`execute`) that needs to be implemented.
- **Factory Method Pattern**: The `SkillResponse` object creation can be seen as a factory method pattern where the response is created based on the parsed date logic.

#### Dependencies
- **Imports**: The skill will import `logging`, `re`, `datetime`, `calendar`, and `engine.base` for `SkillBase`, `SkillRequest`, and `SkillResponse`.
- **No Database Imports**: The skill explicitly avoids importing database-related modules like `psycopg2`.

#### Interfaces
- **SkillBase Class**: The skill inherits from `SkillBase` and implements the `execute` method.
- **SkillResponse**: The skill uses `SkillResponse` to return the parsed date information.

#### Database
- **No Database Interaction**: The skill does not interact with any database.

#### Configuration
- **Environment Variables**: No environment variables are used.
- **Configuration Files**: No configuration files are referenced.

#### Key Logic
- **Date Parsing**: The `_parse_dates` method is responsible for parsing natural language date references into specific date ranges.
- **Date Handling**: The method handles various date references like "today", "yesterday", "this week", "last week", "this month", "last month", "past N days", "N days ago", and specific months like "in march".
- **SkillResponse Construction**: The `execute` method constructs and returns a `SkillResponse` object based on the parsed date information.

#### Integration Points
- **SkillBase Integration**: The skill integrates with the `SkillBase` class, which is part of the Mythos system.
- **SkillResponse Integration**: The skill uses `SkillResponse` to return results, which is a standardized response format used throughout the Mythos system.

### Detailed Breakdown of Key Sections

#### Context
- **System Context**: Specifies the necessary imports.
- **Scaffold**: Provides the class structure and method placeholders.
- **Mandatory Patterns**: Ensures the skill does not query any database and adheres to specific response formats.

#### Build Plan
1. **Pass 1**: Write the file skeleton with necessary imports and class attributes.
2. **Pass 2**: Implement the `_parse_dates` method to handle various date references.
3. **Pass 3**: Implement the `execute` method to call `_parse_dates` and construct the `SkillResponse`.
4. **Pass 4**: Review the implementation for correctness and adherence to guidelines.

#### Test Cases
- **Test Case 1**: Validates the skill's ability to parse "yesterday".
- **Test Case 2**: Validates the skill's ability to parse "last week".
- **Test Case 3**: Validates the skill's behavior when no date reference is present.

This JSON file serves as a comprehensive guide for implementing the `ExtractDateRangeSkill` within the Mythos system, ensuring it adheres to the specified design patterns, dependencies, and integration points.
