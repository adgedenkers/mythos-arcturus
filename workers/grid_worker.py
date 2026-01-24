#!/usr/bin/env python3
"""
Grid Analysis Worker

Performs Arcturian Grid 9-node analysis on messages.
Stores results in TimescaleDB and Neo4j.
"""

import os
import json
import logging
from typing import Dict, Any
from datetime import datetime

import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("worker.grid")

GRID_NODES = ["anchor", "echo", "beacon", "synth", "nexus", "mirror", "glyph", "harmonia", "gateway"]
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "mythos"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )


def analyze_with_llm(content: str) -> Dict[str, Any]:
    """Call LLM to perform grid analysis"""
    
    prompt = f"""Analyze this text through the Arcturian Grid - a 9-node consciousness processing framework.

Score each node 0-100 based on how present that domain is in the text:

ANCHOR (matter, location, physical world, body, domestic systems):
ECHO (memory, identity, ancestors, past events, timelines):
BEACON (value, manifestation, finance, signaling presence):
SYNTH (systems, logic, code, integration of disparate parts):
NEXUS (time, scheduling, convergence, decision points):
MIRROR (emotions, psyche, shadow work, self-reflection):
GLYPH (symbols, rituals, encoding, artifacts, meta-language):
HARMONIA (relationships, heart field, balance, connection):
GATEWAY (dreams, spiritual contact, transitions, portals):

Text to analyze:
"{content}"

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
    "entities": {{
        "people": ["names mentioned"],
        "places": ["locations mentioned"],
        "concepts": ["key concepts"],
        "symbols": ["symbols or significant objects"]
    }},
    "emotional_tone": "<primary emotion detected>",
    "themes": ["theme1", "theme2"]
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
            timeout=60
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


def store_grid_results(message_id: int, user_uuid: str, conversation_id: str, results: Dict[str, Any]) -> None:
    """Store grid analysis results in TimescaleDB"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        total = sum(results.get(node, 0) for node in GRID_NODES)
        dominant = results.get("dominant_node", max(GRID_NODES, key=lambda n: results.get(n, 0)))
        
        cur.execute("""
            INSERT INTO grid_activation_timeseries (
                time, user_uuid, conversation_id, message_id,
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
            user_uuid, conversation_id, message_id,
            results.get("anchor", 0), results.get("echo", 0), results.get("beacon", 0),
            results.get("synth", 0), results.get("nexus", 0), results.get("mirror", 0),
            results.get("glyph", 0), results.get("harmonia", 0), results.get("gateway", 0),
            dominant, total, OLLAMA_MODEL
        ))
        
        # Also store emotional state if detected
        emotional_tone = results.get("emotional_tone")
        if emotional_tone:
            cur.execute("""
                INSERT INTO emotional_state_timeseries (
                    time, user_uuid, conversation_id, message_id,
                    emotional_tone, themes
                ) VALUES (NOW(), %s, %s, %s, %s, %s)
            """, (user_uuid, conversation_id, message_id, emotional_tone, results.get("themes", [])))
        
        conn.commit()
        logger.info(f"Stored grid results: dominant={dominant}, total={total}")
        
    except Exception as e:
        conn.rollback()
        logger.exception(f"Failed to store grid results: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def process_grid_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for grid analysis worker"""
    
    message_id = payload.get("message_id")
    content = payload.get("content", "")
    user_uuid = payload.get("user_uuid")
    conversation_id = payload.get("conversation_id")
    
    if not content:
        logger.warning(f"Empty content for message {message_id}")
        return {"status": "skipped", "message_id": message_id, "reason": "empty_content"}
    
    logger.info(f"Analyzing message {message_id} ({len(content)} chars)")
    
    # Perform LLM analysis
    results = analyze_with_llm(content)
    
    if not results:
        return {"status": "failed", "message_id": message_id, "reason": "llm_failed"}
    
    # Store results
    try:
        store_grid_results(message_id, user_uuid, conversation_id, results)
    except Exception as e:
        return {"status": "failed", "message_id": message_id, "reason": str(e)}
    
    return {
        "status": "success",
        "message_id": message_id,
        "dominant_node": results.get("dominant_node"),
        "total_activation": sum(results.get(node, 0) for node in GRID_NODES),
        "entities": results.get("entities", {})
    }
