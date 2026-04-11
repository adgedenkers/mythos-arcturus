"""
Document Registry API
Iris's authoritative reference library — search, retrieve, register, update documents.

Endpoints:
  GET  /api/docs/search        — Search by query, domain, type, tags
  GET  /api/docs/registry      — List all active documents
  GET  /api/docs/{slug}        — Get registry entry + metadata
  GET  /api/docs/{slug}/content — Get actual file contents
  POST /api/docs/register      — Register a new document
  PUT  /api/docs/{slug}        — Update a document (versions the old one)
  POST /api/docs/{slug}/deprecate — Mark as deprecated, point to replacement
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/docs", tags=["documents"])


def get_db():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor
    )


def json_response(data):
    return JSONResponse(content=json.loads(json.dumps(data, default=str)))


def file_hash(path):
    """SHA-256 hash of file contents."""
    try:
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except (FileNotFoundError, PermissionError):
        return None


# ── Models ─────────────────────────────────────────────────

class DocRegister(BaseModel):
    slug: str
    title: str
    doc_type: str = 'reference'
    domain: str = 'general'
    version: str = '1.0.0'
    summary: Optional[str] = None
    file_path: Optional[str] = None
    tags: List[str] = []
    metadata: dict = {}
    registered_by: str = 'manual'


class DocUpdate(BaseModel):
    title: Optional[str] = None
    version: Optional[str] = None
    summary: Optional[str] = None
    file_path: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None
    change_summary: Optional[str] = None


class DocDeprecate(BaseModel):
    superseded_by: str
    reason: Optional[str] = None


# ── Search ─────────────────────────────────────────────────

@router.get("/search")
async def search_docs(
    request: Request,
    q: Optional[str] = Query(default=None, description="Free-text search across title, summary, tags"),
    domain: Optional[str] = Query(default=None, description="Filter by domain"),
    doc_type: Optional[str] = Query(default=None, description="Filter by doc_type"),
    tag: Optional[str] = Query(default=None, description="Filter by tag"),
    status: str = Query(default='active', description="Filter by status"),
    include_content: bool = Query(default=False, description="Include file contents in results"),
):
    """Search the document registry. Iris's primary discovery mechanism."""
    conn = get_db()
    cur = conn.cursor()

    conditions = []
    params = []

    if status:
        conditions.append("status = %s")
        params.append(status)

    if domain:
        conditions.append("domain = %s")
        params.append(domain)

    if doc_type:
        conditions.append("doc_type = %s")
        params.append(doc_type)

    if tag:
        conditions.append("%s = ANY(tags)")
        params.append(tag)

    if q:
        conditions.append("""(
            title ILIKE %s
            OR summary ILIKE %s
            OR slug ILIKE %s
            OR %s = ANY(tags)
            OR EXISTS (
                SELECT 1 FROM unnest(tags) t WHERE t ILIKE %s
            )
        )""")
        like = f"%{q}%"
        params.extend([like, like, like, q, like])

    where = " AND ".join(conditions) if conditions else "TRUE"

    cur.execute(f"""
        SELECT id, slug, title, doc_type, domain, version, status,
               summary, file_path, tags, metadata, supersedes, superseded_by,
               registered_by, created_at, updated_at
        FROM document_registry
        WHERE {where}
        ORDER BY
            CASE WHEN status = 'active' THEN 0
                 WHEN status = 'draft' THEN 1
                 WHEN status = 'deprecated' THEN 2
                 ELSE 3 END,
            updated_at DESC
    """, params)

    results = [dict(r) for r in cur.fetchall()]

    # Optionally include file contents
    if include_content:
        for r in results:
            if r.get('file_path') and os.path.exists(r['file_path']):
                try:
                    with open(r['file_path'], 'r') as f:
                        r['content'] = f.read()
                except Exception:
                    r['content'] = None

    conn.close()
    return json_response({"count": len(results), "results": results})


# ── List All ───────────────────────────────────────────────

@router.get("/registry")
async def list_registry(
    request: Request,
    status: str = Query(default='active'),
):
    """List all documents in the registry. Quick inventory."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT slug, title, doc_type, domain, version, status, summary, tags, updated_at
        FROM document_registry
        WHERE status = %s
        ORDER BY domain, title
    """, (status,))
    results = [dict(r) for r in cur.fetchall()]
    conn.close()

    # Group by domain for readability
    by_domain = {}
    for r in results:
        d = r['domain']
        if d not in by_domain:
            by_domain[d] = []
        by_domain[d].append(r)

    return json_response({"count": len(results), "by_domain": by_domain, "all": results})


# ── Get Single Document ────────────────────────────────────

@router.get("/{slug}")
async def get_doc(request: Request, slug: str):
    """Get full registry entry for a document."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM document_registry WHERE slug = %s", (slug,))
    doc = cur.fetchone()

    if not doc:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Document '{slug}' not found")

    doc = dict(doc)

    # Get version history
    cur.execute("""
        SELECT version, change_summary, created_at
        FROM document_versions
        WHERE registry_id = %s
        ORDER BY created_at DESC
    """, (doc['id'],))
    doc['version_history'] = [dict(r) for r in cur.fetchall()]

    # Check if file exists and is current
    if doc.get('file_path'):
        doc['file_exists'] = os.path.exists(doc['file_path'])
        if doc['file_exists']:
            current_hash = file_hash(doc['file_path'])
            doc['file_changed'] = current_hash != doc.get('file_hash')
            doc['current_file_hash'] = current_hash

    conn.close()
    return json_response(doc)


# ── Get Document Content ───────────────────────────────────

@router.get("/{slug}/content")
async def get_doc_content(request: Request, slug: str):
    """Get the actual file contents of a registered document.
    This is the primary mechanism for Iris to READ reference material."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT file_path, title, status FROM document_registry WHERE slug = %s", (slug,))
    doc = cur.fetchone()
    conn.close()

    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{slug}' not found")

    if doc['status'] == 'deprecated':
        raise HTTPException(status_code=410, detail=f"Document '{slug}' is deprecated")

    if not doc['file_path'] or not os.path.exists(doc['file_path']):
        raise HTTPException(status_code=404, detail=f"File not found at {doc['file_path']}")

    try:
        with open(doc['file_path'], 'r') as f:
            content = f.read()
        return PlainTextResponse(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")


# ── Register New Document ──────────────────────────────────

@router.post("/register")
async def register_doc(request: Request, doc: DocRegister):
    """Register a new document in the registry."""
    conn = get_db()
    cur = conn.cursor()

    # Check for duplicate
    cur.execute("SELECT id FROM document_registry WHERE slug = %s", (doc.slug,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=409, detail=f"Document '{doc.slug}' already exists")

    # Hash the file if path provided
    fhash = file_hash(doc.file_path) if doc.file_path else None

    cur.execute("""
        INSERT INTO document_registry
            (slug, title, doc_type, domain, version, summary, file_path, file_hash, tags, metadata, registered_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, slug, title, version
    """, (
        doc.slug, doc.title, doc.doc_type, doc.domain, doc.version,
        doc.summary, doc.file_path, fhash, doc.tags,
        json.dumps(doc.metadata), doc.registered_by
    ))

    result = dict(cur.fetchone())
    conn.commit()
    conn.close()

    logger.info(f"Document registered: {doc.slug} v{doc.version}")
    return json_response({"status": "registered", "document": result})


# ── Update Document ────────────────────────────────────────

@router.put("/{slug}")
async def update_doc(request: Request, slug: str, update: DocUpdate):
    """Update a document. Automatically versions the previous state."""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM document_registry WHERE slug = %s", (slug,))
    existing = cur.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Document '{slug}' not found")

    existing = dict(existing)

    # Archive current version
    cur.execute("""
        INSERT INTO document_versions (registry_id, version, file_path, file_hash, change_summary)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        existing['id'], existing['version'], existing['file_path'],
        existing['file_hash'], update.change_summary or f"Updated to {update.version or 'new version'}"
    ))

    # Build update
    fields = []
    params = []

    if update.title is not None:
        fields.append("title = %s"); params.append(update.title)
    if update.version is not None:
        fields.append("version = %s"); params.append(update.version)
    if update.summary is not None:
        fields.append("summary = %s"); params.append(update.summary)
    if update.file_path is not None:
        fields.append("file_path = %s"); params.append(update.file_path)
        fields.append("file_hash = %s"); params.append(file_hash(update.file_path))
    if update.tags is not None:
        fields.append("tags = %s"); params.append(update.tags)
    if update.metadata is not None:
        fields.append("metadata = %s"); params.append(json.dumps(update.metadata))

    # If file_path didn't change but file content did, update hash
    if update.file_path is None and existing.get('file_path'):
        new_hash = file_hash(existing['file_path'])
        if new_hash != existing.get('file_hash'):
            fields.append("file_hash = %s"); params.append(new_hash)

    if fields:
        params.append(slug)
        cur.execute(f"UPDATE document_registry SET {', '.join(fields)} WHERE slug = %s", params)

    conn.commit()
    conn.close()

    logger.info(f"Document updated: {slug}")
    return json_response({"status": "updated", "slug": slug, "new_version": update.version})


# ── Deprecate Document ─────────────────────────────────────

@router.post("/{slug}/deprecate")
async def deprecate_doc(request: Request, slug: str, deprecation: DocDeprecate):
    """Mark a document as deprecated and point to its replacement."""
    conn = get_db()
    cur = conn.cursor()

    # Verify both documents exist
    cur.execute("SELECT id FROM document_registry WHERE slug = %s", (slug,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Document '{slug}' not found")

    cur.execute("SELECT id FROM document_registry WHERE slug = %s", (deprecation.superseded_by,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Replacement document '{deprecation.superseded_by}' not found")

    # Deprecate the old one
    cur.execute("""
        UPDATE document_registry
        SET status = 'deprecated', superseded_by = %s
        WHERE slug = %s
    """, (deprecation.superseded_by, slug))

    # Mark the new one as superseding
    cur.execute("""
        UPDATE document_registry
        SET supersedes = %s
        WHERE slug = %s
    """, (slug, deprecation.superseded_by))

    conn.commit()
    conn.close()

    logger.info(f"Document deprecated: {slug} → {deprecation.superseded_by}")
    return json_response({
        "status": "deprecated",
        "slug": slug,
        "superseded_by": deprecation.superseded_by
    })
