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
        conn = None
        try:
            conn = _get_conn()
            
            # Get account IDs from request or use default
            account_ids = request.get('account_ids', [])
            if not account_ids:
                # Default to all accounts if none specified
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id FROM accounts")
                    account_ids = [row['id'] for row in cursor.fetchall()]
            
            # Get date range
            start_date = request.get('start_date')
            end_date = request.get('end_date')
            
            # Get category totals and monthly comparison
            category_totals = self._get_category_totals(conn, account_ids, start_date, end_date)
            monthly_comparison = self._get_monthly_comparison(conn, account_ids, start_date, end_date)
            
            # Build summary
            summary = self._build_summary(category_totals, monthly_comparison)
            
            # Return response
            return SkillResponse(
                skill_name=self.name,
                data={
                    'categories': category_totals.get('categories', []),
                    'comparison': monthly_comparison
                },
                summary=summary,
                confidence=0.95,
                sources=['mythos.transactions']
            )
            
        except Exception as e:
            logging.error(f"Error in spending analysis skill: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

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
        try:
            with conn.cursor() as cursor:
                # Get this month total
                this_month_query = """
                SELECT SUM(amount) as total 
                FROM transactions 
                WHERE date_trunc('month', transaction_date) = date_trunc('month', CURRENT_DATE) 
                AND amount < 0
                """
                cursor.execute(this_month_query)
                this_month_result = cursor.fetchone()
                this_month = this_month_result['total'] if this_month_result else 0
                
                # Get last month total
                last_month_query = """
                SELECT SUM(amount) as total 
                FROM transactions 
                WHERE date_trunc('month', transaction_date) = date_trunc('month', CURRENT_DATE - interval '1 month') 
                AND amount < 0
                """
                cursor.execute(last_month_query)
                last_month_result = cursor.fetchone()
                last_month = last_month_result['total'] if last_month_result else 0
                
                # Calculate change percentage
                if last_month != 0:
                    change_pct = ((this_month - last_month) / abs(last_month)) * 100
                else:
                    change_pct = 0
                
                return {
                    'this_month': this_month,
                    'last_month': last_month,
                    'change_pct': change_pct
                }
        finally:
            pass

    def _build_summary(self, category_totals, monthly_comparison):
        # Format grand total
        grand_total = abs(category_totals.get('grand_total', 0))
        total_formatted = f"${grand_total:,.2f}"
        
        # Get number of categories
        categories = category_totals.get('categories', [])
        num_categories = len(categories)
        
        # Build spending summary
        summary = f"Spending last 30 days: {total_formatted} across {num_categories} categories.\n"
        
        # Add top 5 categories
        top_categories = categories[:5]
        if top_categories:
            summary += "Top 5 categories:\n"
            for cat in top_categories:
                category_name = cat.get('category_primary', 'Unknown')
                amount = abs(cat.get('total', 0))
                count = cat.get('count', 0)
                amount_formatted = f"${amount:,.2f}"
                summary += f"  {category_name}: {amount_formatted} ({count} transactions)\n"
        else:
            summary += "No spending categories found.\n"
        
        # Add monthly comparison
        this_month = abs(monthly_comparison.get('this_month', 0))
        last_month = abs(monthly_comparison.get('last_month', 0))
        change_pct = monthly_comparison.get('change_pct', 0)
        
        this_month_formatted = f"${this_month:,.2f}"
        last_month_formatted = f"${last_month:,.2f}"
        
        if change_pct > 0:
            direction = "UP"
        elif change_pct < 0:
            direction = "DOWN"
        else:
            direction = "SAME"
            
        change_pct_abs = abs(change_pct)
        summary += f"This month: {this_month_formatted} vs last month: {last_month_formatted} ({direction} {change_pct_abs:.1f}%)\n"
        
        # Ensure summary is never empty
        if not summary.strip():
            summary = "No spending data available."
            
        return summary