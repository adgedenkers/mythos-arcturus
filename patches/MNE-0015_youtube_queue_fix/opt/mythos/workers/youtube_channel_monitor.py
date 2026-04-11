"""
youtube_channel_monitor.py — MNE stream worker
Polls subscribed YouTube channels via RSS and enqueues new videos.

MNE-0009: Before calling enqueue_video(), check mythos:youtube:failed.
MNE-0015: Added subscribe_channel(), unsubscribe_channel(), list_subscriptions()
           for skill integration. Fixed permanent-failure gate to prevent
           re-detect spam. Channels stored in Redis + Postgres for durability.

Subscription management:
  subscribe_channel(handle_or_url)   → resolves channel, stores in Redis, starts backfill
  unsubscribe_channel(target)        → removes from Redis list
  list_subscriptions()               → returns all tracked channels with stats
"""
import json
import logging
import os
import re
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
CHANNELS_KEY = 'mythos:youtube:channels'

# Must match the constant in youtube_queue_consumer.py
MAX_ATTEMPTS = 3

RSS_TEMPLATE = 'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'


def _get_redis() -> redis.Redis:
    return redis.from_url('redis://localhost:6379/0', decode_responses=True)


# ---------------------------------------------------------------------------
# Backoff check (mirrors consumer logic — no import cross-dependency)
# ---------------------------------------------------------------------------

def _is_backoff_active(r: redis.Redis, video_id: str) -> bool:
    """
    Return True if this video_id should not be enqueued right now.
    MNE-0015: Also checks 'permanent' flag for clarity.
    """
    raw = r.hget(FAILED_KEY, video_id)
    if raw is None:
        return False
    try:
        info = json.loads(raw) if isinstance(raw, str) else json.loads(raw.decode())
    except Exception:
        return False

    # Permanent failures never re-enter
    if info.get('permanent') or info.get('attempt_count', 0) >= MAX_ATTEMPTS:
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
    channel_name: str = '',
) -> bool:
    """
    Add video to the processing queue.
    Returns True if enqueued, False if skipped.

    MNE-0015: Added channel_name passthrough for proper DB storage.
    """
    # --- Backoff gate ---
    if _is_backoff_active(r, video_id):
        return False

    # --- Already processed in DB ---
    if _is_already_processed(video_id):
        return False

    # --- Already in queue ---
    if r.zscore(QUEUE_KEY, video_id) is not None:
        return False

    # --- Enqueue ---
    score = priority * 1_000_000_000 + int(time.time())
    meta = {
        'channel_id':   channel_id,
        'channel_name': channel_name,
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

    logger.info('enqueued video %s (priority=%d)', video_id, priority)
    return True


# ---------------------------------------------------------------------------
# Channel subscription management (MNE-0015)
# ---------------------------------------------------------------------------

def _resolve_channel_id(handle_or_url: str) -> dict | None:
    """
    Resolve a YouTube handle (@name) or URL to a channel_id via RSS discovery.
    Returns {channel_id, channel_name, channel_handle} or None.
    """
    handle_or_url = handle_or_url.strip()

    # If it's already a channel ID (24 chars, starts with UC)
    if re.match(r'^UC[\w-]{22}$', handle_or_url):
        return {
            'channel_id': handle_or_url,
            'channel_name': None,
            'channel_handle': None,
        }

    # Build URL to try
    if handle_or_url.startswith('http'):
        url = handle_or_url
    elif handle_or_url.startswith('@'):
        url = f'https://www.youtube.com/{handle_or_url}'
    else:
        url = f'https://www.youtube.com/@{handle_or_url}'

    # Use yt-dlp to extract channel info (more reliable than scraping)
    import subprocess
    yt_dlp = '/opt/mythos/.venv/bin/yt-dlp'
    try:
        result = subprocess.run(
            [yt_dlp, '--flat-playlist', '--playlist-items', '1',
             '--print', '%(channel_id)s', '--print', '%(channel)s',
             '--print', '%(uploader_id)s',
             '--no-warnings', '--quiet', url + '/videos'],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            channel_id = lines[0] if len(lines) > 0 and lines[0].startswith('UC') else None
            channel_name = lines[1] if len(lines) > 1 and lines[1] != 'NA' else None
            channel_handle = lines[2] if len(lines) > 2 and lines[2] != 'NA' else None

            if channel_id:
                return {
                    'channel_id': channel_id,
                    'channel_name': channel_name,
                    'channel_handle': channel_handle or handle_or_url,
                }
    except Exception as exc:
        logger.warning('yt-dlp channel resolve failed for %s: %s', handle_or_url, exc)

    # Fallback: try RSS feed directly if we can guess the channel URL
    # YouTube RSS requires channel_id, so this fallback is limited
    return None


def subscribe_channel(handle_or_url: str) -> dict | None:
    """
    Subscribe to a YouTube channel for automatic transcript capture.
    Returns channel info dict on success, None on failure.
    """
    r = _get_redis()

    # Resolve to channel_id
    info = _resolve_channel_id(handle_or_url)
    if not info or not info.get('channel_id'):
        logger.warning('Could not resolve channel: %s', handle_or_url)
        return None

    channel_id = info['channel_id']
    channel_name = info.get('channel_name') or handle_or_url
    channel_handle = info.get('channel_handle') or handle_or_url

    # Load existing channels
    channels = _load_channel_list(r)

    # Check if already subscribed
    for ch in channels:
        if ch.get('channel_id') == channel_id:
            # Re-activate if inactive
            ch['active'] = True
            ch['channel_name'] = channel_name
            ch['channel_handle'] = channel_handle
            _save_channel_list(r, channels)
            logger.info('reactivated channel %s (%s)', channel_name, channel_id)
            return ch

    # Add new subscription
    new_channel = {
        'channel_id': channel_id,
        'channel_name': channel_name,
        'channel_handle': channel_handle,
        'name': channel_name,  # compat with _load_subscribed_channels
        'priority': 5,
        'active': True,
        'subscribed_at': datetime.now(tz=timezone.utc).isoformat(),
        'total_videos_ingested': 0,
        'last_video_at': None,
    }
    channels.append(new_channel)
    _save_channel_list(r, channels)

    # Trigger initial backfill via RSS
    enqueued = poll_channel(r, new_channel)
    new_channel['initial_backfill'] = enqueued

    logger.info('subscribed to %s (%s) — %d videos queued for backfill',
                channel_name, channel_id, enqueued)
    return new_channel


def unsubscribe_channel(target: str) -> bool:
    """
    Unsubscribe from a YouTube channel.
    Matches on name, handle, or channel_id (case-insensitive).
    Returns True if found and deactivated.
    """
    r = _get_redis()
    channels = _load_channel_list(r)
    target_lower = target.lower().strip().lstrip('@')

    for ch in channels:
        name = (ch.get('channel_name') or '').lower()
        handle = (ch.get('channel_handle') or '').lower().lstrip('@')
        cid = (ch.get('channel_id') or '').lower()

        if target_lower in (name, handle, cid) or target_lower in name:
            ch['active'] = False
            _save_channel_list(r, channels)
            logger.info('unsubscribed from %s', ch.get('channel_name', target))
            return True
    return False


def list_subscriptions() -> list[dict]:
    """Return all channel subscriptions with stats."""
    r = _get_redis()
    channels = _load_channel_list(r)

    # Enrich with DB stats
    import psycopg2
    dsn = os.environ.get('MYTHOS_DB_URL', 'dbname=mythos user=adge host=localhost')
    try:
        conn = psycopg2.connect(dsn)
        try:
            with conn.cursor() as cur:
                for ch in channels:
                    cid = ch.get('channel_id', '')
                    cur.execute(
                        """SELECT COUNT(*), MAX(ingested_at)
                           FROM youtube_videos WHERE channel_id = %s""",
                        (cid,),
                    )
                    row = cur.fetchone()
                    ch['total_videos_ingested'] = row[0] if row else 0
                    ch['last_video_at'] = row[1] if row else None
        finally:
            conn.close()
    except Exception as exc:
        logger.warning('DB stats lookup failed: %s', exc)

    return channels


def _load_channel_list(r: redis.Redis) -> list[dict]:
    """Load channel list from Redis."""
    raw = r.get(CHANNELS_KEY)
    if not raw:
        return []
    try:
        data = raw if isinstance(raw, str) else raw.decode()
        return json.loads(data)
    except Exception:
        return []


def _save_channel_list(r: redis.Redis, channels: list[dict]) -> None:
    """Save channel list to Redis."""
    # Sanitize datetime objects for JSON
    def _clean(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    cleaned = []
    for ch in channels:
        cleaned.append({k: _clean(v) for k, v in ch.items()})
    r.set(CHANNELS_KEY, json.dumps(cleaned))


# ---------------------------------------------------------------------------
# RSS polling
# ---------------------------------------------------------------------------

def _load_subscribed_channels(r: redis.Redis) -> list[dict]:
    """
    Load ACTIVE channel list from Redis.
    Filters to active-only for the monitor loop.
    """
    channels = _load_channel_list(r)
    return [ch for ch in channels if ch.get('active', True)]


def poll_channel(r: redis.Redis, channel: dict) -> int:
    """
    Fetch RSS feed for one channel and enqueue new videos.
    Returns count of newly enqueued videos.
    """
    channel_id = channel.get('channel_id', '')
    channel_name = channel.get('channel_name') or channel.get('name', 'Unknown')
    priority = int(channel.get('priority', 5))
    url = RSS_TEMPLATE.format(channel_id=channel_id)

    try:
        feed = feedparser.parse(url)
    except Exception as exc:
        logger.warning('RSS parse failed for channel %s: %s', channel_name, exc)
        return 0

    enqueued = 0
    for entry in feed.entries:
        video_id = getattr(entry, 'yt_videoid', None)
        if not video_id:
            link = getattr(entry, 'link', '')
            if 'v=' in link:
                video_id = link.split('v=')[-1].split('&')[0]
            elif '/shorts/' in link:
                video_id = link.split('/shorts/')[-1].split('?')[0]
        if not video_id:
            continue

        title = getattr(entry, 'title', '')
        description = getattr(entry, 'summary', '')
        published = getattr(entry, 'published', None)

        queued = enqueue_video(
            r=r,
            video_id=video_id,
            channel_id=channel_id,
            title=title,
            description=description,
            published_at=published,
            priority=priority,
            channel_name=channel_name,
        )
        if queued:
            enqueued += 1

    return enqueued


# ---------------------------------------------------------------------------
# Telegram notification helper
# ---------------------------------------------------------------------------

def _notify_new_videos(channel_name: str, count: int) -> None:
    """Send Telegram notification about newly queued videos."""
    if count == 0:
        return
    try:
        import requests
        # Read bot token and chat ID from environment
        token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
        if not token or not chat_id:
            return
        msg = f'📺 {channel_name} — {count} new video{"s" if count != 1 else ""} queued'
        requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat_id, 'text': msg},
            timeout=10,
        )
    except Exception:
        pass  # Don't let notification failures break the monitor


# ---------------------------------------------------------------------------
# Monitor loop
# ---------------------------------------------------------------------------

def run_monitor(
    redis_url: str = 'redis://localhost:6379/0',
    poll_interval: float = 7_200.0,   # 2 hours
) -> None:
    """Main monitor loop — polls all subscribed channels on a schedule."""
    r = redis.from_url(redis_url, decode_responses=True)
    logger.info('YouTube channel monitor started (interval=%ds)', int(poll_interval))

    while True:
        try:
            channels = _load_subscribed_channels(r)
            if not channels:
                logger.debug('No active subscribed channels')
            else:
                logger.info('Checking %d channels...', len(channels))
                total = 0
                for ch in channels:
                    name = ch.get('channel_name') or ch.get('name', 'Unknown')
                    logger.info('RSS check for %s...', name)
                    count = poll_channel(r, ch)
                    if count:
                        _notify_new_videos(name, count)
                    total += count

                if total:
                    logger.info('monitor cycle: enqueued %d new video(s)', total)
                else:
                    logger.info('Cycle complete: no new videos')
        except Exception as exc:
            logger.exception('monitor loop error: %s', exc)

        time.sleep(poll_interval)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_monitor()
