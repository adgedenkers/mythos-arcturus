import logging
from engine.base import SkillBase, SkillRequest, SkillResponse

class FormatFinancialSummarySkill(SkillBase):
    name = 'format_financial_summary'
    version = '1.0'
    category = 'meta'
    description = 'Format financial data into a readable summary'
    triggers = ['format finance', 'financial summary', 'money summary']
    cache_ttl = 0

    async def execute(self, request) -> SkillResponse:
        # Expects request.parameters with 'accounts', 'bills', 'transactions' dicts
        pass

    def _format(self, data) -> str:
        # Build sections for accounts, bills, recent transactions
        pass