#!/usr/bin/env python3
"""
Mythos Quote Telegram Handler
/opt/mythos/telegram_bot/handlers/quote_handler.py

Commands:
    /quote                                      - Show usage help
    /quote add "text" | description | tag1,tag2  - Add a new quote
    /quote <QID>                                - Look up a quote by ID
    /quote list [speaker]                       - List quotes
    /quote search <keyword>                     - Search quotes
    /quote <QID> tag <tag>                      - Add a tag
    /quote <QID> relate <term>                  - Link to ontology term
    /quote <QID> interpret <text>               - Set interpretation
    /quote random                               - Random quote
"""
import os
import uuid
from datetime import datetime, timezone
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')


def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def handle_quote(text: str):
    """Handle /quote command. Returns str or (str, list) tuple for inline buttons."""
    if not text or not text.strip():
        return (
            "✦ Seraphe's Quotes\n\n"
            "Usage:\n"
            '  /quote add "text" | description | tag1,tag2\n'
            "  /quote <QID> — view a quote\n"
            "  /quote list [speaker] — list quotes\n"
            "  /quote search <keyword> — search\n"
            "  /quote <QID> tag <tag> — add tag\n"
            "  /quote <QID> relate <term> — link to ontology\n"
            "  /quote <QID> interpret <text> — set interpretation\n"
            "  /quote random — random quote\n\n"
            "Speaker defaults to Seraphe. Override:\n"
            '  /quote add "text" | desc | tags | speaker:Ka'
        )

    parts = text.strip()

    # /quote list [speaker]
    if parts.lower().startswith('list'):
        speaker = parts[4:].strip() or None
        return _list_quotes(speaker)

    # /quote search <keyword>
    if parts.lower().startswith('search '):
        return _search_quotes(parts[7:].strip())

    # /quote random
    if parts.lower() == 'random':
        return _random_quote()

    # /quote add "text" | description | tags [| speaker:X]
    if parts.lower().startswith('add '):
        return _add_quote(parts[4:])

    # /quote QID tag <tag>
    # /quote QID relate <term>
    # /quote QID interpret <text>
    words = parts.split(None, 2)
    if len(words) >= 2 and words[0].upper().startswith('Q-'):
        qid = words[0]
        subcmd = words[1].lower()
        rest = words[2] if len(words) > 2 else ""

        if subcmd == 'tag':
            return _add_tag(qid, rest)
        elif subcmd == 'relate':
            return _relate_term(qid, rest)
        elif subcmd == 'interpret':
            return _set_interpretation(qid, rest)

    # /quote QID — lookup
    if parts.upper().startswith('Q-'):
        return _lookup_quote(parts.split()[0])

    # Fallback: treat as search
    return _search_quotes(parts)


def _add_quote(text: str) -> str:
    """Add a quote. Format: "quote text" | description | tag1,tag2 [| speaker:Name]"""
    if not text:
        return '✦ Format: /quote add "text" | description | tag1,tag2'

    pipe_parts = [p.strip() for p in text.split('|')]
    quote_text = pipe_parts[0].strip('"').strip("'").strip('"').strip('"')
    description = pipe_parts[1] if len(pipe_parts) > 1 else ""
    tags_str = pipe_parts[2] if len(pipe_parts) > 2 else ""
    speaker = "Seraphe"

    # Check for speaker override in any field
    for i, p in enumerate(pipe_parts):
        if p.strip().lower().startswith('speaker:'):
            speaker = p.strip()[8:].strip()
            pipe_parts[i] = ""

    tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else []

    if not quote_text:
        return "✦ Quote text is required."

    qid = "Q-" + uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc).isoformat()

    driver = get_driver()
    try:
        with driver.session() as session:
            session.run("""
                CREATE (q:Quote {
                    quote_id: $qid, text: $text, speaker: $speaker,
                    description: $description, interpretation: '',
                    context: '', source: 'telegram', date_spoken: '',
                    tags: $tags, created_at: $now, updated_at: $now
                })
            """, qid=qid, text=quote_text, speaker=speaker,
                description=description, tags=tags, now=now)

            # Auto-link to OntologyTerms by tag name
            linked = 0
            for tag in tags:
                result = session.run("""
                    MATCH (q:Quote {quote_id: $qid})
                    MATCH (t:OntologyTerm)
                    WHERE toLower(t.name) = toLower($tag)
                       OR any(a IN t.aliases WHERE toLower(a) = toLower($tag))
                    MERGE (q)-[:TAGGED_WITH]->(t)
                    RETURN count(*) AS cnt
                """, qid=qid, tag=tag)
                linked += result.single()["cnt"]

            tag_info = f" [{', '.join(tags)}]" if tags else ""
            link_info = f" ({linked} auto-linked)" if linked else ""
            return f"✦ Created {qid}: \"{quote_text[:60]}{'…' if len(quote_text) > 60 else ''}\"\n   — {speaker}{tag_info}{link_info}"
    finally:
        driver.close()


def _lookup_quote(qid: str):
    """Returns (text, related_names_list) tuple."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (q:Quote {quote_id: $qid})
                RETURN q.quote_id AS qid, q.text AS text, q.speaker AS speaker,
                       q.description AS description, q.interpretation AS interpretation,
                       q.context AS context, q.tags AS tags,
                       q.date_spoken AS date_spoken
            """, qid=qid)
            record = result.single()
            if not record:
                return (f"✦ No quote found: {qid}", [])

            lines = [
                f"✦ {record['qid']}",
                f'   "{record["text"]}"',
                f"   — {record['speaker']}",
            ]
            if record['description']:
                lines.append(f"\n   {record['description']}")
            if record['interpretation']:
                lines.append(f"\n   ⟐ {record['interpretation']}")
            if record['context']:
                lines.append(f"   ↳ Context: {record['context']}")
            if record['tags']:
                lines.append(f"   Tags: {', '.join(record['tags'])}")
            if record['date_spoken']:
                lines.append(f"   Date: {record['date_spoken']}")

            # Get related items
            rels = session.run("""
                MATCH (q:Quote {quote_id: $qid})-[r]->(t)
                RETURN COALESCE(t.name, t.quote_id) AS name, type(r) AS type
                UNION
                MATCH (t)-[r]->(q:Quote {quote_id: $qid})
                RETURN COALESCE(t.name, t.quote_id) AS name, type(r) AS type
            """, qid=qid)
            rel_list = list(rels)
            related_names = []
            if rel_list:
                seen = set()
                for r in rel_list:
                    if r['name'] not in seen:
                        seen.add(r['name'])
                        related_names.append(r['name'])
                lines.append(f"\n   {len(related_names)} connected terms ↓")

            return ('\n'.join(lines), related_names[:12])
    finally:
        driver.close()


def _list_quotes(speaker: str = None):
    """Returns (str, qid_list) tuple."""
    driver = get_driver()
    try:
        with driver.session() as session:
            if speaker:
                result = session.run("""
                    MATCH (q:Quote)
                    WHERE toLower(q.speaker) = toLower($speaker)
                    RETURN q.quote_id AS qid, q.text AS text, q.speaker AS speaker
                    ORDER BY q.created_at DESC
                """, speaker=speaker)
            else:
                result = session.run("""
                    MATCH (q:Quote)
                    RETURN q.quote_id AS qid, q.text AS text, q.speaker AS speaker
                    ORDER BY q.created_at DESC
                """)

            records = list(result)
            if not records:
                return f"✦ No quotes found{' for ' + speaker if speaker else ''}."

            lines = [f"✦ Quotes{' — ' + speaker if speaker else ''} ({len(records)})\n"]
            for r in records:
                short = r['text'][:60] + '…' if len(r['text']) > 60 else r['text']
                lines.append(f"  {r['qid']} \"{short}\" — {r['speaker']}")

            return '\n'.join(lines)
    finally:
        driver.close()


def _search_quotes(query: str):
    """Search quotes by text, description, or interpretation."""
    if not query:
        return "✦ Usage: /quote search <keyword>"

    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (q:Quote)
                WHERE toLower(q.text) CONTAINS toLower($q)
                   OR toLower(q.description) CONTAINS toLower($q)
                   OR toLower(q.interpretation) CONTAINS toLower($q)
                   OR $q IN q.tags
                RETURN q.quote_id AS qid, q.text AS text, q.speaker AS speaker
                ORDER BY q.created_at DESC
                LIMIT 10
            """, q=query)
            records = list(result)
            if not records:
                return f'✦ No quotes matching "{query}"'

            lines = [f'✦ Search: "{query}" ({len(records)} results)\n']
            for r in records:
                short = r['text'][:60] + '…' if len(r['text']) > 60 else r['text']
                lines.append(f"  {r['qid']} \"{short}\" — {r['speaker']}")

            return '\n'.join(lines)
    finally:
        driver.close()


def _random_quote():
    """Return a random quote."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (q:Quote)
                WITH q, rand() AS r
                ORDER BY r
                LIMIT 1
                RETURN q.quote_id AS qid, q.text AS text, q.speaker AS speaker,
                       q.description AS description
            """)
            record = result.single()
            if not record:
                return "✦ No quotes yet. Add one with /quote add"

            lines = [
                f'✦ "{record["text"]}"',
                f"   — {record['speaker']}  [{record['qid']}]",
            ]
            if record['description']:
                lines.append(f"   {record['description']}")
            return '\n'.join(lines)
    finally:
        driver.close()


def _add_tag(qid: str, tag: str) -> str:
    """Add a tag to a quote."""
    if not tag:
        return "✦ Usage: /quote <QID> tag <tag>"

    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (q:Quote {quote_id: $qid})
                SET q.tags = CASE
                    WHEN $tag IN q.tags THEN q.tags
                    ELSE coalesce(q.tags, []) + $tag
                END,
                q.updated_at = $now
                RETURN q.tags AS tags
            """, qid=qid, tag=tag, now=datetime.now(timezone.utc).isoformat())
            record = result.single()
            if not record:
                return f"✦ Quote {qid} not found"

            # Try auto-link to ontology
            session.run("""
                MATCH (q:Quote {quote_id: $qid})
                MATCH (t:OntologyTerm)
                WHERE toLower(t.name) = toLower($tag)
                   OR any(a IN t.aliases WHERE toLower(a) = toLower($tag))
                MERGE (q)-[:TAGGED_WITH]->(t)
            """, qid=qid, tag=tag)

            return f"✦ Tagged {qid}: +{tag}  [total: {', '.join(record['tags'])}]"
    finally:
        driver.close()


def _relate_term(qid: str, term_name: str) -> str:
    """Link a quote to an ontology term."""
    if not term_name:
        return "✦ Usage: /quote <QID> relate <term>"

    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (q:Quote {quote_id: $qid})
                MATCH (t:OntologyTerm)
                WHERE toLower(t.name) = toLower($term)
                   OR any(a IN t.aliases WHERE toLower(a) = toLower($term))
                MERGE (q)-[:RELATES_TO]->(t)
                RETURN t.name AS name
            """, qid=qid, term=term_name)
            record = result.single()
            if not record:
                return f"✦ Quote {qid} or term \"{term_name}\" not found"
            return f"✦ Linked {qid} → {record['name']}"
    finally:
        driver.close()


def _set_interpretation(qid: str, text: str) -> str:
    """Set the interpretation for a quote."""
    if not text:
        return "✦ Usage: /quote <QID> interpret <text>"

    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (q:Quote {quote_id: $qid})
                SET q.interpretation = $text,
                    q.updated_at = $now
                RETURN q.quote_id AS qid
            """, qid=qid, text=text, now=datetime.now(timezone.utc).isoformat())
            record = result.single()
            if not record:
                return f"✦ Quote {qid} not found"
            return f"✦ {qid} interpretation set."
    finally:
        driver.close()
