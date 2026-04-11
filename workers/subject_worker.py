#!/usr/bin/env python3
"""
Subject Enrichment Worker
=========================
Asynchronously enriches subject points with:
  - LLM-generated subject summaries (better than heuristic)
  - Embedding vectors for similarity matching
  - Refined emotional tone analysis

Consumes from Redis stream: mythos:assignments:subject
Uses the existing worker framework pattern.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")
logger = logging.getLogger("worker.subject")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# Use a small fast model for subject extraction — not the main conversation model
SUBJECT_MODEL = os.getenv("SUBJECT_EXTRACTION_MODEL", "qwen2.5:7b")

DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_NAME = os.getenv('POSTGRES_DB', 'mythos')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASS = os.getenv('POSTGRES_PASSWORD', '')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

# Lazy-loaded embedding model
_embed_model = None


def get_db():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER,
        password=DB_PASS, port=DB_PORT
    )


def get_embed_model():
    """Lazy-load the sentence transformer model."""
    global _embed_model
    if _embed_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("Loaded embedding model: all-MiniLM-L6-v2")
        except ImportError:
            logger.warning("sentence-transformers not available, skipping embeddings")
    return _embed_model


def process_subject(assignment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a subject enrichment assignment.
    
    Assignment payload:
    {
        "point_id": 123,
        "message_text": "the original message",
        "chat_id": 456,
        "role": "user"
    }
    """
    point_id = assignment.get('point_id')
    message_text = assignment.get('message_text', '')
    
    if not point_id or not message_text:
        return {"status": "skipped", "reason": "missing point_id or message_text"}
    
    result = {"point_id": point_id, "enrichments": []}
    
    # ── LLM Subject Extraction ──
    try:
        llm_subject = _extract_subject_llm(message_text)
        if llm_subject:
            _update_subject_point(point_id, llm_subject)
            result["enrichments"].append("llm_subject")
    except Exception as e:
        logger.error(f"LLM extraction failed for point {point_id}: {e}")
    
    # ── Embedding Generation ──
    try:
        model = get_embed_model()
        if model:
            text_for_embedding = llm_subject.get('summary', message_text) if llm_subject else message_text
            vector = model.encode(text_for_embedding).tolist()
            _update_subject_vector(point_id, vector)
            result["enrichments"].append("embedding")
    except Exception as e:
        logger.error(f"Embedding failed for point {point_id}: {e}")
    
    result["status"] = "ok"
    return result


def _extract_subject_llm(message_text: str) -> Optional[Dict]:
    """
    Use a small LLM to extract a refined subject summary and tags.
    """
    prompt = f"""Analyze this message from a conversation. Return ONLY a JSON object with:
- "summary": 1-2 sentence description of what this message is about (the topic, not what the person said)
- "tags": array of 3-8 topic keywords (nouns and specific concepts only, lowercase)
- "tone": one of: neutral, focused, excited, frustrated, contemplative, anxious, playful, reflective
- "energy": one of: low, medium, high

Message: "{message_text[:500]}"

Return ONLY valid JSON, no other text."""

    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": SUBJECT_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 256,
                }
            },
            timeout=30
        )
        
        if resp.status_code != 200:
            logger.warning(f"Ollama returned {resp.status_code}")
            return None
        
        text = resp.json().get('response', '').strip()
        
        # Try to extract JSON from the response
        # Sometimes models wrap in ```json blocks
        if '```' in text:
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
            text = text.strip()
        
        data = json.loads(text)
        return {
            'summary': data.get('summary', '')[:200],
            'tags': [t.lower().strip() for t in data.get('tags', [])][:10],
            'tone': data.get('tone', 'neutral'),
            'energy': data.get('energy', 'medium'),
        }
        
    except json.JSONDecodeError:
        logger.warning(f"Could not parse LLM response as JSON: {text[:100]}")
        return None
    except Exception as e:
        logger.error(f"LLM subject extraction failed: {e}")
        return None


def _update_subject_point(point_id: int, enrichment: Dict) -> None:
    """Update a subject point with LLM-enriched data."""
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE conversation_subject_points SET
                subject_summary = %s,
                subject_tags = %s,
                emotional_tone = %s,
                energy_level = %s
            WHERE id = %s
        """, (
            enrichment['summary'],
            enrichment['tags'],
            enrichment['tone'],
            enrichment['energy'],
            point_id,
        ))
        
        conn.commit()
        logger.debug(f"Enriched subject point {point_id}")
    except Exception as e:
        logger.error(f"Failed to update subject point {point_id}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


def _update_subject_vector(point_id: int, vector: list) -> None:
    """Update a subject point with its embedding vector."""
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Check if the vector column exists
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'conversation_subject_points' 
            AND column_name = 'subject_vector'
        """)
        
        if not cur.fetchone():
            logger.debug("subject_vector column not available, skipping")
            return
        
        cur.execute("""
            UPDATE conversation_subject_points SET
                subject_vector = %s::vector
            WHERE id = %s
        """, (str(vector), point_id))
        
        conn.commit()
        logger.debug(f"Set embedding for subject point {point_id}")
    except Exception as e:
        logger.error(f"Failed to set vector for point {point_id}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
