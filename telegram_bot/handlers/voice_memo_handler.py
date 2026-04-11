#!/usr/bin/env python3
"""
Voice Memo Handler for Mythos Telegram Bot

Commands for querying the voice memo transcription pipeline:
  /voice        — List last 5 voice memos
  /voice <id>   — Show full diarized transcript for a memo
  /voice search <term> — Full-text search across transcripts

Queries the voice_memos table (pipeline DB from patches 0112-0113).
This is SEPARATE from voice_handler.py which handles inline Telegram
voice messages. This handler queries the API-uploaded voice memo archive.
"""
import os
import logging
from datetime import datetime
from typing import Optional

import psycopg2
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger(__name__)

# DB config
DB_HOST = os.getenv('POSTGRES_HOST', '/var/run/postgresql')
DB_NAME = os.getenv('POSTGRES_DB', 'mythos')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASS = os.getenv('POSTGRES_PASSWORD', '')


def get_db_conn():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME,
        user=DB_USER, password=DB_PASS
    )


def format_duration(seconds: Optional[float]) -> str:
    """Format seconds into human-readable duration."""
    if not seconds:
        return "?"
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m{s:02d}s"
    else:
        h, remainder = divmod(seconds, 3600)
        m, s = divmod(remainder, 60)
        return f"{h}h{m:02d}m"


def format_timestamp(ts) -> str:
    """Format a datetime/timestamp for display."""
    if not ts:
        return "?"
    if isinstance(ts, str):
        try:
            ts = datetime.fromisoformat(ts)
        except (ValueError, TypeError):
            return str(ts)[:16]
    try:
        return ts.strftime("%b %d %I:%M %p")
    except Exception:
        return str(ts)[:16]


async def handle_voice_memos(update, context):
    """
    /voice — List recent voice memos
    /voice <id> — Show transcript for a specific memo
    /voice search <term> — Search transcripts
    """
    args = context.args if context.args else []

    # Route to subcommand
    if not args:
        await _list_memos(update)
    elif args[0].lower() == 'search' and len(args) > 1:
        search_term = ' '.join(args[1:])
        await _search_memos(update, search_term)
    elif args[0].isdigit():
        memo_id = int(args[0])
        await _show_transcript(update, memo_id)
    else:
        await update.message.reply_text(
            "📼 Voice Memo Commands\n\n"
            "/voice — List last 5 memos\n"
            "/voice <id> — Show transcript\n"
            "/voice search <term> — Search transcripts"
        )


async def _list_memos(update):
    """List the last 5 voice memos with status."""
    try:
        conn = get_db_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""
            SELECT id, filename, status, duration_seconds, speaker_count,
                   created_at, LEFT(transcript_full, 100) as preview
            FROM voice_memos
            ORDER BY created_at DESC
            LIMIT 5
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            await update.message.reply_text("📼 No voice memos found.")
            return

        lines = ["📼 Recent Voice Memos\n"]
        for row in rows:
            memo_id, filename, status, duration, speakers, created, preview = row

            # Status emoji
            status_icon = {
                'complete': '✅',
                'processing': '⏳',
                'pending': '🔄',
                'error': '❌'
            }.get(status, '❓')

            # Clean filename for display
            display_name = filename or "unknown"
            # Strip voice_ prefix and extension for cleaner display
            if display_name.startswith("voice_"):
                display_name = display_name[6:]
            # Remove extension
            if '.' in display_name:
                display_name = display_name.rsplit('.', 1)[0]
            # Truncate
            if len(display_name) > 35:
                display_name = display_name[:32] + "..."

            dur_str = format_duration(duration)
            spk_str = f"{speakers}spk" if speakers else ""
            time_str = format_timestamp(created)

            lines.append(
                f"{status_icon} #{memo_id} — {dur_str}"
                f"{' · ' + spk_str if spk_str else ''}\n"
                f"  {display_name}\n"
                f"  {time_str}"
            )

            # Show preview snippet if available
            if preview and status == 'complete':
                snippet = preview.strip().replace('\n', ' ')
                if len(snippet) > 80:
                    snippet = snippet[:77] + "..."
                lines.append(f'  "{snippet}"')
            lines.append("")

        lines.append("Use /voice <id> for full transcript")
        await update.message.reply_text('\n'.join(lines))

    except Exception as e:
        logger.error(f"Voice memo list failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Failed to list voice memos: {str(e)[:100]}")


async def _show_transcript(update, memo_id: int):
    """Show full transcript for a specific voice memo."""
    try:
        conn = get_db_conn()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""
            SELECT id, filename, status, duration_seconds, speaker_count,
                   transcript_full, transcript_diarized, created_at,
                   processing_times, error_message
            FROM voice_memos
            WHERE id = %s
        """, (memo_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            await update.message.reply_text(f"❌ Voice memo #{memo_id} not found.")
            return

        (mid, filename, status, duration, speakers,
         transcript, diarized, created, proc_times, error) = row

        dur_str = format_duration(duration)
        time_str = format_timestamp(created)

        # Header
        header = f"📼 Voice Memo #{mid}\n{filename}\n{time_str} · {dur_str}"
        if speakers:
            header += f" · {speakers} speaker{'s' if speakers > 1 else ''}"
        header += f"\nStatus: {status}"

        if status == 'error':
            await update.message.reply_text(
                f"{header}\n\n❌ Error: {error or 'unknown'}"
            )
            return

        if status != 'complete':
            await update.message.reply_text(
                f"{header}\n\n⏳ Transcription not yet complete."
            )
            return

        # Prefer diarized transcript if available, fall back to plain
        text = diarized if diarized else transcript
        if not text:
            await update.message.reply_text(f"{header}\n\n(No transcript text)")
            return

        # Processing stats
        stats = ""
        if proc_times and isinstance(proc_times, dict):
            whisper_t = proc_times.get('whisper_seconds')
            diar_t = proc_times.get('diarization_seconds')
            if whisper_t:
                stats += f"\n⚡ Whisper: {whisper_t:.1f}s"
            if diar_t:
                stats += f" · Diarize: {diar_t:.1f}s"

        # Telegram has a 4096 char limit per message
        full_msg = f"{header}{stats}\n\n{text}"

        if len(full_msg) <= 4096:
            await update.message.reply_text(full_msg)
        else:
            # Send header first, then transcript in chunks
            await update.message.reply_text(f"{header}{stats}\n\n📝 Transcript follows...")

            # Split text into ~4000 char chunks at word boundaries
            chunks = _split_text(text, 4000)
            for i, chunk in enumerate(chunks):
                prefix = f"[{i+1}/{len(chunks)}]\n" if len(chunks) > 1 else ""
                await update.message.reply_text(f"{prefix}{chunk}")

    except Exception as e:
        logger.error(f"Voice memo transcript failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Failed to get transcript: {str(e)[:100]}")


async def _search_memos(update, search_term: str):
    """Full-text search across voice memo transcripts."""
    try:
        conn = get_db_conn()
        conn.autocommit = True
        cur = conn.cursor()

        # Use the GIN full-text search index
        cur.execute("""
            SELECT id, filename, duration_seconds, speaker_count, created_at,
                   ts_headline('english', transcript_full,
                              plainto_tsquery('english', %s),
                              'StartSel=», StopSel=«, MaxWords=40, MinWords=15') as headline,
                   ts_rank(to_tsvector('english', transcript_full),
                          plainto_tsquery('english', %s)) as rank
            FROM voice_memos
            WHERE status = 'complete'
              AND transcript_full IS NOT NULL
              AND to_tsvector('english', transcript_full) @@ plainto_tsquery('english', %s)
            ORDER BY rank DESC
            LIMIT 5
        """, (search_term, search_term, search_term))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            await update.message.reply_text(
                f'📼 No results for "{search_term}" in voice memos.'
            )
            return

        lines = [f'📼 Search: "{search_term}" — {len(rows)} result{"s" if len(rows) != 1 else ""}\n']

        for row in rows:
            memo_id, filename, duration, speakers, created, headline, rank = row
            dur_str = format_duration(duration)
            time_str = format_timestamp(created)

            # Clean up headline markers for Telegram display
            snippet = (headline or "").strip().replace('\n', ' ')

            lines.append(
                f"#{memo_id} — {dur_str} · {time_str}\n"
                f"  {snippet}\n"
            )

        lines.append("Use /voice <id> for full transcript")
        await update.message.reply_text('\n'.join(lines))

    except Exception as e:
        logger.error(f"Voice memo search failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Search failed: {str(e)[:100]}")


def _split_text(text: str, max_len: int) -> list:
    """Split text into chunks at word boundaries."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break

        # Find last space before limit
        split_pos = text.rfind(' ', 0, max_len)
        if split_pos == -1:
            # No space found, force split
            split_pos = max_len

        chunks.append(text[:split_pos])
        text = text[split_pos:].lstrip()

    return chunks
