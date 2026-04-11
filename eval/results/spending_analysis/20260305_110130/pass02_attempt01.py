import os
import logging
from datetime import date, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from engine.base import SkillBase, SkillRequest, SkillResponse

load_dotenv()

def _get_conn():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'mythos'),
        user=os.getenv('DB_USER', 'mythos_user'),
        password=os.getenv('DB_PASSWORD', 'mythos_password'),
        port=os.getenv('DB_PORT', '5432'),
        cursor_factory=RealDictCursor
    )
    return conn

class SpendingAnalysisSkill(SkillBase):
    name = 'spending_analysis'
    triggers = [
        'spending', 'spending analysis', 'category breakdown',
        'where is my money going', 'spending trends', 'how much am i spending',
        'budget', 'expenses', 'monthly spending'
    ]
    cache_ttl = 600

    async def execute(self, request: SkillRequest) -> SkillResponse:
        pass

    def _get_category_totals(self, conn, account_ids, start_date, end_date):
        try:
            with conn.cursor() as cursor:
                # Get category totals
                query = """
                SELECT category_primary, SUM(amount) as total, COUNT(*) as count 
                FROM transactions 
                WHERE transaction_date >= CURRENT_DATE - %s 
                AND amount < 0 
                GROUP BY category_primary 
                ORDER BY total ASC
                """
                cursor.execute(query, (30,))
                categories = cursor.fetchall()
                
                # Get grand total
                grand_total_query = """
                SELECT SUM(amount) as grand_total 
                FROM transactions 
                WHERE transaction_date >= CURRENT_DATE - %s 
                AND amount < 0
                """
                cursor.execute(grand_total_query, (30,))
                grand_total_result = cursor.fetchone()
                grand_total = grand_total_result['grand_total'] if grand_total_result else 0
                
                return {
                    'categories': categories,
                    'grand_total': grand_total
                }
        finally:
            pass

    def _get_monthly_comparison(self, conn, account_ids, start_date, end_date):
        pass

    def _build_summary(self, category_totals, monthly_comparison):
        pass