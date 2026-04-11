# skills/data/financial_overview.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 63

---

### File: `skills/data/financial_overview.py`

#### Purpose
This file defines the `FinancialOverviewSkill` class, which provides a comprehensive financial overview by aggregating data from multiple sub-skills related to balances, bills, and recent transactions.

#### Architecture
- **Classes**: 
  - `FinancialOverviewSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: The main entry point for executing the skill, which aggregates data from sub-skills.
  - `_run_skill`: A helper method to dynamically load and execute sub-skills.
- **Data Flow**: 
  - The `execute` method iterates over predefined sub-skills, dynamically loads each sub-skill, and collects their responses.
  - The responses are merged into a single `SkillResponse` object that includes a summary and detailed data.

#### Patterns
- **Factory Pattern**: The `_run_skill` method dynamically loads and instantiates sub-skills based on their module path and class name.
- **Composite Pattern**: The `FinancialOverviewSkill` composes the results from multiple sub-skills to provide a comprehensive overview.

#### Dependencies
- **Imports**: 
  - `logging`: For logging errors and information.
  - `importlib`: For dynamically importing sub-skills.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response objects.

#### Interfaces
- **Exposed Methods**:
  - `execute(request: SkillRequest) -> SkillResponse`: Asynchronous method to execute the skill and return a response.
  - `_run_skill(module_path: str, class_name: str, request: SkillRequest) -> SkillResponse`: Asynchronous helper method to run a sub-skill.

#### Database
- **References**: 
  - `engine` (PostgreSQL): The file references the `engine` module, which likely interacts with the PostgreSQL database.

#### Configuration
- **Environment Variables**: None explicitly mentioned.
- **Config Files**: None explicitly mentioned.

#### Key Logic
- **Aggregation Logic**:
  - The `execute` method iterates over predefined sub-skills (`balances`, `bills`, `transactions`), dynamically loads each sub-skill, and collects their responses.
  - Responses are merged into a single `SkillResponse` object, which includes a summary and detailed data.
- **Error Handling**:
  - Errors are logged using the `logger` and returned in the `SkillResponse` object.

#### Integration Points
- **Sub-Skills**:
  - The `FinancialOverviewSkill` integrates with three sub-skills:
    - `FinanceBalanceSkill` from `data.finance_balance`.
    - `QueryBillsDueSkill` from `data.query_bills_due`.
    - `QueryTransactionsSkill` from `data.query_transactions`.
- **SkillBase**:
  - Inherits from `SkillBase`, which likely provides common functionality for all skills, such as request handling and response formatting.

### Summary
The `FinancialOverviewSkill` class in `financial_overview.py` provides a comprehensive financial overview by aggregating data from multiple sub-skills. It dynamically loads and executes these sub-skills, merging their responses into a single, cohesive summary. The class is designed to be part of a larger skill-based system, integrating with other components through the `SkillBase` class and dynamically loaded sub-skills.
