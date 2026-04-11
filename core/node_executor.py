#!/usr/bin/env python3
"""
Node Executor — Grid-Aware Data Retrieval
==========================================

Each grid node knows how to pull data from its domain sources.
The executor follows a priority order:

  1. Neo4j FIRST  — "Do I already know about this?"
  2. Postgres SECOND — "Has this come up in my operational data?"
  3. Evaluate — "Do I have enough to answer?"
  4. Web ONLY IF NEEDED — "Go find what's missing"

The executor returns a structured result for each node,
which convergence merges into the final context package.

IMPORTANT: Results are scoped by the research plan. Only nodes
that the router activated will execute. If BEACON (finance) is
dormant because the conversation is about archaeology, its
executor never runs and finance data never enters the prompt.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

sys.path.insert(0, '/opt/mythos/core')

from dotenv import load_dotenv
load_dotenv('/opt/mythos/.env')

logger = logging.getLogger(__name__)


class NodeExecutor:
    """
    Executes research tasks for a single grid node.
    
    Each node has:
      - A domain (what it covers)
      - Data sources (where to look)
      - Query builders (how to look)
    """

    def __init__(self):
        self._pg_conn = None
        self._neo4j_driver = None

    # ── Database Connections ─────────────────────────────────────

    def _get_pg(self):
        """Get or create PostgreSQL connection."""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            if self._pg_conn is None or self._pg_conn.closed:
                self._pg_conn = psycopg2.connect(
                    host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
                    database=os.getenv('POSTGRES_DB', 'mythos'),
                    user=os.getenv('POSTGRES_USER', 'postgres'),
                    password=os.getenv('POSTGRES_PASSWORD', '')
                )
                self._pg_conn.autocommit = True
            return self._pg_conn
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            return None

    def _get_neo4j(self):
        """Get or create Neo4j driver."""
        try:
            if self._neo4j_driver is None:
                from neo4j import GraphDatabase
                self._neo4j_driver = GraphDatabase.driver(
                    os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
                    auth=(
                        os.getenv('NEO4J_USER', 'neo4j'),
                        os.getenv('NEO4J_PASSWORD', '')
                    )
                )
            return self._neo4j_driver
        except Exception as e:
            logger.error(f"Neo4j connection failed: {e}")
            return None

    # ── Query Execution ──────────────────────────────────────────

    def _query_neo4j(self, query_hint: str, node_name: str) -> List[Dict]:
        """
        Search Neo4j based on the router's query hint.
        Uses full-text-ish search across relevant node types.
        """
        driver = self._get_neo4j()
        if not driver or not query_hint:
            return []

        results = []
        try:
            # Extract search terms from the hint
            search_terms = query_hint.lower().strip()

            with driver.session() as session:
                # Search across Person, Soul, OntologyTerm, Memory nodes
                # Using CONTAINS for flexible matching
                cypher = """
                    MATCH (n)
                    WHERE (n:Person OR n:Soul OR n:OntologyTerm OR n:Memory 
                           OR n:Knowledge OR n:Entity)
                    AND (
                        toLower(COALESCE(n.name, '')) CONTAINS $term
                        OR toLower(COALESCE(n.display_name, '')) CONTAINS $term
                        OR toLower(COALESCE(n.full_name, '')) CONTAINS $term
                        OR toLower(COALESCE(n.description, '')) CONTAINS $term
                        OR toLower(COALESCE(n.essence, '')) CONTAINS $term
                        OR toLower(COALESCE(n.definition, '')) CONTAINS $term
                        OR toLower(COALESCE(n.knowing, '')) CONTAINS $term
                    )
                    RETURN labels(n) AS labels, 
                           COALESCE(n.display_name, n.full_name, n.name, 'Unknown') AS name,
                           COALESCE(n.description, n.essence, n.definition, n.knowing, '') AS detail,
                           elementId(n) AS eid
                    LIMIT 10
                """
                # Search for each significant word
                for term in search_terms.split()[:5]:  # Max 5 terms
                    if len(term) < 3:
                        continue
                    records = session.run(cypher, term=term)
                    for record in records:
                        results.append({
                            'source': 'neo4j',
                            'labels': record['labels'],
                            'name': record['name'],
                            'detail': record['detail'][:300],
                            'eid': record['eid']
                        })

            # Deduplicate by eid
            seen = set()
            unique = []
            for r in results:
                if r['eid'] not in seen:
                    seen.add(r['eid'])
                    unique.append(r)
            results = unique[:10]  # Cap at 10 results

            if results:
                logger.info(f"Neo4j [{node_name}]: Found {len(results)} results")

        except Exception as e:
            logger.warning(f"Neo4j query failed [{node_name}]: {e}")

        return results

    def _query_postgres(self, query_hint: str, node_name: str, sources: List[str]) -> List[Dict]:
        """
        Search Postgres tables relevant to this node.
        Uses the query hint to build targeted searches.
        """
        conn = self._get_pg()
        if not conn or not query_hint:
            return []

        results = []
        search_terms = query_hint.lower().strip()

        try:
            from psycopg2.extras import RealDictCursor
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # Node-specific query strategies
            queries = self._build_pg_queries(node_name, search_terms, sources)

            for query_info in queries:
                try:
                    cur.execute(query_info['sql'], query_info.get('params', []))
                    rows = cur.fetchall()
                    for row in rows:
                        results.append({
                            'source': f"postgres:{query_info['table']}",
                            'data': dict(row),
                            'table': query_info['table']
                        })
                except Exception as e:
                    logger.debug(f"PG query failed [{query_info.get('table', '?')}]: {e}")

            cur.close()

            if results:
                logger.info(f"Postgres [{node_name}]: Found {len(results)} results across {len(queries)} queries")

        except Exception as e:
            logger.warning(f"Postgres query failed [{node_name}]: {e}")

        return results[:15]  # Cap total results

    def _build_pg_queries(self, node_name: str, search_terms: str, sources: List[str]) -> List[Dict]:
        """Build node-specific Postgres queries."""
        queries = []

        # BEACON — Finance
        if node_name == 'BEACON':
            queries.append({
                'table': 'accounts',
                'sql': "SELECT abbreviation, account_name, account_type, current_balance FROM accounts WHERE current_balance IS NOT NULL ORDER BY current_balance DESC",
                'params': []
            })
            queries.append({
                'table': 'recurring_bills',
                'sql': """SELECT name, expected_amount, expected_day, category 
                         FROM recurring_bills WHERE active = true 
                         ORDER BY expected_day""",
                'params': []
            })
            queries.append({
                'table': 'transactions',
                'sql': """SELECT date, amount, description, category, account_id
                         FROM transactions 
                         WHERE date >= CURRENT_DATE - INTERVAL '30 days'
                         ORDER BY date DESC LIMIT 20""",
                'params': []
            })

        # ANCHOR — Physical / Routines / Health
        elif node_name == 'ANCHOR':
            queries.append({
                'table': 'routines',
                'sql': """SELECT name, frequency, time_of_day 
                         FROM routines WHERE active = true ORDER BY time_of_day""",
                'params': []
            })
            queries.append({
                'table': 'checkin_log',
                'sql': """SELECT mood, energy, notes, created_at 
                         FROM checkin_log 
                         ORDER BY created_at DESC LIMIT 3""",
                'params': []
            })

        # NEXUS — Time / Calendar / Decisions
        elif node_name == 'NEXUS':
            queries.append({
                'table': 'calendar_events',
                'sql': """SELECT title, event_date, event_time, location, people, notes
                         FROM calendar_events 
                         WHERE event_date >= CURRENT_DATE 
                         AND event_date <= CURRENT_DATE + INTERVAL '14 days'
                         ORDER BY event_date, event_time""",
                'params': []
            })
            queries.append({
                'table': 'idea_backlog',
                'sql': """SELECT title, status, priority 
                         FROM idea_backlog 
                         WHERE status = 'open' 
                         ORDER BY priority DESC NULLS LAST LIMIT 10""",
                'params': []
            })

        # ECHO — Memory / Past patterns
        elif node_name == 'ECHO':
            queries.append({
                'table': 'life_events',
                'sql': """SELECT event_type, description, event_date, people_involved
                         FROM life_events 
                         ORDER BY event_date DESC LIMIT 10""",
                'params': []
            })
            # Search chat history for the topic
            if search_terms:
                queries.append({
                    'table': 'chat_messages',
                    'sql': """SELECT role, LEFT(content, 200) as content, created_at
                             FROM chat_messages 
                             WHERE content ILIKE %s
                             ORDER BY created_at DESC LIMIT 5""",
                    'params': [f'%{search_terms[:50]}%']
                })

        # MIRROR — Emotional state
        elif node_name == 'MIRROR':
            queries.append({
                'table': 'emotional_state_timeseries',
                'sql': """SELECT * FROM emotional_state_timeseries 
                         ORDER BY created_at DESC LIMIT 5""",
                'params': []
            })

        # HARMONIA — People / Relationships
        elif node_name == 'HARMONIA':
            queries.append({
                'table': 'people',
                'sql': """SELECT first_name, last_name, known_as, date_of_birth, notes
                         FROM people ORDER BY last_name LIMIT 20""",
                'params': []
            })

        # GATEWAY — Astrology / Spiritual
        elif node_name == 'GATEWAY':
            queries.append({
                'table': 'astro_natal_charts',
                'sql': """SELECT c.person_id, p.known_as, p.first_name
                         FROM astro_natal_charts c 
                         JOIN people p ON c.person_id = p.id
                         LIMIT 10""",
                'params': []
            })

        # SYNTH — System / Infrastructure
        elif node_name == 'SYNTH':
            # System state is better served by reading files
            # Return a pointer to relevant docs
            queries.append({
                'table': 'idea_backlog',
                'sql': """SELECT title, description, status 
                         FROM idea_backlog 
                         WHERE status = 'open' 
                         AND (title ILIKE %s OR description ILIKE %s)
                         LIMIT 5""",
                'params': [f'%{search_terms[:30]}%', f'%{search_terms[:30]}%']
            })

        # GLYPH — Ontology / Symbols
        elif node_name == 'GLYPH':
            # Primarily Neo4j, but check life_events for archaeological/symbolic references
            if search_terms:
                queries.append({
                    'table': 'life_events',
                    'sql': """SELECT event_type, description, event_date
                             FROM life_events 
                             WHERE description ILIKE %s
                             LIMIT 5""",
                    'params': [f'%{search_terms[:30]}%']
                })

        return queries

    def _query_web(self, query_hint: str, node_name: str) -> List[Dict]:
        """
        Search the web for information not available internally.
        
        STUB — Web search not yet available on Arcturus.
        When implemented, this will use SearXNG or similar.
        """
        # TODO: Implement web search when SearXNG or Brave API is available
        # For now, return empty with a note that web search was requested
        if query_hint:
            logger.info(f"Web search requested [{node_name}]: '{query_hint}' — NOT AVAILABLE (stub)")
            return [{
                'source': 'web:unavailable',
                'query': query_hint,
                'note': 'Web search not yet configured on Arcturus'
            }]
        return []

    # ── Main Execution ───────────────────────────────────────────

    def execute_node(self, node_spec: Dict) -> Dict[str, Any]:
        """
        Execute research for a single grid node.

        Args:
            node_spec: From the research plan, contains:
                - node: Node name (e.g., 'BEACON')
                - reason: Why this node was activated
                - search_queries: {neo4j, postgres, web} query hints

        Returns:
            Node result with data from all sources searched.
        """
        node_name = node_spec.get('node', 'UNKNOWN')
        queries = node_spec.get('search_queries', {})
        
        from research_router import GRID_NODES
        node_info = GRID_NODES.get(node_name, {})
        sources = node_info.get('sources', [])

        result = {
            'node': node_name,
            'emoji': node_info.get('emoji', '?'),
            'reason': node_spec.get('reason', ''),
            'neo4j_results': [],
            'postgres_results': [],
            'web_results': [],
            'has_data': False,
            'needs_web': False,
        }

        # 1. Neo4j FIRST — "Do I already know about this?"
        neo4j_hint = queries.get('neo4j')
        if neo4j_hint:
            result['neo4j_results'] = self._query_neo4j(neo4j_hint, node_name)

        # 2. Postgres SECOND — "Has this come up operationally?"
        pg_hint = queries.get('postgres')
        if pg_hint or sources:
            # Use the postgres hint, or fall back to the neo4j hint for general search
            hint = pg_hint or neo4j_hint or ''
            result['postgres_results'] = self._query_postgres(hint, node_name, sources)

        # 3. Evaluate — do we have enough?
        result['has_data'] = bool(result['neo4j_results'] or result['postgres_results'])

        # 4. Web ONLY IF NEEDED
        web_hint = queries.get('web')
        if web_hint and not result['has_data']:
            result['web_results'] = self._query_web(web_hint, node_name)
            result['needs_web'] = True
        elif web_hint and result['has_data']:
            # We have internal data but web was also requested — note it
            result['needs_web'] = False
            logger.debug(f"[{node_name}] Internal data sufficient, skipping web search")

        return result

    def execute_plan(self, research_plan: Dict) -> List[Dict]:
        """
        Execute all nodes in a research plan.

        Args:
            research_plan: From research_router.route_message()

        Returns:
            List of node results
        """
        if not research_plan.get('needs_research'):
            return []

        active_nodes = research_plan.get('active_nodes', [])
        if not active_nodes:
            return []

        results = []
        for node_spec in active_nodes:
            try:
                result = self.execute_node(node_spec)
                results.append(result)
            except Exception as e:
                logger.error(f"Node executor failed [{node_spec.get('node', '?')}]: {e}")
                results.append({
                    'node': node_spec.get('node', 'UNKNOWN'),
                    'error': str(e),
                    'has_data': False
                })

        logger.info(
            f"Research complete: {len(results)} nodes, "
            f"{sum(1 for r in results if r.get('has_data'))} with data"
        )

        return results

    def close(self):
        """Close database connections."""
        if self._pg_conn and not self._pg_conn.closed:
            self._pg_conn.close()
        if self._neo4j_driver:
            self._neo4j_driver.close()
