#!/usr/bin/env python3

"""
SearchDocumentsSkill for Mythos system on Arcturus.
Searches the document registry by title or type.
"""

import os
import logging
import re
from dotenv import load_dotenv
from engine.base import SkillBase, SkillRequest, SkillResponse
import psycopg2
from psycopg2.extras import RealDictCursor

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

class SearchDocumentsSkill(SkillBase):
    name = 'search_documents'
    version = '1.0'
    category = 'data'
    description = 'Search the document registry by title or type'
    triggers = ['document', 'documents', 'doc', 'docs', 'find document', 'find file', 'where is the', 'file called', 'document about', 'scroll', 'find the doc']
    cache_ttl = 600

    async def execute(self, request: SkillRequest) -> SkillResponse:
        pass

    def _extract_search_terms(self, message: str) -> str:
        message = message.lower()
        
        # Define trigger phrases to remove, longest first
        trigger_phrases = [
            'find the doc',
            'find document',
            'document about',
            'file called',
            'where is the',
            'find file',
            'documents',
            'document',
            'scroll',
            'docs',
            'doc',
            'search for',
            'search about',
            'search',
            'find',
            'about'
        ]
        
        # Remove each trigger phrase
        for phrase in trigger_phrases:
            message = message.replace(phrase, '')
        
        # Clean up extra whitespace
        message = ' '.join(message.split())
        
        # Remove punctuation
        message = re.sub(r'[^\w\s]', '', message)
        
        # Return if length is sufficient
        if len(message) >= 2:
            return message
        return ''

    def _detect_doc_type(self, message: str) -> str:
        # Check for doc type keywords
        type_keywords = {
            'markdown': ['markdown', 'md'],
            'pdf': ['pdf'],
            'scroll': ['scroll'],
            'config': ['config'],
            'yaml': ['yaml'],
            'json': ['json']
        }
        
        message = message.lower()
        
        for doc_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    if doc_type == 'markdown' and 'md' in message:
                        return 'markdown'
                    return doc_type
        
        return None

    def _search_docs(self, search_terms: str, doc_type: str = None, limit: int = 15) -> list:
        conn = None
        try:
            conn = _get_conn()
            with conn.cursor() as cursor:
                if doc_type:
                    cursor.execute("""
                        SELECT id, title, doc_type, file_path, created_at, updated_at
                        FROM document_registry
                        WHERE title ILIKE %s AND doc_type = %s
                        ORDER BY title
                        LIMIT %s
                    """, (f'%{search_terms}%', doc_type, limit))
                else:
                    cursor.execute("""
                        SELECT id, title, doc_type, file_path, created_at, updated_at
                        FROM document_registry
                        WHERE title ILIKE %s
                        ORDER BY title
                        LIMIT %s
                    """, (f'%{search_terms}%', limit))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Database error in _search_docs: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def _format_results(self, rows: list) -> list:
        formatted = []
        for row in rows:
            formatted.append({
                'id': row['id'],
                'title': row['title'],
                'doc_type': row['doc_type'],
                'file_path': row['file_path'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })
        return formatted

    def _build_summary(self, results: list, search_terms: str) -> str:
        if not results:
            return f"No documents found matching '{search_terms}'"
        
        count = len(results)
        if count == 1:
            return f"Found 1 document matching '{search_terms}': {results[0]['title']}"
        
        titles = [r['title'] for r in results[:5]]  # Show first 5 titles
        if count > 5:
            return f"Found {count} documents matching '{search_terms}': {', '.join(titles)} and {count - 5} more"
        else:
            return f"Found {count} documents matching '{search_terms}': {', '.join(titles)}"