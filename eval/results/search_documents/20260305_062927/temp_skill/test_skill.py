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
        message = request.message
        terms = self._extract_search_terms(message)
        doc_type = self._detect_doc_type(message)
        
        conn = None
        try:
            if not terms and not doc_type:
                # Get total count
                conn = _get_conn()
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) as total FROM document_registry")
                    count = cursor.fetchone()['total']
                    summary = f"Document registry has {count} documents. Search by title or type."
                    return SkillResponse(
                        skill_name=self.name,
                        data={'count': count},
                        summary=summary,
                        confidence=0.95,
                        sources=['mythos.document_registry']
                    )
            else:
                # Perform search
                rows = self._search_docs(terms, doc_type)
                formatted = self._format_results(rows)
                summary = self._build_summary(formatted, terms)
                return SkillResponse(
                    skill_name=self.name,
                    data={'matches': formatted, 'search_terms': terms, 'count': len(formatted)},
                    summary=summary,
                    confidence=0.95,
                    sources=['mythos.document_registry']
                )
        except Exception as e:
            logging.error(f"Error in execute: {e}")
            return SkillResponse(
                skill_name=self.name,
                data={},
                summary=f"Error searching documents: {str(e)}",
                confidence=0.0,
                sources=['mythos.document_registry']
            )
        finally:
            if conn:
                conn.close()

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
                query = "SELECT id, title, doc_type, file_path, created_at, updated_at FROM document_registry WHERE 1=1"
                params = []
                
                if search_terms:
                    query += " AND title ILIKE %s"
                    params.append(f'%{search_terms}%')
                
                if doc_type:
                    query += " AND doc_type = %s"
                    params.append(doc_type)
                
                query += " ORDER BY updated_at DESC NULLS LAST, created_at DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
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
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
            })
        return formatted

    def _build_summary(self, results: list, search_terms: str) -> str:
        if not results:
            if search_terms:
                return f"No documents found matching '{search_terms}'"
            else:
                return "No documents found."
        
        count = len(results)
        if count == 1:
            result = results[0]
            return f"Found 1 document matching '{search_terms}': {result['title']} ({result['doc_type']}, {result['file_path']})"
        
        summary = f"Found {count} documents matching '{search_terms}':"
        for i, result in enumerate(results[:5]):
            summary += f" {result['title']} ({result['doc_type']}, {result['file_path']})"
            if i < len(results[:5]) - 1:
                summary += ","
        return summary