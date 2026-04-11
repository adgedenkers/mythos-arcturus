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
        pass

    def _get_category_totals(self, account_id: int, days: int) -> dict:
        conn = None
        try:
            conn = self._get_conn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT category_primary, SUM(amount) as total, COUNT(*) as count FROM transactions WHERE transaction_date >= CURRENT_DATE - %s AND amount < 0 GROUP BY category_primary ORDER BY total ASC", (days,))
            categories = cur.fetchall()
            cur.execute("SELECT SUM(amount) as grand_total FROM transactions WHERE transaction_date >= CURRENT_DATE - %s AND amount < 0", (days,))
            grand_total_result = cur.fetchone()
            grand_total = grand_total_result['grand_total'] if grand_total_result else 0
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
            cur.execute("SELECT SUM(amount) as total FROM transactions WHERE date_trunc('month', transaction_date) = date_trunc('month', CURRENT_DATE) AND amount < 0")
            this_month_result = cur.fetchone()
            this_month = this_month_result['total'] if this_month_result else 0

            cur.execute("SELECT SUM(amount) as total FROM transactions WHERE date_trunc('month', transaction_date) = date_trunc('month', CURRENT_DATE - interval '1 month') AND amount < 0")
            last_month_result = cur.fetchone()
            last_month = last_month_result['total'] if last_month_result else 0

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