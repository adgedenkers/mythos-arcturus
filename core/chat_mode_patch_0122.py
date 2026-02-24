#!/usr/bin/env python3
"""
chat_mode_patch_0122.py — Consciousness Stream Integration
==========================================================
This file contains the functions to patch into chat_mode.py.
The install.sh script applies these changes via sed/patch.

Changes:
1. Import subject_tracker at the top
2. Hook process_message() into handle_chat_message() for both user and assistant messages
3. Queue async enrichment via Redis
4. Pass conversation_awareness into prompt assembly
"""

# === PATCH INSTRUCTIONS ===
# These are the exact code changes needed in chat_mode.py.
# The install.sh will apply them.

IMPORT_BLOCK = '''
# Consciousness Stream — subject tracking (Patch 0122)
try:
    from subject_tracker import process_message as track_subject, build_conversation_awareness
    _subject_tracking_available = True
except ImportError as e:
    logger.warning(f"Subject tracking not available: {e}")
    _subject_tracking_available = False
    def track_subject(*args, **kwargs): return {}
    def build_conversation_awareness(*args, **kwargs): return ""

# Redis for async enrichment queue
try:
    import redis
    _redis_client = redis.Redis.from_url("redis://localhost:6379")
except Exception:
    _redis_client = None
'''

# In handle_chat_message(), AFTER perception logging, BEFORE building messages:
USER_TRACKING_BLOCK = '''
        # ── Consciousness Stream: Track user message subject ──
        user_subject_result = {}
        if _subject_tracking_available:
            try:
                time_gap = None
                last_ts = _get_last_message_timestamp(get_chat_context(session))
                if last_ts and message_timestamp:
                    time_gap = (message_timestamp - last_ts).total_seconds()
                
                user_subject_result = track_subject(
                    chat_id=session.get('chat_id', 0),
                    telegram_id=user_info.get('telegram_id', 0),
                    message=user_message,
                    role='user',
                    perception_id=perception_id,
                    time_gap_seconds=time_gap,
                )
                logger.debug(f"Subject tracked: {user_subject_result.get('segment_action', '?')} "
                           f"segment={str(user_subject_result.get('segment_id', ''))[:8]}")
            except Exception as e:
                logger.warning(f"Subject tracking failed (non-fatal): {e}")
'''

# In handle_chat_message(), AFTER getting iris_response, BEFORE adding to context:
ASSISTANT_TRACKING_BLOCK = '''
        # ── Consciousness Stream: Track assistant response subject ──
        if _subject_tracking_available:
            try:
                track_subject(
                    chat_id=session.get('chat_id', 0),
                    telegram_id=0,  # Iris has no telegram_id
                    message=iris_response,
                    role='assistant',
                    perception_id=response_perception_id,
                )
            except Exception as e:
                logger.warning(f"Assistant subject tracking failed (non-fatal): {e}")
        
        # ── Queue async enrichment ──
        if _redis_client and user_subject_result.get('point_id'):
            try:
                import json as _json
                _redis_client.xadd('mythos:assignments:subject', {
                    'data': _json.dumps({
                        'point_id': user_subject_result['point_id'],
                        'message_text': user_message[:500],
                        'chat_id': session.get('chat_id', 0),
                        'role': 'user',
                    })
                })
            except Exception:
                pass  # Non-fatal
'''
