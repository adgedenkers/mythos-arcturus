import logging
import importlib
from engine.base import SkillBase, SkillRequest, SkillResponse

class FinancialOverviewSkill(SkillBase):
    name = 'financial_overview'
    triggers = [
        'financial overview',
        'money overview',
        'full finance',
        'how are my finances',
        'financial status',
        'finance report'
    ]

    SUB_SKILLS = {
        'balances': ('data.finance_balance', 'FinanceBalanceSkill'),
        'bills': ('data.query_bills_due', 'QueryBillsDueSkill'),
        'transactions': ('data.query_transactions', 'QueryTransactionsSkill'),
    }

    def execute(self, request: SkillRequest) -> SkillResponse:
        pass

    def _run_skill(self, skill_module, skill_class, request: SkillRequest):
        pass

    def _build_overview(self, results):
        pass