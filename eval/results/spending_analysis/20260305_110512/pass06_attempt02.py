import os
import logging
import datetime
from datetime import date, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from engine.base import SkillBase, SkillRequest, SkillResponse

class SpendingAnalysisSkill(SkillBase):
    name = 'spending_analysis'
    triggers = ['spending', 'spending analysis', 'category breakdown', 'where is my money going', 'spending trends', 'how much am i spending', 'budget', 'expenses', 'monthly spending']
    cache_ttl = 600

    async def execute(self, request: SkillRequest) -> SkillResponse:
        try:
            account_id = request.account_id  # Assuming account_id is passed in the request
            cat_data = self._get_category_totals(account_id, 30)
            comp_data = self._get_monthly_comparison(account_id, 2)
            summary = self._build_summary(cat_data, comp_data)
            return SkillResponse(skill_name=self.name, data={'categories': cat_data, 'comparison': comp_data}, summary=summary, confidence=0.95, sources=['mythos.transactions'])
        except Exception as e:
            logging.exception(f"Error executing skill: {e}")
            return SkillResponse(skill_name=self.name, data={'categories': []}, summary="An error occurred while processing your request.", confidence=0.0, sources=['system'])
        finally:
            pass

    def _get_conn(self):
        load_dotenv()
        host = os.getenv("POSTGRES_HOST")
        conn = psycopg2.connect(host=host, database="mythos", user=os.getenv("POSTGRES_USER"), password=os.getenv("POSTGRES_PASSWORD"))
        return conn

    def _get_category_totals(self, account_id: int, days: int) -> dict:
        conn = None
        try:
            conn = self._get_conn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT category_primary, SUM(amount) as total, COUNT(*) as count FROM transactions WHERE transaction_date >= CURRENT_DATE - %s AND account_id = %s AND amount < 0 GROUP BY category_primary ORDER BY total ASC", (days, account_id))
            categories = cur.fetchall()
            cur.execute("SELECT SUM(amount) as grand_total FROM transactions WHERE transaction_date >= CURRENT_DATE - %s AND account_id = %s AND amount < 0", (days, account_id))
            grand_total_result = cur.fetchone()
            grand_total = abs(grand_total_result['grand_total']) if grand_total_result else 0
            return {'categories': categories, 'grand_total': grand_total}
        except Exception as e:
            logging.exception(f"Error getting category totals: {e}")
            return {'categories': [], 'grand_total': 0}
        finally:
            if conn:
                conn.close()

    def _get_monthly_comparison(self, account_id: int, months: int) -> dict:
        conn = None
        try:
            conn = self._get_conn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT SUM(amount) as total FROM transactions WHERE date_trunc('month', transaction_date) = date_trunc('month', CURRENT_DATE) AND account_id = %s AND amount < 0", (account_id,))
            this_month_result = cur.fetchone()
            this_month = abs(this_month_result['total']) if this_month_result else 0

            cur.execute("SELECT SUM(amount) as total FROM transactions WHERE date_trunc('month', transaction_date) = date_trunc('month', CURRENT_DATE - interval '1 month') AND account_id = %s AND amount < 0", (account_id,))
            last_month_result = cur.fetchone()
            last_month = abs(last_month_result['total']) if last_month_result else 0

            if last_month != 0:
                change_pct = ((this_month - last_month) / abs(last_month)) * 100
            else:
                change_pct = 0

            return {'this_month': this_month, 'last_month': last_month, 'change_pct': change_pct}
        except Exception as e:
            logging.exception(f"Error getting monthly comparison: {e}")
            return {'this_month': 0, 'last_month': 0, 'change_pct': 0}
        finally:
            if conn:
                conn.close()

    def _build_summary(self, category_totals: dict, monthly_comparison: dict) -> str:
        categories = category_totals['categories']
        grand_total = abs(category_totals['grand_total'])
        num_categories = len(categories)

        if num_categories == 0:
            summary = "No spending data found for the last 30 days."
        else:
            summary = f"Spending last 30 days: ${grand_total:,.2f} across {num_categories} categories.\n"

            for i, category in enumerate(categories[:5]):
                amount = abs(category['total'])
                count = category['count']
                summary += f"{category['category_primary']}: ${amount:,.2f} ({count} transactions)\n"

            this_month = abs(monthly_comparison['this_month'])
            last_month = abs(monthly_comparison['last_month'])
            change_pct = monthly_comparison['change_pct']

            if change_pct > 0:
                trend = "UP"
            elif change_pct < 0:
                trend = "DOWN"
            else:
                trend = "EVEN"

            summary += f"This month: ${this_month:,.2f} vs last month: ${last_month:,.2f} ({trend} {change_pct:.2f}%)."

        return summary