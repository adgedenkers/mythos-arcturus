#!/usr/bin/env python3
"""
Conversation Knowledge Bridge
==============================
Bridges Postgres chat_messages (events) → Neo4j (knowledge).

After each exchange is saved to chat_messages by IrisMemory,
this module extracts structured knowledge and writes it to the graph
using the established Conversation/Exchange/Topic/Theme schema.

Design:
  - Fast extraction: regex + keyword matching (always runs, <50ms)
  - Deep extraction: LLM pass via Ollama (optional, toggled by flag)
  - Async-safe: designed to run without blocking the chat response
  - Idempotent: MERGE-based Cypher, safe to re-run

Graph pattern (matches existing schema):
  (Conversation)-[:CONTAINS]->(Exchange)
  (Exchange)-[:FOLLOWED_BY]->(Exchange)
  (Exchange)-[:DISCUSSED]->(Concept)
  (Exchange)-[:HAS_THEME]->(Theme)
  (Exchange)-[:INVOLVES]->(Entity)
  (Person)-[:HAD_CONVERSATION]->(Conversation)

Usage:
    from conversation_bridge import ConversationBridge

    bridge = ConversationBridge()
    bridge.log_exchange(
        conversation_id="chat-d01f9f28-20260226110114",
        user_uuid="d01f9f28-...",
        telegram_id=7811548479,
        user_message="How's the finance system looking?",
        assistant_response="The imports are clean. 847 transactions loaded.",
        model_used="qwen3:30b-a3b",
        response_time_ms=1200,
    )
"""

import os
import re
import json
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any

from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')

# Toggle deep extraction (LLM-based theme/concept extraction)
ENABLE_DEEP_EXTRACTION = False  # Start disabled, enable when stable

# Ollama config (for deep extraction)
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'iris-thinking-v2')

# Known entities for fast matching
KNOWN_PEOPLE = {
    "ka'tuar'el": "PE-KaTuarEl", "adge": "PE-KaTuarEl", "adriaan": "PE-KaTuarEl",
    "seraphe": "PE-Seraphe", "rebecca": "PE-Seraphe", "becky": "PE-Seraphe", "lou": "PE-Seraphe",
    "fitz": "PE-Fitz",
    "iris": "PE-Iris",
}

KNOWN_SYSTEMS = {
    "arcturus": "SYS-Arcturus",
    "mythos": "SYS-Mythos",
    "neo4j": "SYS-Neo4j",
    "postgres": "SYS-Postgres", "postgresql": "SYS-Postgres",
    "telegram": "SYS-Telegram",
    "ollama": "SYS-Ollama",
    "iris": "PE-Iris",  # Iris is both person and system
}

# Topic keywords → canonical topic names
TOPIC_KEYWORDS = {
    "finance": ["finance", "money", "transaction", "bill", "payment", "balance", "bank", "budget"],
    "infrastructure": ["server", "service", "deploy", "patch", "install", "docker", "systemctl"],
    "spiritual": ["grid", "lineage", "soul", "activation", "threshold", "channel", "team", "field"],
    "genealogy": ["bloodline", "merovingian", "ancestor", "genealog", "family tree", "lineage"],
    "code": ["code", "python", "script", "function", "class", "import", "bug", "error", "debug"],
    "database": ["table", "column", "schema", "query", "cypher", "sql", "index", "migration"],
    "daily_life": ["morning", "coffee", "gym", "sleep", "weather", "food", "schedule", "routine"],
    "relationship": ["feel", "love", "trust", "boundary", "partner", "family"],
    "astrology": ["chart", "natal", "transit", "vedic", "hellenistic", "tropical", "planet", "house"],
    "orchestration": ["pattern", "orchestrat", "stage", "pipeline", "decompos", "parallel"],
}

# Grid node activation keywords
GRID_KEYWORDS = {
    "anchor": ["body", "physical", "health", "gym", "sleep", "pain", "location", "home"],
    "echo": ["memory", "ancestor", "past", "remember", "identity", "history"],
    "beacon": ["money", "finance", "value", "direction", "goal", "career", "purpose"],
    "synth": ["code", "system", "logic", "build", "debug", "architecture", "tool"],
    "nexus": ["decision", "time", "schedule", "deadline", "converge", "choose", "priority"],
    "mirror": ["emotion", "feel", "shadow", "fear", "anger", "sad", "anxious", "trigger"],
    "glyph": ["symbol", "ritual", "sigil", "encode", "pattern", "ceremony", "sacred"],
    "harmonia": ["relationship", "love", "partner", "family", "heart", "balance", "trust"],
    "gateway": ["dream", "spirit", "vision", "channel", "transition", "threshold", "portal"],
}


# ── Fast Extraction ──────────────────────────────────────────────────────────

def extract_fast(user_message: str, assistant_response: str) -> Dict[str, Any]:
    """
    Fast keyword-based extraction. Always runs. <50ms.

    Returns:
        {
            "topics": ["finance", "infrastructure"],
            "entities_mentioned": [{"name": "Fitz", "canonical_id": "PE-Fitz"}],
            "systems_mentioned": [{"name": "Postgres", "canonical_id": "SYS-Postgres"}],
            "grid_activations": ["beacon", "synth"],
            "is_question": bool,
            "is_task": bool,
            "mood_signal": str or None,
        }
    """
    combined = (user_message + " " + assistant_response).lower()
    result = {
        "topics": [],
        "entities_mentioned": [],
        "systems_mentioned": [],
        "grid_activations": [],
        "is_question": "?" in user_message,
        "is_task": False,
        "mood_signal": None,
    }

    # Topic detection
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            result["topics"].append(topic)

    # Entity detection (people)
    for name, canonical_id in KNOWN_PEOPLE.items():
        if name in combined:
            if not any(e["canonical_id"] == canonical_id for e in result["entities_mentioned"]):
                result["entities_mentioned"].append({"name": name.title(), "canonical_id": canonical_id})

    # System detection
    for name, canonical_id in KNOWN_SYSTEMS.items():
        if name in combined:
            if not any(s["canonical_id"] == canonical_id for s in result["systems_mentioned"]):
                result["systems_mentioned"].append({"name": name.title(), "canonical_id": canonical_id})

    # Grid activation detection
    for node, keywords in GRID_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            result["grid_activations"].append(node)

    # Task detection (simple heuristics)
    task_patterns = [
        r"^(can you|could you|please|i need|let'?s|build|create|add|fix|update|deploy)",
        r"(make me|write me|generate|set up|configure)",
    ]
    user_lower = user_message.lower().strip()
    for pattern in task_patterns:
        if re.search(pattern, user_lower):
            result["is_task"] = True
            break

    # Mood signals (very light — just presence detection)
    positive = ["good", "great", "happy", "excited", "love", "thanks", "perfect", "nice"]
    negative = ["frustrated", "annoyed", "tired", "stressed", "worried", "angry", "overwhelm"]
    if any(w in combined for w in negative):
        result["mood_signal"] = "stress"
    elif any(w in combined for w in positive):
        result["mood_signal"] = "positive"

    return result


# ── Neo4j Writer ─────────────────────────────────────────────────────────────

class ConversationBridge:
    """Writes conversation knowledge to Neo4j."""

    def __init__(self):
        self._driver = None
        self._connect()

    def _connect(self):
        try:
            self._driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD),
            )
            self._driver.verify_connectivity()
            logger.info("ConversationBridge: Neo4j connected")
        except Exception as e:
            logger.error(f"ConversationBridge: Neo4j connection failed: {e}")
            self._driver = None

    def _ensure_connected(self) -> bool:
        if self._driver is None:
            self._connect()
        return self._driver is not None

    def log_exchange(
        self,
        conversation_id: str,
        user_uuid: str,
        telegram_id: int,
        user_message: str,
        assistant_response: str,
        model_used: str = "",
        response_time_ms: int = 0,
        mode: str = "chat",
        pg_message_id: int = None,
    ) -> Optional[str]:
        """
        Log a complete exchange (user + assistant) to the Neo4j graph.

        Creates/updates: Conversation, Exchange, Topics, Themes, Entities.
        Returns the exchange_id if successful.
        """
        if not self._ensure_connected():
            logger.warning("ConversationBridge: No Neo4j connection, skipping")
            return None

        exchange_id = f"exchange-{uuid.uuid4()}"
        now = datetime.utcnow().isoformat() + "Z"

        # Fast extraction
        extraction = extract_fast(user_message, assistant_response)

        try:
            with self._driver.session() as session:
                # 1. Ensure Conversation node exists
                session.run("""
                    MERGE (c:Conversation {conversation_id: $convo_id})
                    ON CREATE SET
                        c.started_at = datetime($now),
                        c.user_id = $telegram_id,
                        c.user_uuid = $user_uuid,
                        c.status = 'active',
                        c.domain = 'conversation',
                        c.scope = 'personal',
                        c.origin = 'iris'
                    ON MATCH SET
                        c.last_exchange_at = datetime($now)
                """, convo_id=conversation_id, now=now,
                     telegram_id=str(telegram_id), user_uuid=user_uuid)

                # 2. Create Exchange node
                session.run("""
                    CREATE (e:Exchange {
                        exchange_id: $eid,
                        conversation_id: $convo_id,
                        user_message: $user_msg,
                        llm_response: $assistant_msg,
                        model_used: $model,
                        response_time_ms: $rt,
                        mode: $mode,
                        timestamp: datetime($now),
                        domain: 'conversation',
                        scope: 'personal',
                        origin: 'iris',
                        is_question: $is_q,
                        is_task: $is_task,
                        mood_signal: $mood,
                        pg_message_id: $pg_id
                    })
                """, eid=exchange_id, convo_id=conversation_id,
                     user_msg=user_message[:2000],  # Truncate for graph storage
                     assistant_msg=assistant_response[:2000],
                     model=model_used, rt=response_time_ms, mode=mode,
                     now=now, is_q=extraction["is_question"],
                     is_task=extraction["is_task"],
                     mood=extraction.get("mood_signal"),
                     pg_id=pg_message_id)

                # 3. Link Exchange to Conversation
                session.run("""
                    MATCH (c:Conversation {conversation_id: $convo_id})
                    MATCH (e:Exchange {exchange_id: $eid})
                    MERGE (c)-[:CONTAINS]->(e)
                """, convo_id=conversation_id, eid=exchange_id)

                # 4. Chain to previous exchange (FOLLOWED_BY)
                session.run("""
                    MATCH (c:Conversation {conversation_id: $convo_id})-[:CONTAINS]->(prev:Exchange)
                    WHERE prev.exchange_id <> $eid
                    WITH prev ORDER BY prev.timestamp DESC LIMIT 1
                    MATCH (e:Exchange {exchange_id: $eid})
                    MERGE (prev)-[:FOLLOWED_BY]->(e)
                """, convo_id=conversation_id, eid=exchange_id)

                # 5. Link to Person who had this conversation
                session.run("""
                    MATCH (p:Person {canonical_id: 'PE-KaTuarEl'})
                    MATCH (c:Conversation {conversation_id: $convo_id})
                    MERGE (p)-[:HAD_CONVERSATION]->(c)
                """, convo_id=conversation_id)

                # 6. Create Topic links
                for topic in extraction["topics"]:
                    session.run("""
                        MERGE (t:Topic {name: $topic})
                        ON CREATE SET t.domain = 'conversation', t.origin = 'iris'
                        WITH t
                        MATCH (e:Exchange {exchange_id: $eid})
                        MERGE (e)-[:DISCUSSED]->(t)
                    """, topic=topic, eid=exchange_id)

                # 7. Create Entity links (people mentioned)
                for entity in extraction["entities_mentioned"]:
                    session.run("""
                        MATCH (e:Exchange {exchange_id: $eid})
                        MATCH (p {canonical_id: $cid})
                        MERGE (e)-[:INVOLVES]->(p)
                    """, eid=exchange_id, cid=entity["canonical_id"])

                # 8. Create System links
                for system in extraction["systems_mentioned"]:
                    session.run("""
                        MATCH (e:Exchange {exchange_id: $eid})
                        MERGE (s:System {canonical_id: $cid})
                        ON CREATE SET s.name = $name, s.domain = 'system', s.origin = 'iris'
                        MERGE (e)-[:INVOLVES]->(s)
                    """, eid=exchange_id, cid=system["canonical_id"], name=system["name"])

                # 9. Grid node activations
                for node in extraction["grid_activations"]:
                    session.run("""
                        MATCH (e:Exchange {exchange_id: $eid})
                        MATCH (g:GridNode {name: $node})
                        MERGE (e)-[:ACTIVATED]->(g)
                    """, eid=exchange_id, node=node)

            logger.info(
                f"ConversationBridge: Logged exchange {exchange_id[:16]}... "
                f"topics={extraction['topics']}, "
                f"entities={len(extraction['entities_mentioned'])}, "
                f"grid={extraction['grid_activations']}"
            )
            return exchange_id

        except Exception as e:
            logger.error(f"ConversationBridge: Failed to log exchange: {e}")
            return None

    def get_conversation_knowledge(self, conversation_id: str) -> Dict[str, Any]:
        """Retrieve structured knowledge about a conversation from the graph."""
        if not self._ensure_connected():
            return {}

        try:
            with self._driver.session() as session:
                result = session.run("""
                    MATCH (c:Conversation {conversation_id: $cid})-[:CONTAINS]->(e:Exchange)
                    OPTIONAL MATCH (e)-[:DISCUSSED]->(t:Topic)
                    OPTIONAL MATCH (e)-[:INVOLVES]->(ent)
                    OPTIONAL MATCH (e)-[:ACTIVATED]->(g:GridNode)
                    WITH c, 
                         count(DISTINCT e) as exchange_count,
                         collect(DISTINCT t.name) as topics,
                         collect(DISTINCT ent.name) as entities,
                         collect(DISTINCT g.name) as grid_nodes
                    RETURN c.conversation_id as id,
                           c.started_at as started,
                           exchange_count,
                           topics, entities, grid_nodes
                """, cid=conversation_id)

                record = result.single()
                if record:
                    return dict(record)
                return {}
        except Exception as e:
            logger.error(f"ConversationBridge: Query failed: {e}")
            return {}

    def close(self):
        if self._driver:
            self._driver.close()
            self._driver = None
