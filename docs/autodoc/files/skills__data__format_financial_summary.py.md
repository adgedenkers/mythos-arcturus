# skills/data/format_financial_summary.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 113

---

### Documentation for `skills/data/format_financial_summary.py`

#### Purpose
This file defines a skill (`FormatFinancialSummarySkill`) that formats financial data into a readable summary. It processes financial data from various categories (accounts, bills, transactions) and formats them into a structured text summary.

#### Architecture
- **Class**: `FormatFinancialSummarySkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: The main entry point for the skill, which processes the incoming request and formats the financial data.
  - `_format`: A helper method that performs the actual formatting of the financial data.

#### Patterns
- **Singleton**: Not explicitly used.
- **Observer**: Not explicitly used.
- **Factory**: Not explicitly used.

#### Dependencies
- **Imports**:
  - `logging`: For logging errors.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response objects for the skill.

#### Interfaces
- **Exposed Methods**:
  - `execute`: An asynchronous method that takes a `SkillRequest` object and returns a `SkillResponse` object.
  - `_format`: A synchronous method that takes a dictionary of financial data and returns a formatted string.

#### Database
- **References**:
  - `engine`: PostgreSQL table used for the skill's operations.
  - `a`: PostgreSQL table used for the skill's operations.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

#### Key Logic
- **`execute` Method**:
  - Processes the incoming request parameters.
  - Calls the `_format` method to format the financial data.
  - Constructs and returns a `SkillResponse` object with the formatted data.
  - Handles exceptions by logging the error and raising it.

- **`_format` Method**:
  - Processes financial data from three categories: accounts, bills, and transactions.
  - Groups accounts by type and calculates the total balance.
  - Lists bills with their expected amounts and days.
  - Lists recent transactions with their amounts and descriptions.
  - Ensures the result is ASCII-only.
  - Returns a formatted string or a default message if no data is available.

#### Integration Points
- **Mythos Subsystems**:
  - **Skill System**: The `FormatFinancialSummarySkill` integrates with the skill system via the `SkillBase` class, which handles the execution and response generation.
  - **Database**: The skill interacts with PostgreSQL tables (`engine` and `a`) for its operations, though the specific interactions are not detailed in the provided code.
  - **Logging**: Uses the `logging` module to log errors, which is part of the overall logging infrastructure in Mythos.

### Summary
The `FormatFinancialSummarySkill` class in `format_financial_summary.py` is designed to format financial data into a structured summary. It processes incoming requests, formats the data, and returns a response. The skill integrates with the Mythos skill system and uses PostgreSQL for its operations, with logging for error handling.
