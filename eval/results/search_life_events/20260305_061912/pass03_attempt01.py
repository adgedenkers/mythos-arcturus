#!/usr/bin/env python3
"""
Search Life Events Skill for Mythos System
"""

import os
import logging
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

class SearchLifeEventsSkill(SkillBase):
    name = 'search_life_events'
    version = '1.0'
    category = 'data'
    description = 'Search life events by keyword, domain, or person'
    triggers = ['life event', 'life events', 'what happened', 'event', 'events', 'remember when', 'happened', 'occurred', 'milestone', 'log entry', 'logged']
    cache_ttl = 300

    async def execute(self, request: SkillRequest) -> SkillResponse:
        # 1. Extract search terms using _extract_search_terms()
        # 2. Detect if a domain or person filter is mentioned
        # 3. If no terms and no filters: return total event count
        # 4. Search using _search_events() with ILIKE + optional filters
        # 5. Format with _format_results(), summarize with _build_summary()
        # 6. Return SkillResponse
        pass

    def _extract_search_terms(self, message: str) -> str:
        # Remove trigger phrases (longest first), normalize whitespace between each
        message = message.lower()
        trigger_phrases = [
            'remember when',
            'what happened',
            'life events',
            'life event',
            'log entry',
            'milestone',
            'occurred',
            'happened',
            'events',
            'event',
            'logged',
            'search for',
            'search about',
            'search',
            'find',
            'about'
        ]
        for phrase in sorted(trigger_phrases, key=len, reverse=True):
            message = message.replace(phrase, '')
        message = ' '.join(message.split())
        # Strip punctuation
        import string
        message = message.translate(str.maketrans('', '', string.punctuation))
        if len(message) >= 2:
            return message
        return ''

    def _detect_filters(self, message: str) -> dict:
        # Check if message mentions a domain (personal, spiritual, technical, financial)
        # Check if message mentions a person (adge, rebecca, seraphe, fitz)
        # Return {'domain': str|None, 'person': str|None}
        message = message.lower()
        domain = None
        person = None

        domains = ['personal', 'spiritual', 'technical', 'financial']
        for d in domains:
            if d in message:
                domain = d
                break

        persons = {
            'adge': 'adge',
            'rebecca': 'rebecca',
            'seraphe': 'rebecca',  # Map to database value
            'fitz': 'fitz'
        }
        for key, value in persons.items():
            if key in message:
                person = value
                break

        return {'domain': domain, 'person': person}

    def _search_events(self, search_terms: str, domain: str = None, person: str = None, limit: int = 15) -> list:
        # ILIKE search on description, optional WHERE domain = %s, optional WHERE person = %s
        # ORDER BY created_at DESC LIMIT %s
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor() as cur:
                query = """
                    SELECT id, description, domain, person, mood, created_at
                    FROM life_events
                    WHERE 1=1
                """
                params = []

                if search_terms:
                    query += " AND description ILIKE %s"
                    params.append(f'%{search_terms}%')

                if domain:
                    query += " AND domain = %s"
                    params.append(domain)

                if person:
                    query += " AND person = %s"
                    params.append(person)

                query += " ORDER BY created_at DESC LIMIT %s"
                params.append(limit)

                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            logging.error(f"Database error in _search_events: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def _format_results(self, rows: list) -> list:
        # Clean dicts: id, description (truncated 200 chars), domain, person, mood, created_at
        formatted = []
        for row in rows:
            desc = row['description'][:200] + '...' if len(row['description']) > 200 else row['description']
            formatted.append({
                'id': row['id'],
                'description': desc,
                'domain': row['domain'],
                'person': row['person'],
                'mood': row['mood'],
                'created_at': row['created_at']
            })
        return formatted

    def _build_summary(self, results: list, search_terms: str) -> str:
        # 'Found N life event(s) matching X: description1 (domain, date), ...'
        count = len(results)
        if count == 0:
            return f"No life events found matching '{search_terms}'."

        if count == 1:
            event = results[0]
            return f"Found 1 life event matching '{search_terms}': {event['description']} ({event['domain']}, {event['created_at'].strftime('%Y-%m-%d')})"

        descriptions = []
        for event in results[:5]:  # Show up to 5
            desc = event['description'][:50] + '...' if len(event['description']) > 50 else event['description']
            date_str = event['created_at'].strftime('%Y-%m-%d')
            descriptions.append(f"{desc} ({event['domain']}, {date_str})")

        summary = f"Found {count} life event(s) matching '{search_terms}': "
        summary += ', '.join(descriptions)
        if count > 5:
            summary += f" ... and {count - 5} more."
        return summary