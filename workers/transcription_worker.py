#!/usr/bin/env python3
"""
Transcription Worker for Mythos

Processes voice memo transcription assignments from Redis stream.
Plugs into the existing worker framework (workers/worker.py).

Stream: mythos:assignments:transcription
Group: transcription_workers

Assignment payload:
{
    "file_path": "/opt/mythos/voice_memos/incoming/recording.m4a",
    "memo_id": "uuid",           # If already created in DB
    "source": "syncthing",       # or "telegram", "manual"
    "notify_telegram": true,
    "telegram_chat_id": "12345"  # Who to notify
}
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, "/opt/mythos")

import psycopg2
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger(__name__)

# DB config
DB_HOST = os.getenv("POSTGRES_HOST", "/var/run/postgresql")
DB_NAME = os.getenv("POSTGRES_DB", "mythos")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "")

# Telegram config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")

# Paths
VOICE_MEMOS_BASE = Path("/opt/mythos/voice_memos")
PROCESSING_DIR = VOICE_MEMOS_BASE / "processing"
ARCHIVE_DIR = VOICE_MEMOS_BASE / "archive"
WAV_CACHE_DIR = VOICE_MEMOS_BASE / "wav_cache"

# Lazy-loaded transcription service
_transcription_service = None


def get_transcription_service():
    """Lazy-load the heavy transcription service"""
    global _transcription_service
    if _transcription_service is None:
        from services.diarized_transcription import DiarizedTranscriptionService
        _transcription_service = DiarizedTranscriptionService()
    return _transcription_service


def get_db_conn():
    """Get a database connection"""
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME,
        user=DB_USER, password=DB_PASS,
    )


def send_telegram_notification(chat_id: str, text: str):
    """Send a Telegram notification (sync, for worker context)"""
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        logger.warning("Telegram notification skipped — no token or chat_id")
        return

    try:
        import httpx

        resp = httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
            },
            timeout=10,
        )
        if resp.status_code != 200:
            logger.error(f"Telegram notification failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        logger.error(f"Telegram notification error: {e}")


def create_memo_record(
    file_path: str, filename: str, source: str, file_size: int
) -> str:
    """Create a voice_memos record in the DB, return memo_id"""
    conn = get_db_conn()
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO voice_memos
            (filename, original_path, source, file_size_bytes, status, created_at)
        VALUES (%s, %s, %s, %s, 'processing', NOW())
        RETURNING id
        """,
        (filename, file_path, source, file_size),
    )
    memo_id = str(cur.fetchone()[0])
    cur.close()
    conn.close()

    logger.info(f"Created voice_memos record: {memo_id}")
    return memo_id


def save_transcription_result(memo_id: str, result: Dict[str, Any]):
    """Save the full transcription result to the database"""
    conn = get_db_conn()
    conn.autocommit = True
    cur = conn.cursor()

    # Update the memo record
    cur.execute(
        """
        UPDATE voice_memos SET
            transcript_full = %s,
            transcript_diarized = %s,
            duration_seconds = %s,
            speaker_count = %s,
            language = %s,
            diarized = %s,
            processing_times = %s,
            speaker_stats = %s,
            status = 'complete',
            processed_at = NOW()
        WHERE id = %s
        """,
        (
            result["text"],
            result.get("formatted_transcript", result["text"]),
            result["duration"],
            len(result.get("speakers", {})),
            result.get("language", ""),
            result.get("diarized", False),
            json.dumps(result.get("processing_times", {})),
            json.dumps(result.get("speakers", {})),
            memo_id,
        ),
    )

    # Save individual segments
    diarized_segments = result.get("diarized_segments", [])
    for i, seg in enumerate(diarized_segments):
        cur.execute(
            """
            INSERT INTO voice_memo_segments
                (memo_id, segment_index, speaker_label, start_time, end_time, text)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                memo_id,
                i,
                seg.get("speaker", "UNKNOWN"),
                float(seg["start"]),
                float(seg["end"]),
                seg["text"],
            ),
        )

    cur.close()
    conn.close()

    logger.info(
        f"Saved transcription for memo {memo_id}: "
        f"{len(result['text'])} chars, {len(diarized_segments)} segments"
    )


def update_memo_status(memo_id: str, status: str, error: str = None):
    """Update memo status (e.g., on error)"""
    conn = get_db_conn()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE voice_memos SET status = %s, error_message = %s WHERE id = %s
        """,
        (status, error, memo_id),
    )
    cur.close()
    conn.close()


def process_transcription(payload: dict) -> dict:
    """
    Main handler for transcription assignments.
    Called by the Worker framework.
    """
    file_path = payload.get("file_path", "")
    memo_id = payload.get("memo_id")
    source = payload.get("source", "unknown")
    notify_telegram = payload.get("notify_telegram", True)
    telegram_chat_id = payload.get("telegram_chat_id", TELEGRAM_ADMIN_CHAT_ID)

    if not file_path or not Path(file_path).exists():
        logger.error(f"File not found: {file_path}")
        return {"status": "error", "error": "file_not_found"}

    filename = Path(file_path).name
    file_size = Path(file_path).stat().st_size

    logger.info(f"Processing voice memo: {filename} ({file_size} bytes, source={source})")

    # Move to processing dir
    PROCESSING_DIR.mkdir(parents=True, exist_ok=True)
    processing_path = PROCESSING_DIR / filename

    try:
        Path(file_path).rename(processing_path)
    except OSError:
        # Cross-device move (different filesystems)
        import shutil
        shutil.move(str(file_path), str(processing_path))

    # Create DB record if not already created
    if not memo_id:
        memo_id = create_memo_record(
            str(processing_path), filename, source, file_size
        )

    try:
        # Send "processing started" notification
        if notify_telegram and telegram_chat_id:
            duration_est = file_size / 16000  # Very rough estimate
            send_telegram_notification(
                telegram_chat_id,
                f"🎙️ Voice memo received: <b>{filename}</b>\n"
                f"Processing (~{duration_est:.0f}s audio)...",
            )

        # Run the full pipeline
        ts = get_transcription_service()
        result = ts.transcribe_with_diarization(
            str(processing_path),
            wav_cache_dir=str(WAV_CACHE_DIR),
        )

        if result.get("error"):
            raise RuntimeError(f"Transcription error: {result['error']}")

        # Save to DB
        save_transcription_result(memo_id, result)

        # Move to archive
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        archive_path = ARCHIVE_DIR / filename
        try:
            processing_path.rename(archive_path)
        except OSError:
            import shutil
            shutil.move(str(processing_path), str(archive_path))

        # Update with archive path
        conn = get_db_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(
            "UPDATE voice_memos SET archive_path = %s WHERE id = %s",
            (str(archive_path), memo_id),
        )
        cur.close()
        conn.close()

        # Send completion notification
        if notify_telegram and telegram_chat_id:
            pt = result.get("processing_times", {})
            speakers = result.get("speakers", {})
            duration = result.get("duration", 0)

            # Build speaker summary
            speaker_lines = []
            for spk, stats in speakers.items():
                pct = (stats["total_duration"] / duration * 100) if duration else 0
                speaker_lines.append(
                    f"  {spk}: {stats['word_count']} words ({pct:.0f}%)"
                )
            speaker_summary = "\n".join(speaker_lines) if speaker_lines else "  (no speakers detected)"

            # Transcript preview
            transcript = result.get("formatted_transcript", result.get("text", ""))
            preview = transcript[:500] + "..." if len(transcript) > 500 else transcript

            send_telegram_notification(
                telegram_chat_id,
                f"✅ Voice memo transcribed: <b>{filename}</b>\n\n"
                f"📊 {duration:.0f}s audio → {len(result['text'])} chars\n"
                f"🔊 {len(speakers)} speakers:\n{speaker_summary}\n"
                f"⏱️ Processing: {pt.get('total_s', 0):.0f}s "
                f"(transcribe={pt.get('transcribe_s', 0):.0f}s, "
                f"diarize={pt.get('diarize_s', 0):.0f}s)\n\n"
                f"📝 Preview:\n<pre>{preview}</pre>",
            )

        logger.info(f"Voice memo {memo_id} complete: {filename}")

        return {
            "status": "complete",
            "memo_id": memo_id,
            "duration": result["duration"],
            "speakers": len(result.get("speakers", {})),
            "chars": len(result["text"]),
            "diarized": result.get("diarized", False),
            "processing_time": result.get("processing_times", {}).get("total_s", 0),
        }

    except Exception as e:
        logger.exception(f"Transcription failed for {filename}: {e}")

        # Update DB status
        if memo_id:
            update_memo_status(memo_id, "error", str(e)[:500])

        # Notify failure
        if notify_telegram and telegram_chat_id:
            send_telegram_notification(
                telegram_chat_id,
                f"❌ Voice memo failed: <b>{filename}</b>\n"
                f"Error: {str(e)[:200]}",
            )

        return {"status": "error", "error": str(e), "memo_id": memo_id}
