#!/usr/bin/env python3
"""
Iris Trigger Engine — Standalone Runner

Runs the trigger engine as an independent service.
Loads .env, connects to Postgres, fires triggers on schedule.

Usage:
    /opt/mythos/.venv/bin/python3 /opt/mythos/iris/core/src/trigger_runner.py
"""

import asyncio
import logging
import os
import signal
import sys

# Load .env if available
def load_env():
    env_path = "/opt/mythos/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key not in os.environ:
                    os.environ[key] = value

load_env()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("iris.trigger_runner")

# Add mythos to path
sys.path.insert(0, "/opt/mythos")
sys.path.insert(0, "/opt/mythos/iris/core")

from src.trigger_engine import TriggerEngine


def build_db_config() -> dict:
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "database": os.getenv("POSTGRES_DB", "mythos"),
        "user": os.getenv("POSTGRES_USER", "adge"),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
    }


def try_load_task_registry(db_config: dict):
    """Try to load the idle task registry for run_task support."""
    try:
        from src.task_registry import TaskRegistry
        registry = TaskRegistry(db_config)
        registry.initialize()
        log.info(f"Task registry loaded: {len(registry.tasks)} tasks")
        return registry
    except Exception as e:
        log.warning(f"Could not load task registry (idle tasks disabled): {e}")
        return None


async def main():
    db_config = build_db_config()

    # Try to load task registry for idle task integration
    task_registry = try_load_task_registry(db_config)

    engine = TriggerEngine(db_config, task_registry=task_registry)

    # Shutdown event
    shutdown = asyncio.Event()

    def signal_handler(sig, frame):
        log.info(f"Received signal {sig}, shutting down...")
        shutdown.set()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    log.info("═══ Iris Trigger Engine Starting ═══")
    log.info(f"  DB: {db_config['host']}:{db_config['port']}/{db_config['database']}")

    await engine.run(shutdown)

    log.info("═══ Iris Trigger Engine Stopped ═══")


if __name__ == "__main__":
    asyncio.run(main())
