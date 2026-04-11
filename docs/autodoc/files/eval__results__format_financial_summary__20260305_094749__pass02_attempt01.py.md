# eval/results/format_financial_summary/20260305_094749/pass02_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 91

---

### Purpose
The `FormatFinancialSummarySkill` class is designed to format financial data (accounts, bills, transactions) into a readable summary. It is part of the Mythos system and is triggered by specific commands like 'format finance', 'financial summary', and 'money summary'.

### Architecture
- **Class**: `FormatFinancialSummarySkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: An asynchronous method that processes the request and returns a formatted summary.
  - `_format`: A synchronous method that formats the financial data into a human-readable string.

### Patterns
- **Singleton**: The class does not explicitly use the singleton pattern, but it could be used as a singleton if instantiated once and reused.
- **Strategy**: The `_format` method could be seen as a strategy for formatting financial data.

### Dependencies
- **Imports**: `logging` for logging purposes.
- **Base Classes**: `SkillBase` from `engine.base` for the base class functionality.

### Interfaces
- **Public Methods**:
  - `execute`: Accepts a `request` object and returns a `SkillResponse`.
  - `_format`: Accepts a `data` dictionary and returns a formatted string.

### Database
- **PostgreSQL Tables**: 
  - `engine`: Likely used for storing or retrieving skill-related metadata.
  - `a`: Possibly used for storing financial data or other related information.

### Configuration
- **Environment Variables**: None explicitly used.
- **Configuration Files**: None explicitly used.

### Key Logic
- **Data Grouping and Formatting**:
  - **Accounts**: Group accounts by type, calculate total balance, and format into a readable summary.
  - **Bills**: Summarize bills by merchant and expected amount, calculate total bills.
  - **Transactions**: Display the top 5 recent transactions and calculate total transaction amount.

### Integration Points
- **Skill Execution**: The `execute` method is expected to be called by the Mythos system when a user triggers the skill with commands like 'format finance', 'financial summary', or 'money summary'.
- **Data Source**: The `execute` method expects `request.parameters` to contain `accounts`, `bills`, and `transactions` dictionaries, which likely come from other subsystems within Mythos.

### Detailed Breakdown

#### Class: `FormatFinancialSummarySkill`
- **Attributes**:
  - `name`: 'format_financial_summary'
  - `version`: '1.0'
  - `category`: 'meta'
  - `description`: 'Format financial data into a readable summary'
  - `triggers`: List of commands that trigger this skill.
  - `cache_ttl`: Cache time-to-live, set to 0 indicating no caching.

#### Method: `execute`
- **Purpose**: Processes the request and formats the financial data.
- **Parameters**: `request` (expected to contain `accounts`, `bills`, and `transactions`).
- **Return**: `SkillResponse` object.

#### Method: `_format`
- **Purpose**: Formats the financial data into a readable string.
- **Parameters**: `data` (dictionary containing `accounts`, `bills`, and `transactions`).
- **Return**: Formatted string.

### Example Data Flow
1. **Trigger**: User triggers the skill with a command like 'financial summary'.
2. **Request Handling**: The `execute` method is called with the request containing financial data.
3. **Data Processing**: The `_format` method processes the financial data into a readable summary.
4. **Response**: The formatted summary is returned as a `SkillResponse`.

### Example Usage
```python
# Assuming a request object with the required parameters
request = SkillRequest(parameters={
    'accounts': [
        {'type': 'savings', 'abbr': 'SAV', 'balance': 1000},
        {'type': 'checking', 'abbr': 'CHK', 'balance': 500}
    ],
    'bills': [
        {'merchant_name': 'Electric Co', 'expected_amount': 150, 'expected_day': 15}
    ],
    'transactions': [
        {'amount': -100, 'description': 'Groceries', 'date': '2023-01-01'},
        {'amount': 200, 'description': 'Paycheck', 'date': '2023-01-15'}
    ]
})

# Create an instance of the skill
skill = FormatFinancialSummarySkill()

# Execute the skill
response = await skill.execute(request)
print(response.result)  # Output the formatted summary
```

This documentation provides a comprehensive overview of the `FormatFinancialSummarySkill` class and its functionality within the Mythos system.
