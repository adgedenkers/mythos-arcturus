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
        message = message.lower().strip()
        
        # Remove triggers LONGEST FIRST
        triggers = [
            'where did i spend',
            'recent purchases',
            'how much did',
            'transactions',
            'transaction',
            'spending',
            'purchase',
            'payment',
            'bought',
            'spent',
            'charge',
            'paid',
            'search for',
            'search about',
            'search',
            'find',
            'about',
            'what',
            'when',
            'any',
            'the'
        ]
        
        for trigger in triggers:
            message = message.replace(trigger, '')
        
        # Normalize whitespace
        words = message.split()
        words = [word for word in words if len(word) >= 2]
        
        # Strip punctuation and rebuild
        import string
        cleaned_words = []
        for word in words:
            cleaned_word = word.translate(str.maketrans('', '', string.punctuation))
            if len(cleaned_word) >= 2:
                cleaned_words.append(cleaned_word)
        
        return ' '.join(cleaned_words)

    def _detect_account(self, message) -> int | None:
        # Check for account abbreviations (case-insensitive)
        abbreviations = {
            'sun': 1,
            'usaa': 2,
            'sid': 3,
            'nbt': 5,
            'llbean': 6,
            'tsc': 7,
            'oldnavy': 8,
            'tjx': 9,
            'amex': 10,
            'usaaloan': 11
        }
        
        message = message.lower()
        for abbrev, account_id in abbreviations.items():
            if abbrev in message:
                return account_id
        return None

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