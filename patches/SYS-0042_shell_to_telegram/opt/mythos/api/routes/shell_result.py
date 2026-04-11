"""
shell_result.py — SYS-0042
Receives command output from the iOS Shell-to-Telegram shortcut
and routes it to Iris via Telegram.
"""
import os
import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
import httpx

logger = logging.getLogger(__name__)
router = APIRouter()

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
SHELL_API_KEY = os.environ.get('SHELL_API_KEY', '')
# Default recipient — Ka'tuar'el's Telegram ID (set in .env or falls back)
DEFAULT_TELEGRAM_ID = os.environ.get('ADGE_TELEGRAM_ID', '')


class ShellResult(BaseModel):
    cmd: str           # The command that was run
    output: str        # stdout + stderr combined
    exit_code: int = 0
    label: str = ""    # Optional human label e.g. "Neo4j diagnostic"


@router.post("/shell-result")
async def receive_shell_result(payload: ShellResult, request: Request):
    """
    Receive command output from iOS Shortcut and forward to Telegram.
    Requires X-API-Key header matching SHELL_API_KEY env var.
    """
    # Auth check
    api_key = request.headers.get('X-API-Key', '')
    if SHELL_API_KEY and api_key != SHELL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if not TELEGRAM_BOT_TOKEN or not DEFAULT_TELEGRAM_ID:
        raise HTTPException(status_code=500, detail="Telegram not configured")

    # Format the message
    label = payload.label or payload.cmd[:60]
    status = "✅" if payload.exit_code == 0 else "❌"
    output = payload.output.strip()

    # Truncate if too long for Telegram (4096 char limit)
    max_output = 3500
    truncated = ""
    if len(output) > max_output:
        output = output[:max_output]
        truncated = "\n\n_[output truncated]_"

    message = (
        f"{status} *Shell Result*\n"
        f"`{label}`\n\n"
        f"```\n{output}\n```"
        f"{truncated}"
    )

    # Send to Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json={
            "chat_id": DEFAULT_TELEGRAM_ID,
            "text": message,
            "parse_mode": "Markdown"
        })

    if resp.status_code != 200:
        logger.error(f"Telegram send failed: {resp.text}")
        raise HTTPException(status_code=502, detail="Telegram delivery failed")

    logger.info(f"Shell result delivered — cmd={payload.cmd[:50]} exit={payload.exit_code}")
    return {"status": "delivered", "telegram_id": DEFAULT_TELEGRAM_ID}


@router.get("/shell-result/ping")
async def ping():
    """Health check for the shell result endpoint."""
    return {"status": "ok", "endpoint": "shell-result"}
