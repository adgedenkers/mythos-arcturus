#!/usr/bin/env python3
"""
SDIP Graph Builder
Creates Neo4j nodes and relationships from SDIP document/chunk data.
Builds SDIPDocument, SDIPChunk, SDIPTopic nodes and cross-reference relationships.

Usage:
    sdip-graph                          # build/update full graph
    sdip-graph --docs-only              # only document + topic nodes
    sdip-graph --chunks                 # include chunk nodes (larger graph)
    sdip-graph --refs                   # detect cross-references between documents
    sdip-graph --propagate              # run sensitivity propagation
    sdip-graph --stats                  # show graph statistics
    sdip-graph --clear                  # wipe all SDIP graph data (with confirmation)
    sdip-graph --dry-run                # show what would be built
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, '/opt/mythos/sdip')

from config import get_db_connection

# Neo4j connection
NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.environ.get('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'neo4j')


def get_neo4j_driver():
    """Get a Neo4j driver."""
    from neo4j import GraphDatabase
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def ensure_constraints(driver):
    """Create uniqueness constraints for SDIP nodes."""
    constraints = [
        "CREATE CONSTRAINT sdip_doc_id IF NOT EXISTS FOR (d:SDIPDocument) REQUIRE d.doc_id IS UNIQUE",
        "CREATE CONSTRAINT sdip_topic_name IF NOT EXISTS FOR (t:SDIPTopic) REQUIRE t.name IS UNIQUE",
        "CREATE CONSTRAINT sdip_system_name IF NOT EXISTS FOR (s:SDIPSystem) REQUIRE s.name IS UNIQUE",
        "CREATE CONSTRAINT sdip_chunk_id IF NOT EXISTS FOR (c:SDIPChunk) REQUIRE c.chunk_id IS UNIQUE",
    ]
    with driver.session() as session:
        for cypher in constraints:
            try:
                session.run(cypher)
            except Exception as e:
                # Constraint may already exist
                if 'already exists' not in str(e).lower():
                    print(f"  ⚠ Constraint warning: {e}")


# ── Topic Extraction ───────────────────────────────────────────

# Keywords that map to known topic clusters
TOPIC_KEYWORDS = {
    # Mythos system
    'iris': 'Iris',
    'mythos': 'Mythos',
    'arcturus': 'Arcturus',
    'telegram': 'Telegram Bot',
    'fastapi': 'FastAPI',
    'neo4j': 'Neo4j',
    'postgresql': 'PostgreSQL',
    'postgres': 'PostgreSQL',
    'qdrant': 'Qdrant',
    'redis': 'Redis',
    'ollama': 'Ollama',

    # Spiritual
    'astrology': 'Astrology',
    'natal chart': 'Astrology',
    'tarot': 'Tarot',
    'numerology': 'Numerology',
    'arcturian': 'Arcturian Grid',
    'consciousness': 'Consciousness',
    'spiral time': 'Spiral Time',
    'ontology': 'Ontology',
    'merovingian': 'Merovingian Lineage',
    'cathar': 'Cathar History',
    'montségur': 'Cathar History',

    # People
    "ka'tuar'el": "Ka'tuar'el",
    'seraphe': 'Seraphe',
    'fitz': 'Fitz',

    # Technical domains
    'finance': 'Finance System',
    'voice memo': 'Voice Pipeline',
    'transcription': 'Voice Pipeline',
    'patch': 'Patch System',
    'genealogy': 'Genealogy',
    'immich': 'Photo System',
    'sdip': 'SDIP',

    # Architecture
    'api': 'API Design',
    'database': 'Database Architecture',
    'migration': 'Database Architecture',
    'docker': 'Infrastructure',
    'systemd': 'Infrastructure',
    'nginx': 'Infrastructure',
    'cloudflare': 'Infrastructure',
}

# Systems referenced in documents
SYSTEM_KEYWORDS = {
    'mythos': 'Mythos',
    'iris': 'Iris',
    'arcturus': 'Arcturus',
    'telegram bot': 'Telegram Bot',
    'fastapi': 'FastAPI API',
    'command center': 'Command Center',
    'vault-curator': 'Vault Curator',
    'vault-sorter': 'Vault Sorter',
    'sdip': 'SDIP',
    'finance': 'Finance System',
    'patch monitor': 'Patch Monitor',
    'voice memo': 'Voice Pipeline',
    'immich': 'Immich',
}


def extract_topics(text: str, path: str = '') -> list[str]:
    """Extract topic labels from text content and file path."""
    topics = set()
    combined = (text + ' ' + path).lower()

    for keyword, topic in TOPIC_KEYWORDS.items():
        if keyword in combined:
            topics.add(topic)

    # Path-based topic inference
    path_lower = path.lower()
    if 'astrology/' in path_lower:
        topics.add('Astrology')
    if 'spiritual/' in path_lower or 'scrolls/' in path_lower:
        topics.add('Spiritual')
    if 'technical/' in path_lower:
        topics.add('Technical')
    if 'personal/' in path_lower:
        topics.add('Personal')
    if 'finance/' in path_lower:
        topics.add('Finance System')
    if 'genealogy/' in path_lower:
        topics.add('Genealogy')

    return list(topics)


def extract_systems(text: str) -> list[str]:
    """Extract system/service references from text."""
    systems = set()
    text_lower = text.lower()

    for keyword, system in SYSTEM_KEYWORDS.items():
        if keyword in text_lower:
            systems.add(system)

    return list(systems)


def detect_references(doc_path: str, doc_text: str, all_paths: dict) -> list[int]:
    """
    Detect cross-references to other documents.
    Returns list of referenced document IDs.
    """
    refs = set()

    # Look for markdown links: [text](path) or [[wikilinks]]
    # Markdown links
    for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', doc_text):
        link_target = match.group(2)
        # Normalize and look up
        for path, doc_id in all_paths.items():
            if link_target.rstrip('/').endswith(path.rstrip('/')):
                refs.add(doc_id)
            elif Path(link_target).stem == Path(path).stem:
                refs.add(doc_id)

    # Wiki-style links: [[filename]] or [[filename|display]]
    for match in re.finditer(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', doc_text):
        link_name = match.group(1).strip()
        for path, doc_id in all_paths.items():
            if Path(path).stem.lower() == link_name.lower():
                refs.add(doc_id)

    # Remove self-references
    self_id = all_paths.get(doc_path)
    if self_id in refs:
        refs.discard(self_id)

    return list(refs)


# ── Graph Building ─────────────────────────────────────────────

def build_document_nodes(driver, pg_conn, dry_run: bool = False):
    """Create SDIPDocument nodes from PostgreSQL data."""
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT d.id, d.relative_path, d.filename, d.file_format,
                   d.category, d.quality, d.status,
                   (SELECT COUNT(*) FROM sdip_chunks c WHERE c.document_id = d.id) as chunk_count,
                   (SELECT SUM(c.word_count) FROM sdip_chunks c WHERE c.document_id = d.id) as total_words,
                   (SELECT MAX(c.sensitivity_level) FROM sdip_chunks c WHERE c.document_id = d.id) as max_sensitivity
            FROM sdip_documents d
            WHERE d.status = 'active'
            ORDER BY d.id
        """)
        docs = cur.fetchall()

    print(f"  Building {len(docs)} document nodes...")
    if dry_run:
        return len(docs)

    with driver.session() as session:
        for doc_id, path, filename, fmt, category, quality, status, chunks, words, sensitivity in docs:
            session.run("""
                MERGE (d:SDIPDocument {doc_id: $doc_id})
                SET d.path = $path,
                    d.filename = $filename,
                    d.format = $format,
                    d.category = $category,
                    d.quality = $quality,
                    d.status = $status,
                    d.chunk_count = $chunks,
                    d.word_count = $words,
                    d.max_sensitivity = $sensitivity
            """, doc_id=doc_id, path=path, filename=filename, format=fmt,
                category=category or '', quality=quality or '', status=status,
                chunks=chunks or 0, words=words or 0, sensitivity=sensitivity or 'PUBLIC')

    return len(docs)


def build_topic_nodes(driver, pg_conn, dry_run: bool = False):
    """Create SDIPTopic nodes and COVERS_TOPIC relationships."""
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT d.id, d.relative_path,
                   string_agg(c.content_text, ' ') as full_text
            FROM sdip_documents d
            JOIN sdip_chunks c ON c.document_id = d.id
            WHERE d.status = 'active'
            GROUP BY d.id, d.relative_path
        """)
        docs = cur.fetchall()

    topic_counts = defaultdict(int)
    doc_topics = {}

    for doc_id, path, text in docs:
        # Limit text to first 5000 chars for topic extraction
        topics = extract_topics(text[:5000], path)
        doc_topics[doc_id] = topics
        for t in topics:
            topic_counts[t] += 1

    print(f"  Extracted {len(topic_counts)} topics across {len(docs)} documents...")
    if dry_run:
        for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1])[:15]:
            print(f"    {topic}: {count} docs")
        return len(topic_counts)

    with driver.session() as session:
        # Create topic nodes
        for topic, count in topic_counts.items():
            session.run("""
                MERGE (t:SDIPTopic {name: $name})
                SET t.document_count = $count
            """, name=topic, count=count)

        # Create COVERS_TOPIC relationships
        for doc_id, topics in doc_topics.items():
            for topic in topics:
                weight = 1.0 / len(topics) if topics else 0
                session.run("""
                    MATCH (d:SDIPDocument {doc_id: $doc_id})
                    MATCH (t:SDIPTopic {name: $topic})
                    MERGE (d)-[r:COVERS_TOPIC]->(t)
                    SET r.weight = $weight
                """, doc_id=doc_id, topic=topic, weight=weight)

    return len(topic_counts)


def build_system_nodes(driver, pg_conn, dry_run: bool = False):
    """Create SDIPSystem nodes and DESCRIBES_SYSTEM relationships."""
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT d.id, string_agg(c.content_text, ' ') as full_text
            FROM sdip_documents d
            JOIN sdip_chunks c ON c.document_id = d.id
            WHERE d.status = 'active'
            GROUP BY d.id
        """)
        docs = cur.fetchall()

    system_counts = defaultdict(int)
    doc_systems = {}

    for doc_id, text in docs:
        systems = extract_systems(text[:5000])
        doc_systems[doc_id] = systems
        for s in systems:
            system_counts[s] += 1

    print(f"  Extracted {len(system_counts)} system references...")
    if dry_run:
        for system, count in sorted(system_counts.items(), key=lambda x: -x[1]):
            print(f"    {system}: {count} docs")
        return len(system_counts)

    with driver.session() as session:
        for system, count in system_counts.items():
            session.run("""
                MERGE (s:SDIPSystem {name: $name})
                SET s.document_count = $count
            """, name=system, count=count)

        for doc_id, systems in doc_systems.items():
            for system in systems:
                session.run("""
                    MATCH (d:SDIPDocument {doc_id: $doc_id})
                    MATCH (s:SDIPSystem {name: $system})
                    MERGE (d)-[:DESCRIBES_SYSTEM]->(s)
                """, doc_id=doc_id, system=system)

    return len(system_counts)


def build_chunk_nodes(driver, pg_conn, dry_run: bool = False):
    """Create SDIPChunk nodes for sensitive chunks and link to documents."""
    with pg_conn.cursor() as cur:
        # Only create chunk nodes for non-PUBLIC chunks to keep graph manageable
        cur.execute("""
            SELECT c.id, c.document_id, c.chunk_index, c.parent_heading,
                   c.word_count, c.sensitivity_level, c.sensitivity_tags
            FROM sdip_chunks c
            WHERE c.sensitivity_level != 'PUBLIC'
            ORDER BY c.document_id, c.chunk_index
        """)
        chunks = cur.fetchall()

    print(f"  Building {len(chunks)} chunk nodes (non-PUBLIC only)...")
    if dry_run:
        return len(chunks)

    with driver.session() as session:
        for chunk_id, doc_id, idx, heading, words, level, tags in chunks:
            session.run("""
                MERGE (c:SDIPChunk {chunk_id: $chunk_id})
                SET c.document_id = $doc_id,
                    c.chunk_index = $idx,
                    c.heading = $heading,
                    c.word_count = $words,
                    c.sensitivity_level = $level,
                    c.sensitivity_tags = $tags
            """, chunk_id=chunk_id, doc_id=doc_id, idx=idx,
                heading=heading or '', words=words or 0,
                level=level, tags=tags or [])

            # Link to parent document
            session.run("""
                MATCH (d:SDIPDocument {doc_id: $doc_id})
                MATCH (c:SDIPChunk {chunk_id: $chunk_id})
                MERGE (d)-[:HAS_CHUNK {index: $idx}]->(c)
            """, doc_id=doc_id, chunk_id=chunk_id, idx=idx)

    return len(chunks)


def build_references(driver, pg_conn, dry_run: bool = False):
    """Detect and create REFERENCES relationships between documents."""
    with pg_conn.cursor() as cur:
        cur.execute("""
            SELECT d.id, d.relative_path,
                   string_agg(c.content_text, ' ') as full_text
            FROM sdip_documents d
            JOIN sdip_chunks c ON c.document_id = d.id
            WHERE d.status = 'active'
            GROUP BY d.id, d.relative_path
        """)
        docs = cur.fetchall()

    # Build path->id lookup
    all_paths = {path: doc_id for doc_id, path, _ in docs}

    ref_count = 0
    for doc_id, path, text in docs:
        refs = detect_references(path, text[:10000], all_paths)
        if refs:
            ref_count += len(refs)
            if not dry_run:
                with driver.session() as session:
                    for ref_id in refs:
                        session.run("""
                            MATCH (a:SDIPDocument {doc_id: $from_id})
                            MATCH (b:SDIPDocument {doc_id: $to_id})
                            MERGE (a)-[:REFERENCES]->(b)
                        """, from_id=doc_id, to_id=ref_id)

    print(f"  Found {ref_count} cross-references...")
    return ref_count


def run_sensitivity_propagation(driver, dry_run: bool = False):
    """
    Layer 3: Propagate sensitivity through document references.
    If Doc A has RESTRICTED chunks and Doc B references Doc A,
    Doc B gets a SENSITIVITY_SPREAD relationship.
    """
    if dry_run:
        print("  [DRY RUN] Would run sensitivity propagation...")
        return 0

    with driver.session() as session:
        # Find documents that reference sensitive documents
        result = session.run("""
            MATCH (a:SDIPDocument)-[:REFERENCES]->(b:SDIPDocument)
            WHERE b.max_sensitivity IN ['SENSITIVE', 'RESTRICTED']
            AND NOT (a)-[:SENSITIVITY_SPREAD]->(b)
            RETURN a.doc_id as from_id, b.doc_id as to_id, b.max_sensitivity as level
        """)

        spread_count = 0
        for record in result:
            session.run("""
                MATCH (a:SDIPDocument {doc_id: $from_id})
                MATCH (b:SDIPDocument {doc_id: $to_id})
                MERGE (a)-[r:SENSITIVITY_SPREAD]->(b)
                SET r.propagated_level = $level
            """, from_id=record['from_id'], to_id=record['to_id'],
                level=record['level'])
            spread_count += 1

    print(f"  Propagated sensitivity to {spread_count} documents...")
    return spread_count


# ── Stats ──────────────────────────────────────────────────────

def show_stats():
    """Show SDIP graph statistics."""
    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            # Node counts
            doc_count = session.run("MATCH (d:SDIPDocument) RETURN count(d) as c").single()['c']
            topic_count = session.run("MATCH (t:SDIPTopic) RETURN count(t) as c").single()['c']
            system_count = session.run("MATCH (s:SDIPSystem) RETURN count(s) as c").single()['c']
            chunk_count = session.run("MATCH (c:SDIPChunk) RETURN count(c) as c").single()['c']

            # Relationship counts
            covers = session.run("MATCH ()-[r:COVERS_TOPIC]->() RETURN count(r) as c").single()['c']
            describes = session.run("MATCH ()-[r:DESCRIBES_SYSTEM]->() RETURN count(r) as c").single()['c']
            refs = session.run("MATCH ()-[r:REFERENCES]->() RETURN count(r) as c").single()['c']
            has_chunk = session.run("MATCH ()-[r:HAS_CHUNK]->() RETURN count(r) as c").single()['c']
            spread = session.run("MATCH ()-[r:SENSITIVITY_SPREAD]->() RETURN count(r) as c").single()['c']

            # Top topics
            top_topics = session.run("""
                MATCH (t:SDIPTopic)
                RETURN t.name as name, t.document_count as count
                ORDER BY count DESC LIMIT 15
            """).data()

            # Top systems
            top_systems = session.run("""
                MATCH (s:SDIPSystem)
                RETURN s.name as name, s.document_count as count
                ORDER BY count DESC LIMIT 10
            """).data()

            # Sensitivity spread
            spread_docs = session.run("""
                MATCH (a:SDIPDocument)-[r:SENSITIVITY_SPREAD]->(b:SDIPDocument)
                RETURN a.path as from_path, b.path as to_path, r.propagated_level as level
                LIMIT 10
            """).data()

        print("SDIP Graph Statistics")
        print("=" * 50)
        print(f"\nNodes:")
        print(f"  SDIPDocument: {doc_count}")
        print(f"  SDIPTopic:    {topic_count}")
        print(f"  SDIPSystem:   {system_count}")
        print(f"  SDIPChunk:    {chunk_count}")

        print(f"\nRelationships:")
        print(f"  COVERS_TOPIC:      {covers}")
        print(f"  DESCRIBES_SYSTEM:  {describes}")
        print(f"  REFERENCES:        {refs}")
        print(f"  HAS_CHUNK:         {has_chunk}")
        print(f"  SENSITIVITY_SPREAD: {spread}")

        if top_topics:
            print(f"\nTop Topics:")
            for t in top_topics:
                print(f"  {t['name']}: {t['count']} docs")

        if top_systems:
            print(f"\nSystems:")
            for s in top_systems:
                print(f"  {s['name']}: {s['count']} docs")

        if spread_docs:
            print(f"\nSensitivity Spread:")
            for s in spread_docs:
                print(f"  {s['from_path'][:50]} ← [{s['level']}] ← {s['to_path'][:50]}")

    finally:
        driver.close()


def clear_graph():
    """Remove all SDIP nodes and relationships."""
    confirm = input("⚠ This will delete ALL SDIP graph data. Type 'yes' to confirm: ")
    if confirm.strip().lower() != 'yes':
        print("Cancelled.")
        return

    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            session.run("MATCH (n:SDIPChunk) DETACH DELETE n")
            session.run("MATCH (n:SDIPDocument) DETACH DELETE n")
            session.run("MATCH (n:SDIPTopic) DETACH DELETE n")
            session.run("MATCH (n:SDIPSystem) DETACH DELETE n")
        print("✓ All SDIP graph data cleared.")
    finally:
        driver.close()


# ── Main Pipeline ──────────────────────────────────────────────

def build_graph(docs_only: bool = False, include_chunks: bool = False,
                include_refs: bool = False, propagate: bool = False,
                dry_run: bool = False):
    """Main graph building pipeline."""
    print(f"{'[DRY RUN] ' if dry_run else ''}SDIP Graph Builder")

    driver = get_neo4j_driver()
    pg_conn = get_db_connection()

    try:
        if not dry_run:
            ensure_constraints(driver)

        # Always build document nodes + topics + systems
        n_docs = build_document_nodes(driver, pg_conn, dry_run)
        n_topics = build_topic_nodes(driver, pg_conn, dry_run)
        n_systems = build_system_nodes(driver, pg_conn, dry_run)

        n_chunks = 0
        n_refs = 0
        n_spread = 0

        if not docs_only:
            if include_chunks:
                n_chunks = build_chunk_nodes(driver, pg_conn, dry_run)

            if include_refs:
                n_refs = build_references(driver, pg_conn, dry_run)

            if propagate:
                n_spread = run_sensitivity_propagation(driver, dry_run)

        print(f"\n✓ Graph build complete:")
        print(f"  Documents: {n_docs}")
        print(f"  Topics:    {n_topics}")
        print(f"  Systems:   {n_systems}")
        if n_chunks:
            print(f"  Chunks:    {n_chunks}")
        if n_refs:
            print(f"  References: {n_refs}")
        if n_spread:
            print(f"  Propagated: {n_spread}")

    finally:
        driver.close()
        pg_conn.close()


def main():
    parser = argparse.ArgumentParser(description='SDIP Graph Builder')
    parser.add_argument('--docs-only', action='store_true',
                        help='Only build document + topic + system nodes')
    parser.add_argument('--chunks', action='store_true',
                        help='Include chunk nodes (non-PUBLIC only)')
    parser.add_argument('--refs', action='store_true',
                        help='Detect cross-references between documents')
    parser.add_argument('--propagate', action='store_true',
                        help='Run sensitivity propagation through references')
    parser.add_argument('--stats', action='store_true',
                        help='Show graph statistics')
    parser.add_argument('--clear', action='store_true',
                        help='Clear all SDIP graph data')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be built')
    parser.add_argument('--full', action='store_true',
                        help='Build everything: docs, chunks, refs, propagation')

    args = parser.parse_args()

    if args.stats:
        show_stats()
    elif args.clear:
        clear_graph()
    else:
        if args.full:
            args.chunks = True
            args.refs = True
            args.propagate = True

        build_graph(
            docs_only=args.docs_only,
            include_chunks=args.chunks,
            include_refs=args.refs,
            propagate=args.propagate,
            dry_run=args.dry_run,
        )


if __name__ == '__main__':
    main()
