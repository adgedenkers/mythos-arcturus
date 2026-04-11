#!/usr/bin/env python3
"""
Summary Rebuild Worker

Rebuilds conversation summaries (Tier 1 and Tier 2) when triggered.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("worker.summary")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "mythos"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )


def get_messages_for_summary(conversation_id: str, start_idx: int, end_idx: int) -> List[Dict]:
    """Get messages within a range for summarization"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            WITH ranked AS (
                SELECT 
                    message_id, role, content, created_at,
                    ROW_NUMBER() OVER (ORDER BY created_at) as rn
                FROM chat_messages
                WHERE conversation_id = %s
            )
            SELECT message_id, role, content, created_at
            FROM ranked
            WHERE rn BETWEEN %s AND %s
            ORDER BY created_at
        """, (conversation_id, start_idx, end_idx))
        
        messages = []
        for row in cur.fetchall():
            messages.append({
                "message_id": row[0],
                "role": row[1],
                "content": row[2],
                "timestamp": row[3].isoformat() if row[3] else None
            })
        
        return messages
        
    finally:
        cur.close()
        conn.close()


def generate_summary(messages: List[Dict], tier: int) -> Dict[str, Any]:
    """Generate summary using LLM"""
    
    # Format messages for prompt
    formatted = []
    for msg in messages:
        role = msg["role"].upper()
        content = msg["content"][:500] if len(msg["content"]) > 500 else msg["content"]
        formatted.append(f"{role}: {content}")
    
    messages_text = "\n\n".join(formatted)
    
    # Tier determines verbosity
    word_target = 500 if tier == 1 else 800
    
    prompt = f"""Summarize this conversation segment. Target length: ~{word_target} words.

PRIORITIZE:
1. Main themes and topics discussed
2. Emotional tone and shifts
3. Key entities mentioned (people, places, concepts)
4. Important decisions or realizations
5. Context (where, when, circumstances)

CONVERSATION TO SUMMARIZE:
{messages_text}

Respond in JSON format:
{{
    "summary": "The narrative summary...",
    "themes": ["theme1", "theme2"],
    "emotional_tone": "primary emotion",
    "context_notes": "environmental/situational context",
    "key_entities": {{
        "people": ["names"],
        "concepts": ["concepts"],
        "places": ["places"]
    }}
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
            return json.loads(result.get("response", "{}"))
        else:
            logger.error(f"LLM call failed: {response.status_code}")
            return None
            
    except Exception as e:
        logger.exception(f"Summary generation failed: {e}")
        return None


def store_summary(conversation_id: str, user_uuid: str, tier: int, 
                  start_msg_id: int, end_msg_id: int, summary_data: Dict) -> str:
    """Store summary in database"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Mark old summary as superseded
        cur.execute("""
            UPDATE conversation_summaries
            SET is_current = FALSE, superseded_by = NULL
            WHERE conversation_id = %s AND tier = %s AND is_current = TRUE
            RETURNING id
        """, (conversation_id, tier))
        old_id = cur.fetchone()
        
        # Calculate metrics
        summary_text = summary_data.get("summary", "")
        original_tokens = len(summary_text.split()) * 2  # Rough estimate
        summary_tokens = len(summary_text.split())
        compression = original_tokens / summary_tokens if summary_tokens > 0 else 1.0
        
        # Insert new summary
        cur.execute("""
            INSERT INTO conversation_summaries (
                conversation_id, user_uuid, tier,
                start_message_id, end_message_id, message_count,
                summary_text, themes, emotional_tone, context_notes, key_entities,
                original_tokens, summary_tokens, compression_ratio,
                is_current
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE
            )
            RETURNING id
        """, (
            conversation_id, user_uuid, tier,
            start_msg_id, end_msg_id, end_msg_id - start_msg_id + 1,
            summary_text,
            summary_data.get("themes", []),
            summary_data.get("emotional_tone"),
            summary_data.get("context_notes"),
            json.dumps(summary_data.get("key_entities", {})),
            original_tokens, summary_tokens, compression
        ))
        
        new_id = cur.fetchone()[0]
        
        # Link old to new
        if old_id:
            cur.execute("""
                UPDATE conversation_summaries
                SET superseded_by = %s
                WHERE id = %s
            """, (new_id, old_id[0]))
        
        conn.commit()
        return str(new_id)
        
    except Exception as e:
        conn.rollback()
        logger.exception(f"Failed to store summary: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def process_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for summary rebuild worker"""
    
    conversation_id = payload.get("conversation_id")
    user_uuid = payload.get("user_uuid")
    tier = payload.get("tier", 1)
    start_idx = payload.get("start_idx", 1)
    end_idx = payload.get("end_idx", 20)
    
    logger.info(f"Rebuilding Tier {tier} summary for conversation {conversation_id[:8]}...")
    
    # Get messages
    messages = get_messages_for_summary(conversation_id, start_idx, end_idx)
    
    if not messages:
        return {"status": "skipped", "conversation_id": conversation_id, "reason": "no_messages"}
    
    logger.info(f"Summarizing {len(messages)} messages")
    
    # Generate summary
    summary_data = generate_summary(messages, tier)
    
    if not summary_data:
        return {"status": "failed", "conversation_id": conversation_id, "reason": "generation_failed"}
    
    # Store summary
    try:
        start_msg_id = messages[0]["message_id"]
        end_msg_id = messages[-1]["message_id"]
        summary_id = store_summary(
            conversation_id, user_uuid, tier,
            start_msg_id, end_msg_id, summary_data
        )
    except Exception as e:
        return {"status": "failed", "conversation_id": conversation_id, "error": str(e)}
    
    return {
        "status": "success",
        "conversation_id": conversation_id,
        "tier": tier,
        "summary_id": summary_id,
        "messages_summarized": len(messages),
        "themes": summary_data.get("themes", [])
    }
