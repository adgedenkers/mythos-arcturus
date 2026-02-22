#!/usr/bin/env python3
"""
Voice Memo File Watcher for Mythos

Monitors /opt/mythos/voice_memos/incoming/ for new audio files.
When a file appears (from Syncthing or manual placement), dispatches
a transcription task to the Redis stream.

Runs as a systemd service: mythos-voice-watcher.service

Handles:
- .m4a (iPhone Voice Memos)
- .mp3, .wav, .ogg, .opus, .flac, .aac, .wma
- Waits for files to finish writing (stable size check)
- Deduplicates by filename to prevent re-processing
"""

import os
import sys
import json
import time
import signal
import logging
import hashlib
from pathlib import Path
from datetime import datetime

sys.path.insert(0, "/opt/mythos")

import redis
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

# Configuration
WATCH_DIR = Path("/opt/mythos/voice_memos/incoming")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
TELEGRAM_ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")

# Audio file extensions we process
AUDIO_EXTENSIONS = {
    ".m4a", ".mp3", ".wav", ".ogg", ".opus",
    ".flac", ".aac", ".wma", ".mp4", ".webm",
}

# Stream config — matches worker framework
STREAM = "mythos:assignments:transcription"

# Polling interval (seconds)
POLL_INTERVAL = 5

# How long to wait for file to stabilize (seconds)
STABLE_WAIT = 3

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("voice_watcher")

# Track which files we've already dispatched (prevents re-dispatch on restart)
# Also stored in Redis for persistence across restarts
DISPATCHED_SET_KEY = "mythos:voice_memos:dispatched"


class VoiceWatcher:
    """Watches incoming directory and dispatches transcription tasks."""

    def __init__(self):
        self.redis = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
            decode_responses=True,
        )
        self.running = True
        self._pending_files = {}  # path → last_size (for stability check)

        # Ensure watch directory exists
        WATCH_DIR.mkdir(parents=True, exist_ok=True)

        logger.info(f"VoiceWatcher initialized — watching {WATCH_DIR}")

    def _is_audio_file(self, path: Path) -> bool:
        """Check if file has a supported audio extension"""
        return path.suffix.lower() in AUDIO_EXTENSIONS

    def _is_already_dispatched(self, filepath: str) -> bool:
        """Check if file was already dispatched (stored in Redis)"""
        file_key = hashlib.sha256(filepath.encode()).hexdigest()[:16]
        return self.redis.sismember(DISPATCHED_SET_KEY, file_key)

    def _mark_dispatched(self, filepath: str):
        """Mark file as dispatched in Redis"""
        file_key = hashlib.sha256(filepath.encode()).hexdigest()[:16]
        self.redis.sadd(DISPATCHED_SET_KEY, file_key)

    def _is_file_stable(self, filepath: Path) -> bool:
        """
        Check if file has finished writing by comparing sizes.
        Syncthing writes incrementally, so we wait for the size to stop changing.
        """
        try:
            current_size = filepath.stat().st_size
        except FileNotFoundError:
            return False

        str_path = str(filepath)

        if str_path not in self._pending_files:
            # First time seeing this file — record size and wait
            self._pending_files[str_path] = current_size
            return False

        if self._pending_files[str_path] != current_size:
            # Still changing
            self._pending_files[str_path] = current_size
            return False

        # Size hasn't changed since last check — file is stable
        # (We check every POLL_INTERVAL seconds, so file has been
        # stable for at least POLL_INTERVAL seconds)
        del self._pending_files[str_path]
        return True

    def dispatch_transcription(self, filepath: Path):
        """Push a transcription task to the Redis stream"""
        payload = {
            "file_path": str(filepath),
            "source": "syncthing",
            "notify_telegram": True,
            "telegram_chat_id": TELEGRAM_ADMIN_CHAT_ID,
            "dispatched_at": datetime.now().isoformat(),
        }

        # Push to Redis stream
        message_id = self.redis.xadd(
            STREAM,
            {"data": json.dumps(payload)},
        )

        self._mark_dispatched(str(filepath))

        logger.info(
            f"Dispatched transcription task: {filepath.name} → "
            f"stream={STREAM}, msg_id={message_id}"
        )

    def scan(self):
        """Scan incoming directory for new audio files"""
        if not WATCH_DIR.exists():
            return

        for entry in WATCH_DIR.iterdir():
            if not entry.is_file():
                continue
            if not self._is_audio_file(entry):
                continue

            # Skip hidden/temp files (Syncthing uses .syncthing.* temp files)
            if entry.name.startswith("."):
                continue

            # Skip already dispatched
            if self._is_already_dispatched(str(entry)):
                continue

            # Check if file is done writing
            if not self._is_file_stable(entry):
                logger.debug(f"File still writing: {entry.name}")
                continue

            # File is ready — dispatch it
            logger.info(f"New voice memo detected: {entry.name} ({entry.stat().st_size} bytes)")
            self.dispatch_transcription(entry)

    def run(self):
        """Main watch loop"""
        logger.info(f"Starting voice memo watcher — polling every {POLL_INTERVAL}s")
        logger.info(f"Watch directory: {WATCH_DIR}")
        logger.info(f"Supported formats: {', '.join(sorted(AUDIO_EXTENSIONS))}")

        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)

        while self.running:
            try:
                self.scan()
            except redis.ConnectionError as e:
                logger.error(f"Redis connection error: {e}")
            except Exception as e:
                logger.exception(f"Scan error: {e}")

            time.sleep(POLL_INTERVAL)

        logger.info("Voice watcher stopped")

    def _shutdown(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False


if __name__ == "__main__":
    watcher = VoiceWatcher()
    watcher.run()
