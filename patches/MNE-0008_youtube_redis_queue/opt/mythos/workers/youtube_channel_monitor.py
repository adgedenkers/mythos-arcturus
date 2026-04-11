#!/usr/bin/env python3
"""
YouTube Channel Monitor Worker (v2 — Queue-based)
===================================================
Polls subscribed YouTube channels and queues new videos for ingestion.

v2 changes (MNE-0008):
- New videos go to Redis queue instead of direct ingestion
- Full channel backfill via yt-dlp on first subscribe (all videos, LOW priority)
- RSS polling for ongoing new video detection (NORMAL priority)

Stream: MNE (memory intake)
"""

import os
import sys
import time
import logging
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

sys.path.insert(0, '/opt/mythos/workers')

logger = logging.getLogger('mythos.youtube_monitor')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

YT_NS = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'atom': 'http://www.w3.org/2005/Atom'}

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_NOTIFY_ID = os.getenv('TELEGRAM_ADMIN_ID', '7811548479')

DEFAULT_CHECK_INTERVAL = 120
SLEEP_BETWEEN_CHECKS = 300


def get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor,
    )


def get_due_channels() -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM youtube_channel_subscriptions
        WHERE active = TRUE
        AND (
            last_checked_at IS NULL
            OR last_checked_at < NOW() - (check_interval_minutes || ' minutes')::interval
        )
        ORDER BY last_checked_at ASC NULLS FIRST
    """)
    channels = [dict(r) for r in cur.fetchall()]
    conn.close()
    return channels


def fetch_rss_videos(rss_url: str) -> List[Dict]:
    try:
        resp = requests.get(rss_url, timeout=15)
        if resp.status_code != 200:
            return []

        root = ET.fromstring(resp.text)
        videos = []
        for entry in root.findall('atom:entry', YT_NS):
            video_id_el = entry.find('yt:videoId', YT_NS)
            title_el = entry.find('atom:title', YT_NS)
            published_el = entry.find('atom:published', YT_NS)

            if video_id_el is not None:
                videos.append({
                    'video_id': video_id_el.text,
                    'title': title_el.text if title_el is not None else '',
                    'published': published_el.text if published_el is not None else None,
                })
        return videos
    except Exception as e:
        logger.error(f"RSS parse error for {rss_url}: {e}")
        return []


def get_existing_video_ids(video_ids: List[str]) -> set:
    if not video_ids:
        return set()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT video_id FROM youtube_videos WHERE video_id = ANY(%s)", (video_ids,))
    existing = {r['video_id'] for r in cur.fetchall()}
    conn.close()
    return existing


def get_all_channel_video_ids(channel_url: str) -> List[str]:
    """Use yt-dlp to get ALL video IDs from a channel (full backfill)."""
    try:
        result = subprocess.run(
            ['/opt/mythos/.venv/bin/yt-dlp', '--flat-playlist', '--print', 'id', channel_url],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            logger.warning(f"yt-dlp failed for {channel_url}: {result.stderr[:200]}")
            return []

        video_ids = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        logger.info(f"yt-dlp found {len(video_ids)} videos for {channel_url}")
        return video_ids

    except subprocess.TimeoutExpired:
        logger.warning(f"yt-dlp timed out for {channel_url}")
        return []
    except Exception as e:
        logger.error(f"yt-dlp error for {channel_url}: {e}")
        return []


def update_channel_status(channel_id: str, new_queued: int = 0, latest_published: str = None):
    conn = get_conn()
    cur = conn.cursor()
    if latest_published:
        cur.execute("""
            UPDATE youtube_channel_subscriptions
            SET last_checked_at = NOW(),
                last_video_at = GREATEST(last_video_at, %s::timestamp)
            WHERE channel_id = %s
        """, (latest_published, channel_id))
    else:
        cur.execute("""
            UPDATE youtube_channel_subscriptions
            SET last_checked_at = NOW()
            WHERE channel_id = %s
        """, (channel_id,))
    conn.commit()
    conn.close()


def notify_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_NOTIFY_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={'chat_id': TELEGRAM_NOTIFY_ID, 'text': message, 'parse_mode': 'Markdown'},
            timeout=10,
        )
    except Exception:
        pass


def check_channel(channel: Dict) -> int:
    """Check a single channel for new videos. Queue them for ingestion."""
    from youtube_queue_consumer import enqueue_video, PRIORITY_NORMAL, PRIORITY_LOW

    channel_name = channel['channel_name']
    channel_id = channel['channel_id']
    rss_url = channel['rss_url']
    is_first_check = channel['last_checked_at'] is None

    if not rss_url:
        logger.warning(f"No RSS URL for {channel_name} — skipping")
        update_channel_status(channel_id)
        return 0

    queued_count = 0

    if is_first_check:
        # First check — do a full backfill via yt-dlp
        channel_url = channel.get('channel_url') or f"https://www.youtube.com/channel/{channel_id}"
        logger.info(f"First check for {channel_name} — running full backfill via yt-dlp...")

        all_video_ids = get_all_channel_video_ids(channel_url)
        existing = get_existing_video_ids(all_video_ids)
        new_ids = [vid for vid in all_video_ids if vid not in existing]

        if new_ids:
            logger.info(f"Queueing {len(new_ids)} videos from {channel_name} for backfill")
            for vid in new_ids:
                if enqueue_video(vid, channel_name=channel_name, priority=PRIORITY_LOW, source='backfill'):
                    queued_count += 1

            notify_telegram(
                f"📚 *{channel_name}* — Full backfill started\n"
                f"{len(new_ids)} videos queued for transcript capture\n"
                f"({len(all_video_ids)} total, {len(existing)} already captured)"
            )
        else:
            logger.info(f"All {len(all_video_ids)} videos from {channel_name} already captured")

    # Always do RSS check (catches newest videos faster than yt-dlp)
    logger.info(f"RSS check for {channel_name}...")
    rss_videos = fetch_rss_videos(rss_url)

    if rss_videos:
        video_ids = [v['video_id'] for v in rss_videos]
        existing = get_existing_video_ids(video_ids)
        new_videos = [v for v in rss_videos if v['video_id'] not in existing]

        latest_published = None
        for video in new_videos:
            # Don't double-queue if already queued from backfill
            if enqueue_video(video['video_id'], channel_name=channel_name,
                           priority=PRIORITY_NORMAL, source='rss'):
                queued_count += 1
            if video.get('published'):
                if latest_published is None or video['published'] > latest_published:
                    latest_published = video['published']

        if new_videos and not is_first_check:
            # Only notify about RSS new videos if this isn't the first check
            # (backfill notification already sent above)
            notify_telegram(
                f"📺 *{channel_name}* — {len(new_videos)} new video{'s' if len(new_videos) > 1 else ''} queued"
            )

        update_channel_status(channel_id, latest_published=latest_published)
    else:
        update_channel_status(channel_id)

    if queued_count:
        logger.info(f"Queued {queued_count} videos from {channel_name}")

    return queued_count


# ── Channel management functions (used by skill) ──

def resolve_channel_id(handle_or_url: str) -> Optional[Dict]:
    """Resolve a YouTube handle or URL to channel metadata."""
    import re

    handle_or_url = handle_or_url.strip()
    if handle_or_url.startswith('@'):
        url = f"https://www.youtube.com/{handle_or_url}"
    elif 'youtube.com' in handle_or_url:
        url = handle_or_url
    else:
        url = f"https://www.youtube.com/@{handle_or_url}"

    try:
        resp = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        if resp.status_code != 200:
            return None

        text = resp.text

        match = re.search(r'"channelId":"(UC[a-zA-Z0-9_-]+)"', text)
        if not match:
            match = re.search(r'"externalId":"(UC[a-zA-Z0-9_-]+)"', text)
        if not match:
            return None

        channel_id = match.group(1)
        name_match = re.search(r'"name":"([^"]+)"', text)
        channel_name = name_match.group(1) if name_match else None

        handle_match = re.search(r'"vanityChannelUrl":"[^"]*/@([^"]+)"', text)
        if not handle_match:
            handle_match = re.search(r'youtube\.com/@([a-zA-Z0-9_.-]+)', url)
        channel_handle = f"@{handle_match.group(1)}" if handle_match else None

        return {
            'channel_id': channel_id,
            'channel_name': channel_name,
            'channel_handle': channel_handle,
            'channel_url': url,
            'rss_url': f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}",
        }
    except Exception as e:
        logger.error(f"Failed to resolve channel: {handle_or_url}: {e}")
        return None


def subscribe_channel(handle_or_url: str, added_by: str = 'ka_tuarel') -> Optional[Dict]:
    info = resolve_channel_id(handle_or_url)
    if not info:
        return None

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO youtube_channel_subscriptions
                (channel_id, channel_handle, channel_name, channel_url, rss_url, added_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (channel_id) DO UPDATE SET
                active = TRUE,
                channel_handle = EXCLUDED.channel_handle,
                channel_name = COALESCE(EXCLUDED.channel_name, youtube_channel_subscriptions.channel_name),
                last_checked_at = NULL
            RETURNING *
        """, (
            info['channel_id'],
            info.get('channel_handle'),
            info.get('channel_name') or 'Unknown',
            info.get('channel_url'),
            info['rss_url'],
            added_by,
        ))
        record = dict(cur.fetchone())
        conn.commit()
        return record
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to subscribe: {e}")
        return None
    finally:
        conn.close()


def unsubscribe_channel(identifier: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE youtube_channel_subscriptions SET active = FALSE
        WHERE channel_handle ILIKE %s OR channel_name ILIKE %s OR channel_id = %s
        RETURNING channel_name
    """, (f"%{identifier}%", f"%{identifier}%", identifier))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    return result is not None


def list_subscriptions() -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT channel_name, channel_handle, total_videos_ingested,
               last_checked_at, last_video_at, active
        FROM youtube_channel_subscriptions
        ORDER BY active DESC, channel_name
    """)
    subs = [dict(r) for r in cur.fetchall()]
    conn.close()
    return subs


def main_loop():
    """Main monitor loop — check channels and queue new videos."""
    logger.info("YouTube Channel Monitor (v2 — queue-based) starting...")

    while True:
        try:
            channels = get_due_channels()
            if channels:
                logger.info(f"Checking {len(channels)} channels...")
                total_queued = 0
                for channel in channels:
                    queued = check_channel(channel)
                    total_queued += queued
                    time.sleep(5)

                if total_queued > 0:
                    logger.info(f"Cycle complete: {total_queued} videos queued")
                else:
                    logger.info("Cycle complete: no new videos")
            else:
                logger.debug("No channels due for check")

        except Exception as e:
            logger.error(f"Monitor cycle error: {e}", exc_info=True)

        time.sleep(SLEEP_BETWEEN_CHECKS)


if __name__ == '__main__':
    main_loop()
