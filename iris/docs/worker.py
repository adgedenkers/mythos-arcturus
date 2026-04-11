"""Core documentation worker - polls Redis queues, dispatches to handlers."""
import os, json, time, hashlib, logging, signal
import psycopg2
import redis as redis_lib

from iris.docs.handlers import component as component_handler
from iris.docs.handlers import architecture as architecture_handler
from iris.docs.handlers import system_map as system_map_handler

logger = logging.getLogger("iris.docs.worker")

QUEUES_TO_HANDLERS = {
    "iris:docs:queue:component": component_handler,
    "iris:docs:queue:architecture": architecture_handler,
    "iris:docs:queue:system_map": system_map_handler,
}

DEDUP_KEY = "iris:docs:dedup"
PROCESSING_KEY = "iris:docs:processing"
COMPLETED_KEY = "iris:docs:completed"

_shutdown = False


def _signal_handler(signum, frame):
    global _shutdown
    logger.info("Shutdown signal received, finishing current task...")
    _shutdown = True


def task_hash(task):
    return hashlib.sha256(json.dumps(task, sort_keys=True).encode()).hexdigest()[:16]


def run_worker(mode="daemon", queue_filter=None, dry_run=False):
    """Main worker entry point."""
    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)

    r = redis_lib.Redis(host="localhost", port=6379, decode_responses=True)

    if queue_filter:
        queue_key = f"iris:docs:queue:{queue_filter}"
        if queue_key not in QUEUES_TO_HANDLERS:
            logger.error(f"Unknown queue: {queue_filter}. Options: component, architecture, system_map")
            return
        queues = {queue_key: QUEUES_TO_HANDLERS[queue_key]}
    else:
        queues = QUEUES_TO_HANDLERS

    queue_names = list(queues.keys())

    conn = psycopg2.connect(dbname="mythos")
    run_id = _create_worker_run(conn, mode, queue_filter)
    tasks_processed = 0
    tasks_failed = 0
    docs_written = 0

    logger.info(f"Doc worker started: mode={mode}, queues={list(queues.keys())}, dry_run={dry_run}")

    try:
        while not _shutdown:
            result = r.blpop(queue_names, timeout=5)

            if result is None:
                if mode == "run_once":
                    total = sum(r.llen(q) for q in queue_names)
                    if total == 0:
                        logger.info("All queues drained, exiting")
                        break
                continue

            queue_key, task_json = result
            try:
                task = json.loads(task_json)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in queue {queue_key}: {task_json[:100]}")
                tasks_failed += 1
                continue

            th = task_hash(task)
            handler = queues.get(queue_key)
            if not handler:
                logger.warning(f"No handler for queue {queue_key}")
                continue

            r.sadd(PROCESSING_KEY, th)
            task_type = task.get("type", "unknown")
            task_comp = task.get("component", task.get("components", "global"))
            logger.info(f"Processing: {task_type} / {task_comp}")

            try:
                success, output_path = handler.handle(task, dry_run=dry_run)
                if success:
                    tasks_processed += 1
                    if output_path:
                        docs_written += 1
                    r.srem(PROCESSING_KEY, th)
                    r.zadd(COMPLETED_KEY, {th: time.time()})
                    logger.info(f"Completed: {task_type} / {task_comp}")
                else:
                    tasks_failed += 1
                    r.srem(PROCESSING_KEY, th)
                    logger.warning(f"Failed: {task_type} / {task_comp}")
            except Exception as e:
                tasks_failed += 1
                r.srem(PROCESSING_KEY, th)
                logger.error(f"Error processing {task_type} / {task_comp}: {e}")

    except Exception as e:
        logger.error(f"Worker error: {e}")
        _finish_worker_run(conn, run_id, tasks_processed, tasks_failed, docs_written, "failed", str(e))
        raise
    finally:
        _finish_worker_run(conn, run_id, tasks_processed, tasks_failed, docs_written, "completed")
        conn.close()

    logger.info(f"Worker finished: processed={tasks_processed}, failed={tasks_failed}, docs={docs_written}")


def _create_worker_run(conn, mode, queue_filter):
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO doc_worker_runs (mode, queue_filter) VALUES (%s, %s) RETURNING run_id""", (mode, queue_filter))
        run_id = cur.fetchone()[0]
        conn.commit()
        return str(run_id)


def _finish_worker_run(conn, run_id, processed, failed, docs, status, error=None):
    try:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE doc_worker_runs SET finished_at = now(), tasks_processed = %s,
                   tasks_failed = %s, docs_written = %s, status = %s, error_message = %s
                   WHERE run_id = %s::uuid""",
                (processed, failed, docs, status, error, run_id),
            )
            conn.commit()
    except Exception as e:
        logger.warning(f"Could not update worker run: {e}")
