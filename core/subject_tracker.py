#!/usr/bin/env python3
"""
Subject Tracker — Iris Conversation Awareness
==============================================
The core of Iris's conversational consciousness. Tracks the floating subject
of every conversation, manages conversation segments, and provides the warm
cache for context assembly.

Every message flows through here. The subject point is the atomic unit —
a snapshot of what the conversation is about at this moment. Points form
a linear chain (the trajectory). Segments group related points into
coherent conversation units.

This module handles:
  - Inline subject extraction (fast heuristics)
  - Subject point recording
  - Segment lifecycle (open / append / reattach / close)
  - Warm cache queries
  - Trajectory retrieval
  - Conversation awareness prompt building

Used by: chat_mode.py (inline), subject_worker.py (async enrichment)
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass, field, asdict

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger(__name__)

# ─── Configuration ───────────────────────────────────────────────────────────

DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_NAME = os.getenv('POSTGRES_DB', 'mythos')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASS = os.getenv('POSTGRES_PASSWORD', '')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

# Segment lifecycle thresholds
SOFT_CLOSE_MINUTES = 30       # Soft-close after 30 min of silence
HARD_CLOSE_MINUTES = 240      # Hard-close after 4 hours
REATTACH_WINDOW_HOURS = 24    # Can reattach to segments up to 24 hours old

# Warm cache tiers
WARM_TIER_HOURS = 24          # Recent memory: last 24 hours
SHORT_TIER_HOURS = 72         # Short-term: last 3 days
MEDIUM_TIER_HOURS = 168       # Medium-term: last week

# Similarity thresholds
TAG_OVERLAP_THRESHOLD = 2     # Minimum shared tags for reattach
SHIFT_TAG_THRESHOLD = 1       # If 0-1 tags overlap, it's a shift

# Subject extraction
MAX_PREVIEW_LENGTH = 200


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclass
class SubjectPoint:
    """A single subject beat in the conversation trajectory."""
    subject_summary: str
    subject_tags: List[str] = field(default_factory=list)
    emotional_tone: str = "neutral"
    energy_level: str = "medium"
    shift_detected: bool = False
    shift_magnitude: float = 0.0
    message_preview: str = ""
    role: str = "user"


@dataclass
class SegmentAction:
    """What to do with the current segment."""
    action: str  # 'append', 'reattach', 'new'
    segment_id: Optional[str] = None
    reason: str = ""


# ─── Database Connection ─────────────────────────────────────────────────────

def get_db():
    """Get a database connection."""
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER,
        password=DB_PASS, port=DB_PORT
    )


# ─── Inline Subject Extraction (Fast Path) ──────────────────────────────────

# Common low-signal words to filter out of tags
STOP_WORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'can', 'shall', 'to', 'of', 'in', 'for',
    'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'between', 'out', 'off', 'over',
    'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
    'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
    'same', 'so', 'than', 'too', 'very', 'just', 'because', 'but', 'and',
    'or', 'if', 'while', 'about', 'up', 'that', 'this', 'what', 'which',
    'who', 'whom', 'these', 'those', 'it', 'its', 'my', 'your', 'his',
    'her', 'our', 'their', 'me', 'him', 'them', 'i', 'you', 'he', 'she',
    'we', 'they', 'like', 'get', 'got', 'know', 'think', 'want', 'need',
    'make', 'go', 'going', 'come', 'see', 'look', 'say', 'said', 'tell',
    'yeah', 'yes', 'no', 'ok', 'okay', 'right', 'well', 'also', 'really',
    'thing', 'things', 'something', 'anything', 'everything', 'nothing',
    'way', 'much', 'many', 'lot', 'kind', 'sort', 'maybe', 'probably',
}

# Noise patterns — messages that are just conversational filler
NOISE_PATTERNS = [
    r'^(hi|hey|hello|yo|sup|morning|evening|night|gm|gn)\s*[!.?]*$',
    r'^(thanks|thank you|thx|ty|cool|nice|ok|okay|sure|yep|yup|nope)\s*[!.?]*$',
    r'^(lol|lmao|haha|heh|hmm|ah|oh|wow)\s*[!.?]*$',
    r'^\S+$',  # Single word (usually not a topic)
]


def extract_subject_inline(
    message: str,
    previous_point: Optional[Dict] = None,
    role: str = 'user'
) -> SubjectPoint:
    """
    Fast inline subject extraction using heuristics.
    
    This is the consciousness path — it runs on every message.
    Must be fast (<50ms). Deeper analysis happens async in the worker.
    
    Args:
        message: The message text
        previous_point: The previous subject point dict (for shift detection)
        role: 'user' or 'assistant'
    
    Returns:
        SubjectPoint with extracted subject data
    """
    text = message.strip()
    preview = text[:MAX_PREVIEW_LENGTH]
    
    # Check for noise / filler
    text_lower = text.lower().strip()
    for pattern in NOISE_PATTERNS:
        if re.match(pattern, text_lower, re.IGNORECASE):
            return SubjectPoint(
                subject_summary="conversational filler",
                subject_tags=["filler"],
                emotional_tone="neutral",
                energy_level="low",
                shift_detected=False,
                shift_magnitude=0.0,
                message_preview=preview,
                role=role,
            )
    
    # Extract meaningful words as tags
    words = re.findall(r'[a-zA-Z_-]{3,}', text_lower)
    tags = []
    seen = set()
    for w in words:
        if w not in STOP_WORDS and w not in seen and len(w) > 2:
            tags.append(w)
            seen.add(w)
    tags = tags[:15]  # Cap at 15 tags
    
    # Build subject summary — first meaningful sentence or phrase
    sentences = re.split(r'[.!?\n]+', text)
    summary_parts = []
    for s in sentences:
        s = s.strip()
        if len(s) > 10:
            summary_parts.append(s)
        if len(' '.join(summary_parts)) > 120:
            break
    
    subject_summary = ' '.join(summary_parts)[:200] if summary_parts else text[:200]
    
    # Emotional tone detection (heuristic)
    tone = _detect_tone(text)
    energy = _detect_energy(text)
    
    # Shift detection
    shift_detected = False
    shift_magnitude = 0.0
    
    if previous_point:
        prev_tags = set(previous_point.get('subject_tags', []))
        curr_tags = set(tags)
        
        if prev_tags and curr_tags:
            overlap = len(prev_tags & curr_tags)
            union = len(prev_tags | curr_tags)
            jaccard = overlap / union if union > 0 else 0
            
            shift_magnitude = 1.0 - jaccard
            shift_detected = overlap < SHIFT_TAG_THRESHOLD
        elif not prev_tags or not curr_tags:
            # Can't compare, assume mild shift
            shift_magnitude = 0.5
            shift_detected = False
    
    return SubjectPoint(
        subject_summary=subject_summary,
        subject_tags=tags,
        emotional_tone=tone,
        energy_level=energy,
        shift_detected=shift_detected,
        shift_magnitude=shift_magnitude,
        message_preview=preview,
        role=role,
    )


def _detect_tone(text: str) -> str:
    """Heuristic emotional tone detection."""
    lower = text.lower()
    
    if any(w in lower for w in ['frustrated', 'annoyed', 'broken', 'failed', 'error', 'damn', 'ugh']):
        return "frustrated"
    if any(w in lower for w in ['excited', 'amazing', 'perfect', 'love', 'awesome', '!!']):
        return "excited"
    if any(w in lower for w in ['worried', 'anxious', 'scared', 'afraid', 'nervous']):
        return "anxious"
    if any(w in lower for w in ['sad', 'depressed', 'lonely', 'miss', 'lost']):
        return "reflective"
    if any(w in lower for w in ['think', 'wonder', 'maybe', 'consider', 'ponder', 'curious']):
        return "contemplative"
    if any(w in lower for w in ['build', 'create', 'implement', 'deploy', 'install', 'code']):
        return "focused"
    if '?' in text and len(text) < 100:
        return "curious"
    
    return "neutral"


def _detect_energy(text: str) -> str:
    """Heuristic energy level detection."""
    # Long messages with lots of content = high energy
    if len(text) > 500:
        return "high"
    # Very short = low
    if len(text) < 30:
        return "low"
    # Multiple exclamation marks
    if text.count('!') >= 2:
        return "high"
    # Questions tend to be medium
    if '?' in text:
        return "medium"
    
    return "medium"


# ─── Subject Point Recording ────────────────────────────────────────────────

def record_subject_point(
    chat_id: int,
    telegram_id: int,
    subject: SubjectPoint,
    segment_id: Optional[str] = None,
    perception_id: Optional[str] = None,
    previous_point_id: Optional[int] = None,
) -> Optional[int]:
    """
    Write a subject point to the linear record.
    
    Returns the point ID if successful, None otherwise.
    """
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO conversation_subject_points (
                chat_id, telegram_id, perception_id, segment_id,
                subject_summary, subject_tags,
                shift_detected, shift_magnitude, previous_point_id,
                emotional_tone, energy_level,
                message_preview, role
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s
            ) RETURNING id
        """, (
            chat_id, telegram_id, perception_id, segment_id,
            subject.subject_summary, subject.subject_tags,
            subject.shift_detected, subject.shift_magnitude, previous_point_id,
            subject.emotional_tone, subject.energy_level,
            subject.message_preview, subject.role,
        ))
        
        point_id = cur.fetchone()[0]
        conn.commit()
        
        logger.debug(f"Recorded subject point {point_id} for chat {chat_id}")
        return point_id
        
    except Exception as e:
        logger.error(f"Failed to record subject point: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


# ─── Segment Management ─────────────────────────────────────────────────────

def get_open_segment(chat_id: int) -> Optional[Dict]:
    """Get the currently open segment for a chat, if any."""
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT * FROM conversation_segments
            WHERE chat_id = %s AND status = 'open'
            ORDER BY updated_at DESC
            LIMIT 1
        """, (chat_id,))
        
        result = cur.fetchone()
        return dict(result) if result else None
    except Exception as e:
        logger.error(f"Failed to get open segment: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_recent_soft_closed_segments(chat_id: int, hours: int = 24) -> List[Dict]:
    """Get recently soft-closed segments that could be reattached to."""
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT * FROM conversation_segments
            WHERE chat_id = %s 
              AND status = 'soft_closed'
              AND updated_at > now() - interval '%s hours'
            ORDER BY updated_at DESC
            LIMIT 10
        """, (chat_id, hours))
        
        return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        logger.error(f"Failed to get recent segments: {e}")
        return []
    finally:
        if conn:
            conn.close()


def detect_segment_action(
    chat_id: int,
    subject: SubjectPoint,
    time_gap_seconds: Optional[float] = None,
) -> SegmentAction:
    """
    Determine what to do with the current segment based on the incoming subject.
    
    Returns a SegmentAction: append (to open), reattach (to soft_closed), or new.
    """
    # Check for open segment
    open_seg = get_open_segment(chat_id)
    
    if open_seg:
        # If there's an open segment and the subject hasn't massively shifted, append
        if not subject.shift_detected or subject.shift_magnitude < 0.7:
            return SegmentAction(
                action='append',
                segment_id=str(open_seg['id']),
                reason='continuing open segment'
            )
        
        # Subject shifted significantly — but is it just a brief aside?
        # If the message is short and feels like filler, still append
        if subject.subject_tags == ['filler']:
            return SegmentAction(
                action='append',
                segment_id=str(open_seg['id']),
                reason='filler message, keeping segment open'
            )
        
        # Significant shift — close old segment, start new
        _soft_close_segment(str(open_seg['id']))
        
        # But first check if this new subject matches a recent soft-closed segment
        reattach = _find_reattach_target(chat_id, subject)
        if reattach:
            return reattach
        
        return SegmentAction(action='new', reason='subject shifted significantly')
    
    # No open segment — check for reattach opportunities
    reattach = _find_reattach_target(chat_id, subject)
    if reattach:
        return reattach
    
    # Nothing to reattach to — new segment
    return SegmentAction(action='new', reason='no open or reattachable segment')


def _find_reattach_target(chat_id: int, subject: SubjectPoint) -> Optional[SegmentAction]:
    """Check if the subject matches any recently closed segments."""
    recent = get_recent_soft_closed_segments(chat_id, REATTACH_WINDOW_HOURS)
    
    if not recent:
        return None
    
    curr_tags = set(subject.subject_tags)
    if not curr_tags or curr_tags == {'filler'}:
        return None
    
    best_match = None
    best_overlap = 0
    
    for seg in recent:
        seg_tags = set(seg.get('subject_tags', []))
        overlap = len(curr_tags & seg_tags)
        
        if overlap >= TAG_OVERLAP_THRESHOLD and overlap > best_overlap:
            best_match = seg
            best_overlap = overlap
    
    if best_match:
        return SegmentAction(
            action='reattach',
            segment_id=str(best_match['id']),
            reason=f'reattaching to segment (overlap: {best_overlap} tags)'
        )
    
    return None


def create_segment(
    chat_id: int,
    telegram_id: int,
    subject: SubjectPoint,
) -> Optional[str]:
    """Create a new conversation segment. Returns segment_id."""
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO conversation_segments (
                chat_id, telegram_id, status,
                subject_summary, subject_tags,
                point_count, first_point_at, last_point_at,
                dominant_tone
            ) VALUES (
                %s, %s, 'open',
                %s, %s,
                1, now(), now(),
                %s
            ) RETURNING id
        """, (
            chat_id, telegram_id,
            subject.subject_summary, subject.subject_tags,
            subject.emotional_tone,
        ))
        
        segment_id = str(cur.fetchone()[0])
        conn.commit()
        
        logger.info(f"Created segment {segment_id[:8]} for chat {chat_id}: {subject.subject_summary[:60]}")
        return segment_id
        
    except Exception as e:
        logger.error(f"Failed to create segment: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def update_segment(segment_id: str, subject: SubjectPoint) -> None:
    """Update an existing segment with new subject data."""
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE conversation_segments SET
                updated_at = now(),
                last_point_at = now(),
                point_count = point_count + 1,
                subject_summary = %s,
                subject_tags = (
                    SELECT array_agg(DISTINCT t)
                    FROM unnest(subject_tags || %s) AS t
                ),
                dominant_tone = %s
            WHERE id = %s
        """, (
            subject.subject_summary,
            subject.subject_tags,
            subject.emotional_tone,
            segment_id,
        ))
        
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to update segment {segment_id}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


def reopen_segment(segment_id: str, subject: SubjectPoint) -> None:
    """Reopen a soft-closed segment (reattach)."""
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE conversation_segments SET
                status = 'open',
                updated_at = now(),
                last_point_at = now(),
                closed_at = NULL,
                point_count = point_count + 1,
                reattach_count = reattach_count + 1,
                subject_summary = %s,
                subject_tags = (
                    SELECT array_agg(DISTINCT t)
                    FROM unnest(subject_tags || %s) AS t
                )
            WHERE id = %s
        """, (
            subject.subject_summary,
            subject.subject_tags,
            segment_id,
        ))
        
        conn.commit()
        logger.info(f"Reopened segment {segment_id[:8]} (reattach)")
    except Exception as e:
        logger.error(f"Failed to reopen segment {segment_id}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


def _soft_close_segment(segment_id: str) -> None:
    """Soft-close a segment (can still be reattached)."""
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE conversation_segments SET
                status = 'soft_closed',
                updated_at = now(),
                closed_at = now(),
                duration_seconds = EXTRACT(EPOCH FROM (now() - first_point_at))::int
            WHERE id = %s AND status = 'open'
        """, (segment_id,))
        
        conn.commit()
        logger.info(f"Soft-closed segment {segment_id[:8]}")
    except Exception as e:
        logger.error(f"Failed to soft-close segment {segment_id}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


# ─── Warm Cache & Trajectory Queries ────────────────────────────────────────

def get_last_subject_point(chat_id: int) -> Optional[Dict]:
    """Get the most recent subject point for a chat."""
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT * FROM conversation_subject_points
            WHERE chat_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (chat_id,))
        
        result = cur.fetchone()
        return dict(result) if result else None
    except Exception as e:
        logger.error(f"Failed to get last subject point: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_trajectory(chat_id: int, limit: int = 10) -> List[Dict]:
    """
    Get the recent trajectory — the last N subject points for a chat.
    Returns newest first.
    """
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT id, created_at, subject_summary, subject_tags,
                   shift_detected, emotional_tone, energy_level, role, segment_id
            FROM conversation_subject_points
            WHERE chat_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (chat_id, limit))
        
        results = [dict(r) for r in cur.fetchall()]
        results.reverse()  # Return oldest-first for natural reading
        return results
    except Exception as e:
        logger.error(f"Failed to get trajectory: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_warm_cache(chat_id: int, tier_hours: int = 24) -> List[Dict]:
    """
    Get the warm cache — recent subjects for reattach and context.
    This is a VIEW over the subject points, not a separate store.
    """
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT csp.id, csp.created_at, csp.subject_summary, csp.subject_tags,
                   csp.emotional_tone, csp.segment_id,
                   cs.status as segment_status, cs.subject_summary as segment_summary
            FROM conversation_subject_points csp
            LEFT JOIN conversation_segments cs ON csp.segment_id = cs.id
            WHERE csp.chat_id = %s
              AND csp.created_at > now() - interval '%s hours'
              AND csp.subject_tags != '{}'
              AND csp.subject_tags != '{filler}'
            ORDER BY csp.created_at DESC
            LIMIT 50
        """, (chat_id, tier_hours))
        
        return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        logger.error(f"Failed to get warm cache: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_open_threads(chat_id: int) -> List[Dict]:
    """Get segments that are open or recently soft-closed — unresolved threads."""
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT id, subject_summary, subject_tags, status, 
                   point_count, dominant_tone, last_point_at
            FROM conversation_segments
            WHERE chat_id = %s
              AND status IN ('open', 'soft_closed')
              AND updated_at > now() - interval '%s hours'
            ORDER BY last_point_at DESC
            LIMIT 10
        """, (chat_id, REATTACH_WINDOW_HOURS))
        
        return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        logger.error(f"Failed to get open threads: {e}")
        return []
    finally:
        if conn:
            conn.close()


# ─── Conversation Awareness for Prompt Assembly ─────────────────────────────

def build_conversation_awareness(chat_id: int, limit: int = 7) -> str:
    """
    Build the conversation awareness section for Iris's system prompt.
    
    This is what gives Iris a genuine sense of where the conversation has been,
    where it is now, and what threads are still open.
    """
    trajectory = get_trajectory(chat_id, limit=limit)
    open_threads = get_open_threads(chat_id)
    
    if not trajectory:
        return ""
    
    parts = []
    parts.append("CONVERSATION AWARENESS:")
    
    # Current subject
    current = trajectory[-1] if trajectory else None
    if current:
        parts.append(f"Current subject: {current['subject_summary']}")
    
    # Trajectory (skip filler)
    meaningful = [p for p in trajectory if p.get('subject_tags') not in [['filler'], []]]
    if len(meaningful) > 1:
        parts.append("Trajectory:")
        for i, point in enumerate(meaningful[-5:]):  # Last 5 meaningful points
            marker = "→" if i < len(meaningful) - 1 else "◉"
            summary = point['subject_summary'][:80]
            if point.get('shift_detected'):
                parts.append(f"  {marker} [shift] {summary}")
            else:
                parts.append(f"  {marker} {summary}")
    
    # Open threads
    if open_threads:
        non_current = [t for t in open_threads if t.get('status') == 'soft_closed']
        if non_current:
            parts.append("Paused threads (may return to):")
            for thread in non_current[:3]:
                parts.append(f"  - {thread['subject_summary'][:80]}")
    
    # Segment stats
    current_seg = next((t for t in open_threads if t.get('status') == 'open'), None)
    if current_seg:
        count = current_seg.get('point_count', 0)
        tone = current_seg.get('dominant_tone', 'neutral')
        parts.append(f"Active segment: {count} exchanges, {tone} tone.")
    
    return "\n".join(parts) if len(parts) > 1 else ""


# ─── High-Level: Process a Message ──────────────────────────────────────────

def process_message(
    chat_id: int,
    telegram_id: int,
    message: str,
    role: str = 'user',
    perception_id: Optional[str] = None,
    time_gap_seconds: Optional[float] = None,
) -> Dict:
    """
    Main entry point: Process an incoming message through the consciousness stream.
    
    Called by chat_mode.py for every message (user and assistant).
    
    Returns dict with:
        - point_id: The recorded subject point ID
        - segment_id: The segment this point belongs to
        - segment_action: What happened (append/reattach/new)
        - subject: The extracted subject data
    """
    # Get previous point for shift detection
    prev_point = get_last_subject_point(chat_id)
    
    # Extract subject
    subject = extract_subject_inline(message, prev_point, role=role)
    
    # Determine segment action
    action = detect_segment_action(chat_id, subject, time_gap_seconds)
    
    # Execute segment action
    segment_id = action.segment_id
    
    if action.action == 'new':
        segment_id = create_segment(chat_id, telegram_id, subject)
    elif action.action == 'reattach':
        reopen_segment(action.segment_id, subject)
        segment_id = action.segment_id
    elif action.action == 'append':
        update_segment(action.segment_id, subject)
        segment_id = action.segment_id
    
    # Record the subject point
    point_id = record_subject_point(
        chat_id=chat_id,
        telegram_id=telegram_id,
        subject=subject,
        segment_id=segment_id,
        perception_id=perception_id,
        previous_point_id=prev_point['id'] if prev_point else None,
    )
    
    return {
        'point_id': point_id,
        'segment_id': segment_id,
        'segment_action': action.action,
        'segment_reason': action.reason,
        'subject': asdict(subject),
    }


# ─── Background: Segment Lifecycle Management ───────────────────────────────

def close_stale_segments() -> int:
    """
    Background task: Soft-close segments with no activity for SOFT_CLOSE_MINUTES,
    hard-close segments with no activity for HARD_CLOSE_MINUTES.
    
    Returns number of segments closed.
    """
    conn = None
    closed = 0
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Soft-close stale open segments
        cur.execute("""
            UPDATE conversation_segments SET
                status = 'soft_closed',
                closed_at = now(),
                updated_at = now(),
                duration_seconds = EXTRACT(EPOCH FROM (now() - first_point_at))::int
            WHERE status = 'open'
              AND last_point_at < now() - interval '%s minutes'
            RETURNING id
        """, (SOFT_CLOSE_MINUTES,))
        soft_closed = cur.rowcount
        
        # Hard-close old soft-closed segments
        cur.execute("""
            UPDATE conversation_segments SET
                status = 'closed',
                updated_at = now()
            WHERE status = 'soft_closed'
              AND closed_at < now() - interval '%s minutes'
            RETURNING id
        """, (HARD_CLOSE_MINUTES,))
        hard_closed = cur.rowcount
        
        conn.commit()
        closed = soft_closed + hard_closed
        
        if closed > 0:
            logger.info(f"Segment lifecycle: {soft_closed} soft-closed, {hard_closed} hard-closed")
        
        return closed
    except Exception as e:
        logger.error(f"Failed to close stale segments: {e}")
        if conn:
            conn.rollback()
        return 0
    finally:
        if conn:
            conn.close()
