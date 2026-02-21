"""
Mythos Audio Upload API
========================
FastAPI router for receiving audio uploads from iPhone Voice Memos
or any HTTP client.

Endpoints:
    POST /api/upload/audio         — Upload audio file
    GET  /api/upload/audio/status  — Check inbox status
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse

# Config
AUDIO_INBOX = "/opt/mythos/audio/inbox"
AUDIO_PROCESSED = "/opt/mythos/audio/processed"
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_EXTENSIONS = {
    ".m4a", ".mp3", ".wav", ".ogg", ".opus", ".aac",
    ".flac", ".mp4", ".caf", ".aiff", ".wma", ".webm"
}

API_KEY_ENV = "MYTHOS_AUDIO_API_KEY"

router = APIRouter(prefix="/api/upload", tags=["audio"])


def _ensure_dirs():
    os.makedirs(AUDIO_INBOX, exist_ok=True)
    os.makedirs(AUDIO_PROCESSED, exist_ok=True)


def _check_auth(request: Request):
    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        # No key configured = no auth required (initial setup)
        return True

    provided = (
        request.headers.get("X-API-Key")
        or request.headers.get("Authorization", "").replace("Bearer ", "")
        or request.query_params.get("key")
    )

    if provided != api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True


def _human_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


@router.post("/audio")
async def upload_audio(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(default=""),
    tags: str = Form(default=""),
    source: str = Form(default="voice_memo"),
):
    """Upload an audio file to the Mythos audio inbox."""
    _check_auth(request)
    _ensure_dirs()

    # Validate extension
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Timestamped filename
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in (file.filename or "audio"))
    filename = f"{timestamp}_{safe_name}"
    filepath = os.path.join(AUDIO_INBOX, filename)

    # Stream to disk
    file_size = 0
    sha256 = hashlib.sha256()

    try:
        with open(filepath, "wb") as f:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    os.remove(filepath)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Max: {MAX_FILE_SIZE // (1024*1024)}MB"
                    )
                sha256.update(chunk)
                f.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

    # Write metadata sidecar
    metadata = {
        "filename": filename,
        "original_name": file.filename,
        "filepath": filepath,
        "size_bytes": file_size,
        "size_human": _human_size(file_size),
        "sha256": sha256.hexdigest(),
        "content_type": file.content_type,
        "extension": ext,
        "uploaded_at": now.isoformat(),
        "title": title or file.filename,
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "source": source,
        "status": "pending",
    }

    meta_path = filepath + ".json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)

    return JSONResponse(content={
        "status": "ok",
        "message": f"Uploaded {filename}",
        "file": metadata,
    })


@router.get("/audio/status")
async def audio_status(request: Request):
    """Check audio inbox status."""
    _check_auth(request)
    _ensure_dirs()

    inbox_files = [f for f in os.listdir(AUDIO_INBOX) if not f.endswith(".json")]
    processed_files = []
    if os.path.exists(AUDIO_PROCESSED):
        processed_files = [f for f in os.listdir(AUDIO_PROCESSED) if not f.endswith(".json")]

    total_size = sum(
        os.path.getsize(os.path.join(AUDIO_INBOX, f))
        for f in inbox_files
        if os.path.isfile(os.path.join(AUDIO_INBOX, f))
    )

    return {
        "inbox_count": len(inbox_files),
        "inbox_size": _human_size(total_size),
        "processed_count": len(processed_files),
        "recent": sorted(inbox_files, reverse=True)[:10],
    }
