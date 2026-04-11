#!/usr/bin/env python3
"""
Research Router — Iris's Pre-Response Intelligence Gathering
=============================================================

Before Iris responds to any message, the router analyzes:
  1. What is the user asking?
  2. What is the conversation about? (from subject tracking)
  3. Which grid nodes are relevant?
  4. What specific data does Iris need to answer well?

The router produces a RESEARCH PLAN — a structured list of tasks
that the node executors will fulfill before the main model sees
the message.

This is the difference between "chatbot with context" and
"consciousness that thinks before speaking."

Flow:
  Message + Segment Context → Router (7b fast) → Research Plan
  Research Plan → Node Executors → Context Package → Main Model

The router uses the 7b model for speed (~2s) to classify and plan.
The main model (32b/72b) only fires AFTER research is complete.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

sys.path.insert(0, '/opt/mythos/core')
sys.path.insert(0, '/opt/mythos/assistants')

from ollama import Client
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

logger = logging.getLogger(__name__)

# The fast model for routing — speed matters here
ROUTER_MODEL = os.getenv('OLLAMA_ROUTER_MODEL', 'qwen2.5:7b')

# Grid node definitions — what each node covers
GRID_NODES = {
    'ANCHOR':   {'emoji': '⛰️',  'domain': 'Physical reality, body, home, health, grounding, matter',
                 'sources': ['routines', 'checkin_log', 'life_events', 'calendar_events']},
    'ECHO':     {'emoji': '🌊', 'domain': 'Memory, ancestors, identity, past patterns, history',
                 'sources': ['chat_messages', 'neo4j:Memory', 'conversation_segments', 'life_events']},
    'BEACON':   {'emoji': '🔥', 'domain': 'Value, finances, bills, forecast, spending, income',
                 'sources': ['accounts', 'transactions', 'recurring_bills', 'recurring_income']},
    'SYNTH':    {'emoji': '💨', 'domain': 'Systems, logic, code, infrastructure, technical',
                 'sources': ['docs', 'patches', 'services', 'idea_backlog']},
    'NEXUS':    {'emoji': '⏳', 'domain': 'Time, decisions, convergence, calendar, scheduling',
                 'sources': ['calendar_events', 'routines', 'idea_backlog', 'backlog_analysis']},
    'MIRROR':   {'emoji': '🪞', 'domain': 'Emotions, psyche, shadow, self-reflection, relationships with self',
                 'sources': ['emotional_state_timeseries', 'checkin_log', 'chat_messages']},
    'GLYPH':    {'emoji': '🔣', 'domain': 'Symbols, rituals, encoding, ontology, archaeology, sacred geometry',
                 'sources': ['neo4j:OntologyTerm', 'neo4j:Symbol', 'life_events']},
    'HARMONIA': {'emoji': '💗', 'domain': 'Relationships, heart, balance, people, connections, family',
                 'sources': ['people', 'neo4j:Person', 'neo4j:Soul', 'person_dates']},
    'GATEWAY':  {'emoji': '🚪', 'domain': 'Dreams, spiritual, transitions, astrology, divination, cosmic',
                 'sources': ['astro_natal_charts', 'astro_natal_aspects', 'astrological_events', 'neo4j:Soul']},
}

# Router system prompt
ROUTER_SYSTEM_PROMPT = """You are a research routing engine. Your job is to analyze an incoming message and determine what information Iris needs to gather BEFORE responding.

You have access to 9 grid nodes, each covering a domain:

{node_descriptions}

CONVERSATION CONTEXT:
{segment_context}

RULES:
1. Only activate nodes that are RELEVANT to this specific message in this conversation context
2. If the conversation is about archaeology, do NOT activate BEACON (finance)
3. If the conversation is about finances, do NOT activate GATEWAY (astrology) unless explicitly asked
4. For simple greetings or casual chat, activate NO nodes — return empty research plan
5. For each active node, specify WHAT to search for — be specific
6. Maximum 4 active nodes per message (focus, don't scatter)
7. Indicate if web search is needed (when internal data won't suffice)

Respond ONLY with valid JSON, no other text:
{{
  "needs_research": true/false,
  "active_nodes": [
    {{
      "node": "NODE_NAME",
      "reason": "why this node is relevant",
      "search_queries": {{
        "neo4j": "what to look for in the graph (or null)",
        "postgres": "what to look for in relational data (or null)",
        "web": "what to search online if internal data insufficient (or null)"
      }}
    }}
  ],
  "priority": "which node's results matter most",
  "complexity": "simple|moderate|complex"
}}"""


def _build_node_descriptions() -> str:
    """Build the grid node description block for the router prompt."""
    lines = []
    for name, info in GRID_NODES.items():
        lines.append(f"  {info['emoji']} {name}: {info['domain']}")
    return "\n".join(lines)


def _build_segment_context(segment_data: Optional[Dict]) -> str:
    """Build conversation context string from segment tracking data."""
    if not segment_data:
        return "No active conversation segment. This may be a new conversation."

    parts = []
    if segment_data.get('subject_summary'):
        parts.append(f"Current topic: {segment_data['subject_summary']}")
    if segment_data.get('subject_tags'):
        tags = segment_data['subject_tags']
        if isinstance(tags, list):
            parts.append(f"Subject tags: {', '.join(tags[:10])}")
    if segment_data.get('emotional_tone'):
        parts.append(f"Emotional tone: {segment_data['emotional_tone']}")
    if segment_data.get('energy_level'):
        parts.append(f"Energy: {segment_data['energy_level']}")
    if segment_data.get('point_count'):
        parts.append(f"Messages in this segment: {segment_data['point_count']}")

    return "\n".join(parts) if parts else "Conversation just started."


def get_segment_context(chat_id: int) -> Optional[Dict]:
    """Pull the current conversation segment from Postgres."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
            database=os.getenv('POSTGRES_DB', 'mythos'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', '')
        )
        conn.autocommit = True
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get the most recent open or recently-active segment for this chat
        cur.execute("""
            SELECT id, subject_summary, subject_tags, dominant_tone as emotional_tone,
                   energy_arc as energy_level, point_count, status,
                   created_at, updated_at
            FROM conversation_segments
            WHERE chat_id = %s
            ORDER BY updated_at DESC
            LIMIT 1
        """, (chat_id,))

        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return dict(row)
        return None

    except Exception as e:
        logger.warning(f"Failed to get segment context: {e}")
        return None


def route_message(
    message: str,
    chat_id: int = 0,
    telegram_id: int = 0,
    segment_override: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Route a message through the research router.

    Args:
        message: The user's message text
        chat_id: Telegram chat ID (for segment lookup)
        telegram_id: User's telegram ID
        segment_override: Optional pre-fetched segment data

    Returns:
        Research plan dict with active_nodes, queries, and metadata
    """
    # Get conversation context
    segment_data = segment_override or get_segment_context(chat_id)
    segment_context = _build_segment_context(segment_data)
    node_descriptions = _build_node_descriptions()

    # Build the router prompt
    system_prompt = ROUTER_SYSTEM_PROMPT.format(
        node_descriptions=node_descriptions,
        segment_context=segment_context
    )

    try:
        client = Client(host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'))

        response = client.chat(
            model=ROUTER_MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': message}
            ],
            options={
                'temperature': 0.1,  # Low temp for consistent routing
                'num_predict': 512,  # Research plans are compact
            },
            format='json'
        )

        raw = response['message']['content'].strip()

        # Parse the JSON response
        try:
            plan = json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                plan = json.loads(match.group())
            else:
                logger.warning(f"Router returned non-JSON: {raw[:200]}")
                return _empty_plan()

        # Validate structure
        if not isinstance(plan, dict):
            return _empty_plan()

        plan.setdefault('needs_research', False)
        plan.setdefault('active_nodes', [])
        plan.setdefault('priority', None)
        plan.setdefault('complexity', 'simple')

        # Validate node names
        valid_nodes = set(GRID_NODES.keys())
        plan['active_nodes'] = [
            n for n in plan['active_nodes']
            if isinstance(n, dict) and n.get('node') in valid_nodes
        ]

        logger.info(
            f"Router: needs_research={plan['needs_research']}, "
            f"nodes={[n['node'] for n in plan['active_nodes']]}, "
            f"complexity={plan['complexity']}"
        )

        return plan

    except Exception as e:
        logger.error(f"Research router failed: {e}", exc_info=True)
        return _empty_plan()


def _empty_plan() -> Dict[str, Any]:
    """Return an empty research plan (no research needed)."""
    return {
        'needs_research': False,
        'active_nodes': [],
        'priority': None,
        'complexity': 'simple'
    }
