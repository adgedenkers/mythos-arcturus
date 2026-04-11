#!/usr/bin/env python3
"""
Segment Manager — Background Segment Lifecycle Service
======================================================
Runs periodically to:
  - Soft-close stale open segments (30 min no activity)
  - Hard-close old soft-closed segments (4 hours)
  - Archive very old closed segments (7 days)
  - (Future) Trigger Neo4j distillation for closed segments

Designed to run as a lightweight loop, not a full worker.
Can be called from a systemd timer or run as a persistent service.
"""

import os
import sys
import time
import logging
import signal

sys.path.insert(0, '/opt/mythos')
sys.path.insert(0, '/opt/mythos/core')

from dotenv import load_dotenv
load_dotenv('/opt/mythos/.env')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('segment_manager')

# Graceful shutdown
_running = True

def _signal_handler(signum, frame):
    global _running
    logger.info(f"Received signal {signum}, shutting down...")
    _running = False

signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)

# Run interval
CHECK_INTERVAL_SECONDS = 300  # Every 5 minutes


def run_lifecycle_check():
    """Run one lifecycle check cycle."""
    try:
        from subject_tracker import close_stale_segments
        closed = close_stale_segments()
        if closed > 0:
            logger.info(f"Lifecycle check: closed {closed} segments")
    except Exception as e:
        logger.error(f"Lifecycle check failed: {e}", exc_info=True)


def main():
    """Main loop — run lifecycle checks periodically."""
    logger.info("Segment Manager starting...")
    
    while _running:
        run_lifecycle_check()
        
        # Sleep in small increments so we can respond to signals
        for _ in range(CHECK_INTERVAL_SECONDS):
            if not _running:
                break
            time.sleep(1)
    
    logger.info("Segment Manager stopped.")


if __name__ == '__main__':
    main()
