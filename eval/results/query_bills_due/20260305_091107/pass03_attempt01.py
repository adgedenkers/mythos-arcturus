#!/usr/bin/env python3

"""
Query Bills Due Skill
=====================

This skill queries upcoming bills due in the next N days.
"""

import os
import logging
import re
from datetime import date, timedelta, datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from engine.base import SkillBase, SkillRequest, SkillResponse

load_dotenv()

def _get_conn():
    """Get database connection."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'mythos'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', '5432'),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        if conn:
            conn.close()
        raise e

class QueryBillsDueSkill(SkillBase):
    name = 'query_bills_due'
    version = '1.0'
    category = 'data'
    description = 'Show upcoming bills due in the next N days'
    triggers = ['bill', 'bills', 'due', 'bills due', 'upcoming bills', 'what do I owe', 'payments coming', 'when is the next bill']
    cache_ttl = 300

    async def execute(self, request) -> SkillResponse:
        # 1. Determine lookahead days (default 7, detect from message)
        # 2. Query bills due between today's day-of-month and today+N
        # 3. Check overrides to see which are already paid
        # 4. Format and summarize
        message = request.message.lower()
        days = self._detect_days(message)
        rows = self._query_bills(days_ahead=days)
        results = self._format_results(rows)
        summary = self._build_summary(results, days)
        return SkillResponse(text=summary)

    def _detect_days(self, message) -> int:
        # Look for numbers in message, default to 7
        # Check for keywords: 'week' = 7, 'month' = 30, 'today' = 1, 'tomorrow' = 2
        message = message.lower()
        
        # Check for keywords first
        if 'week' in message:
            return 7
        elif 'month' in message:
            return 30
        elif 'today' in message:
            return 1
        elif 'tomorrow' in message:
            return 2
            
        # Look for numbers
        match = re.search(r'(\d+)\s*days?', message)
        if match:
            days = int(match.group(1))
            return min(days, 31)  # Cap at 31 days
            
        return 7  # Default to 7 days

    def _query_bills(self, days_ahead=7) -> list:
        # Get today's day of month, query bills with expected_day between today and today+days
        # LEFT JOIN bill_overrides for current month to check payment status
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor() as cur:
                today = date.today()
                month_str = today.strftime('%Y-%m')
                dom = today.day
                
                # Calculate end day of month
                end_dom = dom + days_ahead
                
                # Query bills due in the next N days
                query = """
                SELECT rb.id, rb.merchant_name, rb.expected_amount, rb.expected_day, rb.category_primary,
                       COALESCE(bo.is_paid, false) as is_paid
                FROM recurring_bills rb
                LEFT JOIN bill_overrides bo ON bo.bill_id = rb.id AND bo.month = %s
                WHERE rb.is_active = true
                  AND rb.expected_day IS NOT NULL
                  AND rb.expected_day >= %s AND rb.expected_day <= %s
                  AND COALESCE(bo.is_paid, false) = false
                ORDER BY rb.expected_day
                """
                
                # Handle month wraparound
                if end_dom > 31:
                    # Query for the remaining days in current month
                    cur.execute(query, (month_str, dom, 31))
                    rows1 = cur.fetchall()
                    
                    # Query for days in next month
                    next_month = today.replace(day=1) + timedelta(days=32)
                    next_month_str = next_month.strftime('%Y-%m')
                    days_in_next_month = end_dom - 31
                    
                    cur.execute(query, (next_month_str, 1, days_in_next_month))
                    rows2 = cur.fetchall()
                    
                    # Combine results
                    rows = rows1 + rows2
                else:
                    # Simple case - all days in same month
                    cur.execute(query, (month_str, dom, end_dom))
                    rows = cur.fetchall()
                    
                return rows
        except Exception as e:
            logging.error(f"Error querying bills: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _format_results(self, rows) -> list:
        results = []
        for row in rows:
            results.append({
                'id': row['id'],
                'merchant_name': row['merchant_name'],
                'expected_amount': float(row['expected_amount']),
                'expected_day': row['expected_day'],
                'category_primary': row['category_primary'],
                'is_paid': row['is_paid']
            })
        return results

    def _build_summary(self, results, days) -> str:
        # 'N bills due in the next X days, totaling $Y: merchant1 $amt (day N), ...'
        if not results:
            return "No bills due in the next {} days.".format(days)
            
        total_amount = sum(item['expected_amount'] for item in results)
        bill_count = len(results)
        
        # Format the list of bills
        bill_details = []
        for item in results:
            if not item['is_paid']:
                bill_details.append("{} ${:.2f} (day {})".format(
                    item['merchant_name'], 
                    item['expected_amount'], 
                    item['expected_day']
                ))
        
        if not bill_details:
            return "All bills for the next {} days are already paid.".format(days)
            
        summary = "{} bills due in the next {} days, totaling ${:.2f}: {}".format(
            bill_count,
            days,
            total_amount,
            ", ".join(bill_details)
        )
        
        return summary