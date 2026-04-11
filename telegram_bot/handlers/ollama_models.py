#!/usr/bin/env python3
"""
Ollama Model Manager — Telegram Handler

Commands:
    /models              — List all pulled models with sizes and which is active
    /pull <model>        — Pull a new model in background (non-blocking)
    /setmodel <model>    — Set active model for Iris conversations
    /pulling             — Check status of any active pull operations
    /removemodel <model> — Remove a pulled model

Pulls run as background asyncio tasks so Iris remains fully responsive.
"""

import os
import asyncio
import logging
import time
from datetime import datetime
from typing import Optional, Dict

import httpx

logger = logging.getLogger(__name__)

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')

# ── Global state ────────────────────────────────────────────────────────────

# Active pull operations: { model_name: { status, started, progress, error } }
ACTIVE_PULLS: Dict[str, dict] = {}

# Model override per user: { telegram_id: "exact_model_name" }
# Persisted to file so API process can read it too
USER_MODEL_OVERRIDE: Dict[int, Optional[str]] = {}
OVERRIDE_FILE = "/opt/mythos/.model_overrides.json"


def _save_overrides():
    """Persist overrides to file for cross-process access"""
    try:
        import json
        # Convert int keys to strings for JSON
        data = {str(k): v for k, v in USER_MODEL_OVERRIDE.items()}
        with open(OVERRIDE_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Failed to save overrides: {e}")


def _load_overrides():
    """Load overrides from file"""
    global USER_MODEL_OVERRIDE
    try:
        import json
        if os.path.exists(OVERRIDE_FILE):
            with open(OVERRIDE_FILE, "r") as f:
                data = json.load(f)
            USER_MODEL_OVERRIDE = {int(k): v for k, v in data.items()}
    except Exception as e:
        logger.error(f"Failed to load overrides: {e}")


# Load on import
_load_overrides()


# ── Ollama API helpers ──────────────────────────────────────────────────────

async def ollama_list_models() -> list:
    """Get all pulled models from Ollama API"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{OLLAMA_HOST}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return data.get("models", [])
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return []


async def ollama_model_exists(model_name: str) -> bool:
    """Check if a model is already pulled"""
    models = await ollama_list_models()
    names = [m["name"] for m in models]
    # Check exact match and also without tag (e.g. 'llama3.2:3b' matches 'llama3.2:3b')
    return model_name in names or f"{model_name}:latest" in names


def format_size(size_bytes: int) -> str:
    """Format byte count to human readable"""
    if size_bytes >= 1_000_000_000:
        return f"{size_bytes / 1_000_000_000:.1f} GB"
    elif size_bytes >= 1_000_000:
        return f"{size_bytes / 1_000_000:.0f} MB"
    else:
        return f"{size_bytes / 1_000:.0f} KB"


# ── Background pull task ────────────────────────────────────────────────────

async def _pull_model_background(model_name: str, telegram_id: int, bot):
    """
    Pull a model in the background using streaming API.
    Updates ACTIVE_PULLS with progress. Sends Telegram notification on complete.
    """
    ACTIVE_PULLS[model_name] = {
        "status": "pulling",
        "started": datetime.now().isoformat(),
        "progress": "starting...",
        "percent": 0,
        "error": None,
        "requested_by": telegram_id,
    }

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(None)) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_HOST}/api/pull",
                json={"name": model_name, "stream": True},
            ) as response:
                last_update = 0
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        import json
                        data = json.loads(line)
                    except Exception:
                        continue

                    status = data.get("status", "")

                    # Track download progress
                    total = data.get("total", 0)
                    completed = data.get("completed", 0)
                    if total > 0:
                        pct = int(completed / total * 100)
                        ACTIVE_PULLS[model_name]["percent"] = pct
                        ACTIVE_PULLS[model_name]["progress"] = (
                            f"{status} — {format_size(completed)}/{format_size(total)} ({pct}%)"
                        )
                    else:
                        ACTIVE_PULLS[model_name]["progress"] = status

                    # Log periodically (every 10 seconds)
                    now = time.time()
                    if now - last_update > 10:
                        logger.info(f"Pull {model_name}: {ACTIVE_PULLS[model_name]['progress']}")
                        last_update = now

        # Done
        ACTIVE_PULLS[model_name]["status"] = "complete"
        ACTIVE_PULLS[model_name]["progress"] = "✅ Ready to use"
        ACTIVE_PULLS[model_name]["percent"] = 100

        logger.info(f"Pull complete: {model_name}")

        # Notify user via Telegram
        try:
            await bot.send_message(
                chat_id=telegram_id,
                text=(
                    f"✅ <b>{model_name}</b> pulled successfully!\n\n"
                    f"Set it active with:\n<code>/setmodel {model_name}</code>"
                ),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Failed to send pull notification: {e}")

    except Exception as e:
        ACTIVE_PULLS[model_name]["status"] = "error"
        ACTIVE_PULLS[model_name]["error"] = str(e)
        ACTIVE_PULLS[model_name]["progress"] = f"❌ {e}"
        logger.error(f"Pull failed for {model_name}: {e}")

        try:
            await bot.send_message(
                chat_id=telegram_id,
                text=f"❌ Failed to pull <b>{model_name}</b>:\n<code>{e}</code>",
                parse_mode="HTML",
            )
        except Exception:
            pass


# ── Command handlers ────────────────────────────────────────────────────────

async def models_command(update, context):
    """
    /models — List all pulled Ollama models
    Shows name, parameter size, quantization, disk size, and which is active.
    """
    models = await ollama_list_models()

    if not models:
        await update.message.reply_text("❌ No models found (is Ollama running?)")
        return

    telegram_id = update.effective_user.id
    override = USER_MODEL_OVERRIDE.get(telegram_id)
    env_default = os.getenv("OLLAMA_MODEL", "iris-deep:latest")

    lines = ["🤖 Ollama Models", ""]

    for m in sorted(models, key=lambda x: x["name"]):
        name = m["name"]
        details = m.get("details", {})
        param_size = details.get("parameter_size", "?")
        quant = details.get("quantization_level", "?")
        size = format_size(m.get("size", 0))
        families = details.get("families", [])

        # Active indicator
        if override and name == override:
            indicator = " ⚡ ACTIVE"
        elif not override and name == env_default:
            indicator = " ⚡ DEFAULT"
        else:
            indicator = ""

        vision = " 👁" if "clip" in families else ""

        lines.append(f"  {name}{vision}{indicator}")
        lines.append(f"    {param_size} | {quant} | {size}")

    lines.append("")
    lines.append(f"Default: {env_default}")
    if override:
        lines.append(f"Override: {override}")
    lines.append("")
    lines.append("/setmodel <name> to switch")
    lines.append("/pull <name> to download new")

    await update.message.reply_text("\n".join(lines))


async def pull_command(update, context):
    """
    /pull <model_name> — Pull a model from Ollama registry in background
    Non-blocking: Iris stays responsive during download.
    """
    if not context.args:
        await update.message.reply_text(
            "Usage: `/pull <model_name><code>\n\n"
            "Examples:\n"
            "</code>/pull mistral:7b<code>\n"
            "</code>/pull gemma2:9b<code>\n"
            "</code>/pull phi3:medium<code>\n"
            "</code>/pull deepseek-r1:14b`",
            parse_mode="HTML",
        )
        return

    model_name = context.args[0].strip()
    telegram_id = update.effective_user.id

    # Check if already being pulled
    if model_name in ACTIVE_PULLS and ACTIVE_PULLS[model_name]["status"] == "pulling":
        progress = ACTIVE_PULLS[model_name]["progress"]
        await update.message.reply_text(
            f"⏳ <b>{model_name}</b> is already being pulled.\n\n"
            f"Progress: {progress}\n\n"
            "Use <code>/pulling</code> to check status.",
            parse_mode="HTML",
        )
        return

    # Check if already pulled
    if await ollama_model_exists(model_name):
        await update.message.reply_text(
            f"✅ <b>{model_name}</b> is already pulled.\n\n"
            f"Use <code>/setmodel {model_name}</code> to make it active.",
            parse_mode="HTML",
        )
        return

    # Start background pull
    bot = context.bot
    asyncio.create_task(_pull_model_background(model_name, telegram_id, bot))

    await update.message.reply_text(
        f"⬇️ Pulling <b>{model_name}</b> in background...\n\n"
        "Iris stays responsive — keep chatting.\n"
        "Use <code>/pulling</code> to check progress.\n"
        "You'll get a notification when it's done.",
        parse_mode="HTML",
    )


async def pulling_command(update, context):
    """
    /pulling — Show status of all active/recent pull operations
    """
    if not ACTIVE_PULLS:
        await update.message.reply_text("No pull operations in progress or recent history.")
        return

    lines = ["📦 <b>Pull Status</b>\n"]

    for model_name, info in ACTIVE_PULLS.items():
        status = info["status"]
        progress = info["progress"]
        started = info.get("started", "?")

        if status == "pulling":
            pct = info.get("percent", 0)
            bar_len = 10
            filled = int(bar_len * pct / 100) if pct else 0
            bar = "█" * filled + "░" * (bar_len - filled)
            lines.append(f"⬇️ <code>{model_name}</code>")
            lines.append(f"  [{bar}] {pct}%")
            lines.append(f"  {progress}")
        elif status == "complete":
            lines.append(f"✅ <code>{model_name}</code> — ready")
        elif status == "error":
            error = info.get("error", "unknown")
            lines.append(f"❌ <code>{model_name}</code> — failed")
            lines.append(f"  {error[:80]}")

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def setmodel_command(update, context):
    """
    /setmodel <model_name> — Set the active model for Iris chat
    /setmodel reset — Clear override and use env default
    """
    telegram_id = update.effective_user.id

    if not context.args:
        override = USER_MODEL_OVERRIDE.get(telegram_id)
        env_default = os.getenv("OLLAMA_MODEL", "iris-deep:latest")
        current = override if override else env_default

        await update.message.reply_text(
            f"Current model: <code>{current}</code>\n"
            + (f"_(override active)_\n" if override else f"_(env default)_\n")
            + f"\nUsage: `/setmodel <model_name><code>\n"
            f"</code>/setmodel reset<code> to clear override\n\n"
            f"Use </code>/models<code> to see available models.",
            parse_mode="HTML",
        )
        return

    model_name = context.args[0].strip()

    # Handle reset
    if model_name.lower() == "reset":
        if telegram_id in USER_MODEL_OVERRIDE:
            del USER_MODEL_OVERRIDE[telegram_id]
        _save_overrides()
        env_default = os.getenv("OLLAMA_MODEL", "iris-deep:latest")
        await update.message.reply_text(
            f"🔄 Override cleared. Using default: </code>{env_default}<code>",
            parse_mode="HTML",
        )
        return

    # Resolve short aliases
    if model_name.lower() in MODEL_ALIASES:
        resolved = MODEL_ALIASES[model_name.lower()]
        await update.message.reply_text(
            f"\u2699\ufe0f {model_name} \u2192 <code>{resolved}</code>",
            parse_mode="HTML",
        )
        model_name = resolved

    # Check if it's one of the old aliases
    if model_name in ("auto", "fast", "deep"):
        from handlers.chat_mode import MODEL_MAP
        resolved = MODEL_MAP.get(model_name, os.getenv("OLLAMA_MODEL", "iris-deep:latest"))
        await update.message.reply_text(
            f"ℹ️ </code>{model_name}<code> → </code>{resolved}<code>\n\n"
            f"Setting to </code>{resolved}<code>. Use exact model names with </code>/setmodel<code>.\n"
            f"Use </code>/models` to see all options.",
            parse_mode="HTML",
        )
        model_name = resolved

    # Verify model exists locally
    if not await ollama_model_exists(model_name):
        await update.message.reply_text(
            f"❌ <b>{model_name}</b> is not pulled.\n\n"
            f"Pull it first: <code>/pull {model_name}</code>\n"
            f"Or use <code>/models</code> to see what's available.",
            parse_mode="HTML",
        )
        return

    USER_MODEL_OVERRIDE[telegram_id] = model_name
    _save_overrides()
    await update.message.reply_text(
        f"⚡ Active model set to <code>{model_name}</code>\n\n"
        f"All Iris conversations now use this model.\n"
        f"<code>/setmodel reset</code> to go back to default.",
        parse_mode="HTML",
    )


async def removemodel_command(update, context):
    """
    /removemodel <model_name> — Delete a pulled model from Ollama
    """
    if not context.args:
        await update.message.reply_text(
            "Usage: `/removemodel <model_name><code>\n\n"
            "Use </code>/models<code> to see pulled models.",
            parse_mode="HTML",
        )
        return

    model_name = context.args[0].strip()
    env_default = os.getenv("OLLAMA_MODEL", "iris-deep:latest")

    # Don't allow removing the active default
    if model_name == env_default:
        await update.message.reply_text(
            f"⚠️ Can't remove </code>{model_name}<code> — it's the system default.\n"
            f"Change OLLAMA_MODEL in .env first.",
            parse_mode="HTML",
        )
        return

    # Check if it exists
    if not await ollama_model_exists(model_name):
        await update.message.reply_text(f"❌ </code>{model_name}<code> is not pulled.", parse_mode="HTML")
        return

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.delete(
                f"{OLLAMA_HOST}/api/delete",
                json={"name": model_name},
            )
            if resp.status_code == 200:
                # Clear any user overrides pointing to this model
                for uid, override in list(USER_MODEL_OVERRIDE.items()):
                    if override == model_name:
                        del USER_MODEL_OVERRIDE[uid]
                _save_overrides()

                await update.message.reply_text(
                    f"🗑️ </code>{model_name}<code> removed.\n\nUse </code>/models<code> to see remaining.",
                    parse_mode="HTML",
                )
            else:
                await update.message.reply_text(
                    f"❌ Failed to remove: HTTP {resp.status_code}\n</code>{resp.text[:200]}`",
                    parse_mode="HTML",
                )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


# ── Integration helper ──────────────────────────────────────────────────────

def get_active_model(telegram_id: int) -> str:
    """
    Get the active model for a user.
    Reads from file each time so it works cross-process (bot + API).
    """
    try:
        import json
        if os.path.exists(OVERRIDE_FILE):
            with open(OVERRIDE_FILE, "r") as f:
                data = json.load(f)
            override = data.get(str(telegram_id))
            if override:
                return override
    except Exception:
        pass
    return os.getenv("OLLAMA_MODEL", "iris-deep:latest")


# ── Short aliases — imported from single source of truth ────────────────────
from core.model_aliases import MODEL_ALIASES
