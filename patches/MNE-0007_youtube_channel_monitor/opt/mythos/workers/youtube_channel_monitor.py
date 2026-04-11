#!/usr/bin/env python3
"""
YouTube Channel Monitor Worker
================================
Polls subscribed YouTube channels via RSS feeds and auto-ingests
new video transcripts into the Mythos memory lattice.

Runs as a systemd service on a loop:
1. Query youtube_channel_subscriptions for active channels due for check
2. Fetch RSS feed for each channel
3. Compare video IDs against youtube_videos table
4. For any new videos, run the youtube_intake pipeline
5. Update last_checked_at and counters
6. Notify via Telegram when new videos are ingested
7. Sleep until next check cycle

Stream: MNE (memory intake)
"""

import os
import sys
import time
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

# Add skills to path for youtube_intake functions
sys.path.insert(0, '/opt/mythos/skills/data')
sys.path.insert(0, '/opt/mythos/skills')

logger = logging.getLogger('mythos.youtube_monitor')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# YouTube RSS feed namespace
YT_NS = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'atom': 'http://www.w3.org/2005/Atom'}

# Telegram notification config
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_NOTIFY_ID = os.getenv('TELEGRAM_ADMIN_ID', '7811548479')  # Ka'tuar'el

DEFAULT_CHECK_INTERVAL = 120  # minutes
SLEEP_BETWEEN_CHECKS = 300   # 5 minutes between full scan loops


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
    """Get channels that are due for a check."""
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
    """Fetch video entries from a YouTube channel RSS feed."""
    try:
        resp = requests.get(rss_url, timeout=15)
        if resp.status_code != 200:
            logger.warning(f"RSS fetch failed ({resp.status_code}): {rss_url}")
            return []

        root = ET.fromstring(resp.text)
        videos = []

        for entry in root.findall('atom:entry', YT_NS):
            video_id_el = entry.find('yt:videoId', YT_NS)
            title_el = entry.find('atom:title', YT_NS)
            published_el = entry.find('atom:published', YT_NS)
            author_el = entry.find('atom:author/atom:name', YT_NS)

            if video_id_el is not None:
                video = {
                    'video_id': video_id_el.text,
                    'title': title_el.text if title_el is not None else '',
                    'published': published_el.text if published_el is not None else None,
                    'author': author_el.text if author_el is not None else '',
                }
                videos.append(video)

        return videos

    except Exception as e:
        logger.error(f"RSS parse error for {rss_url}: {e}")
        return []


def get_existing_video_ids(video_ids: List[str]) -> set:
    """Check which video IDs are already in the database."""
    if not video_ids:
        return set()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT video_id FROM youtube_videos WHERE video_id = ANY(%s)",
        (video_ids,)
    )
    existing = {r['video_id'] for r in cur.fetchall()}
    conn.close()
    return existing


def ingest_video(video_id: str) -> Optional[Dict]:
    """Run the full intake pipeline for a single video."""
    from youtube_intake import fetch_transcript, fetch_metadata, store_video, log_to_graph

    try:
        metadata = fetch_metadata(video_id)
        title = metadata.get('title') or f'Video {video_id}'
        channel = metadata.get('channel_name') or 'Unknown'

        transcript_data = fetch_transcript(video_id)

        if transcript_data.get('error') and not transcript_data.get('segments'):
            logger.warning(f"No transcript for {video_id} ({title}): {transcript_data['error']}")
            return None

        record = store_video(video_id, metadata, transcript_data)
        log_to_graph(video_id, title, channel, record.get('word_count', 0))

        logger.info(f"Ingested: {title} ({record.get('word_count', 0)} words)")
        return {
            'video_id': video_id,
            'title': title,
            'channel': channel,
            'word_count': record.get('word_count', 0),
        }

    except Exception as e:
        logger.error(f"Failed to ingest {video_id}: {e}")
        return None


def update_channel_status(channel_id: str, new_videos_count: int, latest_published: str = None):
    """Update the subscription record after a check."""
    conn = get_conn()
    cur = conn.cursor()

    if latest_published:
        cur.execute("""
            UPDATE youtube_channel_subscriptions
            SET last_checked_at = NOW(),
                total_videos_ingested = total_videos_ingested + %s,
                last_video_at = GREATEST(last_video_at, %s::timestamp)
            WHERE channel_id = %s
        """, (new_videos_count, latest_published, channel_id))
    else:
        cur.execute("""
            UPDATE youtube_channel_subscriptions
            SET last_checked_at = NOW(),
                total_videos_ingested = total_videos_ingested + %s
            WHERE channel_id = %s
        """, (new_videos_count, channel_id))

    conn.commit()
    conn.close()


def notify_telegram(message: str):
    """Send a notification to Ka'tuar'el via Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_NOTIFY_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                'chat_id': TELEGRAM_NOTIFY_ID,
                'text': message,
                'parse_mode': 'Markdown',
            },
            timeout=10,
        )
    except Exception as e:
        logger.warning(f"Telegram notify failed: {e}")


def check_channel(channel: Dict) -> int:
    """Check a single channel for new videos. Returns count of new videos ingested."""
    channel_name = channel['channel_name']
    rss_url = channel['rss_url']

    if not rss_url:
        logger.warning(f"No RSS URL for {channel_name} — skipping")
        update_channel_status(channel['channel_id'], 0)
        return 0

    logger.info(f"Checking {channel_name}...")
    rss_videos = fetch_rss_videos(rss_url)

    if not rss_videos:
        logger.info(f"  No videos in RSS for {channel_name}")
        update_channel_status(channel['channel_id'], 0)
        return 0

    # Check which are new
    video_ids = [v['video_id'] for v in rss_videos]
    existing = get_existing_video_ids(video_ids)
    new_videos = [v for v in rss_videos if v['video_id'] not in existing]

    if not new_videos:
        logger.info(f"  No new videos from {channel_name}")
        update_channel_status(channel['channel_id'], 0)
        return 0

    logger.info(f"  Found {len(new_videos)} new videos from {channel_name}")

    # Ingest each new video
    ingested = []
    latest_published = None

    for video in new_videos:
        result = ingest_video(video['video_id'])
        if result:
            ingested.append(result)
            if video.get('published'):
                if latest_published is None or video['published'] > latest_published:
                    latest_published = video['published']

        # Small delay between ingestions to be respectful
        time.sleep(2)

    # Update channel status
    update_channel_status(channel['channel_id'], len(ingested), latest_published)

    # Notify if we got new content
    if ingested:
        lines = [f"📺 *{channel_name}* — {len(ingested)} new video{'s' if len(ingested) > 1 else ''}:"]
        for v in ingested:
            lines.append(f"  • _{v['title']}_ ({v['word_count']:,} words)")
        notify_telegram('\n'.join(lines))

    return len(ingested)


def resolve_channel_id(handle_or_url: str) -> Optional[Dict]:
    """Resolve a YouTube handle or URL to a channel ID and metadata.
    
    Uses the YouTube page to extract the channel ID from meta tags.
    Works with @handles, /channel/ URLs, and /c/ URLs.
    """
    # Normalize to a URL we can fetch
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

        # Extract channel ID from meta tag or page source
        import re

        # Try meta tag: <meta itemprop="channelId" content="UCxxxxxxx">
        match = re.search(r'"channelId":"(UC[a-zA-Z0-9_-]+)"', text)
        if not match:
            match = re.search(r'channel_id=([UC][a-zA-Z0-9_-]+)', text)
        if not match:
            match = re.search(r'"externalId":"(UC[a-zA-Z0-9_-]+)"', text)

        if not match:
            return None

        channel_id = match.group(1)

        # Try to get channel name
        name_match = re.search(r'"name":"([^"]+)"', text)
        channel_name = name_match.group(1) if name_match else None

        # Extract handle
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
    """Subscribe to a YouTube channel. Returns the subscription record or None."""
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
                channel_name = COALESCE(EXCLUDED.channel_name, youtube_channel_subscriptions.channel_name)
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
        logger.error(f"Failed to subscribe to {handle_or_url}: {e}")
        return None
    finally:
        conn.close()


def unsubscribe_channel(identifier: str) -> bool:
    """Deactivate a subscription by handle, name, or channel_id."""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE youtube_channel_subscriptions
        SET active = FALSE
        WHERE channel_handle ILIKE %s
           OR channel_name ILIKE %s
           OR channel_id = %s
        RETURNING channel_name
    """, (f"%{identifier}%", f"%{identifier}%", identifier))

    result = cur.fetchone()
    conn.commit()
    conn.close()
    return result is not None


def list_subscriptions() -> List[Dict]:
    """List all active subscriptions."""
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
    """Main worker loop — check channels forever."""
    logger.info("YouTube Channel Monitor starting...")

    while True:
        try:
            channels = get_due_channels()

            if channels:
                logger.info(f"Checking {len(channels)} channels due for update...")
                total_new = 0

                for channel in channels:
                    new_count = check_channel(channel)
                    total_new += new_count
                    time.sleep(5)  # Be respectful between channels

                if total_new > 0:
                    logger.info(f"Cycle complete: {total_new} new videos ingested")
                else:
                    logger.info(f"Cycle complete: no new videos")
            else:
                logger.debug("No channels due for check")

        except Exception as e:
            logger.error(f"Monitor cycle error: {e}", exc_info=True)

        time.sleep(SLEEP_BETWEEN_CHECKS)


if __name__ == '__main__':
    main_loop()
