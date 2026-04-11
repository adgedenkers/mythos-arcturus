#!/usr/bin/env python3
"""
YouTube Queue Consumer
=======================
Processes YouTube video transcript ingestion from a Redis priority queue.

Three priority levels:
  - HIGH (0): Manual requests from Iris — processed immediately
  - NORMAL (1): New videos from RSS monitor — processed promptly  
  - LOW (2): Backfill from full channel scrape — processed leisurely

Queue format (Redis sorted set):
  Key: mythos:youtube:queue
  Score: priority * 1_000_000_000 + timestamp (ensures priority ordering, FIFO within priority)
  Value: JSON {video_id, channel_name, priority, queued_at, source}

Status tracking:
  Key: mythos:youtube:queue:status — hash with counts and current state
  Key: mythos:youtube:queue:processing — currently processing video ID (or empty)
  Key: mythos:youtube:queue:errors — list of recent errors

Stream: MNE (memory intake)
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Optional, Dict

import redis
import requests
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

sys.path.insert(0, '/opt/mythos/skills/data')
sys.path.insert(0, '/opt/mythos/skills')
sys.path.insert(0, '/opt/mythos/workers')

logger = logging.getLogger('mythos.youtube_queue')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Redis config
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

QUEUE_KEY = 'mythos:youtube:queue'
STATUS_KEY = 'mythos:youtube:queue:status'
PROCESSING_KEY = 'mythos:youtube:queue:processing'
ERRORS_KEY = 'mythos:youtube:queue:errors'

# Priority levels
PRIORITY_HIGH = 0    # Manual request — jump the line
PRIORITY_NORMAL = 1  # New video from RSS
PRIORITY_LOW = 2     # Backfill from full channel scrape

# Delays between ingestions (seconds)
DELAY_AFTER_HIGH = 5
DELAY_AFTER_NORMAL = 30
DELAY_AFTER_LOW = 60

# Telegram notification
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_NOTIFY_ID = os.getenv('TELEGRAM_ADMIN_ID', '7811548479')


def get_redis():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)


def enqueue_video(video_id: str, channel_name: str = '', priority: int = PRIORITY_NORMAL,
                  source: str = 'monitor') -> bool:
    """Add a video to the ingestion queue. Returns True if newly added."""
    r = get_redis()

    # Check if already in queue
    existing = r.zscore(QUEUE_KEY, video_id)
    if existing is not None:
        # Already queued — but if new request is higher priority, update it
        existing_priority = int(existing // 1_000_000_000)
        if priority < existing_priority:
            # Higher priority — re-score
            score = priority * 1_000_000_000 + time.time()
            r.zadd(QUEUE_KEY, {video_id: score})
            # Update metadata
            r.hset(f'{QUEUE_KEY}:meta:{video_id}', mapping={
                'priority': str(priority),
                'source': source,
                'bumped_at': datetime.now().isoformat(),
            })
            logger.info(f"Bumped {video_id} to priority {priority}")
            return True
        return False

    # Add to queue
    score = priority * 1_000_000_000 + time.time()
    r.zadd(QUEUE_KEY, {video_id: score})

    # Store metadata
    r.hset(f'{QUEUE_KEY}:meta:{video_id}', mapping={
        'video_id': video_id,
        'channel_name': channel_name,
        'priority': str(priority),
        'source': source,
        'queued_at': datetime.now().isoformat(),
    })

    # Update status counts
    r.hincrby(STATUS_KEY, 'total_queued', 1)
    r.hincrby(STATUS_KEY, f'queued_{_priority_name(priority)}', 1)

    return True


def dequeue_video() -> Optional[Dict]:
    """Pop the highest-priority video from the queue."""
    r = get_redis()

    # Get the lowest-scored item (highest priority)
    items = r.zrange(QUEUE_KEY, 0, 0, withscores=True)
    if not items:
        return None

    video_id, score = items[0]

    # Remove from queue
    r.zrem(QUEUE_KEY, video_id)

    # Get metadata
    meta = r.hgetall(f'{QUEUE_KEY}:meta:{video_id}')
    r.delete(f'{QUEUE_KEY}:meta:{video_id}')

    # Mark as processing
    r.set(PROCESSING_KEY, video_id)

    priority = int(meta.get('priority', PRIORITY_NORMAL))

    return {
        'video_id': video_id,
        'channel_name': meta.get('channel_name', ''),
        'priority': priority,
        'source': meta.get('source', 'unknown'),
        'queued_at': meta.get('queued_at', ''),
    }


def get_queue_status() -> Dict:
    """Get current queue status for Iris to report."""
    r = get_redis()

    total = r.zcard(QUEUE_KEY)
    processing = r.get(PROCESSING_KEY) or ''

    # Count by priority
    high = 0
    normal = 0
    low = 0

    if total > 0:
        all_items = r.zrange(QUEUE_KEY, 0, -1, withscores=True)
        for vid, score in all_items:
            p = int(score // 1_000_000_000)
            if p == PRIORITY_HIGH:
                high += 1
            elif p == PRIORITY_NORMAL:
                normal += 1
            else:
                low += 1

    # Count by channel
    channels = {}
    if total > 0:
        all_items = r.zrange(QUEUE_KEY, 0, -1)
        for vid in all_items:
            meta = r.hgetall(f'{QUEUE_KEY}:meta:{vid}')
            ch = meta.get('channel_name', 'Unknown')
            channels[ch] = channels.get(ch, 0) + 1

    status = r.hgetall(STATUS_KEY)

    return {
        'pending': total,
        'processing': processing,
        'by_priority': {'high': high, 'normal': normal, 'low': low},
        'by_channel': channels,
        'total_processed': int(status.get('total_processed', 0)),
        'total_errors': int(status.get('total_errors', 0)),
    }


def _priority_name(p: int) -> str:
    return {0: 'high', 1: 'normal', 2: 'low'}.get(p, 'unknown')


def notify_telegram(message: str):
    """Send notification to Ka'tuar'el."""
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


def process_video(item: Dict) -> bool:
    """Ingest a single video. Returns True on success."""
    video_id = item['video_id']
    r = get_redis()

    try:
        from youtube_intake import fetch_transcript, fetch_metadata, store_video, log_to_graph
        import psycopg2
        from psycopg2.extras import RealDictCursor

        # Check if already in DB (might have been ingested manually while queued)
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'mythos'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            port=os.getenv('POSTGRES_PORT', '5432'),
            cursor_factory=RealDictCursor,
        )
        cur = conn.cursor()
        cur.execute("SELECT id FROM youtube_videos WHERE video_id = %s", (video_id,))
        existing = cur.fetchone()
        conn.close()

        if existing:
            logger.info(f"Already ingested: {video_id} — skipping")
            r.hincrby(STATUS_KEY, 'total_processed', 1)
            r.hincrby(STATUS_KEY, 'skipped_existing', 1)
            return True

        # Fetch and ingest
        metadata = fetch_metadata(video_id)
        title = metadata.get('title') or f'Video {video_id}'
        channel = metadata.get('channel_name') or item.get('channel_name', 'Unknown')

        transcript_data = fetch_transcript(video_id)

        if transcript_data.get('error') and not transcript_data.get('segments'):
            logger.warning(f"No transcript for {video_id} ({title}): {transcript_data['error']}")
            r.hincrby(STATUS_KEY, 'total_errors', 1)
            r.lpush(ERRORS_KEY, json.dumps({
                'video_id': video_id,
                'title': title,
                'error': transcript_data['error'],
                'time': datetime.now().isoformat(),
            }))
            r.ltrim(ERRORS_KEY, 0, 49)  # Keep last 50 errors
            return False

        record = store_video(video_id, metadata, transcript_data)
        log_to_graph(video_id, title, channel, record.get('word_count', 0))

        # Update status
        r.hincrby(STATUS_KEY, 'total_processed', 1)

        word_count = record.get('word_count', 0)
        priority = item.get('priority', PRIORITY_NORMAL)

        logger.info(f"Ingested: {title} by {channel} ({word_count:,} words) [priority: {_priority_name(priority)}]")

        # Notify on high-priority or if it's from a manual request
        if priority == PRIORITY_HIGH:
            notify_telegram(f"📺 *Ingested* (manual): _{title}_ by {channel}\n{word_count:,} words captured")

        return True

    except Exception as e:
        logger.error(f"Failed to process {video_id}: {e}", exc_info=True)
        r.hincrby(STATUS_KEY, 'total_errors', 1)
        r.lpush(ERRORS_KEY, json.dumps({
            'video_id': video_id,
            'error': str(e),
            'time': datetime.now().isoformat(),
        }))
        r.ltrim(ERRORS_KEY, 0, 49)
        return False

    finally:
        r.delete(PROCESSING_KEY)


def main_loop():
    """Main consumer loop — process videos from the queue forever."""
    logger.info("YouTube Queue Consumer starting...")
    r = get_redis()

    while True:
        try:
            item = dequeue_video()

            if item is None:
                # Nothing in queue — sleep and check again
                time.sleep(10)
                continue

            priority = item.get('priority', PRIORITY_NORMAL)
            logger.info(f"Processing: {item['video_id']} ({_priority_name(priority)}) from {item.get('channel_name', '?')}")

            success = process_video(item)

            # Delay based on priority
            if priority == PRIORITY_HIGH:
                time.sleep(DELAY_AFTER_HIGH)
            elif priority == PRIORITY_NORMAL:
                time.sleep(DELAY_AFTER_NORMAL)
            else:
                time.sleep(DELAY_AFTER_LOW)

        except Exception as e:
            logger.error(f"Consumer loop error: {e}", exc_info=True)
            time.sleep(30)


if __name__ == '__main__':
    main_loop()
