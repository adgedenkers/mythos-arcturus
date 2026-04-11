#!/usr/bin/env python3

"""
Search Ideas Skill for Mythos System
"""

import os
import logging
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from engine.base import SkillBase, SkillRequest, SkillResponse

load_dotenv('/opt/mythos/.env')

def _get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor,
    )

class SearchIdeasSkill(SkillBase):
    name = 'search_ideas'
    version = '1.0'
    category = 'data'
    description = 'Search the idea inbox by keyword, domain, or status'
    triggers = ['idea', 'ideas', 'idea inbox', 'backlog', 'thought', 'suggestion', 'brainstorm', 'what ideas', 'pending ideas', 'remember that idea', 'i had an idea']
    cache_ttl = 300

    async def execute(self, request: SkillRequest) -> SkillResponse:
        # 1. Extract search terms
        # 2. Detect filters (domain, disposition)
        # 3. If no terms and no filters: return pending ideas count
        # 4. Search with _search_ideas() using ILIKE on conversation_context and chosen_text
        # 5. Format and summarize
        pass

    def _extract_search_terms(self, message: str) -> str:
        message = message.lower()
        
        # Remove trigger phrases LONGEST FIRST
        trigger_phrases = [
            'remember that idea',
            'i had an idea',
            'pending ideas',
            'idea inbox',
            'what ideas',
            'brainstorm',
            'suggestion',
            'backlog',
            'thought',
            'ideas',
            'idea',
            'search for',
            'search about',
            'search',
            'find',
            'about'
        ]
        
        for phrase in trigger_phrases:
            message = message.replace(phrase, '', 1)
        
        message = ' '.join(message.split())
        
        # Strip punctuation
        import string
        message = message.translate(str.maketrans('', '', string.punctuation))
        
        # Return if length >= 2
        if len(message) >= 2:
            return message.strip()
        else:
            return ''

    def _detect_filters(self, message: str) -> dict:
        message = message.lower()
        
        disposition_words = {
            'pending': 'pending',
            'kept': 'kept',
            'dismissed': 'dismissed',
            'deferred': 'deferred'
        }
        
        domain_words = {
            'technical': 'technical',
            'spiritual': 'spiritual',
            'personal': 'personal',
            'financial': 'financial'
        }
        
        disposition = None
        domain = None
        
        for word, value in disposition_words.items():
            if word in message:
                disposition = value
                break
        
        for word, value in domain_words.items():
            if word in message:
                domain = value
                break
        
        return {'disposition': disposition, 'domain': domain}

    def _search_ideas(self, search_terms: str, disposition: str = None, domain: str = None, limit: int = 15) -> list:
        conn = _get_conn()
        try:
            with conn.cursor() as cursor:
                query = "SELECT id, conversation_context, items, item_count, chosen_text, disposition, domain, tags, created_at FROM idea_inbox WHERE 1=1"
                params = []
                
                if search_terms:
                    query += " AND (conversation_context ILIKE %s OR chosen_text ILIKE %s)"
                    params.append(f'%{search_terms}%')
                    params.append(f'%{search_terms}%')
                
                if disposition:
                    query += " AND disposition = %s"
                    params.append(disposition)
                
                if domain:
                    query += " AND domain = %s"
                    params.append(domain)
                
                query += " ORDER BY created_at DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        finally:
            conn.close()

    def _format_results(self, rows: list) -> list:
        pass

    def _build_summary(self, results: list, search_terms: str) -> str:
        pass