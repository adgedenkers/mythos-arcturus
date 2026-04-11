# eval/results/format_financial_summary/20260305_094749/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 113

---

### Documentation for `test_skill.py`

#### Purpose
This file defines the `FormatFinancialSummarySkill` class, which is responsible for formatting financial data into a readable summary. It processes input data containing accounts, bills, and transactions, and formats this data into a structured summary.

#### Architecture
- **Class**: `FormatFinancialSummarySkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: Asynchronous method that processes the incoming request and formats the financial data.
  - `_format`: Synchronous method that performs the actual formatting of the financial data.

#### Patterns
- **Decorator Pattern**: The `execute` method is decorated with `async` to handle asynchronous operations.
- **Singleton Pattern**: The `FormatFinancialSummarySkill` class can be treated as a singleton if instantiated once and reused.

#### Dependencies
- **Imports**: `logging` for error logging.
- **Base Class**: `SkillBase` from `engine.base` for the base skill functionality.
- **Request/Response Models**: `SkillRequest` and `SkillResponse` from `engine.base`.

#### Interfaces
- **Public Methods**:
  - `execute`: Accepts a `SkillRequest` object and returns a `SkillResponse` object.
  - `_format`: Accepts a dictionary `data` and returns a formatted string.

#### Database
- **PostgreSQL Tables**:
  - `engine`: Likely used for skill metadata or configuration.
  - `a`: Possibly used for storing financial data or other related information.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Configuration Files**: None explicitly used.

#### Key Logic
- **Data Processing**:
  - **Accounts**: Group accounts by type, calculate total balance, and format into a readable summary.
  - **Bills**: Summarize bills by merchant, expected amount, and expected day.
  - **Transactions**: Summarize the top 5 recent transactions by amount, description, and date.
- **Error Handling**: Logs errors and raises exceptions for unhandled cases.

#### Integration Points
- **SkillBase**: Integrates with the base skill framework to handle requests and responses.
- **PostgreSQL**: Likely integrates with the PostgreSQL database to fetch or store financial data.
- **Logging**: Integrates with the logging system to log errors.

### Detailed Breakdown

#### Class: `FormatFinancialSummarySkill`
- **Attributes**:
  - `name`: 'format_financial_summary'
  - `version`: '1.0'
  - `category`: 'meta'
  - `description`: 'Format financial data into a readable summary'
  - `triggers`: List of strings that trigger this skill.
  - `cache_ttl`: Cache time-to-live set to 0, indicating no caching.

#### Method: `execute`
- **Purpose**: Processes the incoming request and formats the financial data.
- **Parameters**: `request` (SkillRequest object).
- **Returns**: `SkillResponse` object.
- **Logic**:
  - Extracts parameters from the request.
  - Calls `_format` to format the data.
  - Constructs and returns a `SkillResponse` object with the formatted data.

#### Method: `_format`
- **Purpose**: Formats the financial data into a readable summary.
- **Parameters**: `data` (dictionary containing financial data).
- **Returns**: Formatted string.
- **Logic**:
  - Processes accounts, bills, and transactions from the input data.
  - Groups accounts by type and calculates total balances.
  - Summarizes bills and recent transactions.
  - Ensures the output is ASCII-only.
  - Returns a default message if no data is formatted.

#### Database References
- **PostgreSQL Tables**:
  - `engine`: Likely used for skill metadata or configuration.
  - `a`: Possibly used for storing financial data or other related information.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Configuration Files**: None explicitly used.

#### Key Logic
- **Data Processing**:
  - **Accounts**: Group accounts by type, calculate total balance, and format into a readable summary.
  - **Bills**: Summarize bills by merchant, expected amount, and expected day.
  - **Transactions**: Summarize the top 5 recent transactions by amount, description, and date.
- **Error Handling**: Logs errors and raises exceptions for unhandled cases.

#### Integration Points
- **SkillBase**: Integrates with the base skill framework to handle requests and responses.
- **PostgreSQL**: Likely integrates with the PostgreSQL database to fetch or store financial data.
- **Logging**: Integrates with the logging system to log errors.
