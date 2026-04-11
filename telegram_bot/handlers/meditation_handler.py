"""
Meditation Handler — Telegram interface for the meditation renderer.

Commands:
    /meditate              — show usage
    /meditate list         — list rendered meditations
    /meditate <title>      — prompt for script, then render
    /meditations           — alias for /meditate list

File workflow:
    Send a .txt attachment containing [pause:N] lines.
    Bot detects it, renders it, sends back OGG audio.

Pending-text workflow:
    /meditate Morning Grounding
    → bot asks for script text
    → user pastes script
    → bot renders and returns audio
"""

import os
import logging
import tempfile
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("/opt/mythos/public/meditations")

# telegram_id -> title, set when user starts /meditate <title> flow
_pending: dict = {}


async def meditate_command(update, context):
    args = context.args or []
    text = " ".join(args).strip()

    if not text or text.lower() in ("help", "?"):
        await update.message.reply_text(
            "🧘 *Iris Meditation Renderer*\n\n"
            "*Send a .txt script file* — Iris renders it to audio.\n\n"
            "*Script format:*\n"
            "```\n"
            "Find your seat. Take a breath.\n"
            "[pause:5]\n"
            "Feel the weight of your body...\n"
            "[pause:10]\n"
            "Allow yourself to arrive.\n"
            "```\n\n"
            "`[pause:N]` = N seconds of silence. Each other line = spoken text.\n\n"
            "*Commands:*\n"
            "`/meditate list` — list all rendered meditations\n"
            "`/meditate <title>` — I'll ask you for the script",
            parse_mode="Markdown",
        )
        return

    if text.lower() == "list":
        await _send_list(update)
        return

    # Start pending flow
    _pending[update.effective_user.id] = text
    await update.message.reply_text(
        f"📝 *{text}*\n\nSend me the script text now.",
        parse_mode="Markdown",
    )


async def meditations_command(update, context):
    await _send_list(update)


async def handle_meditation_document(update, context) -> bool:
    """
    Called from document handler. Returns True if we handled it.
    Handles .txt files that contain [pause:N] markers.
    """
    doc = update.message.document
    if not doc:
        return False
    if not (doc.file_name or "").lower().endswith(".txt"):
        return False

    try:
        file = await context.bot.get_file(doc.file_id)
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            await file.download_to_drive(tmp.name)
            script = Path(tmp.name).read_text(encoding="utf-8")
        os.unlink(tmp.name)
    except Exception as e:
        logger.error(f"Document download failed: {e}")
        return False

    import re
    if not re.search(r"\[pause:\d+", script):
        return False  # not a meditation script

    title = Path(doc.file_name).stem.replace("_", " ").replace("-", " ")
    await _render_and_send(update, context, script, title)
    return True


async def handle_pending_meditation_text(update, context) -> bool:
    """
    Called from the text handler. Consumes message if a meditation is pending.
    Returns True if consumed.
    """
    uid = update.effective_user.id
    if uid not in _pending:
        return False

    title = _pending.pop(uid)
    script = (update.message.text or "").strip()

    if not script:
        await update.message.reply_text("❌ No script received. Try `/meditate` again.")
        return True

    await _render_and_send(update, context, script, title)
    return True


async def _send_list(update):
    from voice.meditation import list_meditations
    items = list_meditations()
    if not items:
        await update.message.reply_text(
            "No meditations rendered yet.\n\n"
            "Send a `.txt` script file or use `/meditate <title>` to create one."
        )
        return
    lines = ["🧘 *Rendered Meditations*\n"]
    for m in items[:20]:
        lines.append(f"• *{m['title']}* — {m['size_kb']} KB ({m['created'][:10]})")
        lines.append(f"  `{m['filename']}`")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def _render_and_send(update, context, script: str, title: str):
    from voice.meditation import render_meditation, estimate_duration

    est = estimate_duration(script)
    status = await update.message.reply_text(
        f"🧘 Rendering *{title}*...\n"
        f"Estimated: {est/60:.1f} min — synthesizing each segment, won't be instant.",
        parse_mode="Markdown",
    )

    try:
        output_path = render_meditation(script, title=title, voice="af_heart")
    except Exception as e:
        logger.error(f"render_meditation raised: {e}", exc_info=True)
        await status.edit_text(f"❌ Render failed: {str(e)[:200]}")
        return

    if output_path is None:
        await status.edit_text("❌ Render failed — no output. Check Arcturus logs.")
        return

    size_kb = output_path.stat().st_size / 1024
    await status.edit_text(
        f"✅ *{title}* rendered — {size_kb:.0f} KB — sending...",
        parse_mode="Markdown",
    )

    try:
        with open(output_path, "rb") as f:
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=f,
                filename=output_path.name,
                title=title,
                performer="Iris · Arcturus",
                duration=int(est),
                caption=f"🧘 *{title}*\n`{output_path.name}`",
                parse_mode="Markdown",
            )
        await status.delete()
    except Exception as e:
        logger.error(f"send_audio failed: {e}", exc_info=True)
        await status.edit_text(
            f"✅ Rendered but couldn't send: {str(e)[:200]}\n\n"
            f"File at: `{output_path}`",
            parse_mode="Markdown",
        )
