#!/usr/bin/env python3
"""
Media Handler for Mythos Telegram Bot

Handles photos, videos, and video notes from Telegram:
- Photos: Save → vision analysis (llava) → description to Iris
- Videos: Save → extract audio → transcribe → send to Iris
- Video notes (round videos): Same as video

The Thronescribe capture pipeline — all media to memory.
"""

import os
import json
import time
import logging
import subprocess
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
VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava:13b")

# DB config
DB_HOST = os.getenv('POSTGRES_HOST', '/var/run/postgresql')
DB_NAME = os.getenv('POSTGRES_DB', 'mythos')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASS = os.getenv('POSTGRES_PASSWORD', '')


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
                      width=None, height=None, analysis_data=None):
    """Save a media file record to the database"""
    try:
        conn = get_db_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO media_files 
            (user_uuid, filename, file_path, file_size_bytes, mime_type, 
             media_type, telegram_file_id, telegram_file_unique_id,
             width, height, analysis_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (telegram_file_unique_id) DO NOTHING
            RETURNING id
        """, (
            user_uuid, filename, file_path, file_size, mime_type,
            media_type, telegram_file_id, telegram_file_unique_id,
            width, height,
            json.dumps(analysis_data) if analysis_data else None
        ))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return str(row[0]) if row else None
    except Exception as e:
        logger.error(f"Failed to save media record: {e}")
        return None


def update_media_analysis(telegram_file_unique_id, extracted_text=None, analysis_data_update=None):
    """Update media record with analysis results"""
    try:
        conn = get_db_conn()
        conn.autocommit = True
        cur = conn.cursor()
        if extracted_text and analysis_data_update:
            cur.execute("""
                UPDATE media_files 
                SET extracted_text = %s, processed = true, processed_at = NOW(),
                    analysis_data = COALESCE(analysis_data, '{}'::jsonb) || %s
                WHERE telegram_file_unique_id = %s
            """, (extracted_text, json.dumps(analysis_data_update), telegram_file_unique_id))
        elif extracted_text:
            cur.execute("""
                UPDATE media_files 
                SET extracted_text = %s, processed = true, processed_at = NOW()
                WHERE telegram_file_unique_id = %s
            """, (extracted_text, telegram_file_unique_id))
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to update media analysis: {e}")


async def send_to_iris(telegram_id, message):
    """Send a message to Iris via API and return response"""
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{API_URL}/message",
                json={
                    "user_id": str(telegram_id),
                    "message": message,
                    "mode": "chat",
                },
                headers={"X-API-Key": API_KEY}
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
    except Exception as e:
        logger.error(f"Iris API call failed: {e}")
    return None


async def describe_image(image_path: str) -> str:
    """Use llava to describe an image"""
    try:
        from vision import analyze_image_async
        from vision.prompts.journal import MEMORY_CAPTURE
        
        result = await analyze_image_async(
            image_path,
            prompt=MEMORY_CAPTURE,
            model=VISION_MODEL,
            response_format="text",
            timeout=60
        )
        return result if isinstance(result, str) else str(result)
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        return None


def extract_audio_from_video(video_path: str, output_path: str = None) -> Optional[str]:
    """Extract audio track from video file using ffmpeg"""
    if output_path is None:
        output_path = video_path.rsplit('.', 1)[0] + '.wav'
    
    try:
        result = subprocess.run(
            [
                'ffmpeg', '-y', '-i', video_path,
                '-ar', '16000', '-ac', '1',
                '-c:a', 'pcm_s16le',
                output_path
            ],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            return output_path
        logger.error(f"ffmpeg audio extraction failed: {result.stderr[:200]}")
    except Exception as e:
        logger.error(f"Audio extraction error: {e}")
    return None


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
            capture_output=True, text=True, timeout=10
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


# ═══════════════════════════════════════════════════════════════════
# PHOTO HANDLER (replaces existing handle_photo for chat mode)
# ═══════════════════════════════════════════════════════════════════

async def handle_photo_media(update, context):
    """
    Handle photos in chat mode:
    1. Download and save
    2. Run vision analysis (llava)
    3. Send description + caption to Iris
    4. Return Iris's response
    """
    telegram_id = update.effective_user.id
    user_uuid = get_user_uuid(telegram_id)
    
    if not user_uuid:
        await update.message.reply_text("❌ User not recognized")
        return
    
    if not update.message.photo:
        return
    
    photo = update.message.photo[-1]  # highest resolution
    caption = update.message.caption or ""
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    status_msg = await update.message.reply_text("📸 Processing image...")
    
    try:
        # Download
        file = await context.bot.get_file(photo.file_id)
        user_media_dir = MEDIA_BASE / user_uuid
        user_media_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{timestamp}_{photo.file_unique_id[:8]}.jpg"
        file_path = user_media_dir / filename
        
        await file.download_to_drive(str(file_path))
        file_size = file_path.stat().st_size
        
        logger.info(f"Photo saved: {file_path} ({file_size} bytes, {photo.width}x{photo.height})")
        
        # Save to DB
        save_media_record(
            user_uuid=user_uuid,
            filename=filename,
            file_path=str(file_path),
            file_size=file_size,
            mime_type="image/jpeg",
            media_type="photo",
            telegram_file_id=photo.file_id,
            telegram_file_unique_id=photo.file_unique_id,
            width=photo.width,
            height=photo.height,
            analysis_data={"caption": caption} if caption else None
        )
        
        # Vision analysis
        await status_msg.edit_text("📸 Analyzing image with vision...")
        start_time = time.time()
        description = await describe_image(str(file_path))
        vision_time = time.time() - start_time
        
        if description:
            # Update DB with analysis
            update_media_analysis(
                photo.file_unique_id,
                extracted_text=description,
                analysis_data_update={
                    "vision_model": VISION_MODEL,
                    "vision_time_ms": int(vision_time * 1000),
                }
            )
            
            # Build message for Iris
            iris_message = f"[Photo received"
            if caption:
                iris_message += f", caption: \"{caption}\""
            iris_message += f"]\nVision description: {description}"
            
            await status_msg.edit_text(
                f"📸 Analyzed in {vision_time:.1f}s — sending to Iris..."
            )
            
            # Send to Iris
            iris_response = await send_to_iris(telegram_id, iris_message)
            
            if iris_response:
                await status_msg.edit_text(f"📸 Image logged ({file_size // 1024}KB)")
                await update.message.reply_text(iris_response)
            else:
                await status_msg.edit_text(
                    f"📸 Saved & analyzed ({file_size // 1024}KB)\n\n"
                    f"📝 {description[:300]}{'...' if len(description) > 300 else ''}"
                )
        else:
            await status_msg.edit_text(
                f"📸 Saved ({file_size // 1024}KB) — vision analysis unavailable"
            )
    
    except Exception as e:
        logger.error(f"Photo handling error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Photo processing failed: {str(e)[:100]}")


# ═══════════════════════════════════════════════════════════════════
# VIDEO HANDLER
# ═══════════════════════════════════════════════════════════════════

async def handle_video_media(update, context):
    """
    Handle video messages:
    1. Download and save
    2. Extract audio → transcribe with whisper
    3. Send transcript to Iris
    """
    telegram_id = update.effective_user.id
    user_uuid = get_user_uuid(telegram_id)
    
    if not user_uuid:
        await update.message.reply_text("❌ User not recognized")
        return
    
    # Handle both video and video_note (round videos)
    video = update.message.video or update.message.video_note
    if not video:
        return
    
    is_note = update.message.video_note is not None
    caption = update.message.caption or ""
    duration = video.duration or 0
    file_size = video.file_size or 0
    mime_type = getattr(video, 'mime_type', 'video/mp4') or 'video/mp4'
    width = getattr(video, 'width', None)
    height = getattr(video, 'height', None)
    
    media_label = "🎥 Video note" if is_note else "🎬 Video"
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    status_msg = await update.message.reply_text(
        f"{media_label} received ({duration}s, {file_size // 1024}KB) — processing..."
    )
    
    try:
        # Download
        file = await context.bot.get_file(video.file_id)
        user_media_dir = MEDIA_BASE / user_uuid
        user_media_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = '.mp4'
        prefix = "vidnote" if is_note else "video"
        filename = f"{prefix}_{timestamp}_{video.file_unique_id[:8]}{ext}"
        file_path = user_media_dir / filename
        
        await file.download_to_drive(str(file_path))
        actual_size = file_path.stat().st_size
        actual_duration = get_video_duration(str(file_path)) or duration
        
        logger.info(f"Video saved: {file_path} ({actual_size} bytes, {actual_duration:.1f}s)")
        
        # Save to DB
        save_media_record(
            user_uuid=user_uuid,
            filename=filename,
            file_path=str(file_path),
            file_size=actual_size,
            mime_type=mime_type,
            media_type="video",
            telegram_file_id=video.file_id,
            telegram_file_unique_id=video.file_unique_id,
            width=width,
            height=height,
            analysis_data={
                "duration": actual_duration,
                "type": "video_note" if is_note else "video",
                "caption": caption,
            }
        )
        
        # Extract audio and transcribe
        await status_msg.edit_text(f"{media_label} ({duration}s) — extracting audio...")
        
        wav_path = extract_audio_from_video(str(file_path))
        
        if wav_path and os.path.exists(wav_path):
            await status_msg.edit_text(f"{media_label} ({duration}s) — transcribing...")
            
            # Use the transcription service from voice handler
            from handlers.voice_handler import get_transcription_service
            
            start_time = time.time()
            ts = get_transcription_service()
            result = ts.transcribe(wav_path)
            transcribe_time = time.time() - start_time
            
            transcript = result.get("text", "").strip()
            language = result.get("language", "unknown")
            
            # Clean up wav
            try:
                os.remove(wav_path)
            except OSError:
                pass
            
            if transcript:
                # Update DB
                update_media_analysis(
                    video.file_unique_id,
                    extracted_text=transcript,
                    analysis_data_update={
                        "language": language,
                        "transcribe_time_ms": int(transcribe_time * 1000),
                    }
                )
                
                # Send to Iris
                iris_msg = f"[{media_label}, {duration}s"
                if caption:
                    iris_msg += f", caption: \"{caption}\""
                iris_msg += f"]: {transcript}"
                
                await status_msg.edit_text(
                    f"{media_label} ({duration}s) → transcribed in {transcribe_time:.1f}s\n\n"
                    f"📝 \"{transcript[:200]}{'...' if len(transcript) > 200 else ''}\"\n\n"
                    f"Sending to Iris..."
                )
                
                iris_response = await send_to_iris(telegram_id, iris_msg)
                
                if iris_response:
                    await status_msg.edit_text(
                        f"{media_label} logged ({actual_size // 1024}KB, {duration}s)\n"
                        f"📝 \"{transcript[:150]}{'...' if len(transcript) > 150 else ''}\""
                    )
                    await update.message.reply_text(iris_response)
                else:
                    await status_msg.edit_text(
                        f"{media_label} ({duration}s) — transcribed:\n\n"
                        f"📝 \"{transcript[:300]}{'...' if len(transcript) > 300 else ''}\""
                    )
            else:
                await status_msg.edit_text(
                    f"{media_label} saved ({actual_size // 1024}KB, {duration}s) — no speech detected"
                )
        else:
            await status_msg.edit_text(
                f"{media_label} saved ({actual_size // 1024}KB, {duration}s) — no audio track"
            )
    
    except Exception as e:
        logger.error(f"Video handling error: {e}", exc_info=True)
        await status_msg.edit_text(f"❌ Video processing failed: {str(e)[:100]}")
