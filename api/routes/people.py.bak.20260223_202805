#!/usr/bin/env python3
"""
Mythos People API Routes (Neo4j-backed)
/opt/mythos/api/routes/people.py

Manages ALL Person-type nodes in Neo4j:
  - Person (canonical: Ka, Seraphe, Fitz, Dennis, Jennie)
  - Person:Entity (aspects: Ka'tuar'el, Rebecca, Seraphe, Becky, Iris, etc.)
  - Person:GenPerson (GEDCOM genealogy imports)
  - Soul / Soul:Person (soul-level identities)

Endpoints:
    GET    /api/people/                - List people (filterable by type)
    GET    /api/people/stats           - Summary stats
    GET    /api/people/rel-types       - List all relationship types in use
    GET    /api/people/graph           - Graph data for visualization
    GET    /api/people/search-nodes    - Search nodes for relationship target picker
    GET    /api/people/{eid}           - Get person + relationships by elementId
    POST   /api/people/               - Create a Person node
    PATCH  /api/people/{eid}           - Update person properties
    DELETE /api/people/{eid}           - Delete person (with safety check)
    GET    /api/people/{eid}/rels      - Get all relationships
    POST   /api/people/{eid}/rels      - Create a relationship
    DELETE /api/people/{eid}/rels      - Delete a relationship
    GET    /api/people/{eid}/graph     - Ego graph for a specific person
"""
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

router = APIRouter(prefix="/api/people", tags=["people"])

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')

# Valid person_type values
PERSON_TYPES = [
    'Family', 'Personal', 'Contact', 'Business', 'School',
    'Religious', 'Historical', 'Spiritual', 'Musical',
    'Political', 'Literary', 'Scientific', 'Mythological',
]


def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def node_to_dict(record, node_key='p'):
    """Convert a Neo4j result record to a serializable dict."""
    props = dict(record[node_key]) if record[node_key] else {}
    for k, v in props.items():
        if hasattr(v, 'isoformat'):
            props[k] = v.isoformat()
        elif hasattr(v, 'x') and hasattr(v, 'y'):
            props[k] = {"lat": v.y, "lng": v.x}
    props['_element_id'] = record.get('eid', '')
    props['_labels'] = record.get('labels', [])
    props['_type'] = classify_labels(record.get('labels', []))
    return props


def classify_labels(labels):
    labels_set = set(labels)
    if 'Soul' in labels_set and 'Person' in labels_set:
        return 'soul_person'
    if 'Soul' in labels_set:
        return 'soul'
    if 'GenPerson' in labels_set:
        return 'genealogy'
    if 'Entity' in labels_set:
        return 'entity'
    return 'person'


# ── Models ──

class PersonCreate(BaseModel):
    full_name: str
    display_name: Optional[str] = None
    canonical_id: Optional[str] = None
    person_type: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_location: Optional[str] = None
    birth_place: Optional[str] = None
    death_date: Optional[str] = None
    death_location: Optional[str] = None
    current_location: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    labels: List[str] = ["Person"]


class PersonUpdate(BaseModel):
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    name: Optional[str] = None
    canonical_id: Optional[str] = None
    person_type: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_location: Optional[str] = None
    birth_place: Optional[str] = None
    death_date: Optional[str] = None
    death_location: Optional[str] = None
    death_place: Optional[str] = None
    current_location: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    given_name: Optional[str] = None
    surname: Optional[str] = None
    sex: Optional[str] = None
    spiritual_name: Optional[str] = None
    primary_role: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    residence: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


class RelCreate(BaseModel):
    target_eid: str
    rel_type: str
    properties: Optional[Dict[str, str]] = None


class RelDelete(BaseModel):
    target_eid: str
    rel_type: str


# ── Routes ──

@router.get("/stats")
async def people_stats():
    driver = get_driver()
    try:
        with driver.session() as session:
            r = session.run("""
                MATCH (p)
                WHERE 'Person' IN labels(p) OR 'Soul' IN labels(p)
                WITH p, labels(p) AS lbls
                RETURN
                    count(p) AS total,
                    count(CASE WHEN 'GenPerson' IN lbls THEN 1 END) AS genealogy,
                    count(CASE WHEN 'Entity' IN lbls AND 'Person' IN lbls THEN 1 END) AS entities,
                    count(CASE WHEN 'Soul' IN lbls THEN 1 END) AS souls,
                    count(CASE WHEN NOT 'GenPerson' IN lbls AND NOT 'Entity' IN lbls AND NOT 'Soul' IN lbls AND 'Person' IN lbls THEN 1 END) AS canonical,
                    count(CASE WHEN p.birth_date IS NOT NULL THEN 1 END) AS with_dob,
                    count(CASE WHEN p.death_date IS NOT NULL THEN 1 END) AS deceased
            """).single()
            return {
                "total": r['total'], "canonical": r['canonical'],
                "entities": r['entities'], "souls": r['souls'],
                "genealogy": r['genealogy'], "with_dob": r['with_dob'],
                "deceased": r['deceased'],
                "person_types": PERSON_TYPES,
            }
    finally:
        driver.close()


@router.get("/rel-types")
async def relationship_types():
    """List all relationship types currently in use between person/soul nodes."""
    driver = get_driver()
    try:
        with driver.session() as session:
            results = session.run("""
                MATCH (p)-[r]-(q)
                WHERE ('Person' IN labels(p) OR 'Soul' IN labels(p))
                RETURN DISTINCT type(r) AS rel_type, count(r) AS cnt
                ORDER BY cnt DESC
            """)
            types = [{"type": r['rel_type'], "count": r['cnt']} for r in results]
            return {"types": types}
    finally:
        driver.close()


@router.get("/search-nodes")
async def search_nodes(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=50)):
    """Search all nodes for relationship target picker."""
    driver = get_driver()
    try:
        with driver.session() as session:
            results = session.run("""
                MATCH (p)
                WHERE ('Person' IN labels(p) OR 'Soul' IN labels(p) OR 'Incarnation' IN labels(p))
                  AND (
                    toLower(COALESCE(p.full_name, '')) CONTAINS toLower($q)
                    OR toLower(COALESCE(p.display_name, '')) CONTAINS toLower($q)
                    OR toLower(COALESCE(p.name, '')) CONTAINS toLower($q)
                    OR toLower(COALESCE(p.canonical_id, '')) CONTAINS toLower($q)
                    OR toLower(COALESCE(p.given_name, '')) CONTAINS toLower($q)
                    OR toLower(COALESCE(p.spiritual_name, '')) CONTAINS toLower($q)
                  )
                RETURN elementId(p) AS eid,
                       COALESCE(p.display_name, p.full_name, p.name, p.given_name) AS name,
                       p.canonical_id AS canonical_id,
                       labels(p) AS labels
                ORDER BY name
                LIMIT $limit
            """, q=q, limit=limit)
            nodes = [{
                "eid": r['eid'], "name": r['name'],
                "canonical_id": r['canonical_id'],
                "labels": r['labels'],
                "type": classify_labels(r['labels']),
            } for r in results]
            return {"nodes": nodes}
    finally:
        driver.close()


@router.get("/graph")
async def full_graph(
    node_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    """Full graph data for visualization. Excludes GenPerson by default."""
    driver = get_driver()
    try:
        with driver.session() as session:
            where = "NOT 'GenPerson' IN labels(p)" if not node_type or node_type != 'genealogy' else "true"
            if node_type and node_type != 'all' and node_type != 'genealogy':
                type_filter = {
                    'person': "NOT 'GenPerson' IN labels(p) AND NOT 'Entity' IN labels(p) AND NOT 'Soul' IN labels(p)",
                    'entity': "'Entity' IN labels(p)",
                    'soul': "'Soul' IN labels(p)",
                }.get(node_type, "true")
                where = type_filter

            # Get nodes
            nodes_result = session.run(f"""
                MATCH (p)
                WHERE ('Person' IN labels(p) OR 'Soul' IN labels(p))
                  AND {where}
                RETURN elementId(p) AS eid,
                       COALESCE(p.display_name, p.full_name, p.name, p.given_name, 'Unknown') AS name,
                       p.canonical_id AS canonical_id,
                       p.person_type AS person_type,
                       labels(p) AS labels
                LIMIT $limit
            """, limit=limit)
            nodes = []
            node_eids = set()
            for r in nodes_result:
                nodes.append({
                    "eid": r['eid'], "name": r['name'],
                    "canonical_id": r['canonical_id'],
                    "person_type": r['person_type'],
                    "type": classify_labels(r['labels']),
                })
                node_eids.add(r['eid'])

            # Get edges between these nodes
            edges_result = session.run(f"""
                MATCH (a)-[r]->(b)
                WHERE ('Person' IN labels(a) OR 'Soul' IN labels(a))
                  AND ('Person' IN labels(b) OR 'Soul' IN labels(b) OR 'Incarnation' IN labels(b))
                  AND {where.replace('labels(p)', 'labels(a)')}
                RETURN elementId(a) AS source, elementId(b) AS target,
                       type(r) AS rel_type
                LIMIT 1000
            """, limit=limit)
            edges = []
            for r in edges_result:
                if r['source'] in node_eids or r['target'] in node_eids:
                    edges.append({
                        "source": r['source'], "target": r['target'],
                        "type": r['rel_type'],
                    })

            return {"nodes": nodes, "edges": edges}
    finally:
        driver.close()


@router.get("/{eid}/graph")
async def ego_graph(eid: str, depth: int = Query(2, ge=1, le=3)):
    """Get ego-centric graph (neighborhood) for a specific person."""
    driver = get_driver()
    try:
        with driver.session() as session:
            # Get the ego node + neighbors up to depth
            results = session.run("""
                MATCH path = (center)-[*1..""" + str(depth) + """]-()
                WHERE elementId(center) = $eid
                WITH nodes(path) AS ns, relationships(path) AS rs
                UNWIND ns AS n
                WITH DISTINCT n, rs
                WHERE 'Person' IN labels(n) OR 'Soul' IN labels(n) OR 'Incarnation' IN labels(n) OR 'Alias' IN labels(n) OR 'Lineage' IN labels(n)
                RETURN elementId(n) AS eid,
                       COALESCE(n.display_name, n.full_name, n.name, n.given_name, 'Unknown') AS name,
                       n.canonical_id AS canonical_id,
                       n.person_type AS person_type,
                       labels(n) AS labels
            """, eid=eid)

            nodes = []
            node_eids = set()
            for r in results:
                nodes.append({
                    "eid": r['eid'], "name": r['name'],
                    "canonical_id": r['canonical_id'],
                    "person_type": r['person_type'],
                    "type": classify_labels(r['labels']),
                    "is_center": r['eid'] == eid,
                })
                node_eids.add(r['eid'])

            # Get edges between collected nodes
            edges_result = session.run("""
                MATCH (a)-[r]->(b)
                WHERE elementId(a) IN $eids AND elementId(b) IN $eids
                RETURN elementId(a) AS source, elementId(b) AS target,
                       type(r) AS rel_type
            """, eids=list(node_eids))

            edges = [{"source": r['source'], "target": r['target'], "type": r['rel_type']} for r in edges_result]

            return {"nodes": nodes, "edges": edges, "center": eid}
    finally:
        driver.close()


@router.get("/")
async def list_people(
    search: Optional[str] = Query(None),
    node_type: Optional[str] = Query(None),
    person_type: Optional[str] = Query(None),
    sort: str = Query("name"),
    order: str = Query("asc"),
    limit: int = Query(200, ge=1, le=2000),
    offset: int = Query(0, ge=0),
):
    driver = get_driver()
    try:
        with driver.session() as session:
            where_parts = []
            params = {"limit": limit, "offset": offset}

            if node_type and node_type != 'all':
                if node_type == 'person':
                    where_parts.append("NOT 'GenPerson' IN labels(p) AND NOT 'Entity' IN labels(p) AND NOT 'Soul' IN labels(p) AND 'Person' IN labels(p)")
                elif node_type == 'entity':
                    where_parts.append("'Entity' IN labels(p) AND 'Person' IN labels(p)")
                elif node_type == 'soul':
                    where_parts.append("'Soul' IN labels(p)")
                elif node_type == 'soul_person':
                    where_parts.append("'Soul' IN labels(p) AND 'Person' IN labels(p)")
                elif node_type == 'genealogy':
                    where_parts.append("'GenPerson' IN labels(p)")
            else:
                where_parts.append("NOT 'GenPerson' IN labels(p)")

            if person_type:
                where_parts.append("p.person_type = $person_type")
                params["person_type"] = person_type

            if search:
                where_parts.append("""(
                    toLower(COALESCE(p.full_name, '')) CONTAINS toLower($search)
                    OR toLower(COALESCE(p.display_name, '')) CONTAINS toLower($search)
                    OR toLower(COALESCE(p.name, '')) CONTAINS toLower($search)
                    OR toLower(COALESCE(p.canonical_id, '')) CONTAINS toLower($search)
                    OR toLower(COALESCE(p.given_name, '')) CONTAINS toLower($search)
                    OR toLower(COALESCE(p.surname, '')) CONTAINS toLower($search)
                    OR toLower(COALESCE(p.spiritual_name, '')) CONTAINS toLower($search)
                    OR toLower(COALESCE(p.description, '')) CONTAINS toLower($search)
                )""")
                params["search"] = search

            where_clause = " AND ".join(where_parts) if where_parts else "true"

            sort_map = {
                'name': 'COALESCE(p.display_name, p.full_name, p.name, p.given_name, "")',
                'birth_date': 'COALESCE(p.birth_date, "")',
                'canonical_id': 'COALESCE(p.canonical_id, "")',
                'person_type': 'COALESCE(p.person_type, "")',
            }
            sort_expr = sort_map.get(sort, sort_map['name'])
            sort_dir = 'DESC' if order.lower() == 'desc' else 'ASC'

            query = f"""
                MATCH (p)
                WHERE ('Person' IN labels(p) OR 'Soul' IN labels(p))
                  AND {where_clause}
                WITH p, elementId(p) AS eid, labels(p) AS labels
                OPTIONAL MATCH (p)-[:KNOWN_AS]->(a:Alias)
                OPTIONAL MATCH (p)-[rel]-()
                WITH p, eid, labels, collect(DISTINCT a.name) AS aliases, count(DISTINCT rel) AS rel_count
                RETURN p, eid, labels, aliases, rel_count
                ORDER BY {sort_expr} {sort_dir}
                SKIP $offset LIMIT $limit
            """
            results = session.run(query, **params)
            people = []
            for rec in results:
                d = node_to_dict(rec, 'p')
                d['_aliases'] = rec['aliases']
                d['_rel_count'] = rec['rel_count']
                people.append(d)

            count_query = f"""
                MATCH (p)
                WHERE ('Person' IN labels(p) OR 'Soul' IN labels(p))
                  AND {where_clause}
                RETURN count(p) AS total
            """
            total = session.run(count_query, **params).single()['total']
            return {"people": people, "total": total}
    finally:
        driver.close()


@router.get("/{eid}")
async def get_person(eid: str):
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (p)
                WHERE elementId(p) = $eid
                  AND ('Person' IN labels(p) OR 'Soul' IN labels(p))
                OPTIONAL MATCH (p)-[:KNOWN_AS]->(a:Alias)
                RETURN p, elementId(p) AS eid, labels(p) AS labels,
                       collect(DISTINCT a.name) AS aliases
            """, eid=eid)
            rec = result.single()
            if not rec:
                raise HTTPException(status_code=404, detail="Person not found")

            person = node_to_dict(rec, 'p')
            person['_aliases'] = rec['aliases']

            rels_result = session.run("""
                MATCH (p)-[r]-(other)
                WHERE elementId(p) = $eid
                  AND NOT other:Alias
                WITH r, other,
                     elementId(other) AS other_eid,
                     labels(other) AS other_labels,
                     CASE WHEN startNode(r) = p THEN 'outgoing' ELSE 'incoming' END AS direction
                RETURN type(r) AS rel_type,
                       properties(r) AS rel_props,
                       direction,
                       other_eid,
                       other_labels,
                       COALESCE(other.display_name, other.full_name, other.name, other.given_name) AS other_name,
                       other.canonical_id AS other_canonical
                ORDER BY rel_type, other_name
            """, eid=eid)

            relationships = []
            for r in rels_result:
                rel = {
                    "type": r['rel_type'], "direction": r['direction'],
                    "properties": {k: str(v) for k, v in (r['rel_props'] or {}).items()},
                    "target_eid": r['other_eid'], "target_labels": r['other_labels'],
                    "target_name": r['other_name'], "target_canonical": r['other_canonical'],
                }
                relationships.append(rel)

            person['_relationships'] = relationships
            return person
    finally:
        driver.close()


@router.post("/", status_code=201)
async def create_person(body: PersonCreate):
    driver = get_driver()
    now = datetime.now(timezone.utc).isoformat()
    try:
        with driver.session() as session:
            canonical = body.canonical_id
            if not canonical:
                canonical = "person-" + body.full_name.lower().replace(' ', '-').replace("'", '')

            existing = session.run(
                "MATCH (p {canonical_id: $cid}) RETURN elementId(p) AS eid", cid=canonical
            ).single()
            if existing:
                raise HTTPException(status_code=409, detail=f"Node with canonical_id '{canonical}' already exists")

            props = {
                "full_name": body.full_name,
                "display_name": body.display_name or body.full_name,
                "canonical_id": canonical,
                "created_at": now,
            }
            if body.person_type:
                props["person_type"] = body.person_type
            for field in ['birth_date', 'birth_time', 'birth_location', 'birth_place',
                          'death_date', 'death_location', 'current_location', 'description', 'notes']:
                val = getattr(body, field, None)
                if val:
                    props[field] = val

            label_str = ':'.join(body.labels)
            result = session.run(f"""
                CREATE (p:{label_str} $props)
                RETURN p, elementId(p) AS eid, labels(p) AS labels
            """, props=props)
            rec = result.single()
            return node_to_dict(rec, 'p')
    finally:
        driver.close()


@router.patch("/{eid}")
async def update_person(eid: str, body: PersonUpdate):
    driver = get_driver()
    try:
        with driver.session() as session:
            existing = session.run("""
                MATCH (p) WHERE elementId(p) = $eid
                  AND ('Person' IN labels(p) OR 'Soul' IN labels(p))
                RETURN p
            """, eid=eid).single()
            if not existing:
                raise HTTPException(status_code=404, detail="Person not found")

            updates = body.dict(exclude_unset=True, exclude_none=True)
            extra = updates.pop('extra', None)
            if extra:
                updates.update(extra)

            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")

            set_parts = []
            params = {"eid": eid}
            for i, (key, val) in enumerate(updates.items()):
                param_name = f"v{i}"
                set_parts.append(f"p.{key} = ${param_name}")
                params[param_name] = val

            set_clause = ", ".join(set_parts)
            result = session.run(f"""
                MATCH (p) WHERE elementId(p) = $eid
                SET {set_clause}
                RETURN p, elementId(p) AS eid, labels(p) AS labels
            """, **params)
            rec = result.single()
            return node_to_dict(rec, 'p')
    finally:
        driver.close()


@router.delete("/{eid}")
async def delete_person(eid: str, confirm: bool = Query(False)):
    driver = get_driver()
    try:
        with driver.session() as session:
            rec = session.run("""
                MATCH (p) WHERE elementId(p) = $eid
                  AND ('Person' IN labels(p) OR 'Soul' IN labels(p))
                RETURN COALESCE(p.display_name, p.full_name, p.name) AS name,
                       p.canonical_id AS cid, labels(p) AS labels,
                       size([(p)-[]-() | 1]) AS rel_count
            """, eid=eid).single()

            if not rec:
                raise HTTPException(status_code=404, detail="Person not found")

            is_protected = rec['cid'] is not None or 'Soul' in rec['labels']
            if is_protected and not confirm:
                raise HTTPException(status_code=400,
                    detail=f"Protected node ({rec['name']}, {rec['rel_count']} relationships). Pass confirm=true to delete.")

            session.run("MATCH (p) WHERE elementId(p) = $eid DETACH DELETE p", eid=eid)
            return {"status": "deleted", "name": rec['name'], "relationships_removed": rec['rel_count']}
    finally:
        driver.close()


# ── Relationship management ──

@router.get("/{eid}/rels")
async def get_relationships(eid: str):
    driver = get_driver()
    try:
        with driver.session() as session:
            results = session.run("""
                MATCH (p)-[r]-(other)
                WHERE elementId(p) = $eid
                WITH r, other, elementId(r) AS rel_eid,
                     CASE WHEN startNode(r) = p THEN 'outgoing' ELSE 'incoming' END AS direction
                RETURN rel_eid, type(r) AS rel_type, properties(r) AS rel_props,
                       direction, elementId(other) AS other_eid, labels(other) AS other_labels,
                       COALESCE(other.display_name, other.full_name, other.name, other.given_name) AS other_name,
                       other.canonical_id AS other_canonical
                ORDER BY rel_type, other_name
            """, eid=eid)
            rels = [{
                "rel_eid": r['rel_eid'], "type": r['rel_type'], "direction": r['direction'],
                "properties": {k: str(v) for k, v in (r['rel_props'] or {}).items()},
                "target_eid": r['other_eid'], "target_labels": r['other_labels'],
                "target_name": r['other_name'], "target_canonical": r['other_canonical'],
            } for r in results]
            return {"relationships": rels, "count": len(rels)}
    finally:
        driver.close()


@router.post("/{eid}/rels", status_code=201)
async def create_relationship(eid: str, body: RelCreate):
    driver = get_driver()
    try:
        with driver.session() as session:
            source = session.run("MATCH (p) WHERE elementId(p) = $eid RETURN p", eid=eid).single()
            if not source:
                raise HTTPException(status_code=404, detail="Source node not found")
            target = session.run("MATCH (t) WHERE elementId(t) = $teid RETURN t", teid=body.target_eid).single()
            if not target:
                raise HTTPException(status_code=404, detail="Target node not found")

            rel_type = body.rel_type.upper().replace(' ', '_')
            props = body.properties or {}
            props_str = ""
            params = {"eid": eid, "teid": body.target_eid}

            if props:
                prop_parts = []
                for i, (k, v) in enumerate(props.items()):
                    pname = f"rp{i}"
                    prop_parts.append(f"{k}: ${pname}")
                    params[pname] = v
                props_str = " {" + ", ".join(prop_parts) + "}"

            result = session.run(f"""
                MATCH (s) WHERE elementId(s) = $eid
                MATCH (t) WHERE elementId(t) = $teid
                CREATE (s)-[r:{rel_type}{props_str}]->(t)
                RETURN type(r) AS rtype, elementId(r) AS rel_eid
            """, **params)
            rec = result.single()
            return {"status": "created", "type": rec['rtype'], "rel_eid": rec['rel_eid']}
    finally:
        driver.close()


@router.delete("/{eid}/rels")
async def delete_relationship(eid: str, body: RelDelete):
    driver = get_driver()
    try:
        with driver.session() as session:
            rel_type = body.rel_type.upper().replace(' ', '_')
            result = session.run(f"""
                MATCH (s)-[r:{rel_type}]-(t)
                WHERE elementId(s) = $eid AND elementId(t) = $teid
                WITH r LIMIT 1
                DELETE r
                RETURN count(*) AS deleted
            """, eid=eid, teid=body.target_eid)
            count = result.single()['deleted']
            if count == 0:
                raise HTTPException(status_code=404, detail="Relationship not found")
            return {"status": "deleted", "type": rel_type}
    finally:
        driver.close()
