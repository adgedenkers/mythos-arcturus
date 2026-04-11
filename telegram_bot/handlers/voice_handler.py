#!/usr/bin/env python3
"""
Voice Message Handler for Mythos Telegram Bot

Handles voice messages and audio files from Telegram:
1. Downloads the audio file
2. Saves to /opt/mythos/media/{user_uuid}/
3. Records in media_files table
4. Transcribes via faster-whisper (GPU)
5. Saves transcript to chat_messages
6. Sends transcript to Iris for response

The Thronescribe capture pipeline — voice to memory.
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
import psycopg2
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

logger = logging.getLogger(__name__)

# Config
MEDIA_BASE = Path("/opt/mythos/media")
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY_TELEGRAM_BOT", "")

# DB config
DB_HOST = os.getenv('POSTGRES_HOST', '/var/run/postgresql')
DB_NAME = os.getenv('POSTGRES_DB', 'mythos')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASS = os.getenv('POSTGRES_PASSWORD', '')

# Lazy-loaded transcription service (heavy model, load once)
_transcription_service = None


def get_transcription_service():
    """Get or create the transcription service (lazy load)"""
    global _transcription_service
    if _transcription_service is None:
        from services.transcription import TranscriptionService
        _transcription_service = TranscriptionService()
    return _transcription_service


def get_db_conn():
    """Get a database connection"""
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME,
        user=DB_USER, password=DB_PASS
    )


def get_user_uuid(telegram_id: int) -> Optional[str]:
    """Look up user_uuid from telegram_id"""
    try:
        conn = get_db_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT user_uuid FROM users WHERE telegram_id = %s", (telegram_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return str(row[0]) if row else None
    except Exception as e:
        logger.error(f"User lookup failed: {e}")
        return None


def save_media_record(user_uuid, filename, file_path, file_size, mime_type,
                      media_type, telegram_file_id, telegram_file_unique_id,
                      duration=None, analysis_data=None):
    """Save a media file record to the database"""
    try:
        conn = get_db_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO media_files 
            (user_uuid, filename, file_path, file_size_bytes, mime_type, 
             media_type, telegram_file_id, telegram_file_unique_id, analysis_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            user_uuid, filename, file_path, file_size, mime_type,
            media_type, telegram_file_id, telegram_file_unique_id,
            json.dumps(analysis_data) if analysis_data else None
        ))
        media_id = cur.fetchone()[0]
        cur.close()
        conn.close()
        return str(media_id)
    except Exception as e:
        logger.error(f"Failed to save media record: {e}")
        return None


async def handle_voice(update, context):
    """
    Handle voice messages from Telegram.
    
    Flow: Download → Save → Transcribe → Send to Iris → Respond
    """
    telegram_id = update.effective_user.id
    user_uuid = get_user_uuid(telegram_id)
    
    if not user_uuid:
        await update.message.reply_text("❌ User not recognized")
        return
    
    # Get voice message info
    voice = update.message.voice
    if not voice:
        return
    
    duration = voice.duration
    file_size = voice.file_size
    mime_type = voice.mime_type or "audio/ogg"
    
    # Send typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Status message
    status_msg = await update.message.reply_text(
        f"🎙️ Voice received ({duration}s) — transcribing..."
    )
    
    try:
        # Download the voice file
        file = await context.bot.get_file(voice.file_id)
        
        # Create user media directory
        user_media_dir = MEDIA_BASE / user_uuid
        user_media_dir.mkdir(parents=True, exist_ok=True)
        
        # Save with timestamp filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ogg_filename = f"voice_{timestamp}_{voice.file_unique_id[:8]}.ogg"
        ogg_path = user_media_dir / ogg_filename
        
        await file.download_to_drive(str(ogg_path))
        logger.info(f"Voice downloaded: {ogg_path} ({file_size} bytes, {duration}s)")
        
        # Save media record
        media_id = save_media_record(
            user_uuid=user_uuid,
            filename=ogg_filename,
            file_path=str(ogg_path),
            file_size=file_size,
            mime_type=mime_type,
            media_type="audio",
            telegram_file_id=voice.file_id,
            telegram_file_unique_id=voice.file_unique_id,
            analysis_data={"duration": duration, "type": "voice_message"}
        )
        
        # Transcribe
        start_time = time.time()
        ts = get_transcription_service()
        result = ts.transcribe(str(ogg_path))
        transcribe_time = time.time() - start_time
        
        transcript = result.get("text", "").strip()
        language = result.get("language", "unknown")
        
        if not transcript:
            await status_msg.edit_text(
                f"🎙️ Voice ({duration}s) — no speech detected"
            )
            return
        
        # Update media record with transcript
        try:
            conn = get_db_conn()
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("""
                UPDATE media_files 
                SET extracted_text = %s, processed = true, processed_at = NOW(),
                    analysis_data = analysis_data || %s
                WHERE telegram_file_unique_id = %s
            """, (
                transcript,
                json.dumps({
                    "language": language,
                    "transcribe_time_ms": int(transcribe_time * 1000),
                    "segments": result.get("segments", []),
                }),
                voice.file_unique_id
            ))
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to update media with transcript: {e}")
        
        # Update status
        await status_msg.edit_text(
            f"🎙️ Voice ({duration}s) → transcribed in {transcribe_time:.1f}s\n\n"
            f"📝 \"{transcript[:200]}{'...' if len(transcript) > 200 else ''}\"\n\n"
            f"Sending to Iris..."
        )
        
        # Send transcript to Iris via API (as if user typed it)
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{API_URL}/message",
                    json={
                        "user_id": str(telegram_id),
                        "message": f"[Voice message, {duration}s]: {transcript}",
                        "mode": "chat",
                    },
                    headers={"X-API-Key": API_KEY}
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    iris_response = data.get("response", "")
                    
                    # Send Iris's response
                    await status_msg.edit_text(
                        f"🎙️ \"{transcript[:150]}{'...' if len(transcript) > 150 else ''}\""
                    )
                    await update.message.reply_text(iris_response)
                else:
                    await status_msg.edit_text(
                        f"🎙️ Transcribed ({duration}s):\n\n\"{transcript}\"\n\n"
                        f"⚠️ Iris unavailable (API {resp.status_code})"
                    )
        except Exception as e:
            logger.error(f"API call failed: {e}")
            await status_msg.edit_text(
                f"🎙️ Transcribed ({duration}s):\n\n\"{transcript}\"\n\n"
                f"⚠️ Could not reach Iris"
            )
    
    except Exception as e:
        logger.error(f"Voice handling error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Voice processing failed: {str(e)[:100]}")


async def handle_audio(update, context):
    """
    Handle audio files (not voice messages) from Telegram.
    These are music/audio documents, not voice recordings.
    Same pipeline: download → save → transcribe → Iris.
    """
    telegram_id = update.effective_user.id
    user_uuid = get_user_uuid(telegram_id)
    
    if not user_uuid:
        await update.message.reply_text("❌ User not recognized")
        return
    
    audio = update.message.audio
    if not audio:
        return
    
    duration = audio.duration or 0
    file_size = audio.file_size or 0
    mime_type = audio.mime_type or "audio/mpeg"
    original_filename = audio.file_name or "audio"
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    status_msg = await update.message.reply_text(
        f"🎵 Audio received ({duration}s) — transcribing..."
    )
    
    try:
        file = await context.bot.get_file(audio.file_id)
        
        user_media_dir = MEDIA_BASE / user_uuid
        user_media_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = Path(original_filename).suffix or '.mp3'
        audio_filename = f"audio_{timestamp}_{audio.file_unique_id[:8]}{ext}"
        audio_path = user_media_dir / audio_filename
        
        await file.download_to_drive(str(audio_path))
        
        save_media_record(
            user_uuid=user_uuid,
            filename=audio_filename,
            file_path=str(audio_path),
            file_size=file_size,
            mime_type=mime_type,
            media_type="audio",
            telegram_file_id=audio.file_id,
            telegram_file_unique_id=audio.file_unique_id,
            analysis_data={"duration": duration, "type": "audio_file", "original_name": original_filename}
        )
        
        # Transcribe
        start_time = time.time()
        ts = get_transcription_service()
        result = ts.transcribe(str(audio_path))
        transcribe_time = time.time() - start_time
        
        transcript = result.get("text", "").strip()
        
        if transcript:
            await status_msg.edit_text(
                f"🎵 Audio ({duration}s) → transcribed in {transcribe_time:.1f}s\n\n"
                f"📝 \"{transcript[:300]}{'...' if len(transcript) > 300 else ''}\""
            )
        else:
            await status_msg.edit_text(
                f"🎵 Audio ({duration}s) — saved, no speech detected"
            )
    
    except Exception as e:
        logger.error(f"Audio handling error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Audio processing failed: {str(e)[:100]}")
