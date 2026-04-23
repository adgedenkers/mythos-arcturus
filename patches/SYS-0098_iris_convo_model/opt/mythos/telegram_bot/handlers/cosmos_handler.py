#!/usr/bin/env python3
"""
Cosmos Mode Handler — /cosmos and /standard commands
SYS-0098

/cosmos   — Switch to iris:cosmos-deep (full spiritual framework)
/standard — Switch back to iris:convo (default technical partner)

These are convenience wrappers around the /setmodel mechanism.
"""
import logging
from handlers.ollama_models import (
    USER_MODEL_OVERRIDE,
    _save_overrides,
    ollama_model_exists,
)

logger = logging.getLogger(__name__)

COSMOS_MODEL = "iris:cosmos-deep"
CONVO_MODEL = "iris:convo"


async def cosmos_command(update, context):
    """/cosmos — Switch to full spiritual framework model."""
    telegram_id = update.effective_user.id

    # Verify the cosmos model exists
    if not await ollama_model_exists(COSMOS_MODEL):
        await update.message.reply_text(
            f"❌ {COSMOS_MODEL} is not available. "
            f"Check that the model has been built."
        )
        return

    USER_MODEL_OVERRIDE[telegram_id] = COSMOS_MODEL
    _save_overrides()

    await update.message.reply_text(
        f"🌌 Cosmos mode active — using {COSMOS_MODEL}\n\n"
        f"/standard to switch back."
    )
    logger.info(f"User {telegram_id} switched to cosmos mode ({COSMOS_MODEL})")


async def standard_command(update, context):
    """/standard — Switch back to default technical partner model."""
    telegram_id = update.effective_user.id

    # Clear override — falls back to env default (iris:convo)
    if telegram_id in USER_MODEL_OVERRIDE:
        del USER_MODEL_OVERRIDE[telegram_id]
    _save_overrides()

    await update.message.reply_text(
        f"⚡ Standard mode — using default ({CONVO_MODEL})\n\n"
        f"/cosmos to switch to full framework."
    )
    logger.info(f"User {telegram_id} switched to standard mode (default)")
