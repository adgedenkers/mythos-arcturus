"""
Queue Dispatcher - creates documentation tasks in Redis queues.
"""
import json
import hashlib
import logging
import time

logger = logging.getLogger("iris.introspection.queue_dispatcher")

QUEUES = {
    "component": "iris:docs:queue:component",
    "architecture": "iris:docs:queue:architecture",
    "help_telegram": "iris:docs:queue:help_telegram",
    "help_cli": "iris:docs:queue:help_cli",
    "context_claude": "iris:docs:queue:context_claude",
    "system_map": "iris:docs:queue:system_map",
    "todo": "iris:docs:queue:todo",
}
DEDUP_KEY = "iris:docs:dedup"
PROCESSING_KEY = "iris:docs:processing"
COMPLETED_KEY = "iris:docs:completed"


def task_hash(task):
    return hashlib.sha256(json.dumps(task, sort_keys=True).encode()).hexdigest()[:16]


def _enqueue(r, queue, task):
    th = task_hash(task)
    if r.sismember(DEDUP_KEY, th):
        return 0
    r.sadd(DEDUP_KEY, th)
    r.rpush(queue, json.dumps(task))
    return 1


def dispatch_tasks(redis_client, component_groups, file_list, component_analyses=None):
    """Dispatch doc tasks to Redis queues. Returns task count."""
    if redis_client is None:
        logger.warning("No Redis client, skipping dispatch")
        return 0

    dispatched = 0
    ca = component_analyses or {}

    for comp, files in component_groups.items():
        # Component doc
        task = {"type": "component_doc", "component": comp,
                "file_count": len(files), "files": [f["file_path"] for f in files],
                "status": "pending", "created_at": time.time()}
        if comp in ca:
            task["component_summary"] = ca[comp].get("component_summary", "")
            task["health"] = ca[comp].get("health", "unknown")
            task["documentation_gaps"] = ca[comp].get("documentation_gaps", [])
        dispatched += _enqueue(redis_client, QUEUES["component"], task)

        # Architecture entry
        dispatched += _enqueue(redis_client, QUEUES["architecture"], {
            "type": "architecture_entry", "component": comp,
            "file_count": len(files),
            "purpose": ca.get(comp, {}).get("component_summary", ""),
            "status": "pending", "created_at": time.time()})

    # System map (global)
    dispatched += _enqueue(redis_client, QUEUES["system_map"], {
        "type": "system_map", "components": list(component_groups.keys()),
        "total_files": len(file_list), "status": "pending", "created_at": time.time()})

    # CLI help docs
    for f in file_list:
        if f.get("file_path", "").startswith("/opt/mythos/bin/"):
            dispatched += _enqueue(redis_client, QUEUES["help_cli"], {
                "type": "help_cli", "file_path": f["file_path"],
                "component": f.get("component", "bin"),
                "status": "pending", "created_at": time.time()})

    # Telegram help docs
    for f in file_list:
        fp = f.get("file_path", "")
        if "telegram" in fp and fp.endswith(".py"):
            dispatched += _enqueue(redis_client, QUEUES["help_telegram"], {
                "type": "help_telegram", "file_path": fp,
                "component": "telegram_bot",
                "status": "pending", "created_at": time.time()})

    # Claude context doc
    dispatched += _enqueue(redis_client, QUEUES["context_claude"], {
        "type": "context_claude", "components": list(component_groups.keys()),
        "total_files": len(file_list),
        "purpose": "Generate updated Claude session context document",
        "status": "pending", "created_at": time.time()})

    # TODO update
    dispatched += _enqueue(redis_client, QUEUES["todo"], {
        "type": "todo_update", "components": list(component_groups.keys()),
        "purpose": "Update TODO.md from introspection findings",
        "status": "pending", "created_at": time.time()})

    logger.info(f"Dispatched {dispatched} tasks to Redis queues")
    return dispatched


def get_queue_status(redis_client):
    """Return current queue depths and processing stats."""
    status = {}
    for name, key in QUEUES.items():
        status[name] = {"pending": redis_client.llen(key) if redis_client else 0}
    if redis_client:
        status["_meta"] = {
            "dedup_set_size": redis_client.scard(DEDUP_KEY),
            "processing": redis_client.scard(PROCESSING_KEY),
            "completed": redis_client.zcard(COMPLETED_KEY),
        }
    return status
