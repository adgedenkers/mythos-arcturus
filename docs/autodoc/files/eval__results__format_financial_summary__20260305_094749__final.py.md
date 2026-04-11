# eval/results/format_financial_summary/20260305_094749/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 113

---

### Purpose
The `final.py` file contains the `FormatFinancialSummarySkill` class, which is responsible for formatting financial data into a readable summary. It processes data related to accounts, bills, and transactions and returns a formatted string.

### Architecture
The file contains a single class `FormatFinancialSummarySkill` that inherits from `SkillBase`. The class has two methods:
- `execute`: An asynchronous method that processes the request and formats the data.
- `_format`: A synchronous method that performs the actual formatting of the financial data.

### Patterns
- **Decorator Pattern**: The `execute` method is decorated with `async` to handle asynchronous operations.
- **Factory Method**: The `execute` method uses the `_format` method to generate the formatted data.

### Dependencies
- **Imports**: The file imports `logging` for logging errors and `SkillBase`, `SkillRequest`, and `SkillResponse` from `engine.base`.
- **Database**: The file references two PostgreSQL tables: `engine` and `a`.

### Interfaces
- **Public Methods**: 
  - `execute`: Accepts a `request` object and returns a `SkillResponse` object.
  - `_format`: Accepts a `data` dictionary and returns a formatted string.

### Database
- **Tables**: 
  - `engine` (PostgreSQL)
  - `a` (PostgreSQL)

### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: None explicitly used.

### Key Logic
- **Data Processing**: The `_format` method processes the financial data by categorizing accounts, bills, and transactions.
  - **Accounts**: Grouped by type, and balances are summed.
  - **Bills**: Summarized by merchant and expected amount.
  - **Transactions**: Top 5 recent transactions are listed.
- **Error Handling**: The `execute` method catches exceptions and logs errors using `logging.error`.

### Integration Points
- **SkillBase**: The `FormatFinancialSummarySkill` class inherits from `SkillBase`, indicating it integrates with the broader Mythos skill system.
- **SkillRequest and SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse`, indicating integration with the Mythos request-response framework.
- **Database**: The file references PostgreSQL tables `engine` and `a`, suggesting integration with the Mythos database layer for data retrieval or storage.

### Detailed Explanation

#### Class: `FormatFinancialSummarySkill`
- **Attributes**:
  - `name`: 'format_financial_summary'
  - `version`: '1.0'
  - `category`: 'meta'
  - `description`: 'Format financial data into a readable summary'
  - `triggers`: ['format finance', 'financial summary', 'money summary']
  - `cache_ttl`: 0

- **Methods**:
  - **`execute(request)`**:
    - **Purpose**: Processes the request and formats the financial data.
    - **Parameters**: `request` (SkillRequest object)
    - **Returns**: `SkillResponse` object
    - **Logic**:
      - Extracts parameters from the request.
      - Calls `_format` to get the formatted data.
      - Constructs and returns a `SkillResponse` object with the formatted data.
      - Logs errors if any exception occurs.

  - **`_format(data)`**:
    - **Purpose**: Formats the financial data into a readable summary.
    - **Parameters**: `data` (dictionary containing financial data)
    - **Returns**: Formatted string
    - **Logic**:
      - Processes accounts, bills, and transactions.
      - Groups accounts by type and sums balances.
      - Summarizes bills by merchant and expected amount.
      - Lists top 5 recent transactions.
      - Ensures the result is ASCII-only.
      - Returns a formatted string or a default message if no data is available.

### Integration with Mythos System
- **Skill System**: The class integrates with the Mythos skill system by inheriting from `SkillBase` and implementing the `execute` method.
- **Database**: The file references PostgreSQL tables, indicating it interacts with the database layer of Mythos.
- **Logging**: Uses `logging` for error handling, ensuring that any issues are logged for debugging and monitoring.

This documentation provides a comprehensive overview of the `final.py` file, detailing its purpose, architecture, dependencies, and integration points within the Mythos system.
