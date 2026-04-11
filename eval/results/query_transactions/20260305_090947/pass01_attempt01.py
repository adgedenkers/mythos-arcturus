#!/usr/bin/env python3

"""
Query Transactions Skill for Mythos System
"""

import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from engine.base import SkillBase, SkillRequest, SkillResponse

load_dotenv()

def _get_conn():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'mythos'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT', '5432'),
        cursor_factory=RealDictCursor
    )
    return conn

class QueryTransactionsSkill(SkillBase):
    name = 'query_transactions'
    version = '1.0'
    category = 'data'
    description = 'Search transactions by description, merchant, date, amount, or account'
    triggers = ['transaction', 'transactions', 'spent', 'spending', 'purchase', 'bought', 'paid', 'payment', 'charge', 'how much did', 'where did I spend', 'recent purchases']
    cache_ttl = 300

    async def execute(self, request) -> SkillResponse:
        # 1. Extract search terms and detect filters (account, date range)
        # 2. If no terms/filters: return recent 10 transactions
        # 3. Query with ILIKE on description/merchant_name + optional filters
        # 4. Format results with amount, merchant, date, account
        # 5. Build summary with total spent
        pass

    def _extract_search_terms(self, message) -> str:
        pass

    def _detect_account(self, message) -> int | None:
        # Check for account abbreviations: SUN, USAA, LLBEAN, TSC, AMEX, etc.
        # Return account_id or None
        pass

    def _query(self, search_terms, account_id=None, limit=15) -> list:
        # ILIKE on description OR merchant_name, optional account filter
        # JOIN accounts for account name
        # ORDER BY transaction_date DESC
        pass

    def _format_results(self, rows) -> list:
        pass

    def _build_summary(self, results, search_terms) -> str:
        # Include total amount spent and count
        pass