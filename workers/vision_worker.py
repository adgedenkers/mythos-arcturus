#!/usr/bin/env python3
"""
Vision Analysis Worker

Analyzes photos using Llama Vision via Ollama.
Stores results in PostgreSQL and optionally generates image embeddings for Qdrant.
"""

import os
import base64
import json
import logging
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("worker.vision")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")


def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "mythos"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )


def analyze_image(image_path: str) -> Dict[str, Any]:
    """Analyze image using Llama Vision"""
    
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Read and encode image
    with open(path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    prompt = """Analyze this image thoroughly. Provide:

1. A general description (2-3 sentences)
2. Objects and elements visible
3. People (count and brief description if visible)
4. Any text visible (transcribe if possible)
5. Symbols or patterns (especially sacred geometry, spirals, spiritual symbols)
6. The emotional tone or mood
7. Suggested tags for categorization

Respond in JSON format:
{
    "description": "General description of the image",
    "objects": ["object1", "object2"],
    "people_count": 0,
    "people_description": "Description of people if any",
    "text_detected": "Any text found in image",
    "symbols": ["symbol1", "symbol2"],
    "sacred_geometry": false,
    "emotional_tone": "mood/emotion",
    "colors_dominant": ["color1", "color2"],
    "tags": ["tag1", "tag2", "tag3"]
}
"""
    
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": VISION_MODEL,
                "prompt": prompt,
                "images": [image_data],
                "stream": False,
                "format": "json"
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return json.loads(result.get("response", "{}"))
        else:
            logger.error(f"Vision API failed: {response.status_code}")
            return None
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse vision response: {e}")
        return None
    except Exception as e:
        logger.exception(f"Vision analysis failed: {e}")
        return None


def store_analysis(photo_id: str, analysis: Dict[str, Any]) -> None:
    """Store vision analysis results in PostgreSQL"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE media_files SET
                analysis_data = %s,
                auto_tags = %s,
                processed = TRUE,
                processed_at = NOW()
            WHERE id = %s
        """, (
            json.dumps(analysis),
            analysis.get("tags", []),
            photo_id
        ))
        
        if cur.rowcount == 0:
            logger.warning(f"No media_files row found for id {photo_id}")
        
        conn.commit()
        logger.info(f"Stored analysis for photo {photo_id}")
        
    except Exception as e:
        conn.rollback()
        logger.exception(f"Failed to store analysis: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def process_vision(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for vision analysis worker"""
    
    photo_id = payload.get("photo_id")
    file_path = payload.get("file_path")
    user_uuid = payload.get("user_uuid")
    
    if not file_path:
        return {"status": "failed", "photo_id": photo_id, "error": "no_file_path"}
    
    logger.info(f"Analyzing photo {photo_id}: {file_path}")
    
    # Check file exists
    if not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        return {"status": "failed", "photo_id": photo_id, "error": "file_not_found"}
    
    # Analyze image
    analysis = analyze_image(file_path)
    
    if not analysis:
        return {"status": "failed", "photo_id": photo_id, "reason": "analysis_failed"}
    
    # Store results
    try:
        store_analysis(photo_id, analysis)
    except Exception as e:
        return {"status": "failed", "photo_id": photo_id, "error": str(e)}
    
    return {
        "status": "success",
        "photo_id": photo_id,
        "tags_count": len(analysis.get("tags", [])),
        "symbols_detected": len(analysis.get("symbols", [])),
        "has_sacred_geometry": analysis.get("sacred_geometry", False)
    }
