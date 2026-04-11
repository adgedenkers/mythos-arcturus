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
        pass

    def _build_summary(self, category_totals: dict, monthly_comparison: dict) -> str:
        pass