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
        try:
            data = request.parameters if request.parameters else {}
            formatted = self._format(data)
            return SkillResponse(
                skill_name=self.name,
                data={'formatted': formatted},
                summary=formatted if formatted else 'No financial data to format.',
                confidence=0.9,
                sources=['format_financial_summary']
            )
        except Exception as e:
            logging.error(f"Error in format_financial_summary skill: {e}")
            raise

    def _format(self, data) -> str:
        result = []
        
        # ACCOUNTS section
        if 'accounts' in data:
            accounts = data['accounts']
            if accounts:
                result.append("ACCOUNTS")
                result.append("-" * 20)
                
                # Group accounts by type
                account_groups = {}
                total_balance = 0
                
                for account in accounts:
                    acc_type = account.get('type', 'other').lower()
                    if acc_type not in account_groups:
                        account_groups[acc_type] = []
                    account_groups[acc_type].append(account)
                    total_balance += account.get('balance', 0)
                
                # Display each group
                for acc_type, acc_list in account_groups.items():
                    result.append(f"  {acc_type.upper()}:")
                    for account in acc_list:
                        abbr = account.get('abbr', '')
                        balance = account.get('balance', 0)
                        result.append(f"    {abbr}: ${balance:,.2f}")
                    result.append("")
                
                result.append(f"Total Accounts: ${total_balance:,.2f}")
                result.append("")
        
        # BILLS section
        if 'bills' in data:
            bills = data['bills']
            if bills:
                result.append("BILLS")
                result.append("-" * 20)
                
                total_bills = 0
                
                for bill in bills:
                    merchant = bill.get('merchant_name', 'Unknown')
                    amount = bill.get('expected_amount', 0)
                    day = bill.get('expected_day', 'N/A')
                    total_bills += amount
                    result.append(f"  {merchant} ${amount:,.2f} (day {day})")
                
                result.append("")
                result.append(f"Total Bills: ${total_bills:,.2f}")
                result.append("")
        
        # TRANSACTIONS section
        if 'transactions' in data:
            transactions = data['transactions']
            if transactions:
                result.append("RECENT TRANSACTIONS")
                result.append("-" * 20)
                
                # Take top 5 transactions
                top_transactions = transactions[:5]
                total_transactions = 0
                
                for transaction in top_transactions:
                    amount = transaction.get('amount', 0)
                    desc = transaction.get('description', 'Unknown')
                    date = transaction.get('date', 'N/A')
                    total_transactions += amount
                    result.append(f"  ${amount:,.2f} at {desc} ({date})")
                
                result.append("")
                result.append(f"Total Transactions: ${total_transactions:,.2f}")
                result.append("")
        
        return "\n".join(result)