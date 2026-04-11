"""
youtube_channel_monitor.py — MNE stream worker
Polls subscribed YouTube channels via RSS and enqueues new videos.

MNE-0009: Before calling enqueue_video(), check mythos:youtube:failed.
  - If the video is in backoff (cooldown window active) → skip silently.
  - If permanently failed (>= MAX_ATTEMPTS) → skip silently.
  - This prevents the re-detect spam when transcripts are failing.
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Optional

import redis
import feedparser

logger = logging.getLogger(__name__)

# Redis keys
QUEUE_KEY   = 'mythos:youtube:queue'
META_PREFIX = 'mythos:youtube:queue:meta:'
FAILED_KEY  = 'mythos:youtube:failed'

# Must match the constant in youtube_queue_consumer.py
MAX_ATTEMPTS = 3

RSS_TEMPLATE = 'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'


# ---------------------------------------------------------------------------
# Backoff check (mirrors consumer logic — no import cross-dependency)
# ---------------------------------------------------------------------------

def _is_backoff_active(r: redis.Redis, video_id: str) -> bool:
    """
    Return True if this video_id should not be enqueued right now.
    Reads from mythos:youtube:failed hash.
    """
    raw = r.hget(FAILED_KEY, video_id)
    if raw is None:
        return False
    try:
        info = json.loads(raw)
    except Exception:
        return False

    if info.get('attempt_count', 0) >= MAX_ATTEMPTS:
        return True
    if time.time() < info.get('retry_after', 0):
        return True
    return False


# ---------------------------------------------------------------------------
# Already-processed check
# ---------------------------------------------------------------------------

def _is_already_processed(video_id: str) -> bool:
    """Return True if video_id exists in youtube_videos table."""
    import psycopg2
    import os

    dsn = os.environ.get('MYTHOS_DB_URL', 'dbname=mythos user=adge host=localhost')
    try:
        conn = psycopg2.connect(dsn)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT 1 FROM youtube_videos WHERE video_id = %s LIMIT 1',
                    (video_id,),
                )
                return cur.fetchone() is not None
        finally:
            conn.close()
    except Exception as exc:
        logger.warning('DB check failed for %s: %s', video_id, exc)
        return False


# ---------------------------------------------------------------------------
# Enqueue
# ---------------------------------------------------------------------------

def enqueue_video(
    r: redis.Redis,
    video_id: str,
    channel_id: str,
    title: str,
    description: str = '',
    published_at: Optional[str] = None,
    priority: int = 5,
) -> bool:
    """
    Add video to the processing queue.

    Returns True if enqueued, False if skipped (backoff, already processed,
    or already in queue).

    MNE-0009: Checks backoff BEFORE enqueuing to prevent re-detect spam.
    """
    # --- Backoff gate (MNE-0009) ---
    if _is_backoff_active(r, video_id):
        logger.debug('enqueue_video: skipping %s (backoff active)', video_id)
        return False

    # --- Already processed in DB ---
    if _is_already_processed(video_id):
        logger.debug('enqueue_video: skipping %s (already in DB)', video_id)
        return False

    # --- Already in queue ---
    if r.zscore(QUEUE_KEY, video_id) is not None:
        logger.debug('enqueue_video: skipping %s (already queued)', video_id)
        return False

    # --- Enqueue ---
    score = priority * 1_000_000_000 + int(time.time())
    meta = {
        'channel_id':   channel_id,
        'title':        title,
        'description':  description,
        'published_at': published_at or '',
        'queued_at':    datetime.now(tz=timezone.utc).isoformat(),
    }
    meta_key = META_PREFIX + video_id

    pipe = r.pipeline()
    pipe.zadd(QUEUE_KEY, {video_id: score})
    pipe.hset(meta_key, mapping=meta)
    pipe.execute()

    logger.info('enqueued video %s (priority=%d score=%d)', video_id, priority, score)
    return True


# ---------------------------------------------------------------------------
# RSS polling
# ---------------------------------------------------------------------------

def _load_subscribed_channels(r: redis.Redis) -> list[dict]:
    """
    Load channel list from Redis key mythos:youtube:channels.
    Each entry: {channel_id, name, priority}
    Falls back to empty list if key missing.
    """
    raw = r.get('mythos:youtube:channels')
    if not raw:
        return []
    try:
        return json.loads(raw)
    except Exception:
        return []


def poll_channel(r: redis.Redis, channel: dict) -> int:
    """
    Fetch RSS feed for one channel and enqueue new videos.
    Returns count of newly enqueued videos.
    """
    channel_id = channel.get('channel_id', '')
    priority   = int(channel.get('priority', 5))
    url        = RSS_TEMPLATE.format(channel_id=channel_id)

    try:
        feed = feedparser.parse(url)
    except Exception as exc:
        logger.warning('RSS parse failed for channel %s: %s', channel_id, exc)
        return 0

    enqueued = 0
    for entry in feed.entries:
        # feedparser exposes yt:videoid as yt_videoid
        video_id = getattr(entry, 'yt_videoid', None)
        if not video_id:
            # Fallback: parse from entry.id / entry.link
            link = getattr(entry, 'link', '')
            if 'v=' in link:
                video_id = link.split('v=')[-1].split('&')[0]
            elif '/shorts/' in link:
                video_id = link.split('/shorts/')[-1].split('?')[0]
        if not video_id:
            continue

        title       = getattr(entry, 'title', '')
        description = getattr(entry, 'summary', '')
        published   = getattr(entry, 'published', None)

        queued = enqueue_video(
            r=r,
            video_id=video_id,
            channel_id=channel_id,
            title=title,
            description=description,
            published_at=published,
            priority=priority,
        )
        if queued:
            enqueued += 1

    return enqueued


# ---------------------------------------------------------------------------
# Monitor loop
# ---------------------------------------------------------------------------

def run_monitor(
    redis_url: str = 'redis://localhost:6379/0',
    poll_interval: float = 7_200.0,   # 2 hours
) -> None:
    """Main monitor loop — polls all subscribed channels on a schedule."""
    r = redis.from_url(redis_url, decode_responses=False)
    logger.info('YouTube channel monitor started (interval=%ds)', int(poll_interval))

    while True:
        try:
            channels = _load_subscribed_channels(r)
            if not channels:
                logger.debug('No subscribed channels found in mythos:youtube:channels')
            else:
                total = 0
                for ch in channels:
                    count = poll_channel(r, ch)
                    total += count
                if total:
                    logger.info('monitor cycle: enqueued %d new video(s)', total)
                else:
                    logger.debug('monitor cycle: no new videos')

        except Exception as exc:
            logger.exception('monitor loop error: %s', exc)

        time.sleep(poll_interval)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_monitor()
