# eval/challenges/format_financial_summary/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 28

---

### File: eval/challenges/format_financial_summary/build_plan.json

#### Purpose
This JSON file serves as a build plan and specification for the `FormatFinancialSummarySkill` class, which is responsible for formatting financial data into a readable summary. It outlines the steps and requirements for implementing this skill, including the structure of the class, methods, and expected behavior.

#### Architecture
The file is structured as a JSON object with several key sections:
- **plan_id**: Identifies the skill (`format_financial_summary`).
- **version**: Specifies the version of the plan (`1.0`).
- **description**: Describes the purpose of the skill.
- **pattern**: Indicates the pattern to be used (`format_summary`).
- **model_hint**: Suggests the model to be used (`qwen3-coder:30b`).
- **context**: Contains system context, scaffold, and mandatory patterns.
- **build_plan**: Lists the steps for building the skill, including instructions and tests.
- **test_cases**: Provides test cases to validate the skill.

#### Patterns
- **Factory Pattern**: The scaffold section suggests a class (`FormatFinancialSummarySkill`) that extends `SkillBase`, indicating a factory-like approach to skill creation.
- **Singleton Pattern**: Not explicitly used, but the class is designed to be a singleton-like skill with a specific name and version.

#### Dependencies
- **Imports**: The scaffold section specifies the import of `SkillBase`, `SkillRequest`, and `SkillResponse` from `engine.base`.
- **External Libraries**: No external libraries are explicitly mentioned, but the skill is expected to use ASCII only and not interact with databases.

#### Interfaces
- **Class Interface**: The class `FormatFinancialSummarySkill` is expected to have the following methods:
  - `execute(self, request) -> SkillResponse`: Processes the request and returns a formatted summary.
  - `_format(self, data) -> str`: Formats the financial data into a readable string.

#### Database
- **No Database Interaction**: The skill is designed to be purely for formatting and does not interact with any database.

#### Configuration
- **Environment Variables**: No environment variables are mentioned.
- **Configuration Files**: No configuration files are mentioned.

#### Key Logic
- **Formatting Logic**: The `_format` method is responsible for formatting the financial data into a readable summary. It groups accounts by type, formats bills and transactions, and calculates totals for each section.
- **Execution Logic**: The `execute` method processes the request, calls `_format`, and returns a `SkillResponse` object with the formatted data.

#### Integration Points
- **SkillBase Integration**: The class extends `SkillBase`, indicating it integrates with the Mythos skill system.
- **SkillRequest and SkillResponse**: The skill processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos request-response framework.

### Detailed Breakdown of Build Plan Steps

1. **Pass 1**: Write the file skeleton with necessary imports and class attributes. Methods should have `pass` placeholders.
2. **Pass 2**: Implement the `_format` method to build sections for accounts, bills, and transactions. Ensure the method handles different types of financial data and formats them appropriately.
3. **Pass 3**: Implement the `execute` method to process the request, call `_format`, and return a `SkillResponse` object. Handle exceptions and ensure the response is correctly formatted.
4. **Pass 4**: Review the implementation to ensure no database imports, proper formatting of amounts, handling of empty sections, and ASCII-only output. Ensure the skill is production-ready.

### Test Cases
- **Test Case 1**: Validate the skill with the message "format financial data". Expect the response to contain the `formatted` key.
- **Test Case 2**: Validate the skill with the message "money summary". Expect the response to be successful.

This build plan ensures that the `FormatFinancialSummarySkill` is thoroughly designed, implemented, and tested to meet the specified requirements for formatting financial data into a readable summary.
