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
        pass

    def _detect_days(self, message) -> int:
        # Look for numbers in message, default to 7
        pass

    def _query_bills(self, days_ahead=7) -> list:
        # Get today's day of month, query bills with expected_day between today and today+days
        # LEFT JOIN bill_overrides for current month to check payment status
        pass

    def _format_results(self, rows) -> list:
        pass

    def _build_summary(self, results, days) -> str:
        # 'N bills due in the next X days, totaling $Y: merchant1 $amt (day N), ...'
        pass