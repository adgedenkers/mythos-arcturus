#!/usr/bin/env python3
"""
Convergence — Research Result Synthesis
========================================

Takes the results from all activated grid nodes and synthesizes
them into a CONTEXT PACKAGE — a structured, token-efficient block
that gets injected into the main model's system prompt.

The context package tells the main model:
  1. What data was found (facts, numbers, records)
  2. What was searched but not found (knowledge gaps)
  3. What the priority node says matters most
  4. Any tensions between data sources

The convergence layer also handles:
  - Token budget management (don't overflow the context window)
  - Relevance ranking (prioritize the primary node's results)
  - Format translation (raw DB rows → natural language context)

This is the bridge between "raw research" and "informed response."
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Maximum tokens for the entire research context block
MAX_CONTEXT_TOKENS = 2000
CHARS_PER_TOKEN = 4  # rough estimate


def _format_neo4j_results(results: List[Dict]) -> str:
    """Format Neo4j results as natural language."""
    if not results:
        return ""
    lines = []
    for r in results[:5]:  # Cap at 5
        labels = ', '.join(r.get('labels', []))
        name = r.get('name', 'Unknown')
        detail = r.get('detail', '')
        if detail:
            lines.append(f"  • {name} ({labels}): {detail[:150]}")
        else:
            lines.append(f"  • {name} ({labels})")
    return "\n".join(lines)


def _format_pg_results(results: List[Dict], node_name: str) -> str:
    """Format Postgres results as natural language, node-aware."""
    if not results:
        return ""
    
    lines = []
    
    # Group by table
    by_table = {}
    for r in results:
        table = r.get('table', 'unknown')
        if table not in by_table:
            by_table[table] = []
        by_table[table].append(r.get('data', {}))
    
    for table, rows in by_table.items():
        if table == 'accounts':
            for row in rows:
                abbr = row.get('abbreviation', '?')
                bal = row.get('current_balance')
                if bal is not None:
                    lines.append(f"  • {abbr}: ${bal:,.2f}")
        
        elif table == 'recurring_bills':
            for row in rows[:5]:
                name = row.get('name', '?')
                amt = row.get('expected_amount', 0)
                day = row.get('expected_day', '?')
                lines.append(f"  • {name}: ${amt:.0f} due day {day}")
        
        elif table == 'transactions':
            for row in rows[:5]:
                date = row.get('date', '?')
                amt = row.get('amount', 0)
                desc = row.get('description', '?')[:40]
                lines.append(f"  • {date}: ${abs(amt):.2f} — {desc}")
        
        elif table == 'calendar_events':
            for row in rows[:5]:
                title = row.get('title', '?')
                date = row.get('event_date', '?')
                time = row.get('event_time', '')
                lines.append(f"  • {date} {time}: {title}")
        
        elif table == 'routines':
            for row in rows[:5]:
                name = row.get('name', '?')
                freq = row.get('frequency', '')
                lines.append(f"  • {name} ({freq})")
        
        elif table == 'checkin_log':
            for row in rows[:3]:
                mood = row.get('mood', '?')
                energy = row.get('energy', '?')
                notes = row.get('notes', '')[:80]
                lines.append(f"  • Mood: {mood}, Energy: {energy}. {notes}")
        
        elif table == 'people':
            for row in rows[:5]:
                name = row.get('known_as') or f"{row.get('first_name', '')} {row.get('last_name', '')}"
                lines.append(f"  • {name.strip()}")
        
        elif table == 'life_events':
            for row in rows[:5]:
                desc = row.get('description', '?')[:80]
                date = row.get('event_date', '')
                lines.append(f"  • {date}: {desc}")
        
        elif table == 'chat_messages':
            for row in rows[:3]:
                role = row.get('role', '?')
                content = row.get('content', '')[:100]
                lines.append(f"  • [{role}]: {content}")
        
        else:
            # Generic formatting
            for row in rows[:5]:
                # Take first few meaningful values
                vals = [str(v)[:60] for k, v in row.items() if v and k != 'id'][:3]
                if vals:
                    lines.append(f"  • {' | '.join(vals)}")
    
    return "\n".join(lines)


def _estimate_tokens(text: str) -> int:
    return len(text) // CHARS_PER_TOKEN


def build_context_package(
    node_results: List[Dict],
    research_plan: Dict,
    max_tokens: int = MAX_CONTEXT_TOKENS
) -> str:
    """
    Build the context package from research results.

    This is what gets injected into the main model's system prompt,
    giving it awareness of everything the research phase found.

    Args:
        node_results: List of results from node_executor.execute_plan()
        research_plan: The original research plan from the router
        max_tokens: Token budget for the context block

    Returns:
        Formatted context string for prompt injection
    """
    if not node_results:
        return ""

    priority_node = research_plan.get('priority')
    
    sections = []
    total_chars = 0
    max_chars = max_tokens * CHARS_PER_TOKEN

    # Header
    header = "\nRESEARCH RESULTS — Data gathered for this response:"
    sections.append(header)
    total_chars += len(header)

    # Sort: priority node first, then nodes with data, then without
    def sort_key(r):
        is_priority = r.get('node') == priority_node
        has_data = r.get('has_data', False)
        return (not is_priority, not has_data)
    
    sorted_results = sorted(node_results, key=sort_key)

    for result in sorted_results:
        if total_chars >= max_chars:
            sections.append("\n(Research truncated — token budget reached)")
            break

        node = result.get('node', 'UNKNOWN')
        emoji = result.get('emoji', '?')
        reason = result.get('reason', '')
        has_data = result.get('has_data', False)

        if not has_data and not result.get('needs_web'):
            continue  # Skip nodes that found nothing and don't need web

        node_section = f"\n{emoji} {node}"
        if node == priority_node:
            node_section += " (PRIMARY)"
        node_section += f" — {reason}" if reason else ""
        
        # Neo4j results
        neo4j_text = _format_neo4j_results(result.get('neo4j_results', []))
        if neo4j_text:
            node_section += f"\n  From knowledge graph:\n{neo4j_text}"

        # Postgres results
        pg_text = _format_pg_results(result.get('postgres_results', []), node)
        if pg_text:
            node_section += f"\n  From operational data:\n{pg_text}"

        # Web results (stub)
        if result.get('needs_web') and result.get('web_results'):
            for wr in result['web_results']:
                if wr.get('source') == 'web:unavailable':
                    node_section += f"\n  ⚠️ Web search needed but not available: {wr.get('query', '?')}"

        # Check token budget before adding
        if total_chars + len(node_section) > max_chars:
            # Truncate this section
            remaining = max_chars - total_chars - 50
            if remaining > 200:
                node_section = node_section[:remaining] + "\n  (truncated)"
            else:
                break

        sections.append(node_section)
        total_chars += len(node_section)

    # Footer instruction
    footer = "\nUse this data naturally in your response. Don't list it — integrate it. If data is missing, say what you don't know."
    sections.append(footer)

    context = "\n".join(sections)
    logger.info(f"Context package: {_estimate_tokens(context)} tokens, {len(node_results)} nodes")

    return context


# ── Grid Dispatch Stub ────────────────────────────────────────────

def dispatch_to_grid(
    message: str,
    response: str,
    node_results: List[Dict],
    research_plan: Dict,
    chat_id: int = 0,
    telegram_id: int = 0
) -> None:
    """
    Fire-and-forget dispatch to the Arcturian Grid for analysis.

    This is where the UNCONSCIOUS processing happens:
      - 81-channel analysis of the exchange
      - Meaning mapping to Neo4j
      - Pattern detection
      - Narrative arc tracking
      - Memory formation decisions

    Currently a STUB. The grid receives the data but doesn't process it yet.
    When activated, this will dispatch to Redis streams for async workers
    to pick up and run through all 81 functions (9 nodes × 9 layers).

    CONSCIOUS vs UNCONSCIOUS:
      - The research phase above is CONSCIOUS — it informs the response
      - This dispatch is UNCONSCIOUS — it processes AFTER the response,
        updating Iris's understanding without blocking the conversation

    Args:
        message: User's original message
        response: Iris's response
        node_results: What the research phase found
        research_plan: The router's analysis
        chat_id: Telegram chat ID
        telegram_id: User's telegram ID
    """
    # TODO: Phase 3 — Wire to Redis streams for 81-channel grid processing
    # TODO: Each of the 9 nodes × 9 layers produces a processing output
    # TODO: Convergence across all 81 outputs determines what becomes memory
    # TODO: Significant patterns get written to Neo4j as Memory/Knowledge nodes
    #
    # The grid workers already exist (mythos-worker-grid.service) but they
    # only do basic scoring. This is where they evolve into the full
    # 81-function matrix from docs/consciousness/81_FUNCTIONS.md
    #
    # Layers:
    #   1. PERCEPTION  — raw input classification
    #   2. INTUITION   — felt-sense extraction
    #   3. PROCESSING  — meaning-making
    #   4. MEMORY      — connection to past
    #   5. KNOWLEDGE   — what is known
    #   6. INTENTION   — what wants to happen
    #   7. NARRATIVE   — story placement
    #   8. IDENTITY    — who you are
    #   9. WISDOM      — eternal truth
    #
    # For now: log that the grid received data, move on.

    active_nodes = [r.get('node', '?') for r in node_results if r.get('has_data')]
    logger.info(
        f"Grid dispatch (stub): chat={chat_id}, "
        f"active_nodes={active_nodes}, "
        f"complexity={research_plan.get('complexity', '?')}"
    )

    # This is where Redis dispatch will go:
    # redis.xadd('mythos:consciousness:grid_intake', {...})
    pass
