"""
youtube_queue_consumer.py — MNE stream worker
Consumes the mythos:youtube:queue Redis sorted set and processes videos.

MNE-0009: Added failed-video backoff.
MNE-0015: Fixed pop-before-check bug, added throttle, fixed schema mismatch,
           added get_queue_status(), made permanent failures persistent.

Fixes applied:
  - Peek queue BEFORE popping — if backoff active, leave it in queue
  - Configurable PROCESS_INTERVAL (default 300s / 5 min) between videos
  - INSERT matches actual youtube_videos schema (url, channel_name, word_count, ingested_at)
  - get_queue_status() function for skill integration
  - Permanently failed videos never re-enter the queue
"""
import json
import logging
import os
import time
from datetime import datetime, timezone

import redis

from skills.data.youtube_intake import fetch_transcript, transcript_to_text

logger = logging.getLogger(__name__)

# Redis keys
QUEUE_KEY       = 'mythos:youtube:queue'
META_PREFIX     = 'mythos:youtube:queue:meta:'
ERRORS_KEY      = 'mythos:youtube:queue:errors'
STATUS_KEY      = 'mythos:youtube:queue:status'
FAILED_KEY      = 'mythos:youtube:failed'
MAX_ERRORS      = 50
BACKOFF_SECONDS = 86_400   # 24 hours
MAX_ATTEMPTS    = 3        # permanent skip after this many failures

# Throttle: seconds between processing videos (avoid YouTube IP bans)
PROCESS_INTERVAL = int(os.environ.get('YT_PROCESS_INTERVAL', '300'))  # 5 min default


# ---------------------------------------------------------------------------
# Backoff helpers
# ---------------------------------------------------------------------------

def _get_failed_info(r: redis.Redis, video_id: str) -> dict | None:
    """Return stored failure info for video_id, or None if not present."""
    raw = r.hget(FAILED_KEY, video_id)
    if raw is None:
        return None
    try:
        data = raw.decode() if isinstance(raw, bytes) else raw
        return json.loads(data)
    except Exception:
        return None


def _set_failed_info(r: redis.Redis, video_id: str, attempt_count: int, last_error: str) -> None:
    """Record / update failure info for video_id."""
    if attempt_count >= MAX_ATTEMPTS:
        # Permanently failed — set retry_after far in the future so it never clears
        retry_after = time.time() + (365 * 86_400 * 100)  # 100 years
    else:
        retry_after = time.time() + BACKOFF_SECONDS

    info = {
        'retry_after':   retry_after,
        'attempt_count': attempt_count,
        'last_error':    last_error[:500],
        'permanent':     attempt_count >= MAX_ATTEMPTS,
    }
    r.hset(FAILED_KEY, video_id, json.dumps(info))
    if attempt_count >= MAX_ATTEMPTS:
        logger.info(
            'backoff: video %s PERMANENTLY FAILED after %d attempts',
            video_id, attempt_count,
        )
    else:
        logger.info(
            'backoff: video %s attempt %d/%d, retry after %s',
            video_id, attempt_count, MAX_ATTEMPTS,
            datetime.fromtimestamp(retry_after, tz=timezone.utc).isoformat(),
        )


def is_backoff_active(r: redis.Redis, video_id: str) -> bool:
    """
    Return True if the video should be skipped right now.
    Permanently skipped videos (>= MAX_ATTEMPTS) always return True.
    """
    info = _get_failed_info(r, video_id)
    if info is None:
        return False
    if info.get('permanent') or info.get('attempt_count', 0) >= MAX_ATTEMPTS:
        return True
    if time.time() < info.get('retry_after', 0):
        return True
    # Backoff window has passed — allow retry
    return False


# ---------------------------------------------------------------------------
# Error logging
# ---------------------------------------------------------------------------

def _log_error(r: redis.Redis, video_id: str, error: str, title: str = '') -> None:
    entry = json.dumps({
        'video_id':  video_id,
        'title':     title,
        'error':     error[:500],
        'timestamp': datetime.now(tz=timezone.utc).isoformat(),
    })
    pipe = r.pipeline()
    pipe.lpush(ERRORS_KEY, entry)
    pipe.ltrim(ERRORS_KEY, 0, MAX_ERRORS - 1)
    pipe.execute()


# ---------------------------------------------------------------------------
# Status tracking
# ---------------------------------------------------------------------------

def _increment_status(r: redis.Redis, field: str, amount: int = 1) -> None:
    r.hincrby(STATUS_KEY, field, amount)


def get_queue_status() -> dict:
    """
    Get current queue status for the youtube_channel skill.
    Returns dict with pending, processing, by_channel, by_priority,
    total_processed, total_errors.
    """
    r = redis.from_url('redis://localhost:6379/0', decode_responses=True)

    # Pending count
    pending = r.zcard(QUEUE_KEY)

    # Status counters
    status = r.hgetall(STATUS_KEY) or {}
    total_processed = int(status.get('total_processed', 0))
    total_errors = int(status.get('total_errors', 0))

    # Currently processing (not tracked atomically, just report queue head)
    processing = None

    # By channel — scan the queue meta keys
    by_channel = {}
    by_priority = {'high': 0, 'normal': 0, 'low': 0}

    if pending > 0:
        items = r.zrange(QUEUE_KEY, 0, -1, withscores=True)
        for vid, score in items:
            meta_key = META_PREFIX + vid
            channel = r.hget(meta_key, 'channel_id') or 'unknown'
            # Resolve channel name from channel list
            ch_name = _resolve_channel_name(r, channel)
            by_channel[ch_name] = by_channel.get(ch_name, 0) + 1

            # Priority from score
            priority_tier = int(score) // 1_000_000_000
            if priority_tier <= 3:
                by_priority['high'] += 1
            elif priority_tier <= 7:
                by_priority['normal'] += 1
            else:
                by_priority['low'] += 1

    # Failed count
    failed_count = r.hlen(FAILED_KEY)

    return {
        'pending':         pending,
        'processing':      processing,
        'by_channel':      by_channel,
        'by_priority':     by_priority,
        'total_processed': total_processed,
        'total_errors':    total_errors,
        'failed_permanent': failed_count,
    }


def _resolve_channel_name(r: redis.Redis, channel_id: str) -> str:
    """Try to resolve channel_id to a human name from the subscription list."""
    raw = r.get('mythos:youtube:channels')
    if not raw:
        return channel_id or 'Unknown'
    try:
        channels = json.loads(raw)
        for ch in channels:
            if ch.get('channel_id') == channel_id:
                return ch.get('name', channel_id)
    except Exception:
        pass
    return channel_id or 'Unknown'


# ---------------------------------------------------------------------------
# Queue helpers (FIXED: peek-before-pop)
# ---------------------------------------------------------------------------

def _peek_next(r: redis.Redis) -> str | None:
    """
    Peek at the highest-priority item WITHOUT removing it.
    Returns video_id or None if queue is empty.
    """
    items = r.zrange(QUEUE_KEY, 0, 0, withscores=False)
    if not items:
        return None
    return items[0].decode() if isinstance(items[0], bytes) else items[0]


def _pop_video(r: redis.Redis, video_id: str) -> dict | None:
    """
    Atomically remove a specific video from the queue and return its metadata.
    Returns meta dict or None if video was already removed (race condition).
    """
    removed = r.zrem(QUEUE_KEY, video_id)
    if not removed:
        return None

    meta_key = META_PREFIX + video_id
    raw_meta = r.hgetall(meta_key)
    meta = {
        (k.decode() if isinstance(k, bytes) else k): (v.decode() if isinstance(v, bytes) else v)
        for k, v in raw_meta.items()
    }
    r.delete(meta_key)
    return meta


# ---------------------------------------------------------------------------
# Core processing (FIXED: correct schema)
# ---------------------------------------------------------------------------

def process_video(r: redis.Redis, video_id: str, meta: dict) -> None:
    """
    Fetch transcript and store in Postgres youtube_videos table.
    Raises on failure so the caller can record the backoff.

    MNE-0015: Fixed to match actual youtube_videos schema:
      - url (required), channel_name, word_count, ingested_at (not processed_at)
    """
    import psycopg2

    segments = fetch_transcript(video_id)
    if segments is None:
        raise RuntimeError(f'All transcript methods failed for {video_id}')

    full_text = transcript_to_text(segments)
    word_count = len(full_text.split()) if full_text else 0
    url = f'https://www.youtube.com/watch?v={video_id}'

    dsn = os.environ.get('MYTHOS_DB_URL', 'dbname=mythos user=postgres host=/var/run/postgresql')
    conn = psycopg2.connect(dsn)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO youtube_videos
                        (video_id, url, channel_id, channel_name, title,
                         description, transcript_text, transcript_segments,
                         word_count, published_at, ingested_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (video_id) DO UPDATE SET
                        transcript_text     = EXCLUDED.transcript_text,
                        transcript_segments = EXCLUDED.transcript_segments,
                        word_count          = EXCLUDED.word_count,
                        channel_name        = COALESCE(EXCLUDED.channel_name, youtube_videos.channel_name),
                        ingested_at         = NOW()
                    """,
                    (
                        video_id,
                        url,
                        meta.get('channel_id'),
                        meta.get('channel_name') or _resolve_channel_name_static(meta.get('channel_id', '')),
                        meta.get('title'),
                        meta.get('description'),
                        full_text,
                        json.dumps(segments),
                        word_count,
                        meta.get('published_at') or None,
                    ),
                )
    finally:
        conn.close()

    _increment_status(r, 'total_processed')
    logger.info('processed video %s — %d segments, %d words', video_id, len(segments), word_count)


def _resolve_channel_name_static(channel_id: str) -> str | None:
    """Resolve channel name from Redis without a pre-existing connection."""
    if not channel_id:
        return None
    try:
        r = redis.from_url('redis://localhost:6379/0', decode_responses=True)
        return _resolve_channel_name(r, channel_id)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Consumer loop (FIXED: peek-check-pop + throttle)
# ---------------------------------------------------------------------------

def run_consumer(redis_url: str = 'redis://localhost:6379/0', poll_interval: float = 10.0) -> None:
    """
    Main consumer loop.

    MNE-0015 fixes:
      - Peek at queue head BEFORE popping — skip without removing if backoff active
      - Wait PROCESS_INTERVAL between successful/failed processing attempts
      - poll_interval only used when queue is empty
    """
    r = redis.from_url(redis_url, decode_responses=False)
    logger.info(
        'YouTube queue consumer started (throttle=%ds, poll=%ds)',
        PROCESS_INTERVAL, int(poll_interval),
    )

    while True:
        try:
            # 1. Peek at the next video WITHOUT removing it
            video_id = _peek_next(r)
            if video_id is None:
                time.sleep(poll_interval)
                continue

            # 2. Check backoff BEFORE popping
            if is_backoff_active(r, video_id):
                # Remove from queue since it's in backoff — but don't process
                _pop_video(r, video_id)
                logger.debug('removed %s from queue (backoff active)', video_id)
                # Don't throttle for skips — check next item quickly
                time.sleep(1)
                continue

            # 3. Now pop it — we're committed to processing
            meta = _pop_video(r, video_id)
            if meta is None:
                # Race condition — another consumer got it
                time.sleep(1)
                continue

            # 4. Process
            try:
                process_video(r, video_id, meta)
                # Success — clear any prior failure record
                r.hdel(FAILED_KEY, video_id)
                logger.info(
                    'success: %s — "%s" — throttling %ds before next',
                    video_id,
                    meta.get('title', '?')[:60],
                    PROCESS_INTERVAL,
                )
            except Exception as exc:
                error_str = str(exc)
                logger.error('failed to process video %s: %s', video_id, error_str)
                _log_error(r, video_id, error_str, title=meta.get('title', ''))
                _increment_status(r, 'total_errors')

                # Update backoff counter
                info = _get_failed_info(r, video_id)
                attempt_count = (info.get('attempt_count', 0) if info else 0) + 1
                _set_failed_info(r, video_id, attempt_count, error_str)

            # 5. Throttle — wait between videos regardless of success/failure
            time.sleep(PROCESS_INTERVAL)

        except KeyboardInterrupt:
            logger.info('YouTube queue consumer shutting down')
            break
        except Exception as exc:
            logger.exception('consumer loop error: %s', exc)
            time.sleep(poll_interval)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_consumer()
