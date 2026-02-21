"""
Mythos Task Dispatcher
=======================
Standardized Redis task queue dispatch.

Uses Redis Streams (matching existing mythos:assignments:* pattern)
to dispatch async jobs to workers.

Usage:
    from core.task_dispatch import dispatch_task

    # Dispatch a transcription job
    await dispatch_task("transcription", {
        "filepath": "/opt/mythos/audio/inbox/file.m4a",
        "callback_chat_id": "7811548479",
    })

    # Dispatch any job
    await dispatch_task("grid_analysis", {
        "message_id": 123,
        "content": "some text",
    })

Workers consume from streams named: mythos:assignments:<task_type>
"""

import json
import os
from datetime import datetime

import redis


def _get_redis() -> redis.Redis:
    """Get Redis connection."""
    return redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", 6379)),
        db=int(os.environ.get("REDIS_DB", 0)),
        decode_responses=True,
    )


def dispatch_task(task_type: str, payload: dict, priority: str = "normal") -> str:
    """
    Dispatch a task to a Redis stream for async processing.

    Args:
        task_type: The type of task (becomes stream name: mythos:assignments:<task_type>)
        payload: Dict of task data
        priority: "normal" or "high" (metadata only for now)

    Returns:
        The Redis stream message ID
    """
    r = _get_redis()
    stream_name = f"mythos:assignments:{task_type}"

    message = {
        "payload": json.dumps(payload),
        "dispatched_at": datetime.now().isoformat(),
        "priority": priority,
        "status": "pending",
    }

    msg_id = r.xadd(stream_name, message)

    # Update stats
    r.hincrby("mythos:stats:assignments", f"{task_type}:dispatched", 1)

    return msg_id


def get_queue_status() -> dict:
    """Get status of all task queues."""
    r = _get_redis()

    # Find all assignment streams
    keys = r.keys("mythos:assignments:*")
    queues = {}
    for key in keys:
        task_type = key.replace("mythos:assignments:", "")
        length = r.xlen(key)
        queues[task_type] = {"pending": length}

    # Get stats
    stats = r.hgetall("mythos:stats:assignments") or {}

    return {
        "queues": queues,
        "stats": stats,
    }
