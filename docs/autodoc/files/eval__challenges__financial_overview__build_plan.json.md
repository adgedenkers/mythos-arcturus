# eval/challenges/financial_overview/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 29

---

### File: `eval/challenges/financial_overview/build_plan.json`

#### Purpose
This JSON file serves as a blueprint for constructing the `FinancialOverviewSkill` composite skill, which combines account balances, upcoming bills, and recent transactions to provide a comprehensive financial overview.

#### Architecture
The file is structured as a JSON object containing metadata and a step-by-step build plan for the `FinancialOverviewSkill`. It includes:
- **Metadata**: `plan_id`, `version`, `description`, `pattern`, `model_hint`, and `context`.
- **Build Plan**: A list of steps (`build_plan`) detailing the implementation process.
- **Test Cases**: A set of test cases to validate the skill's functionality.

#### Patterns
- **Composite Pattern**: The `FinancialOverviewSkill` is a composite skill that aggregates the results of multiple sub-skills.
- **Factory Pattern**: The sub-skills are dynamically loaded using `importlib.import_module` and `getattr`.

#### Dependencies
- **Imports**: The skill relies on `logging`, `importlib`, and `engine.base`.
- **Sub-Skills**: The skill depends on `FinanceBalanceSkill`, `QueryBillsDueSkill`, and `QueryTransactionsSkill`.

#### Interfaces
- **SkillBase Interface**: The `FinancialOverviewSkill` class implements the `SkillBase` interface, inheriting methods like `execute`.
- **SkillRequest/SkillResponse**: The skill uses `SkillRequest` and `SkillResponse` for request and response handling.

#### Database
- **No Database Access**: The skill does not directly access any database. It relies on sub-skills to fetch data, which may or may not involve database access.

#### Configuration
- **Environment Variables**: No specific environment variables are mentioned.
- **Context Configuration**: The `context` section provides system context and mandatory patterns for implementation.

#### Key Logic
1. **Sub-Skill Execution**: The skill dynamically loads and executes sub-skills (`FinanceBalanceSkill`, `QueryBillsDueSkill`, `QueryTransactionsSkill`) using `importlib.import_module` and `getattr`.
2. **Data Aggregation**: The skill aggregates the results from sub-skills to build a comprehensive financial overview.
3. **Error Handling**: The skill includes error handling to manage failures in sub-skill execution.

#### Integration Points
- **SkillBase Integration**: The skill integrates with the `SkillBase` class and uses `SkillRequest` and `SkillResponse` for interaction.
- **Sub-Skill Integration**: The skill integrates with sub-skills (`FinanceBalanceSkill`, `QueryBillsDueSkill`, `QueryTransactionsSkill`) to fetch and aggregate financial data.
- **Test Cases**: The skill is validated using predefined test cases.

### Detailed Breakdown of Build Plan Steps

1. **Step 1**: Write the file skeleton, including necessary imports and class definition with triggers and sub-skills.
2. **Step 2**: Implement the `_run_skill` method to dynamically load and execute sub-skills. Implement `_build_overview` to aggregate summaries from sub-skills.
3. **Step 3**: Implement the `execute` method to run all sub-skills, build the overview, and return a `SkillResponse`.
4. **Step 4**: Review the implementation to ensure no database imports, correct sub-skill references, and ASCII-only compliance.

### Example Code Snippet for `FinancialOverviewSkill` Class

```python
import logging
import importlib
from engine.base import SkillBase, SkillRequest, SkillResponse

class FinancialOverviewSkill(SkillBase):
    name = 'financial_overview'
    triggers = ['financial overview', 'money overview', 'full finance', 'how are my finances', 'financial status', 'finance report']

    SUB_SKILLS = {
        'balances': ('data.finance_balance', 'FinanceBalanceSkill'),
        'bills': ('data.query_bills_due', 'QueryBillsDueSkill'),
        'transactions': ('data.query_transactions', 'QueryTransactionsSkill'),
    }

    async def execute(self, request: SkillRequest) -> SkillResponse:
        responses = await self._run_skill()
        overview = self._build_overview(responses)
        merged_data = self._merge_data(responses)
        return SkillResponse(
            skill_name=self.name,
            data=merged_data,
            summary=overview,
            confidence=0.9,
            sources=['financial_overview']
        )

    async def _run_skill(self):
        responses = {}
        for sub_skill_name, (module_path, class_name) in self.SUB_SKILLS.items():
            try:
                module = importlib.import_module(module_path)
                skill_class = getattr(module, class_name)
                response = await skill_class().run(request)
                responses[sub_skill_name] = response
            except Exception as e:
                logging.error(f"Error running sub-skill {sub_skill_name}: {e}")
        return responses

    def _build_overview(self, responses):
        summaries = []
        for sub_skill_name in ['balances', 'bills', 'transactions']:
            response = responses.get(sub_skill_name)
            if response and response.summary:
                summaries.append(response.summary)
        overview = ' | '.join(summaries) if summaries else 'No financial data available.'
        return overview

    def _merge_data(self, responses):
        merged_data = {}
        for sub_skill_name, response in responses.items():
            if response.data:
                merged_data[sub_skill_name] = response.data
        return merged_data
```

This code snippet illustrates the implementation of the `FinancialOverviewSkill` class as per the build plan.
