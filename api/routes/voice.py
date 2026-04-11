#!/usr/bin/env python3
"""
Voice Memo Upload API

POST /api/voice/upload — Upload a voice memo for transcription
GET  /api/voice/status/{memo_id} — Check transcription status
GET  /api/voice/list — List recent voice memos
GET  /api/voice/transcript/{memo_id} — Get full transcript

Auth: X-API-Key header (same keys as Telegram bot)
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Header, Query
from pydantic import BaseModel

import psycopg2
from dotenv import load_dotenv

load_dotenv("/opt/mythos/.env")

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice"])

# Config
INCOMING_DIR = Path("/opt/mythos/voice_memos/incoming")
VALID_API_KEYS = {
    os.getenv("API_KEY_TELEGRAM_BOT", ""),
    os.getenv("API_KEY_KA", ""),
    os.getenv("API_KEY_SERAPHE", ""),
}
# Remove empty strings
VALID_API_KEYS.discard("")

TELEGRAM_ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")

# Allowed audio extensions
ALLOWED_EXTENSIONS = {
    ".m4a", ".mp3", ".wav", ".ogg", ".opus",
    ".flac", ".aac", ".wma", ".mp4", ".webm",
    ".caf",  # iOS Core Audio Format
}

# Max file size: 500MB
MAX_FILE_SIZE = 500 * 1024 * 1024

# DB config
DB_HOST = os.getenv("POSTGRES_HOST", "/var/run/postgresql")
DB_NAME = os.getenv("POSTGRES_DB", "mythos")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "")


def get_db_conn():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME,
        user=DB_USER, password=DB_PASS,
    )


def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from header"""
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


# ── Response Models ─────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    status: str
    filename: str
    file_size: int
    message: str


class MemoStatus(BaseModel):
    id: int
    filename: str
    status: str
    duration_seconds: Optional[float] = None
    speaker_count: Optional[int] = None
    diarized: Optional[bool] = None
    created_at: Optional[str] = None
    processed_at: Optional[str] = None
    error_message: Optional[str] = None


class MemoTranscript(BaseModel):
    id: int
    filename: str
    status: str
    duration_seconds: Optional[float] = None
    transcript_full: Optional[str] = None
    transcript_diarized: Optional[str] = None
    speaker_count: Optional[int] = None
    speaker_stats: Optional[dict] = None
    processing_times: Optional[dict] = None


# ── Routes ──────────────────────────────────────────────────────────────

@router.post("/upload", response_model=UploadResponse)
async def upload_voice_memo(
    file: UploadFile = File(...),
    x_api_key: str = Header(...),
):
    """
    Upload a voice memo for transcription.

    Accepts any audio file. Saves to incoming directory where the
    file watcher picks it up and dispatches to the transcription worker.
    """
    verify_api_key(x_api_key)

    # Validate extension
    original_name = file.filename or "recording.m4a"
    ext = Path(original_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Generate unique filename (preserve extension)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in Path(original_name).stem if c.isalnum() or c in "-_ ")[:50]
    filename = f"voice_{timestamp}_{safe_name}{ext}"

    # Ensure incoming dir exists
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    dest_path = INCOMING_DIR / filename

    # Stream file to disk (handles large files)
    file_size = 0
    try:
        with open(dest_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    # Clean up partial file
                    f.close()
                    dest_path.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB",
                    )
                f.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        dest_path.unlink(missing_ok=True)
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    logger.info(f"Voice memo uploaded: {filename} ({file_size} bytes)")

    return UploadResponse(
        status="queued",
        filename=filename,
        file_size=file_size,
        message=f"Voice memo saved. Transcription will begin shortly. "
                f"Check status at /api/voice/list",
    )


@router.get("/status/{memo_id}", response_model=MemoStatus)
async def get_memo_status(
    memo_id: int,
    x_api_key: str = Header(...),
):
    """Get the status of a voice memo transcription."""
    verify_api_key(x_api_key)

    try:
        conn = get_db_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, filename, status, duration_seconds, speaker_count,
                   diarized, created_at, processed_at, error_message
            FROM voice_memos WHERE id = %s
            """,
            (memo_id,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Voice memo not found")

        return MemoStatus(
            id=row[0],
            filename=row[1],
            status=row[2],
            duration_seconds=row[3],
            speaker_count=row[4],
            diarized=row[5],
            created_at=str(row[6]) if row[6] else None,
            processed_at=str(row[7]) if row[7] else None,
            error_message=row[8],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_voice_memos(
    x_api_key: str = Header(...),
    limit: int = Query(default=20, le=100),
    status_filter: Optional[str] = Query(default=None),
):
    """List recent voice memos with status."""
    verify_api_key(x_api_key)

    try:
        conn = get_db_conn()
        conn.autocommit = True
        cur = conn.cursor()

        query = """
            SELECT id, filename, status, duration_seconds, speaker_count,
                   diarized, created_at, processed_at, error_message
            FROM voice_memos
        """
        params = []

        if status_filter:
            query += " WHERE status = %s"
            params.append(status_filter)

        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)

        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "count": len(rows),
            "memos": [
                {
                    "id": r[0],
                    "filename": r[1],
                    "status": r[2],
                    "duration_seconds": r[3],
                    "speaker_count": r[4],
                    "diarized": r[5],
                    "created_at": str(r[6]) if r[6] else None,
                    "processed_at": str(r[7]) if r[7] else None,
                    "error_message": r[8],
                }
                for r in rows
            ],
        }
    except Exception as e:
        logger.error(f"List query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcript/{memo_id}", response_model=MemoTranscript)
async def get_transcript(
    memo_id: int,
    x_api_key: str = Header(...),
):
    """Get the full transcript of a voice memo."""
    verify_api_key(x_api_key)

    try:
        conn = get_db_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, filename, status, duration_seconds,
                   transcript_full, transcript_diarized,
                   speaker_count, speaker_stats, processing_times
            FROM voice_memos WHERE id = %s
            """,
            (memo_id,),
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Voice memo not found")

        return MemoTranscript(
            id=row[0],
            filename=row[1],
            status=row[2],
            duration_seconds=row[3],
            transcript_full=row[4],
            transcript_diarized=row[5],
            speaker_count=row[6],
            speaker_stats=row[7] if isinstance(row[7], dict) else (json.loads(row[7]) if row[7] else None),
            processing_times=row[8] if isinstance(row[8], dict) else (json.loads(row[8]) if row[8] else None),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcript query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
