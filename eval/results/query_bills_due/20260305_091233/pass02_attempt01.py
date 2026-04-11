#!/usr/bin/env python3

"""
Query Bills Due Skill
=====================

This skill queries upcoming bills due in the next N days.
It uses the Mythos database to retrieve bill information and
checks for overrides to determine payment status.
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
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'mythos'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', '5432'),
        cursor_factory=RealDictCursor
    )
    return conn

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
        bills = self._query_bills(days_ahead=days)
        results = self._format_results(bills)
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
            cur = conn.cursor()
            
            today = date.today()
            end_date = today + timedelta(days=days_ahead)
            
            # Get the current month as 'YYYY-MM'
            current_month = today.strftime('%Y-%m')
            
            # Query bills due in the next N days
            query = """
                SELECT 
                    rb.id,
                    rb.merchant_name,
                    rb.expected_amount,
                    rb.expected_day,
                    COALESCE(bo.is_paid, false) as is_paid
                FROM recurring_bills rb
                LEFT JOIN bill_overrides bo 
                    ON rb.id = bo.bill_id 
                    AND bo.month = %s
                WHERE rb.is_active = true
                    AND rb.expected_day >= %s
                    AND rb.expected_day <= %s
                ORDER BY rb.expected_day
            """
            
            # Calculate the range of expected days to check
            start_day = today.day
            end_day = end_date.day
            
            # If the range spans across months, we need to handle that
            if end_date.month != today.month:
                # Query for current month
                cur.execute(query, (current_month, start_day, 31))
                bills_current = cur.fetchall()
                
                # Query for next month
                next_month = today.replace(day=1) + timedelta(days=32)
                next_month_str = next_month.strftime('%Y-%m')
                cur.execute(query, (next_month_str, 1, end_day))
                bills_next = cur.fetchall()
                
                # Combine results
                bills = bills_current + bills_next
            else:
                # Same month
                cur.execute(query, (current_month, start_day, end_day))
                bills = cur.fetchall()
                
            return bills
            
        except Exception as e:
            logging.error(f"Error querying bills: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def _format_results(self, rows) -> list:
        formatted = []
        for row in rows:
            formatted.append({
                'id': row['id'],
                'merchant_name': row['merchant_name'],
                'expected_amount': float(row['expected_amount']),
                'expected_day': row['expected_day'],
                'is_paid': row['is_paid']
            })
        return formatted

    def _build_summary(self, results, days) -> str:
        # 'N bills due in the next X days, totaling $Y: merchant1 $amt (day N), ...'
        if not results:
            return "No bills due in the next {} days.".format(days)
            
        total_bills = len(results)
        total_amount = sum(item['expected_amount'] for item in results)
        
        # Separate paid and unpaid bills
        unpaid_bills = [item for item in results if not item['is_paid']]
        paid_bills = [item for item in results if item['is_paid']]
        
        if not unpaid_bills:
            return "All {} bills due in the next {} days are paid.".format(total_bills, days)
            
        summary_parts = []
        summary_parts.append("{} bills due in the next {} days, totaling ${:.2f}".format(
            len(unpaid_bills), days, total_amount))
            
        if unpaid_bills:
            unpaid_details = []
            for bill in unpaid_bills:
                unpaid_details.append("{} ${:.2f} (day {})".format(
                    bill['merchant_name'], bill['expected_amount'], bill['expected_day']))
            summary_parts.append(": ".join(unpaid_details))
            
        return ", ".join(summary_parts)