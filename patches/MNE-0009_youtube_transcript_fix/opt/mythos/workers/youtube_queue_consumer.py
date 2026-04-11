"""
youtube_queue_consumer.py — MNE stream worker
Consumes the mythos:youtube:queue Redis sorted set and processes videos.

MNE-0009: Added failed-video backoff.
  - On failure, writes to Redis hash mythos:youtube:failed:
      key   = video_id
      value = JSON {retry_after, attempt_count, last_error}
  - 24-hour backoff per attempt; permanently skipped after 3 failures.
"""

import json
import logging
import time
from datetime import datetime, timezone

import redis

from skills.data.youtube_intake import fetch_transcript, transcript_to_text

logger = logging.getLogger(__name__)

# Redis keys
QUEUE_KEY       = 'mythos:youtube:queue'
META_PREFIX     = 'mythos:youtube:queue:meta:'
ERRORS_KEY      = 'mythos:youtube:queue:errors'
FAILED_KEY      = 'mythos:youtube:failed'

MAX_ERRORS      = 50
BACKOFF_SECONDS = 86_400   # 24 hours
MAX_ATTEMPTS    = 3        # permanent skip after this many failures


# ---------------------------------------------------------------------------
# Backoff helpers
# ---------------------------------------------------------------------------

def _get_failed_info(r: redis.Redis, video_id: str) -> dict | None:
    """Return stored failure info for video_id, or None if not present."""
    raw = r.hget(FAILED_KEY, video_id)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


def _set_failed_info(r: redis.Redis, video_id: str, attempt_count: int, last_error: str) -> None:
    """Record / update failure info for video_id."""
    retry_after = time.time() + BACKOFF_SECONDS
    info = {
        'retry_after':   retry_after,
        'attempt_count': attempt_count,
        'last_error':    last_error[:500],
    }
    r.hset(FAILED_KEY, video_id, json.dumps(info))
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
    if info.get('attempt_count', 0) >= MAX_ATTEMPTS:
        logger.debug('backoff: video %s permanently skipped', video_id)
        return True
    if time.time() < info.get('retry_after', 0):
        logger.debug('backoff: video %s still in cooldown', video_id)
        return True
    # Backoff window has passed — allow retry
    return False


# ---------------------------------------------------------------------------
# Error logging
# ---------------------------------------------------------------------------

def _log_error(r: redis.Redis, video_id: str, error: str) -> None:
    entry = json.dumps({
        'video_id':  video_id,
        'error':     error,
        'timestamp': datetime.now(tz=timezone.utc).isoformat(),
    })
    pipe = r.pipeline()
    pipe.lpush(ERRORS_KEY, entry)
    pipe.ltrim(ERRORS_KEY, 0, MAX_ERRORS - 1)
    pipe.execute()


# ---------------------------------------------------------------------------
# Queue helpers
# ---------------------------------------------------------------------------

def _pop_next(r: redis.Redis) -> tuple[str | None, dict | None]:
    """
    Pop the highest-priority item from the queue.
    Returns (video_id, meta) or (None, None) if queue is empty.
    """
    items = r.zrange(QUEUE_KEY, 0, 0, withscores=False)
    if not items:
        return None, None

    video_id = items[0].decode() if isinstance(items[0], bytes) else items[0]

    # Atomic remove
    removed = r.zrem(QUEUE_KEY, video_id)
    if not removed:
        return None, None  # Race condition — another consumer got it

    meta_key = META_PREFIX + video_id
    raw_meta = r.hgetall(meta_key)
    meta = {
        (k.decode() if isinstance(k, bytes) else k): (v.decode() if isinstance(v, bytes) else v)
        for k, v in raw_meta.items()
    }
    r.delete(meta_key)
    return video_id, meta


# ---------------------------------------------------------------------------
# Core processing
# ---------------------------------------------------------------------------

def process_video(r: redis.Redis, video_id: str, meta: dict) -> None:
    """
    Fetch transcript and store in Postgres youtube_videos table.
    Raises on failure so the caller can record the backoff.
    """
    import psycopg2
    import os

    segments = fetch_transcript(video_id)
    if segments is None:
        raise RuntimeError(f'All transcript methods failed for {video_id}')

    full_text = transcript_to_text(segments)

    dsn = os.environ.get('MYTHOS_DB_URL', 'dbname=mythos user=adge host=localhost')
    conn = psycopg2.connect(dsn)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO youtube_videos
                        (video_id, channel_id, title, description, transcript_text,
                         transcript_segments, published_at, processed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (video_id) DO UPDATE SET
                        transcript_text     = EXCLUDED.transcript_text,
                        transcript_segments = EXCLUDED.transcript_segments,
                        processed_at        = NOW()
                    """,
                    (
                        video_id,
                        meta.get('channel_id'),
                        meta.get('title'),
                        meta.get('description'),
                        full_text,
                        json.dumps(segments),
                        meta.get('published_at'),
                    ),
                )
    finally:
        conn.close()

    logger.info('processed video %s (%d segments)', video_id, len(segments))


# ---------------------------------------------------------------------------
# Consumer loop
# ---------------------------------------------------------------------------

def run_consumer(redis_url: str = 'redis://localhost:6379/0', poll_interval: float = 5.0) -> None:
    """Main consumer loop — call this from the service entry point."""
    r = redis.from_url(redis_url, decode_responses=False)
    logger.info('YouTube queue consumer started')

    while True:
        try:
            video_id, meta = _pop_next(r)

            if video_id is None:
                time.sleep(poll_interval)
                continue

            # Check backoff before processing
            if is_backoff_active(r, video_id):
                logger.info('skipping %s (backoff active)', video_id)
                continue

            try:
                process_video(r, video_id, meta or {})
                # Success — clear any prior failure record
                r.hdel(FAILED_KEY, video_id)

            except Exception as exc:
                error_str = str(exc)
                logger.error('failed to process video %s: %s', video_id, error_str)
                _log_error(r, video_id, error_str)

                # Update backoff counter
                info = _get_failed_info(r, video_id)
                attempt_count = (info.get('attempt_count', 0) if info else 0) + 1
                _set_failed_info(r, video_id, attempt_count, error_str)

        except KeyboardInterrupt:
            logger.info('YouTube queue consumer shutting down')
            break
        except Exception as exc:
            logger.exception('consumer loop error: %s', exc)
            time.sleep(poll_interval)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_consumer()
