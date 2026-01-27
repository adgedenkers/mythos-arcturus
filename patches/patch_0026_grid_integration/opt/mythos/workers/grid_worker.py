#!/usr/bin/env python3
"""
Grid Analysis Worker

Performs Arcturian Grid 9-node analysis on message exchanges.
Stores results in PostgreSQL (timeseries) and Neo4j (graph).

The 9 nodes of the Arcturian Grid:
- ANCHOR: matter, location, physical world, body, domestic systems
- ECHO: memory, identity, ancestors, past events, timelines
- BEACON: value, manifestation, finance, signaling presence
- SYNTH: systems, logic, code, integration of disparate parts
- NEXUS: time, scheduling, convergence, decision points
- MIRROR: emotions, psyche, shadow work, self-reflection
- GLYPH: symbols, rituals, encoding, artifacts, meta-language
- HARMONIA: relationships, heart field, balance, connection
- GATEWAY: dreams, spiritual contact, transitions, portals
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

import requests
import psycopg2
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("worker.grid")

GRID_NODES = ["anchor", "echo", "beacon", "synth", "nexus", "mirror", "glyph", "harmonia", "gateway"]

# LLM Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:32b")

# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")


def get_db():
    """Get PostgreSQL connection"""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "mythos"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )


def get_neo4j_driver():
    """Get Neo4j driver"""
    return GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )


def analyze_with_llm(user_message: str, assistant_response: str) -> Optional[Dict[str, Any]]:
    """
    Call LLM to perform grid analysis on an exchange pair.
    
    Analyzes the combined user message and assistant response to understand
    which consciousness domains are being activated in the conversation.
    """
    
    prompt = f"""Analyze this conversation exchange through the Arcturian Grid - a 9-node consciousness processing framework.

Score each node 0-100 based on how present that domain is in the exchange:

ANCHOR (matter, location, physical world, body, domestic systems, hardware, infrastructure):
ECHO (memory, identity, ancestors, past events, timelines, history, continuity):
BEACON (value, manifestation, finance, signaling presence, worth, resources):
SYNTH (systems, logic, code, integration, patterns, synthesis, technical):
NEXUS (time, scheduling, convergence, decision points, pivots, timing):
MIRROR (emotions, psyche, shadow work, self-reflection, feelings, inner state):
GLYPH (symbols, rituals, encoding, artifacts, meta-language, sacred geometry):
HARMONIA (relationships, heart field, balance, connection, love, partnership):
GATEWAY (dreams, spiritual contact, transitions, portals, transcendence, visions):

=== EXCHANGE TO ANALYZE ===

USER MESSAGE:
{user_message}

ASSISTANT RESPONSE:
{assistant_response}

=== END EXCHANGE ===

Respond ONLY with valid JSON in this exact format:
{{
    "anchor": <0-100>,
    "echo": <0-100>,
    "beacon": <0-100>,
    "synth": <0-100>,
    "nexus": <0-100>,
    "mirror": <0-100>,
    "glyph": <0-100>,
    "harmonia": <0-100>,
    "gateway": <0-100>,
    "dominant_node": "<name of highest scoring node>",
    "secondary_node": "<name of second highest scoring node>",
    "entities": {{
        "people": ["names of people mentioned"],
        "places": ["locations mentioned"],
        "concepts": ["key concepts discussed"],
        "symbols": ["symbols or significant objects"],
        "systems": ["systems, tools, or technologies mentioned"]
    }},
    "emotional_tone": "<primary emotion or tone of exchange>",
    "themes": ["theme1", "theme2", "theme3"],
    "exchange_summary": "<one sentence summary of what was discussed>"
}}
"""
    
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=90
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "{}")
            return json.loads(response_text)
        else:
            logger.error(f"LLM call failed: {response.status_code} - {response.text}")
            return None
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"LLM request failed: {e}")
        return None
    except Exception as e:
        logger.exception(f"LLM analysis failed: {e}")
        return None


def store_grid_results_postgres(
    exchange_id: str,
    user_uuid: str,
    conversation_id: str,
    results: Dict[str, Any]
) -> None:
    """Store grid analysis results in PostgreSQL timeseries"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        total = sum(results.get(node, 0) for node in GRID_NODES)
        dominant = results.get("dominant_node", max(GRID_NODES, key=lambda n: results.get(n, 0)))
        
        cur.execute("""
            INSERT INTO grid_activation_timeseries (
                time, user_uuid, conversation_id, exchange_id,
                anchor_score, echo_score, beacon_score, synth_score,
                nexus_score, mirror_score, glyph_score, harmonia_score,
                gateway_score, dominant_node, total_activation,
                analysis_model
            ) VALUES (
                NOW(), %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s
            )
        """, (
            user_uuid, conversation_id, exchange_id,
            results.get("anchor", 0), results.get("echo", 0), results.get("beacon", 0),
            results.get("synth", 0), results.get("nexus", 0), results.get("mirror", 0),
            results.get("glyph", 0), results.get("harmonia", 0), results.get("gateway", 0),
            dominant, total, OLLAMA_MODEL
        ))
        
        # Store emotional state if detected
        emotional_tone = results.get("emotional_tone")
        if emotional_tone:
            themes = results.get("themes", [])
            cur.execute("""
                INSERT INTO emotional_state_timeseries (
                    time, user_uuid, conversation_id, emotional_tone, themes
                ) VALUES (NOW(), %s, %s, %s, %s)
            """, (user_uuid, conversation_id, emotional_tone, themes))
        
        conn.commit()
        logger.info(f"Stored grid results in Postgres: dominant={dominant}, total={total}")
        
    except Exception as e:
        conn.rollback()
        logger.exception(f"Failed to store grid results in Postgres: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def store_grid_results_neo4j(
    exchange_id: str,
    user_uuid: str,
    conversation_id: str,
    user_message: str,
    assistant_response: str,
    model_used: str,
    results: Dict[str, Any]
) -> None:
    """
    Store grid analysis results in Neo4j graph.
    
    Creates:
    - Exchange node with grid scores as properties
    - Links to GridNode nodes for dominant activations
    - Entity nodes for extracted entities
    - Theme nodes for themes
    """
    
    driver = get_neo4j_driver()
    
    try:
        with driver.session() as session:
            # Create/update Exchange node with grid scores
            session.run("""
                MERGE (e:Exchange {exchange_id: $exchange_id})
                SET e.user_uuid = $user_uuid,
                    e.conversation_id = $conversation_id,
                    e.user_message = $user_message,
                    e.assistant_response = $assistant_response,
                    e.model_used = $model_used,
                    e.timestamp = datetime(),
                    e.anchor_score = $anchor,
                    e.echo_score = $echo,
                    e.beacon_score = $beacon,
                    e.synth_score = $synth,
                    e.nexus_score = $nexus,
                    e.mirror_score = $mirror,
                    e.glyph_score = $glyph,
                    e.harmonia_score = $harmonia,
                    e.gateway_score = $gateway,
                    e.dominant_node = $dominant_node,
                    e.secondary_node = $secondary_node,
                    e.total_activation = $total_activation,
                    e.emotional_tone = $emotional_tone,
                    e.summary = $summary
            """, {
                "exchange_id": exchange_id,
                "user_uuid": user_uuid,
                "conversation_id": conversation_id,
                "user_message": user_message[:1000],  # Truncate for graph storage
                "assistant_response": assistant_response[:2000],
                "model_used": model_used,
                "anchor": results.get("anchor", 0),
                "echo": results.get("echo", 0),
                "beacon": results.get("beacon", 0),
                "synth": results.get("synth", 0),
                "nexus": results.get("nexus", 0),
                "mirror": results.get("mirror", 0),
                "glyph": results.get("glyph", 0),
                "harmonia": results.get("harmonia", 0),
                "gateway": results.get("gateway", 0),
                "dominant_node": results.get("dominant_node", ""),
                "secondary_node": results.get("secondary_node", ""),
                "total_activation": sum(results.get(node, 0) for node in GRID_NODES),
                "emotional_tone": results.get("emotional_tone", ""),
                "summary": results.get("exchange_summary", "")
            })
            
            # Create relationships to GridNode nodes for significant activations (score > 30)
            for node in GRID_NODES:
                score = results.get(node, 0)
                if score > 30:
                    session.run("""
                        MERGE (g:GridNode {name: $node_name})
                        WITH g
                        MATCH (e:Exchange {exchange_id: $exchange_id})
                        MERGE (e)-[r:ACTIVATED]->(g)
                        SET r.score = $score,
                            r.timestamp = datetime()
                    """, {
                        "node_name": node,
                        "exchange_id": exchange_id,
                        "score": score
                    })
            
            # Create Entity nodes and relationships
            entities = results.get("entities", {})
            
            # People
            for person in entities.get("people", []):
                if person and len(person) > 1:
                    session.run("""
                        MERGE (p:Entity:Person {name: $name})
                        WITH p
                        MATCH (e:Exchange {exchange_id: $exchange_id})
                        MERGE (e)-[:MENTIONED]->(p)
                    """, {"name": person, "exchange_id": exchange_id})
            
            # Concepts
            for concept in entities.get("concepts", []):
                if concept and len(concept) > 1:
                    session.run("""
                        MERGE (c:Entity:Concept {name: $name})
                        WITH c
                        MATCH (e:Exchange {exchange_id: $exchange_id})
                        MERGE (e)-[:DISCUSSED]->(c)
                    """, {"name": concept, "exchange_id": exchange_id})
            
            # Systems/Technologies
            for system in entities.get("systems", []):
                if system and len(system) > 1:
                    session.run("""
                        MERGE (s:Entity:System {name: $name})
                        WITH s
                        MATCH (e:Exchange {exchange_id: $exchange_id})
                        MERGE (e)-[:INVOLVES]->(s)
                    """, {"name": system, "exchange_id": exchange_id})
            
            # Themes
            for theme in results.get("themes", []):
                if theme and len(theme) > 1:
                    session.run("""
                        MERGE (t:Theme {name: $name})
                        WITH t
                        MATCH (e:Exchange {exchange_id: $exchange_id})
                        MERGE (e)-[:HAS_THEME]->(t)
                    """, {"name": theme, "exchange_id": exchange_id})
            
            # Link to User's Soul node if exists
            session.run("""
                MATCH (s:Soul)-[:CURRENTLY_EMBODIED_AS]->(p:Person)
                WHERE p.user_uuid = $user_uuid OR s.user_uuid = $user_uuid
                WITH s
                MATCH (e:Exchange {exchange_id: $exchange_id})
                MERGE (s)-[:HAD_EXCHANGE]->(e)
            """, {"user_uuid": user_uuid, "exchange_id": exchange_id})
            
            logger.info(f"Stored grid results in Neo4j for exchange {exchange_id[:8]}")
            
    except Exception as e:
        logger.exception(f"Failed to store grid results in Neo4j: {e}")
        raise
    finally:
        driver.close()


def process_grid_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for grid analysis worker.
    
    Accepts either:
    - Old format: {message_id, content, user_uuid, conversation_id}
    - New format: {exchange_id, user_message, assistant_response, user_uuid, conversation_id}
    """
    
    start_time = datetime.now()
    
    # Handle both old and new payload formats
    exchange_id = payload.get("exchange_id") or f"legacy-{payload.get('message_id', 'unknown')}"
    user_uuid = payload.get("user_uuid", "")
    conversation_id = payload.get("conversation_id", "")
    model_used = payload.get("model_used", OLLAMA_MODEL)
    
    # New format: separate user_message and assistant_response
    user_message = payload.get("user_message", "")
    assistant_response = payload.get("assistant_response", "")
    
    # Old format fallback: just content
    if not user_message and payload.get("content"):
        content = payload.get("content", "")
        user_message = content
        assistant_response = ""
    
    # Combined content for analysis
    combined_content = payload.get("combined_content") or f"{user_message}\n{assistant_response}".strip()
    
    if not combined_content:
        logger.warning(f"Empty content for exchange {exchange_id}")
        return {"status": "skipped", "exchange_id": exchange_id, "reason": "empty_content"}
    
    logger.info(f"Analyzing exchange {exchange_id[:8]} ({len(combined_content)} chars)")
    
    # Perform LLM analysis
    results = analyze_with_llm(user_message, assistant_response or user_message)
    
    if not results:
        return {"status": "failed", "exchange_id": exchange_id, "reason": "llm_failed"}
    
    # Store results in PostgreSQL
    try:
        store_grid_results_postgres(exchange_id, user_uuid, conversation_id, results)
    except Exception as e:
        logger.error(f"Postgres storage failed: {e}")
        # Continue to try Neo4j
    
    # Store results in Neo4j
    try:
        store_grid_results_neo4j(
            exchange_id=exchange_id,
            user_uuid=user_uuid,
            conversation_id=conversation_id,
            user_message=user_message,
            assistant_response=assistant_response,
            model_used=model_used,
            results=results
        )
    except Exception as e:
        logger.error(f"Neo4j storage failed: {e}")
    
    processing_time = (datetime.now() - start_time).total_seconds() * 1000
    
    return {
        "status": "success",
        "exchange_id": exchange_id,
        "dominant_node": results.get("dominant_node"),
        "secondary_node": results.get("secondary_node"),
        "total_activation": sum(results.get(node, 0) for node in GRID_NODES),
        "emotional_tone": results.get("emotional_tone"),
        "themes": results.get("themes", []),
        "entities": results.get("entities", {}),
        "processing_time_ms": int(processing_time)
    }
