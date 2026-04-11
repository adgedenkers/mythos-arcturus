#!/usr/bin/env python3
"""
Mythos Rolodex API Routes (Neo4j + PostgreSQL)
/opt/mythos/api/routes/rolodex.py

The Rolodex is the identity and directory layer of Mythos.
Every person, soul, entity, and incarnation is registered here.

Node Types:
    PO - PersonOwner    (system owner identity)
    PP - Person         (canonical person record)
    PS - Soul           (eternal non-incarnate identity)
    PE - Entity         (auto-created mention node)
    PI - Incarnation    (soul expressed in specific body/time)
    PX - PersonProxy    (subsystem-specific proxy)

Endpoints:
    GET    /api/rolodex/                 - Browse directory (filterable)
    GET    /api/rolodex/stats            - Dashboard stats
    GET    /api/rolodex/graph            - Graph data for visualization
    GET    /api/rolodex/unresolved       - Unresolved entities
    GET    /api/rolodex/node/{cid}       - Node detail by canonical_id
    GET    /api/rolodex/node/{cid}/graph - Ego graph for a node
    POST   /api/rolodex/resolve          - Resolve entity → person
    POST   /api/rolodex/node             - Create a node
    PATCH  /api/rolodex/node/{cid}       - Update a node
    POST   /api/rolodex/node/{cid}/rel   - Create a relationship
    DELETE /api/rolodex/node/{cid}/rel   - Delete a relationship
"""
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from neo4j import GraphDatabase
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

router = APIRouter(prefix="/api/rolodex", tags=["rolodex"])

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'mythos')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'mythos')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')

# ── Node type classification ──

NODE_TYPES = {
    'owner':       {'prefix': 'PO', 'label': 'PersonOwner',  'color': '#d4a574'},
    'person':      {'prefix': 'PP', 'label': 'Person',       'color': '#06b6d4'},
    'soul':        {'prefix': 'PS', 'label': 'Soul',         'color': '#a855f7'},
    'entity':      {'prefix': 'PE', 'label': 'Entity',       'color': '#3b82f6'},
    'incarnation': {'prefix': 'PI', 'label': 'Incarnation',  'color': '#f59e0b'},
    'proxy':       {'prefix': 'PX', 'label': 'PersonProxy',  'color': '#22c55e'},
    'genealogy':   {'prefix': 'GP', 'label': 'GenPerson',    'color': '#64748b'},
}

DOMAINS = ['people', 'genealogy', 'spiritual', 'system', 'analysis', 'conversation', 'finance', 'concept']
SCOPES = ['personal', 'shared', 'public', 'system']
ORIGINS = ['manual', 'grid', 'import', 'derived', 'patch']
TIERS = ['soul_family', 'family', 'friend', 'public', 'business']


def get_neo4j():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def get_pg():
    return psycopg2.connect(
        host=POSTGRES_HOST, database=POSTGRES_DB,
        user=POSTGRES_USER, password=POSTGRES_PASSWORD,
        cursor_factory=psycopg2.extras.RealDictCursor
    )


def classify_node(labels, canonical_id=None):
    """Classify a node into its Rolodex type."""
    labels_set = set(labels) if labels else set()
    cid = canonical_id or ''

    if 'PersonOwner' in labels_set or cid.startswith('PO-'):
        return 'owner'
    if 'PersonProxy' in labels_set or cid.startswith('PX-'):
        return 'proxy'
    if 'Incarnation' in labels_set or cid.startswith('PI-'):
        return 'incarnation'
    if 'Soul' in labels_set or cid.startswith('PS-'):
        return 'soul'
    if 'GenPerson' in labels_set:
        return 'genealogy'
    if 'Entity' in labels_set or cid.startswith('PE-'):
        return 'entity'
    if 'Person' in labels_set or cid.startswith('PP-'):
        return 'person'
    return 'unknown'


def node_to_dict(record, node_key='n'):
    """Convert Neo4j record to serializable dict."""
    props = dict(record[node_key]) if record[node_key] else {}
    for k, v in props.items():
        if hasattr(v, 'isoformat'):
            props[k] = v.isoformat()
        elif hasattr(v, 'x') and hasattr(v, 'y'):
            props[k] = {"lat": v.y, "lng": v.x}

    labels = record.get('labels', [])
    cid = props.get('canonical_id', '')
    node_type = classify_node(labels, cid)

    props['_element_id'] = record.get('eid', '')
    props['_labels'] = labels
    props['_type'] = node_type
    props['_type_info'] = NODE_TYPES.get(node_type, {})
    return props


# ── Models ──

class NodeCreate(BaseModel):
    label: str  # Primary label: Person, Soul, Entity, Incarnation
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    name: Optional[str] = None
    canonical_id: Optional[str] = None
    domain: str = 'people'
    scope: str = 'personal'
    origin: str = 'manual'
    tier: Optional[str] = None
    entity_type: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class NodeUpdate(BaseModel):
    properties: Dict[str, Any]


class RelCreate(BaseModel):
    target_canonical_id: Optional[str] = None
    target_eid: Optional[str] = None
    rel_type: str
    properties: Optional[Dict[str, str]] = None


class RelDelete(BaseModel):
    target_canonical_id: Optional[str] = None
    target_eid: Optional[str] = None
    rel_type: str


class ResolveEntity(BaseModel):
    entity_canonical_id: str
    person_canonical_id: str


# ── Routes ──

@router.get("/stats")
async def rolodex_stats():
    """Dashboard stats for the Rolodex."""
    driver = get_neo4j()
    try:
        with driver.session() as session:
            r = session.run("""
                MATCH (n)
                WHERE any(l IN labels(n) WHERE l IN ['PersonOwner', 'Person', 'Soul', 'Entity', 'Incarnation', 'PersonProxy', 'GenPerson'])
                WITH n, labels(n) AS lbls
                RETURN
                    count(n) AS total,
                    count(CASE WHEN 'PersonOwner' IN lbls THEN 1 END) AS owners,
                    count(CASE WHEN 'Person' IN lbls AND NOT 'GenPerson' IN lbls AND NOT 'Entity' IN lbls AND NOT 'Soul' IN lbls AND NOT 'PersonOwner' IN lbls THEN 1 END) AS persons,
                    count(CASE WHEN 'Soul' IN lbls THEN 1 END) AS souls,
                    count(CASE WHEN 'Entity' IN lbls AND NOT 'Person' IN lbls AND NOT 'System' IN lbls AND NOT 'Concept' IN lbls THEN 1 END) AS entities,
                    count(CASE WHEN 'Incarnation' IN lbls THEN 1 END) AS incarnations,
                    count(CASE WHEN 'PersonProxy' IN lbls THEN 1 END) AS proxies,
                    count(CASE WHEN 'GenPerson' IN lbls THEN 1 END) AS genealogy
            """).single()

            # Unresolved entities
            unresolved = session.run("""
                MATCH (e:Entity)
                WHERE e.entity_type = 'person_mention' AND e.person_id IS NULL
                RETURN count(e) AS count
            """).single()['count']

            return {
                "total": r['total'],
                "owners": r['owners'],
                "persons": r['persons'],
                "souls": r['souls'],
                "entities": r['entities'],
                "incarnations": r['incarnations'],
                "proxies": r['proxies'],
                "genealogy": r['genealogy'],
                "unresolved": unresolved,
                "node_types": NODE_TYPES,
                "domains": DOMAINS,
                "scopes": SCOPES,
                "origins": ORIGINS,
                "tiers": TIERS,
            }
    finally:
        driver.close()


@router.get("/")
async def browse_directory(
    search: Optional[str] = Query(None),
    node_type: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    scope: Optional[str] = Query(None),
    origin: Optional[str] = Query(None),
    tier: Optional[str] = Query(None),
    sort: str = Query("name"),
    order: str = Query("asc"),
    limit: int = Query(200, ge=1, le=2000),
    offset: int = Query(0, ge=0),
):
    """Browse the directory with Rolodex-aware filtering."""
    driver = get_neo4j()
    try:
        with driver.session() as session:
            where_parts = []
            params = {"limit": limit, "offset": offset}

            # Base filter: person-type nodes only
            base = "any(l IN labels(n) WHERE l IN ['PersonOwner', 'Person', 'Soul', 'Entity', 'Incarnation', 'PersonProxy'])"
            where_parts.append(base)

            # Node type filter
            if node_type and node_type != 'all':
                type_filters = {
                    'owner': "'PersonOwner' IN labels(n)",
                    'person': "'Person' IN labels(n) AND NOT 'GenPerson' IN labels(n) AND NOT 'Entity' IN labels(n) AND NOT 'Soul' IN labels(n) AND NOT 'PersonOwner' IN labels(n)",
                    'soul': "'Soul' IN labels(n)",
                    'entity': "'Entity' IN labels(n) AND NOT 'Concept' IN labels(n) AND NOT 'System' IN labels(n)",
                    'incarnation': "'Incarnation' IN labels(n)",
                    'proxy': "'PersonProxy' IN labels(n)",
                    'genealogy': "'GenPerson' IN labels(n)",
                }
                if node_type in type_filters:
                    where_parts.append(type_filters[node_type])
                    # For genealogy, replace the base filter
                    if node_type == 'genealogy':
                        where_parts = ["'GenPerson' IN labels(n)"]
            else:
                # Default: exclude genealogy
                where_parts.append("NOT 'GenPerson' IN labels(n)")
                # Exclude Concept:Entity and System:Entity
                where_parts.append("NOT ('Concept' IN labels(n) AND 'Entity' IN labels(n))")
                where_parts.append("NOT ('System' IN labels(n) AND 'Entity' IN labels(n))")

            # Universal property filters
            if domain:
                where_parts.append("n.domain = $domain")
                params["domain"] = domain
            if scope:
                where_parts.append("n.scope = $scope")
                params["scope"] = scope
            if origin:
                where_parts.append("n.origin = $origin")
                params["origin"] = origin
            if tier:
                where_parts.append("n.tier = $tier")
                params["tier"] = tier

            # Search
            if search:
                where_parts.append("""(
                    toLower(COALESCE(n.full_name, '')) CONTAINS toLower($search)
                    OR toLower(COALESCE(n.display_name, '')) CONTAINS toLower($search)
                    OR toLower(COALESCE(n.name, '')) CONTAINS toLower($search)
                    OR toLower(COALESCE(n.canonical_id, '')) CONTAINS toLower($search)
                    OR toLower(COALESCE(n.spiritual_name, '')) CONTAINS toLower($search)
                    OR toLower(COALESCE(n.descriptor, '')) CONTAINS toLower($search)
                )""")
                params["search"] = search

            where_clause = " AND ".join(where_parts)

            sort_map = {
                'name': 'COALESCE(n.display_name, n.full_name, n.name, "")',
                'canonical_id': 'COALESCE(n.canonical_id, "")',
                'domain': 'COALESCE(n.domain, "")',
                'tier': 'COALESCE(n.tier, "")',
                'type': 'head(labels(n))',
            }
            sort_expr = sort_map.get(sort, sort_map['name'])
            sort_dir = 'DESC' if order.lower() == 'desc' else 'ASC'

            query = f"""
                MATCH (n)
                WHERE {where_clause}
                WITH n, elementId(n) AS eid, labels(n) AS labels
                OPTIONAL MATCH (n)-[rel]-()
                WITH n, eid, labels, count(DISTINCT rel) AS rel_count
                RETURN n, eid, labels, rel_count
                ORDER BY {sort_expr} {sort_dir}
                SKIP $offset LIMIT $limit
            """
            results = session.run(query, **params)
            nodes = []
            for rec in results:
                d = node_to_dict(rec, 'n')
                d['_rel_count'] = rec['rel_count']
                nodes.append(d)

            count_query = f"""
                MATCH (n)
                WHERE {where_clause}
                RETURN count(n) AS total
            """
            total = session.run(count_query, **params).single()['total']

            return {"nodes": nodes, "total": total}
    finally:
        driver.close()


@router.get("/unresolved")
async def unresolved_entities():
    """List entity mentions that haven't been resolved to a person."""
    driver = get_neo4j()
    try:
        with driver.session() as session:
            results = session.run("""
                MATCH (e:Entity)
                WHERE e.entity_type = 'person_mention' AND e.person_id IS NULL
                OPTIONAL MATCH (e)-[r]-()
                WITH e, elementId(e) AS eid, labels(e) AS labels, count(r) AS rel_count
                RETURN e AS n, eid, labels, rel_count
                ORDER BY e.name
            """)
            nodes = []
            for rec in results:
                d = node_to_dict(rec, 'n')
                d['_rel_count'] = rec['rel_count']
                nodes.append(d)
            return {"nodes": nodes, "total": len(nodes)}
    finally:
        driver.close()


@router.get("/graph")
async def rolodex_graph(
    node_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    """Graph data for visualization. Returns nodes + edges."""
    driver = get_neo4j()
    try:
        with driver.session() as session:
            # Get Rolodex nodes (exclude bulk genealogy and concept/system entities)
            type_filter = "true"
            if node_type and node_type != 'all':
                type_filters = {
                    'owner': "'PersonOwner' IN labels(n)",
                    'person': "'Person' IN labels(n) AND NOT 'GenPerson' IN labels(n) AND NOT 'Entity' IN labels(n) AND NOT 'Soul' IN labels(n) AND NOT 'PersonOwner' IN labels(n)",
                    'soul': "'Soul' IN labels(n)",
                    'entity': "'Entity' IN labels(n) AND NOT 'Concept' IN labels(n) AND NOT 'System' IN labels(n)",
                    'incarnation': "'Incarnation' IN labels(n)",
                }
                type_filter = type_filters.get(node_type, "true")

            nodes_result = session.run(f"""
                MATCH (n)
                WHERE any(l IN labels(n) WHERE l IN ['PersonOwner', 'Person', 'Soul', 'Entity', 'Incarnation'])
                  AND NOT 'GenPerson' IN labels(n)
                  AND NOT ('Concept' IN labels(n) AND 'Entity' IN labels(n))
                  AND NOT ('System' IN labels(n) AND 'Entity' IN labels(n))
                  AND {type_filter}
                RETURN elementId(n) AS eid,
                       COALESCE(n.display_name, n.full_name, n.name, 'Unknown') AS name,
                       n.canonical_id AS canonical_id,
                       n.domain AS domain,
                       n.tier AS tier,
                       labels(n) AS labels
                LIMIT $limit
            """, limit=limit)

            nodes = []
            node_eids = set()
            for r in nodes_result:
                node_type_val = classify_node(r['labels'], r['canonical_id'])
                nodes.append({
                    "eid": r['eid'],
                    "name": r['name'],
                    "canonical_id": r['canonical_id'],
                    "domain": r['domain'],
                    "tier": r['tier'],
                    "type": node_type_val,
                    "color": NODE_TYPES.get(node_type_val, {}).get('color', '#64748b'),
                })
                node_eids.add(r['eid'])

            # Get edges
            edges_result = session.run("""
                MATCH (a)-[r]->(b)
                WHERE elementId(a) IN $eids AND elementId(b) IN $eids
                RETURN elementId(a) AS source, elementId(b) AS target,
                       type(r) AS rel_type
            """, eids=list(node_eids))

            edges = [{"source": r['source'], "target": r['target'], "type": r['rel_type']} for r in edges_result]

            return {"nodes": nodes, "edges": edges}
    finally:
        driver.close()


@router.get("/node/{cid}")
async def get_node(cid: str):
    """Get full node detail by canonical_id."""
    driver = get_neo4j()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (n {canonical_id: $cid})
                RETURN n, elementId(n) AS eid, labels(n) AS labels
            """, cid=cid)
            rec = result.single()
            if not rec:
                raise HTTPException(status_code=404, detail=f"Node {cid} not found")

            node = node_to_dict(rec, 'n')

            # Get relationships
            rels_result = session.run("""
                MATCH (n {canonical_id: $cid})-[r]-(other)
                WITH r, other, elementId(other) AS other_eid,
                     labels(other) AS other_labels,
                     CASE WHEN startNode(r) = n THEN 'outgoing' ELSE 'incoming' END AS direction
                RETURN type(r) AS rel_type,
                       properties(r) AS rel_props,
                       direction,
                       other_eid,
                       other_labels,
                       COALESCE(other.display_name, other.full_name, other.name) AS other_name,
                       other.canonical_id AS other_canonical
                ORDER BY rel_type, other_name
            """, cid=cid)

            relationships = []
            for r in rels_result:
                rel = {
                    "type": r['rel_type'],
                    "direction": r['direction'],
                    "properties": {k: str(v) for k, v in (r['rel_props'] or {}).items()},
                    "target_eid": r['other_eid'],
                    "target_labels": r['other_labels'],
                    "target_name": r['other_name'],
                    "target_canonical": r['other_canonical'],
                    "target_type": classify_node(r['other_labels'], r['other_canonical']),
                }
                relationships.append(rel)

            node['_relationships'] = relationships

            # Get Postgres data if this is a PP- person
            if cid.startswith('PP-'):
                try:
                    conn = get_pg()
                    cur = conn.cursor()
                    cur.execute("SELECT * FROM rolodex.persons WHERE canonical_id = %s", (cid,))
                    pg_person = cur.fetchone()
                    if pg_person:
                        node['_pg_person'] = dict(pg_person)

                    cur.execute("SELECT * FROM rolodex.contacts WHERE uid = (SELECT uid FROM rolodex.graph_nodes WHERE canonical_id = %s)", (cid,))
                    contacts = cur.fetchall()
                    node['_contacts'] = [dict(c) for c in contacts]

                    cur.execute("SELECT * FROM rolodex.astro_charts WHERE uid = (SELECT uid FROM rolodex.graph_nodes WHERE canonical_id = %s)", (cid,))
                    charts = cur.fetchall()
                    node['_astro_charts'] = [dict(c) for c in charts]

                    conn.close()
                except Exception:
                    pass  # Postgres data is supplementary

            return node
    finally:
        driver.close()


@router.get("/node/{cid}/graph")
async def node_ego_graph(cid: str, depth: int = Query(2, ge=1, le=3)):
    """Ego-centric graph for a specific node."""
    driver = get_neo4j()
    try:
        with driver.session() as session:
            nodes_result = session.run("""
                MATCH (center {canonical_id: $cid})
                MATCH path = (center)-[*1..""" + str(depth) + """]-()
                WITH nodes(path) AS ns
                UNWIND ns AS n
                WITH DISTINCT n
                WHERE any(l IN labels(n) WHERE l IN ['PersonOwner', 'Person', 'Soul', 'Entity', 'Incarnation', 'Lineage'])
                  AND NOT 'GenPerson' IN labels(n)
                RETURN elementId(n) AS eid,
                       COALESCE(n.display_name, n.full_name, n.name, 'Unknown') AS name,
                       n.canonical_id AS canonical_id,
                       n.domain AS domain,
                       labels(n) AS labels
            """, cid=cid)

            nodes = []
            node_eids = set()
            for r in nodes_result:
                nt = classify_node(r['labels'], r['canonical_id'])
                nodes.append({
                    "eid": r['eid'],
                    "name": r['name'],
                    "canonical_id": r['canonical_id'],
                    "domain": r['domain'],
                    "type": nt,
                    "color": NODE_TYPES.get(nt, {}).get('color', '#64748b'),
                    "is_center": r['canonical_id'] == cid,
                })
                node_eids.add(r['eid'])

            edges_result = session.run("""
                MATCH (a)-[r]->(b)
                WHERE elementId(a) IN $eids AND elementId(b) IN $eids
                RETURN elementId(a) AS source, elementId(b) AS target,
                       type(r) AS rel_type
            """, eids=list(node_eids))

            edges = [{"source": r['source'], "target": r['target'], "type": r['rel_type']} for r in edges_result]

            return {"nodes": nodes, "edges": edges, "center": cid}
    finally:
        driver.close()


@router.post("/resolve")
async def resolve_entity(body: ResolveEntity):
    """Link an entity mention to a canonical person."""
    driver = get_neo4j()
    try:
        with driver.session() as session:
            # Verify entity exists
            entity = session.run(
                "MATCH (e:Entity {canonical_id: $ecid}) RETURN e",
                ecid=body.entity_canonical_id
            ).single()
            if not entity:
                raise HTTPException(status_code=404, detail=f"Entity {body.entity_canonical_id} not found")

            # Verify person exists
            person = session.run(
                "MATCH (p:Person {canonical_id: $pcid}) RETURN p",
                pcid=body.person_canonical_id
            ).single()
            if not person:
                raise HTTPException(status_code=404, detail=f"Person {body.person_canonical_id} not found")

            # Set person_id and create REFERS_TO
            session.run("""
                MATCH (e:Entity {canonical_id: $ecid})
                MATCH (p:Person {canonical_id: $pcid})
                SET e.person_id = $pcid, e.entity_type = 'person_mention'
                MERGE (e)-[:REFERS_TO]->(p)
            """, ecid=body.entity_canonical_id, pcid=body.person_canonical_id)

            return {
                "status": "resolved",
                "entity": body.entity_canonical_id,
                "person": body.person_canonical_id,
            }
    finally:
        driver.close()


@router.post("/node", status_code=201)
async def create_node(body: NodeCreate):
    """Create a new node in the Rolodex."""
    driver = get_neo4j()
    now = datetime.now(timezone.utc).isoformat()
    try:
        with driver.session() as session:
            name = body.full_name or body.display_name or body.name or 'Unknown'
            cid = body.canonical_id
            if not cid:
                prefix = {'Person': 'PP', 'Soul': 'PS', 'Entity': 'PE', 'Incarnation': 'PI'}.get(body.label, 'PP')
                safe_name = name.replace(' ', '').replace("'", '')
                cid = f"{prefix}-{safe_name}"

            # Check for collision
            existing = session.run(
                "MATCH (n {canonical_id: $cid}) RETURN n", cid=cid
            ).single()
            if existing:
                raise HTTPException(status_code=409, detail=f"Node {cid} already exists")

            props = {
                "canonical_id": cid,
                "display_name": body.display_name or name,
                "domain": body.domain,
                "scope": body.scope,
                "origin": body.origin,
                "created_at": now,
                "updated_at": now,
            }
            if body.full_name:
                props["full_name"] = body.full_name
            if body.name:
                props["name"] = body.name
            if body.tier:
                props["tier"] = body.tier
            if body.entity_type:
                props["entity_type"] = body.entity_type
            if body.properties:
                props.update(body.properties)

            label = body.label
            result = session.run(f"""
                CREATE (n:{label} $props)
                RETURN n, elementId(n) AS eid, labels(n) AS labels
            """, props=props)

            rec = result.single()
            return node_to_dict(rec, 'n')
    finally:
        driver.close()


@router.patch("/node/{cid}")
async def update_node(cid: str, body: NodeUpdate):
    """Update node properties."""
    driver = get_neo4j()
    try:
        with driver.session() as session:
            existing = session.run(
                "MATCH (n {canonical_id: $cid}) RETURN n", cid=cid
            ).single()
            if not existing:
                raise HTTPException(status_code=404, detail=f"Node {cid} not found")

            updates = body.properties
            if not updates:
                raise HTTPException(status_code=400, detail="No properties to update")

            updates['updated_at'] = datetime.now(timezone.utc).isoformat()

            set_parts = []
            params = {"cid": cid}
            for i, (key, val) in enumerate(updates.items()):
                pname = f"v{i}"
                set_parts.append(f"n.{key} = ${pname}")
                params[pname] = val

            result = session.run(f"""
                MATCH (n {{canonical_id: $cid}})
                SET {', '.join(set_parts)}
                RETURN n, elementId(n) AS eid, labels(n) AS labels
            """, **params)

            rec = result.single()
            return node_to_dict(rec, 'n')
    finally:
        driver.close()


@router.post("/node/{cid}/rel", status_code=201)
async def create_relationship(cid: str, body: RelCreate):
    """Create a relationship from this node to another."""
    driver = get_neo4j()
    try:
        with driver.session() as session:
            # Find target
            target_match = ""
            params = {"cid": cid}
            if body.target_canonical_id:
                target_match = "MATCH (t {canonical_id: $tcid})"
                params["tcid"] = body.target_canonical_id
            elif body.target_eid:
                target_match = "MATCH (t) WHERE elementId(t) = $teid"
                params["teid"] = body.target_eid
            else:
                raise HTTPException(status_code=400, detail="Provide target_canonical_id or target_eid")

            rel_type = body.rel_type.upper().replace(' ', '_')
            props_str = ""
            if body.properties:
                prop_parts = []
                for i, (k, v) in enumerate(body.properties.items()):
                    pname = f"rp{i}"
                    prop_parts.append(f"{k}: ${pname}")
                    params[pname] = v
                props_str = " {" + ", ".join(prop_parts) + "}"

            result = session.run(f"""
                MATCH (s {{canonical_id: $cid}})
                {target_match}
                CREATE (s)-[r:{rel_type}{props_str}]->(t)
                RETURN type(r) AS rtype, elementId(r) AS rel_eid
            """, **params)

            rec = result.single()
            if not rec:
                raise HTTPException(status_code=404, detail="Source or target not found")

            return {"status": "created", "type": rec['rtype'], "rel_eid": rec['rel_eid']}
    finally:
        driver.close()


@router.delete("/node/{cid}/rel")
async def delete_relationship(cid: str, body: RelDelete):
    """Delete a relationship from this node."""
    driver = get_neo4j()
    try:
        with driver.session() as session:
            rel_type = body.rel_type.upper().replace(' ', '_')
            params = {"cid": cid}

            target_match = ""
            if body.target_canonical_id:
                target_match = "AND t.canonical_id = $tcid"
                params["tcid"] = body.target_canonical_id
            elif body.target_eid:
                target_match = "AND elementId(t) = $teid"
                params["teid"] = body.target_eid

            result = session.run(f"""
                MATCH (s {{canonical_id: $cid}})-[r:{rel_type}]-(t)
                WHERE true {target_match}
                WITH r LIMIT 1
                DELETE r
                RETURN count(*) AS deleted
            """, **params)

            count = result.single()['deleted']
            if count == 0:
                raise HTTPException(status_code=404, detail="Relationship not found")

            return {"status": "deleted", "type": rel_type}
    finally:
        driver.close()


@router.get("/search")
async def search_nodes(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=50)):
    """Search all Rolodex nodes for relationship target picker."""
    driver = get_neo4j()
    try:
        with driver.session() as session:
            results = session.run("""
                MATCH (n)
                WHERE any(l IN labels(n) WHERE l IN ['PersonOwner', 'Person', 'Soul', 'Entity', 'Incarnation'])
                  AND NOT 'GenPerson' IN labels(n)
                  AND (
                    toLower(COALESCE(n.full_name, '')) CONTAINS toLower($q)
                    OR toLower(COALESCE(n.display_name, '')) CONTAINS toLower($q)
                    OR toLower(COALESCE(n.name, '')) CONTAINS toLower($q)
                    OR toLower(COALESCE(n.canonical_id, '')) CONTAINS toLower($q)
                    OR toLower(COALESCE(n.spiritual_name, '')) CONTAINS toLower($q)
                  )
                RETURN elementId(n) AS eid,
                       COALESCE(n.display_name, n.full_name, n.name) AS name,
                       n.canonical_id AS canonical_id,
                       labels(n) AS labels
                ORDER BY name
                LIMIT $limit
            """, q=q, limit=limit)

            nodes = [{
                "eid": r['eid'],
                "name": r['name'],
                "canonical_id": r['canonical_id'],
                "labels": r['labels'],
                "type": classify_node(r['labels'], r['canonical_id']),
            } for r in results]

            return {"nodes": nodes}
    finally:
        driver.close()
