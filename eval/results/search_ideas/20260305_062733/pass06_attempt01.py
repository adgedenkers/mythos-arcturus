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
        try:
            message = request.message
            terms = self._extract_search_terms(message)
            filters = self._detect_filters(message)
            
            # If no search terms and no filters, return count of pending ideas
            if not terms and not any(filters.values()):
                conn = _get_conn()
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT COUNT(*) as total FROM idea_inbox WHERE disposition = 'pending'")
                        count = cursor.fetchone()['total']
                        summary = f'You have {count} pending ideas in the inbox.'
                        return SkillResponse(
                            skill_name=self.name,
                            data={'count': count},
                            summary=summary,
                            confidence=0.95,
                            sources=['mythos.idea_inbox']
                        )
                finally:
                    conn.close()
            
            # Search with terms and/or filters
            rows = self._search_ideas(
                search_terms=terms,
                disposition=filters['disposition'],
                domain=filters['domain']
            )
            
            formatted = self._format_results(rows)
            summary = self._build_summary(formatted, terms)
            
            return SkillResponse(
                skill_name=self.name,
                data={
                    'matches': formatted,
                    'search_terms': terms,
                    'count': len(formatted),
                    'filters': filters
                },
                summary=summary,
                confidence=0.95,
                sources=['mythos.idea_inbox']
            )
        except Exception as e:
            logging.error(f"Error in SearchIdeasSkill.execute: {e}")
            raise
        finally:
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
        formatted = []
        for row in rows:
            context = row['conversation_context']
            if context and len(context) > 200:
                context = context[:197] + '...'
            
            formatted.append({
                'id': str(row['id']),
                'context': context,
                'chosen_text': row['chosen_text'],
                'items': row['items'],
                'item_count': row['item_count'],
                'disposition': row['disposition'],
                'domain': row['domain'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None
            })
        return formatted

    def _build_summary(self, results: list, search_terms: str) -> str:
        if not results:
            if search_terms:
                return f'No ideas found matching "{search_terms}".'
            else:
                return 'No ideas found.'
        
        if not search_terms:
            return 'Search results returned.'
        
        return f'Found {len(results)} ideas matching "{search_terms}".'