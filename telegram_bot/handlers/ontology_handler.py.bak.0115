#!/usr/bin/env python3
"""
Mythos Ontology Telegram Handler
/opt/mythos/telegram_bot/handlers/ontology_handler.py

Commands:
    /define <term>                          - Look up a term
    /define add <term> | <def> | <category> - Add a new term
    /define list [category]                 - List terms
"""

import os
from datetime import datetime, UTC
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')


def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def handle_define(text: str):
    """Handle /define command. Returns str or (str, list) tuple."""
    if not text or not text.strip():
        return (
            "✦ Ontology — Mythos Glossary\n\n"
            "Usage:\n"
            "  /define <term> — look up a term\n"
            "  /define add <name> | <definition> | <category> — add a term\n"
            "  /define list [category] — list terms\n\n"
            "Categories: Astrology, Numerology, Tarot, Mythos Core"
        )

    parts = text.strip().replace('_', ' ')

    # /define list [category]
    if parts.lower().startswith('list'):
        cat_filter = parts[4:].strip() or None
        return _list_terms(cat_filter)

    # /define add name | definition | category
    if parts.lower().startswith('add '):
        return _add_term(parts[4:])

    # /define <term> — lookup (returns tuple)
    return _lookup_term(parts)


def _lookup_term(query: str):
    """Returns (text, related_names_list) tuple for inline buttons."""
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (t:OntologyTerm)
                WHERE t.name = $q
                   OR toLower(t.name) = toLower($q)
                   OR any(a IN t.aliases WHERE toLower(a) = toLower($q))
                RETURN t.name AS name, t.definition AS definition,
                       t.category AS category, t.aliases AS aliases
                LIMIT 1
            """, q=query)
            record = result.single()

            if not record:
                result = session.run("""
                    MATCH (t:OntologyTerm)
                    WHERE toLower(t.name) CONTAINS toLower($q)
                       OR toLower(t.definition) CONTAINS toLower($q)
                    RETURN t.name AS name, t.definition AS definition,
                           t.category AS category, t.aliases AS aliases
                    LIMIT 3
                """, q=query)
                records = list(result)
                if not records:
                    return (f"✦ No term found for \"{query}\"\n\nUse /define add to create it.", [])
                if len(records) == 1:
                    record = records[0]
                else:
                    lines = [f"✦ Multiple matches for \"{query}\":\n"]
                    names = []
                    for r in records:
                        lines.append(f"  • {r['name']} [{r['category']}]")
                        names.append(r['name'])
                    return ('\n'.join(lines), names)

            name = record['name']
            defn = record['definition']
            cat = record['category']
            aliases = record['aliases'] or []

            lines = [f"✦ {name}", f"   [{cat}]", ""]
            lines.append(defn)

            if aliases:
                lines.append(f"\n   aka: {', '.join(aliases)}")

            # Get relationships
            rels = session.run("""
                MATCH (t:OntologyTerm {name: $name})-[r:RELATED_TO]->(o:OntologyTerm)
                RETURN o.name AS name, r.type AS type
                UNION
                MATCH (o:OntologyTerm)-[r:RELATED_TO]->(t:OntologyTerm {name: $name})
                RETURN o.name AS name, r.type AS type
            """, name=name)
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


def _add_term(text: str) -> str:
    parts = [p.strip() for p in text.split('|')]
    if len(parts) < 3:
        return "✦ Format: /define add <name> | <definition> | <category>"

    name, definition, category = parts[0], parts[1], parts[2]
    if not name or not definition or not category:
        return "✦ All three fields required: name, definition, category"

    driver = get_driver()
    now = datetime.now(UTC).isoformat()
    try:
        with driver.session() as session:
            existing = session.run(
                "MATCH (t:OntologyTerm {name: $name}) RETURN t.name", name=name
            ).single()
            if existing:
                return f"✦ \"{name}\" already exists. Use the web UI to edit."

            session.run("""
                CREATE (t:OntologyTerm {
                    name: $name, definition: $definition,
                    category: $category, aliases: [],
                    created_at: $now, updated_at: $now
                })
            """, name=name, definition=definition, category=category, now=now)
            return f"✦ Created: {name} [{category}]"
    finally:
        driver.close()


def _list_terms(category: str = None) -> str:
    driver = get_driver()
    try:
        with driver.session() as session:
            if category:
                result = session.run("""
                    MATCH (t:OntologyTerm)
                    WHERE toLower(t.category) = toLower($cat)
                    RETURN t.name AS name, t.category AS category
                    ORDER BY t.name
                """, cat=category)
            else:
                result = session.run("""
                    MATCH (t:OntologyTerm)
                    RETURN t.name AS name, t.category AS category
                    ORDER BY t.category, t.name
                """)

            records = list(result)
            if not records:
                return f"✦ No terms found{' in ' + category if category else ''}."

            lines = [f"✦ Ontology{' — ' + category if category else ''} ({len(records)} terms)\n"]
            current_cat = None
            for r in records:
                if r['category'] != current_cat:
                    current_cat = r['category']
                    lines.append(f"\n  [{current_cat}]")
                lines.append(f"  • {r['name']}")

            return '\n'.join(lines)
    finally:
        driver.close()
