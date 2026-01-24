#!/usr/bin/env python3
"""
Temporal Extraction Worker

Extracts dates, times, and temporal references from messages.
Links to astrological events when relevant.
"""

import os
import re
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

import psycopg2
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger("worker.temporal")

# Relative time patterns
RELATIVE_PATTERNS = {
    r"\byesterday\b": -1,
    r"\btoday\b": 0,
    r"\btomorrow\b": 1,
    r"\blast week\b": -7,
    r"\bnext week\b": 7,
    r"\blast month\b": -30,
    r"\bnext month\b": 30,
    r"\blast year\b": -365,
    r"\bnext year\b": 365,
}


def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        database=os.getenv("POSTGRES_DB", "mythos"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "")
    )


def extract_dates(text: str) -> List[datetime]:
    """Extract date references from text"""
    dates = []
    now = datetime.now()
    
    # Check relative patterns
    for pattern, days_offset in RELATIVE_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            dates.append(now + timedelta(days=days_offset))
    
    # ISO format dates: 2026-01-21
    iso_matches = re.findall(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    for match in iso_matches:
        try:
            dates.append(datetime.strptime(match, "%Y-%m-%d"))
        except ValueError:
            pass
    
    # US format dates: 1/21/2026 or 01/21/2026
    us_matches = re.findall(r"\b(\d{1,2}/\d{1,2}/\d{4})\b", text)
    for match in us_matches:
        try:
            dates.append(datetime.strptime(match, "%m/%d/%Y"))
        except ValueError:
            pass
    
    # Month name dates: January 21, 2026
    month_matches = re.findall(
        r"\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b",
        text, re.IGNORECASE
    )
    for match in month_matches:
        try:
            # Try multiple formats
            for fmt in ["%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y"]:
                try:
                    dates.append(datetime.strptime(match.replace(",", ""), fmt.replace(",", "")))
                    break
                except ValueError:
                    continue
        except Exception:
            pass
    
    return dates


def find_active_transits(date: datetime) -> List[Dict[str, Any]]:
    """Find astrological events active on a given date"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, event_type, body1, body2, description, significance
            FROM astrological_events
            WHERE %s BETWEEN COALESCE(influence_start, exact_time - INTERVAL '7 days') 
                        AND COALESCE(influence_end, exact_time + INTERVAL '7 days')
        """, (date,))
        
        results = []
        for row in cur.fetchall():
            results.append({
                "id": str(row[0]),
                "event_type": row[1],
                "body1": row[2],
                "body2": row[3],
                "description": row[4],
                "significance": row[5]
            })
        
        return results
        
    finally:
        cur.close()
        conn.close()


def store_temporal_data(message_id: int, user_uuid: str, dates: List[datetime], transits: List[Dict]) -> None:
    """Store extracted temporal data and link to astrological events"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Update message with mentioned dates (if column exists)
        if dates:
            try:
                cur.execute("""
                    UPDATE chat_messages
                    SET mentioned_dates = %s
                    WHERE message_id = %s
                """, ([d.date() for d in dates], message_id))
            except psycopg2.Error:
                # Column might not exist yet
                pass
        
        # Link to astrological events
        for transit in transits:
            cur.execute("""
                INSERT INTO message_astrological_context (message_id, astrological_event_id, auto_linked, relevance_score)
                VALUES (%s, %s, TRUE, 0.8)
                ON CONFLICT (message_id, astrological_event_id) DO NOTHING
            """, (message_id, transit["id"]))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        logger.exception(f"Failed to store temporal data: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def process_temporal(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for temporal extraction worker"""
    
    message_id = payload.get("message_id")
    content = payload.get("content", "")
    user_uuid = payload.get("user_uuid")
    
    if not content:
        return {"status": "skipped", "message_id": message_id, "reason": "empty_content"}
    
    logger.info(f"Extracting temporal data from message {message_id}")
    
    # Extract dates from text
    dates = extract_dates(content)
    logger.info(f"Found {len(dates)} date references")
    
    # Find active transits for mentioned dates
    all_transits = []
    for date in dates:
        transits = find_active_transits(date)
        all_transits.extend(transits)
    
    # Also check current date for context
    current_transits = find_active_transits(datetime.now())
    
    # Deduplicate transits
    seen_ids = set()
    unique_transits = []
    for t in all_transits + current_transits:
        if t["id"] not in seen_ids:
            seen_ids.add(t["id"])
            unique_transits.append(t)
    
    # Store results
    if dates or unique_transits:
        try:
            store_temporal_data(message_id, user_uuid, dates, unique_transits)
        except Exception as e:
            return {"status": "failed", "message_id": message_id, "error": str(e)}
    
    return {
        "status": "success",
        "message_id": message_id,
        "dates_found": len(dates),
        "transits_linked": len(unique_transits),
        "dates": [d.isoformat() for d in dates]
    }
