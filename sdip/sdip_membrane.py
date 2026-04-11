"""
SDIP Access Membrane — FastAPI Routes
Provides sensitivity-aware document and chunk access.

Endpoints:
    GET  /api/sdip/stats          — overall SDIP statistics
    GET  /api/sdip/documents      — list/search documents
    GET  /api/sdip/documents/{id} — document detail with chunks
    GET  /api/sdip/chunks/search  — search chunks by content
    GET  /api/sdip/sensitivity    — sensitivity report
    GET  /api/sdip/topics         — topic list with doc counts
    POST /api/sdip/query          — natural language document query
"""

import os
import sys
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

sys.path.insert(0, '/opt/mythos/sdip')
from config import get_db_connection

router = APIRouter(prefix="/api/sdip", tags=["sdip"])


# ── Models ─────────────────────────────────────────────────────

class DocumentSummary(BaseModel):
    id: int
    relative_path: str
    filename: str
    file_format: Optional[str] = None
    category: Optional[str] = None
    quality: Optional[str] = None
    status: str = 'active'
    chunk_count: int = 0
    word_count: int = 0
    max_sensitivity: str = 'PUBLIC'

class ChunkResult(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    parent_heading: Optional[str] = None
    content_text: str
    word_count: int
    sensitivity_level: str = 'PUBLIC'
    sensitivity_tags: list[str] = []
    document_path: Optional[str] = None

class SensitivityFinding(BaseModel):
    id: int
    chunk_id: int
    sensitivity_type: str
    detection_method: str
    detected_pattern: Optional[str] = None
    confidence: float = 1.0
    document_path: Optional[str] = None


# ── Redaction ──────────────────────────────────────────────────

# Clearance levels — what each requester role can see
CLEARANCE_LEVELS = {
    'public': ['PUBLIC'],
    'internal': ['PUBLIC', 'INTERNAL'],
    'sensitive': ['PUBLIC', 'INTERNAL', 'SENSITIVE'],
    'admin': ['PUBLIC', 'INTERNAL', 'SENSITIVE', 'RESTRICTED'],
}

def get_allowed_levels(clearance: str = 'admin') -> list[str]:
    """Get allowed sensitivity levels for a clearance."""
    return CLEARANCE_LEVELS.get(clearance, CLEARANCE_LEVELS['public'])


def redact_content(text: str, sensitivity_level: str, clearance: str) -> str:
    """Apply redaction based on sensitivity and clearance."""
    allowed = get_allowed_levels(clearance)
    if sensitivity_level in allowed:
        return text

    # Redact based on mode
    if sensitivity_level == 'RESTRICTED':
        return '[REDACTED — RESTRICTED ACCESS REQUIRED]'
    elif sensitivity_level == 'SENSITIVE':
        # Return first sentence as preview
        first_sentence = text.split('.')[0] + '...' if '.' in text else text[:100] + '...'
        return f'[PREVIEW] {first_sentence} [SENSITIVE — ELEVATED ACCESS REQUIRED]'
    else:
        return f'[FILTERED — {sensitivity_level} ACCESS REQUIRED]'


# ── Endpoints ──────────────────────────────────────────────────

@router.get("/stats")
async def get_stats():
    """Overall SDIP database statistics."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM sdip_sources")
            sources = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM sdip_documents")
            docs = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM sdip_chunks")
            chunks = cur.fetchone()[0]

            cur.execute("SELECT COALESCE(SUM(word_count), 0) FROM sdip_chunks")
            words = cur.fetchone()[0]

            cur.execute("""
                SELECT sensitivity_level, COUNT(*) 
                FROM sdip_chunks 
                GROUP BY sensitivity_level
                ORDER BY CASE sensitivity_level
                    WHEN 'PUBLIC' THEN 0 WHEN 'INTERNAL' THEN 1
                    WHEN 'SENSITIVE' THEN 2 WHEN 'RESTRICTED' THEN 3
                END
            """)
            sensitivity = {row[0]: row[1] for row in cur.fetchall()}

            cur.execute("""
                SELECT file_format, COUNT(*) 
                FROM sdip_documents 
                GROUP BY file_format 
                ORDER BY COUNT(*) DESC
            """)
            formats = {row[0]: row[1] for row in cur.fetchall()}

            cur.execute("SELECT COUNT(*) FROM sdip_sensitivity")
            findings = cur.fetchone()[0]

        return {
            "sources": sources,
            "documents": docs,
            "chunks": chunks,
            "total_words": words,
            "sensitivity_findings": findings,
            "sensitivity_distribution": sensitivity,
            "format_distribution": formats,
        }
    finally:
        conn.close()


@router.get("/documents")
async def list_documents(
    search: Optional[str] = Query(None, description="Search in filename/path"),
    category: Optional[str] = Query(None, description="Filter by category"),
    format: Optional[str] = Query(None, description="Filter by file format"),
    sensitivity: Optional[str] = Query(None, description="Filter by max sensitivity level"),
    status: str = Query('active', description="Document status filter"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    clearance: str = Query('admin', description="Requester clearance level"),
):
    """List and search documents."""
    conn = get_db_connection()
    try:
        conditions = ["d.status = %s"]
        params = [status]

        if search:
            conditions.append("(d.relative_path ILIKE %s OR d.filename ILIKE %s)")
            params.extend([f'%{search}%', f'%{search}%'])

        if category:
            conditions.append("d.category = %s")
            params.append(category)

        if format:
            conditions.append("d.file_format = %s")
            params.append(format)

        where = " AND ".join(conditions)

        with conn.cursor() as cur:
            # Get total count
            cur.execute(f"SELECT COUNT(*) FROM sdip_documents d WHERE {where}", params)
            total = cur.fetchone()[0]

            # Get documents with chunk stats
            cur.execute(f"""
                SELECT d.id, d.relative_path, d.filename, d.file_format,
                       d.category, d.quality, d.status,
                       COALESCE(cs.chunk_count, 0),
                       COALESCE(cs.total_words, 0),
                       COALESCE(cs.max_sens, 'PUBLIC')
                FROM sdip_documents d
                LEFT JOIN (
                    SELECT document_id,
                           COUNT(*) as chunk_count,
                           SUM(word_count) as total_words,
                           MAX(CASE sensitivity_level
                               WHEN 'RESTRICTED' THEN 4 WHEN 'SENSITIVE' THEN 3
                               WHEN 'INTERNAL' THEN 2 ELSE 1
                           END) as sens_ord,
                           MAX(sensitivity_level) as max_sens
                    FROM sdip_chunks GROUP BY document_id
                ) cs ON cs.document_id = d.id
                WHERE {where}
                ORDER BY d.relative_path
                LIMIT %s OFFSET %s
            """, params + [limit, offset])

            docs = []
            allowed = get_allowed_levels(clearance)
            for row in cur.fetchall():
                max_sens = row[9]
                # Filter by sensitivity if requested
                if sensitivity and max_sens != sensitivity:
                    continue

                docs.append({
                    "id": row[0],
                    "relative_path": row[1],
                    "filename": row[2],
                    "file_format": row[3],
                    "category": row[4],
                    "quality": row[5],
                    "status": row[6],
                    "chunk_count": row[7],
                    "word_count": row[8],
                    "max_sensitivity": max_sens,
                    "accessible": max_sens in allowed,
                })

        return {"total": total, "documents": docs, "limit": limit, "offset": offset}
    finally:
        conn.close()


@router.get("/documents/{doc_id}")
async def get_document(
    doc_id: int,
    clearance: str = Query('admin', description="Requester clearance level"),
):
    """Get document detail with all chunks (sensitivity-filtered)."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Document info
            cur.execute("""
                SELECT id, relative_path, filename, file_format,
                       category, subcategory, quality, summary, status,
                       content_hash, file_size, last_modified
                FROM sdip_documents WHERE id = %s
            """, (doc_id,))
            doc = cur.fetchone()
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found")

            # Chunks
            cur.execute("""
                SELECT id, chunk_index, parent_heading, content_text,
                       word_count, sensitivity_level, sensitivity_tags
                FROM sdip_chunks
                WHERE document_id = %s
                ORDER BY chunk_index
            """, (doc_id,))

            allowed = get_allowed_levels(clearance)
            chunks = []
            for row in cur.fetchall():
                level = row[5]
                content = row[3] if level in allowed else redact_content(row[3], level, clearance)
                chunks.append({
                    "id": row[0],
                    "chunk_index": row[1],
                    "parent_heading": row[2],
                    "content_text": content,
                    "word_count": row[4],
                    "sensitivity_level": level,
                    "sensitivity_tags": row[6] or [],
                    "redacted": level not in allowed,
                })

            # Sensitivity findings for this doc
            cur.execute("""
                SELECT s.id, s.chunk_id, s.sensitivity_type,
                       s.detection_method, s.detected_pattern, s.confidence
                FROM sdip_sensitivity s
                JOIN sdip_chunks c ON c.id = s.chunk_id
                WHERE c.document_id = %s
                ORDER BY s.id
            """, (doc_id,))
            findings = [{
                "id": r[0], "chunk_id": r[1], "type": r[2],
                "method": r[3], "pattern": r[4], "confidence": r[5],
            } for r in cur.fetchall()]

        return {
            "document": {
                "id": doc[0], "relative_path": doc[1], "filename": doc[2],
                "file_format": doc[3], "category": doc[4], "subcategory": doc[5],
                "quality": doc[6], "summary": doc[7], "status": doc[8],
                "content_hash": doc[9], "file_size": doc[10],
                "last_modified": doc[11].isoformat() if doc[11] else None,
            },
            "chunks": chunks,
            "findings": findings,
            "chunk_count": len(chunks),
            "word_count": sum(c["word_count"] for c in chunks),
        }
    finally:
        conn.close()


@router.get("/chunks/search")
async def search_chunks(
    q: str = Query(..., description="Search query"),
    sensitivity: Optional[str] = Query(None, description="Filter by sensitivity level"),
    limit: int = Query(20, ge=1, le=100),
    clearance: str = Query('admin', description="Requester clearance level"),
):
    """Search chunks by content (full text search)."""
    conn = get_db_connection()
    try:
        allowed = get_allowed_levels(clearance)

        with conn.cursor() as cur:
            conditions = ["c.content_text ILIKE %s"]
            params = [f'%{q}%']

            if sensitivity:
                conditions.append("c.sensitivity_level = %s")
                params.append(sensitivity)

            where = " AND ".join(conditions)

            cur.execute(f"""
                SELECT c.id, c.document_id, c.chunk_index, c.parent_heading,
                       c.content_text, c.word_count, c.sensitivity_level,
                       c.sensitivity_tags, d.relative_path
                FROM sdip_chunks c
                JOIN sdip_documents d ON d.id = c.document_id
                WHERE {where}
                ORDER BY c.document_id, c.chunk_index
                LIMIT %s
            """, params + [limit])

            results = []
            for row in cur.fetchall():
                level = row[6]
                content = row[4] if level in allowed else redact_content(row[4], level, clearance)
                results.append({
                    "id": row[0],
                    "document_id": row[1],
                    "chunk_index": row[2],
                    "parent_heading": row[3],
                    "content_text": content,
                    "word_count": row[5],
                    "sensitivity_level": level,
                    "sensitivity_tags": row[7] or [],
                    "document_path": row[8],
                    "redacted": level not in allowed,
                })

        return {"query": q, "results": results, "count": len(results)}
    finally:
        conn.close()


@router.get("/sensitivity")
async def sensitivity_report(
    level: Optional[str] = Query(None, description="Filter by level"),
    type: Optional[str] = Query(None, description="Filter by sensitivity type"),
    limit: int = Query(50, ge=1, le=200),
):
    """Sensitivity findings report."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            conditions = []
            params = []

            if level:
                conditions.append("c.sensitivity_level = %s")
                params.append(level)
            if type:
                conditions.append("s.sensitivity_type = %s")
                params.append(type)

            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

            cur.execute(f"""
                SELECT s.id, s.chunk_id, s.sensitivity_type, s.detection_method,
                       s.detected_pattern, s.confidence, s.reviewed_by,
                       c.sensitivity_level, d.relative_path, c.chunk_index
                FROM sdip_sensitivity s
                JOIN sdip_chunks c ON c.id = s.chunk_id
                JOIN sdip_documents d ON d.id = c.document_id
                {where}
                ORDER BY
                    CASE c.sensitivity_level
                        WHEN 'RESTRICTED' THEN 0 WHEN 'SENSITIVE' THEN 1
                        WHEN 'INTERNAL' THEN 2 ELSE 3
                    END,
                    s.confidence DESC
                LIMIT %s
            """, params + [limit])

            findings = [{
                "id": r[0], "chunk_id": r[1], "type": r[2],
                "method": r[3], "pattern": r[4], "confidence": r[5],
                "reviewed_by": r[6], "chunk_level": r[7],
                "document_path": r[8], "chunk_index": r[9],
            } for r in cur.fetchall()]

            # Summary stats
            cur.execute("""
                SELECT sensitivity_type, COUNT(*) 
                FROM sdip_sensitivity 
                GROUP BY sensitivity_type 
                ORDER BY COUNT(*) DESC
            """)
            by_type = {r[0]: r[1] for r in cur.fetchall()}

            cur.execute("""
                SELECT detection_method, COUNT(*) 
                FROM sdip_sensitivity 
                GROUP BY detection_method 
                ORDER BY COUNT(*) DESC
            """)
            by_method = {r[0]: r[1] for r in cur.fetchall()}

        return {
            "findings": findings,
            "count": len(findings),
            "summary": {"by_type": by_type, "by_method": by_method},
        }
    finally:
        conn.close()


@router.get("/topics")
async def list_topics():
    """List topics from the Neo4j graph."""
    try:
        from dotenv import load_dotenv
        load_dotenv('/opt/mythos/.env')
        from neo4j import GraphDatabase

        uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
        user = os.environ.get('NEO4J_USER', 'neo4j')
        password = os.environ.get('NEO4J_PASSWORD', 'neo4j')
        driver = GraphDatabase.driver(uri, auth=(user, password))

        with driver.session() as session:
            result = session.run("""
                MATCH (t:SDIPTopic)
                OPTIONAL MATCH (d:SDIPDocument)-[r:COVERS_TOPIC]->(t)
                RETURN t.name as name, t.document_count as count,
                       collect(d.path)[..5] as sample_docs
                ORDER BY count DESC
            """)
            topics = [{
                "name": r["name"],
                "document_count": r["count"],
                "sample_documents": r["sample_docs"],
            } for r in result]

        driver.close()
        return {"topics": topics, "count": len(topics)}

    except Exception as e:
        return {"topics": [], "count": 0, "error": str(e)}


@router.post("/query")
async def query_documents(
    q: str = Query(..., description="Natural language query"),
    clearance: str = Query('admin', description="Requester clearance level"),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Query documents by content.
    Searches across chunks and returns matching documents with relevant chunks.
    """
    conn = get_db_connection()
    try:
        allowed = get_allowed_levels(clearance)

        with conn.cursor() as cur:
            # Search chunks
            cur.execute("""
                SELECT DISTINCT ON (d.id)
                    d.id, d.relative_path, d.filename, d.file_format,
                    c.id as chunk_id, c.chunk_index, c.parent_heading,
                    c.content_text, c.word_count, c.sensitivity_level,
                    c.sensitivity_tags
                FROM sdip_chunks c
                JOIN sdip_documents d ON d.id = c.document_id
                WHERE c.content_text ILIKE %s
                AND d.status = 'active'
                ORDER BY d.id, c.chunk_index
                LIMIT %s
            """, (f'%{q}%', limit))

            results = []
            for row in cur.fetchall():
                level = row[9]
                content = row[7] if level in allowed else redact_content(row[7], level, clearance)

                results.append({
                    "document": {
                        "id": row[0],
                        "relative_path": row[1],
                        "filename": row[2],
                        "file_format": row[3],
                    },
                    "matched_chunk": {
                        "id": row[4],
                        "chunk_index": row[5],
                        "parent_heading": row[6],
                        "content_preview": content[:500],
                        "word_count": row[8],
                        "sensitivity_level": level,
                        "sensitivity_tags": row[10] or [],
                        "redacted": level not in allowed,
                    },
                })

        return {"query": q, "results": results, "count": len(results)}
    finally:
        conn.close()


# ── Audit Logging ──────────────────────────────────────────────

def log_access(requester: str, document_id: int = None, chunk_id: int = None,
               action: str = 'read', content_served: bool = True,
               redaction_applied: str = None):
    """Log an access event to the audit table."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sdip_audit_log
                    (requester, document_id, chunk_id, action,
                     content_served, redaction_applied)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (requester, document_id, chunk_id, action,
                  content_served, redaction_applied))
        conn.commit()
        conn.close()
    except Exception:
        pass  # Audit logging should never break the request
