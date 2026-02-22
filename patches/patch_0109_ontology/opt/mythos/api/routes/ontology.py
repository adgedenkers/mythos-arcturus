#!/usr/bin/env python3
"""
Mythos Ontology API Routes
/opt/mythos/api/routes/ontology.py

Endpoints:
    GET    /api/ontology/terms          - List/search terms
    GET    /api/ontology/terms/{name}   - Get term with relationships
    POST   /api/ontology/terms          - Create term
    PATCH  /api/ontology/terms/{name}   - Update term
    DELETE /api/ontology/terms/{name}   - Delete term
    GET    /api/ontology/categories     - List categories with counts
    GET    /api/ontology/graph          - Full relationship graph data
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

router = APIRouter(prefix="/api/ontology", tags=["ontology"])

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')


def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# ── Models ──────────────────────────────────────────

class TermCreate(BaseModel):
    name: str
    definition: str
    category: str
    aliases: List[str] = []

class TermUpdate(BaseModel):
    definition: Optional[str] = None
    category: Optional[str] = None
    aliases: Optional[List[str]] = None

class RelationshipCreate(BaseModel):
    source: str
    target: str
    relationship_type: str


# ── Endpoints ───────────────────────────────────────

@router.get("/terms")
async def list_terms(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search name, definition, aliases"),
    limit: int = Query(200, ge=1, le=500),
):
    """List all ontology terms, optionally filtered."""
    driver = get_driver()
    try:
        with driver.session() as session:
            if search:
                query = """
                    MATCH (t:OntologyTerm)
                    WHERE toLower(t.name) CONTAINS toLower($search)
                       OR toLower(t.definition) CONTAINS toLower($search)
                       OR any(a IN t.aliases WHERE toLower(a) CONTAINS toLower($search))
                """
                params = {"search": search, "limit": limit}
                if category:
                    query += " AND t.category = $category"
                    params["category"] = category
            elif category:
                query = "MATCH (t:OntologyTerm) WHERE t.category = $category"
                params = {"category": category, "limit": limit}
            else:
                query = "MATCH (t:OntologyTerm)"
                params = {"limit": limit}

            query += """
                OPTIONAL MATCH (t)-[r:RELATED_TO]-()
                WITH t, count(r) AS rel_count
                RETURN t.name AS name, t.definition AS definition,
                       t.category AS category, t.aliases AS aliases,
                       t.created_at AS created_at, t.updated_at AS updated_at,
                       rel_count
                ORDER BY t.category, t.name
                LIMIT $limit
            """
            results = session.run(query, **params)
            terms = []
            for r in results:
                terms.append({
                    "name": r["name"],
                    "definition": r["definition"],
                    "category": r["category"],
                    "aliases": r["aliases"] or [],
                    "relationship_count": r["rel_count"],
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                })
            return {"terms": terms, "count": len(terms)}
    finally:
        driver.close()


@router.get("/terms/{name}")
async def get_term(name: str):
    """Get a single term with all its relationships."""
    driver = get_driver()
    try:
        with driver.session() as session:
            # Get term
            result = session.run("""
                MATCH (t:OntologyTerm {name: $name})
                RETURN t.name AS name, t.definition AS definition,
                       t.category AS category, t.aliases AS aliases,
                       t.created_at AS created_at, t.updated_at AS updated_at
            """, name=name)
            record = result.single()

            if not record:
                # Try case-insensitive / alias match
                result = session.run("""
                    MATCH (t:OntologyTerm)
                    WHERE toLower(t.name) = toLower($name)
                       OR any(a IN t.aliases WHERE toLower(a) = toLower($name))
                    RETURN t.name AS name, t.definition AS definition,
                           t.category AS category, t.aliases AS aliases,
                           t.created_at AS created_at, t.updated_at AS updated_at
                    LIMIT 1
                """, name=name)
                record = result.single()

            if not record:
                raise HTTPException(status_code=404, detail=f"Term '{name}' not found")

            term = {
                "name": record["name"],
                "definition": record["definition"],
                "category": record["category"],
                "aliases": record["aliases"] or [],
                "created_at": record["created_at"],
                "updated_at": record["updated_at"],
            }

            # Get outgoing relationships
            outgoing = session.run("""
                MATCH (t:OntologyTerm {name: $name})-[r:RELATED_TO]->(other:OntologyTerm)
                RETURN other.name AS name, other.category AS category, r.type AS rel_type
                ORDER BY r.type, other.name
            """, name=record["name"])
            term["related_to"] = [
                {"name": r["name"], "category": r["category"], "type": r["rel_type"]}
                for r in outgoing
            ]

            # Get incoming relationships
            incoming = session.run("""
                MATCH (other:OntologyTerm)-[r:RELATED_TO]->(t:OntologyTerm {name: $name})
                RETURN other.name AS name, other.category AS category, r.type AS rel_type
                ORDER BY r.type, other.name
            """, name=record["name"])
            term["related_from"] = [
                {"name": r["name"], "category": r["category"], "type": r["rel_type"]}
                for r in incoming
            ]

            return term
    finally:
        driver.close()


@router.post("/terms", status_code=201)
async def create_term(body: TermCreate):
    """Create a new ontology term."""
    driver = get_driver()
    now = datetime.utcnow().isoformat()
    try:
        with driver.session() as session:
            # Check for duplicate
            existing = session.run(
                "MATCH (t:OntologyTerm {name: $name}) RETURN t.name", name=body.name
            ).single()
            if existing:
                raise HTTPException(status_code=409, detail=f"Term '{body.name}' already exists")

            session.run("""
                CREATE (t:OntologyTerm {
                    name: $name,
                    definition: $definition,
                    category: $category,
                    aliases: $aliases,
                    created_at: $now,
                    updated_at: $now
                })
            """, name=body.name, definition=body.definition,
                category=body.category, aliases=body.aliases, now=now)

            return {"status": "created", "name": body.name}
    finally:
        driver.close()


@router.patch("/terms/{name}")
async def update_term(name: str, body: TermUpdate):
    """Update an existing ontology term."""
    driver = get_driver()
    now = datetime.utcnow().isoformat()
    try:
        with driver.session() as session:
            existing = session.run(
                "MATCH (t:OntologyTerm {name: $name}) RETURN t.name", name=name
            ).single()
            if not existing:
                raise HTTPException(status_code=404, detail=f"Term '{name}' not found")

            sets = ["t.updated_at = $now"]
            params = {"name": name, "now": now}

            if body.definition is not None:
                sets.append("t.definition = $definition")
                params["definition"] = body.definition
            if body.category is not None:
                sets.append("t.category = $category")
                params["category"] = body.category
            if body.aliases is not None:
                sets.append("t.aliases = $aliases")
                params["aliases"] = body.aliases

            session.run(f"""
                MATCH (t:OntologyTerm {{name: $name}})
                SET {', '.join(sets)}
            """, **params)

            return {"status": "updated", "name": name}
    finally:
        driver.close()


@router.delete("/terms/{name}")
async def delete_term(name: str):
    """Delete an ontology term and its relationships."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (t:OntologyTerm {name: $name})
                DETACH DELETE t
                RETURN count(*) AS deleted
            """, name=name)
            count = result.single()["deleted"]
            if count == 0:
                raise HTTPException(status_code=404, detail=f"Term '{name}' not found")
            return {"status": "deleted", "name": name}
    finally:
        driver.close()


@router.get("/categories")
async def list_categories():
    """List all categories with term counts."""
    driver = get_driver()
    try:
        with driver.session() as session:
            results = session.run("""
                MATCH (t:OntologyTerm)
                RETURN t.category AS category, count(t) AS count
                ORDER BY count DESC
            """)
            cats = [{"category": r["category"], "count": r["count"]} for r in results]
            return {"categories": cats}
    finally:
        driver.close()


@router.get("/graph")
async def get_graph():
    """Get full relationship graph data for visualization."""
    driver = get_driver()
    try:
        with driver.session() as session:
            # Nodes
            nodes_result = session.run("""
                MATCH (t:OntologyTerm)
                RETURN t.name AS name, t.category AS category
                ORDER BY t.category, t.name
            """)
            nodes = [{"name": r["name"], "category": r["category"]} for r in nodes_result]

            # Edges
            edges_result = session.run("""
                MATCH (s:OntologyTerm)-[r:RELATED_TO]->(t:OntologyTerm)
                RETURN s.name AS source, t.name AS target, r.type AS type
            """)
            edges = [{"source": r["source"], "target": r["target"], "type": r["type"]} for r in edges_result]

            return {"nodes": nodes, "edges": edges}
    finally:
        driver.close()


@router.post("/relationships")
async def create_relationship(body: RelationshipCreate):
    """Create a relationship between two terms."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (s:OntologyTerm {name: $source})
                MATCH (t:OntologyTerm {name: $target})
                MERGE (s)-[r:RELATED_TO {type: $rel_type}]->(t)
                RETURN type(r) AS rel
            """, source=body.source, target=body.target, rel_type=body.relationship_type)
            if not result.single():
                raise HTTPException(status_code=404, detail="One or both terms not found")
            return {"status": "created", "source": body.source, "target": body.target, "type": body.relationship_type}
    finally:
        driver.close()


@router.delete("/relationships")
async def delete_relationship(source: str, target: str, relationship_type: str):
    """Delete a specific relationship between two terms."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (s:OntologyTerm {name: $source})-[r:RELATED_TO {type: $rel_type}]->(t:OntologyTerm {name: $target})
                DELETE r
                RETURN count(*) AS deleted
            """, source=source, target=target, rel_type=relationship_type)
            count = result.single()["deleted"]
            if count == 0:
                raise HTTPException(status_code=404, detail="Relationship not found")
            return {"status": "deleted"}
    finally:
        driver.close()
