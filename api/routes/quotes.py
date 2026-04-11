#!/usr/bin/env python3
"""
Mythos Quotes API Routes
/opt/mythos/api/routes/quotes.py

Stores and manages quotes — primarily from Seraphe, but open to any speaker.
Mirrors the OntologyTerm pattern: Neo4j nodes with tags and relationships.

Endpoints:
    GET    /api/quotes/              - List/search quotes
    GET    /api/quotes/{qid}         - Get quote with relationships
    POST   /api/quotes/              - Create quote
    PATCH  /api/quotes/{qid}         - Update quote
    DELETE /api/quotes/{qid}         - Delete quote
    GET    /api/quotes/tags          - List tags with counts
    GET    /api/quotes/speakers      - List speakers with counts
    GET    /api/quotes/graph         - Full relationship graph data
    POST   /api/quotes/relationships - Create a relationship
    DELETE /api/quotes/relationships - Delete a relationship
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os
import uuid
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

router = APIRouter(prefix="/api/quotes", tags=["quotes"])

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')


def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# ── Models ──────────────────────────────────────────

class QuoteCreate(BaseModel):
    text: str
    speaker: str = "Seraphe"
    description: str = ""
    interpretation: str = ""
    context: str = ""
    source: str = ""
    date_spoken: str = ""
    tags: List[str] = []

class QuoteUpdate(BaseModel):
    text: Optional[str] = None
    speaker: Optional[str] = None
    description: Optional[str] = None
    interpretation: Optional[str] = None
    context: Optional[str] = None
    source: Optional[str] = None
    date_spoken: Optional[str] = None
    tags: Optional[List[str]] = None

class RelationshipCreate(BaseModel):
    source_qid: str
    target_name: str
    target_label: str = "OntologyTerm"
    relationship_type: str = "RELATES_TO"

# ── Endpoints ───────────────────────────────────────

@router.get("/")
async def list_quotes(
    speaker: Optional[str] = Query(None, description="Filter by speaker"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    search: Optional[str] = Query(None, description="Search text, description, interpretation"),
    limit: int = Query(200, ge=1, le=500),
):
    """List all quotes, optionally filtered."""
    driver = get_driver()
    try:
        with driver.session() as session:
            where_parts = []
            params = {"limit": limit}

            if search:
                where_parts.append("""(
                    toLower(q.text) CONTAINS toLower($search)
                    OR toLower(q.description) CONTAINS toLower($search)
                    OR toLower(q.interpretation) CONTAINS toLower($search)
                    OR toLower(q.context) CONTAINS toLower($search)
                )""")
                params["search"] = search

            if speaker:
                where_parts.append("toLower(q.speaker) = toLower($speaker)")
                params["speaker"] = speaker

            if tag:
                where_parts.append("$tag IN q.tags")
                params["tag"] = tag

            where_clause = " AND ".join(where_parts) if where_parts else "true"

            query = f"""
                MATCH (q:Quote)
                WHERE {where_clause}
                OPTIONAL MATCH (q)-[r]-()
                WITH q, count(r) AS rel_count
                RETURN q.quote_id AS quote_id, q.text AS text,
                       q.speaker AS speaker, q.description AS description,
                       q.interpretation AS interpretation, q.context AS context,
                       q.source AS source, q.date_spoken AS date_spoken,
                       q.tags AS tags, q.created_at AS created_at,
                       q.updated_at AS updated_at, rel_count
                ORDER BY q.created_at DESC
                LIMIT $limit
            """
            results = session.run(query, **params)
            quotes = []
            for r in results:
                quotes.append({
                    "quote_id": r["quote_id"],
                    "text": r["text"],
                    "speaker": r["speaker"],
                    "description": r["description"] or "",
                    "interpretation": r["interpretation"] or "",
                    "context": r["context"] or "",
                    "source": r["source"] or "",
                    "date_spoken": r["date_spoken"] or "",
                    "tags": r["tags"] or [],
                    "relationship_count": r["rel_count"],
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                })
            return {"quotes": quotes, "count": len(quotes)}
    finally:
        driver.close()


@router.get("/tags")
async def list_tags():
    """List all tags with counts."""
    driver = get_driver()
    try:
        with driver.session() as session:
            results = session.run("""
                MATCH (q:Quote)
                WHERE q.tags IS NOT NULL
                UNWIND q.tags AS tag
                RETURN tag, count(*) AS count
                ORDER BY count DESC
            """)
            tags = [{"tag": r["tag"], "count": r["count"]} for r in results]
            return {"tags": tags}
    finally:
        driver.close()


@router.get("/speakers")
async def list_speakers():
    """List all speakers with counts."""
    driver = get_driver()
    try:
        with driver.session() as session:
            results = session.run("""
                MATCH (q:Quote)
                RETURN q.speaker AS speaker, count(q) AS count
                ORDER BY count DESC
            """)
            speakers = [{"speaker": r["speaker"], "count": r["count"]} for r in results]
            return {"speakers": speakers}
    finally:
        driver.close()


@router.get("/graph")
async def get_graph():
    """Get full relationship graph data for visualization."""
    driver = get_driver()
    try:
        with driver.session() as session:
            # Quote nodes
            nodes_result = session.run("""
                MATCH (q:Quote)
                RETURN q.quote_id AS id, q.text AS text, q.speaker AS speaker,
                       q.tags AS tags, 'quote' AS node_type
            """)
            nodes = []
            for r in nodes_result:
                label = r["text"][:50] + "…" if len(r["text"] or "") > 50 else r["text"]
                nodes.append({
                    "id": r["id"], "label": label,
                    "speaker": r["speaker"], "tags": r["tags"] or [],
                    "node_type": "quote",
                })

            # Connected OntologyTerm / Tag nodes
            connected_result = session.run("""
                MATCH (q:Quote)-[r]->(t)
                WHERE NOT t:Quote
                RETURN DISTINCT
                    COALESCE(t.name, t.quote_id) AS id,
                    COALESCE(t.name, 'unknown') AS label,
                    labels(t)[0] AS node_type,
                    COALESCE(t.category, '') AS category
            """)
            for r in connected_result:
                nodes.append({
                    "id": r["id"], "label": r["label"],
                    "node_type": r["node_type"], "category": r["category"],
                })

            # Edges
            edges_result = session.run("""
                MATCH (q:Quote)-[r]->(t)
                RETURN q.quote_id AS source,
                       COALESCE(t.name, t.quote_id) AS target,
                       type(r) AS type
            """)
            edges = [{"source": r["source"], "target": r["target"], "type": r["type"]} for r in edges_result]

            return {"nodes": nodes, "edges": edges}
    finally:
        driver.close()


@router.get("/{qid}")
async def get_quote(qid: str):
    """Get a single quote with all its relationships."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (q:Quote {quote_id: $qid})
                RETURN q.quote_id AS quote_id, q.text AS text,
                       q.speaker AS speaker, q.description AS description,
                       q.interpretation AS interpretation, q.context AS context,
                       q.source AS source, q.date_spoken AS date_spoken,
                       q.tags AS tags, q.created_at AS created_at,
                       q.updated_at AS updated_at
            """, qid=qid)
            record = result.single()
            if not record:
                raise HTTPException(status_code=404, detail=f"Quote '{qid}' not found")

            quote = {k: (record[k] or "" if k != "tags" else record[k] or []) for k in record.keys()}

            # Outgoing relationships
            out_result = session.run("""
                MATCH (q:Quote {quote_id: $qid})-[r]->(t)
                RETURN COALESCE(t.name, t.quote_id) AS name,
                       labels(t)[0] AS label,
                       COALESCE(t.category, '') AS category,
                       type(r) AS rel_type
                ORDER BY rel_type, name
            """, qid=qid)
            quote["related_to"] = [
                {"name": r["name"], "label": r["label"],
                 "category": r["category"], "type": r["rel_type"]}
                for r in out_result
            ]

            # Incoming relationships
            in_result = session.run("""
                MATCH (t)-[r]->(q:Quote {quote_id: $qid})
                RETURN COALESCE(t.name, t.quote_id) AS name,
                       labels(t)[0] AS label,
                       COALESCE(t.category, '') AS category,
                       type(r) AS rel_type
                ORDER BY rel_type, name
            """, qid=qid)
            quote["related_from"] = [
                {"name": r["name"], "label": r["label"],
                 "category": r["category"], "type": r["rel_type"]}
                for r in in_result
            ]

            return quote
    finally:
        driver.close()


@router.post("/", status_code=201)
async def create_quote(body: QuoteCreate):
    """Create a new quote."""
    driver = get_driver()
    now = datetime.now(timezone.utc).isoformat()
    qid = "Q-" + uuid.uuid4().hex[:8]
    try:
        with driver.session() as session:
            session.run("""
                CREATE (q:Quote {
                    quote_id: $qid,
                    text: $text,
                    speaker: $speaker,
                    description: $description,
                    interpretation: $interpretation,
                    context: $context,
                    source: $source,
                    date_spoken: $date_spoken,
                    tags: $tags,
                    created_at: $now,
                    updated_at: $now
                })
            """, qid=qid, text=body.text, speaker=body.speaker,
                description=body.description, interpretation=body.interpretation,
                context=body.context, source=body.source,
                date_spoken=body.date_spoken, tags=body.tags, now=now)

            # Auto-link to OntologyTerms by tag name
            for tag in body.tags:
                session.run("""
                    MATCH (q:Quote {quote_id: $qid})
                    MATCH (t:OntologyTerm)
                    WHERE toLower(t.name) = toLower($tag)
                       OR any(a IN t.aliases WHERE toLower(a) = toLower($tag))
                    MERGE (q)-[:TAGGED_WITH]->(t)
                """, qid=qid, tag=tag)

            return {"status": "created", "quote_id": qid}
    finally:
        driver.close()


@router.patch("/{qid}")
async def update_quote(qid: str, body: QuoteUpdate):
    """Update an existing quote."""
    driver = get_driver()
    now = datetime.now(timezone.utc).isoformat()
    try:
        with driver.session() as session:
            existing = session.run(
                "MATCH (q:Quote {quote_id: $qid}) RETURN q.quote_id", qid=qid
            ).single()
            if not existing:
                raise HTTPException(status_code=404, detail=f"Quote '{qid}' not found")

            sets = ["q.updated_at = $now"]
            params = {"qid": qid, "now": now}

            for field in ['text', 'speaker', 'description', 'interpretation',
                          'context', 'source', 'date_spoken', 'tags']:
                val = getattr(body, field, None)
                if val is not None:
                    sets.append(f"q.{field} = ${field}")
                    params[field] = val

            session.run(f"""
                MATCH (q:Quote {{quote_id: $qid}})
                SET {', '.join(sets)}
            """, **params)

            return {"status": "updated", "quote_id": qid}
    finally:
        driver.close()


@router.delete("/{qid}")
async def delete_quote(qid: str):
    """Delete a quote and its relationships."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (q:Quote {quote_id: $qid})
                DETACH DELETE q
                RETURN count(*) AS deleted
            """, qid=qid)
            count = result.single()["deleted"]
            if count == 0:
                raise HTTPException(status_code=404, detail=f"Quote '{qid}' not found")
            return {"status": "deleted", "quote_id": qid}
    finally:
        driver.close()


@router.post("/relationships")
async def create_relationship(body: RelationshipCreate):
    """Create a relationship from a quote to another node."""
    driver = get_driver()
    try:
        with driver.session() as session:
            # Validate quote exists
            q = session.run(
                "MATCH (q:Quote {quote_id: $qid}) RETURN q", qid=body.source_qid
            ).single()
            if not q:
                raise HTTPException(status_code=404, detail=f"Quote '{body.source_qid}' not found")

            # Find target by name and label
            result = session.run(f"""
                MATCH (q:Quote {{quote_id: $qid}})
                MATCH (t:{body.target_label} {{name: $name}})
                MERGE (q)-[r:{body.relationship_type}]->(t)
                RETURN type(r) AS rel
            """, qid=body.source_qid, name=body.target_name)

            if not result.single():
                raise HTTPException(status_code=404,
                    detail=f"{body.target_label} '{body.target_name}' not found")

            return {"status": "created", "source": body.source_qid,
                    "target": body.target_name, "type": body.relationship_type}
    finally:
        driver.close()


@router.delete("/relationships")
async def delete_relationship(
    source_qid: str, target_name: str, relationship_type: str
):
    """Delete a specific relationship from a quote."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run(f"""
                MATCH (q:Quote {{quote_id: $qid}})-[r:{relationship_type}]->(t {{name: $name}})
                DELETE r
                RETURN count(*) AS deleted
            """, qid=source_qid, name=target_name)
            count = result.single()["deleted"]
            if count == 0:
                raise HTTPException(status_code=404, detail="Relationship not found")
            return {"status": "deleted"}
    finally:
        driver.close()
