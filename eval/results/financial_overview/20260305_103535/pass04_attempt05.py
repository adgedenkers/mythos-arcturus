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
        try:
            results = []
            merged_data = {}
            
            for key, (module_path, class_name) in self.SUB_SKILLS.items():
                try:
                    result = self._run_skill(module_path, class_name, request)
                    results.append(result)
                    
                    # Merge data from each sub-skill
                    if result and hasattr(result, 'data') and result.data:
                        merged_data.update(result.data)
                        
                except Exception as e:
                    logging.error(f"Error running {key} skill: {e}")
                    results.append(None)
            
            overview = self._build_overview(results)
            
            return SkillResponse(
                skill_name=self.name,
                data=merged_data,
                summary=overview,
                confidence=0.9,
                sources=['financial_overview']
            )
            
        except Exception as e:
            logging.error(f"Error in financial overview skill: {e}")
            return SkillResponse(
                skill_name=self.name,
                data={},
                summary='Error generating financial overview.',
                confidence=0.0,
                sources=['financial_overview']
            )

    def _run_skill(self, skill_module, skill_class, request: SkillRequest):
        try:
            module = importlib.import_module(skill_module)
            skill = getattr(module, skill_class)
            instance = skill()
            return instance.execute(request)
        except Exception as e:
            logging.error(f"Error executing skill {skill_class}: {e}")
            raise

    def _build_overview(self, results):
        summaries = []
        for result in results:
            if result and hasattr(result, 'response') and result.response != 'ok':
                summaries.append(result.response)
            elif result and hasattr(result, 'response') and result.response == 'ok':
                # For 'ok' responses, we still want to include some summary
                if hasattr(result, 'data') and result.data:
                    summaries.append(str(result.data))
                else:
                    summaries.append('Data retrieved successfully')
            elif result and hasattr(result, 'data') and result.data:
                summaries.append(str(result.data))
        
        if summaries:
            return ' | '.join(summaries)
        else:
            return 'No financial data available.'