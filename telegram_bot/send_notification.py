#!/usr/bin/env python3
"""
Mythos Telegram Bot - Send Notification
/opt/mythos/telegram_bot/send_notification.py

Standalone script to send a Telegram notification to Ka'tuar'el.
Used by patch monitor and other services.

Usage:
    python send_notification.py "Your message here"
    python send_notification.py --chat_id 123456 "Message to specific chat"
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

logger = logging.getLogger(__name__)

# Default chat ID - Ka'tuar'el's Telegram
DEFAULT_CHAT_ID = os.getenv('TELEGRAM_ADMIN_CHAT_ID', '')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')


async def send_message(text: str, chat_id: str = None):
    """Send a message via the Telegram Bot API"""
    import httpx

    token = BOT_TOKEN
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in environment")
        sys.exit(1)

    target_chat = chat_id or DEFAULT_CHAT_ID
    if not target_chat:
        print("ERROR: No chat_id provided and TELEGRAM_ADMIN_CHAT_ID not set")
        sys.exit(1)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": target_chat,
        "text": text,
        "parse_mode": "Markdown",
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                print(f"✓ Notification sent to {target_chat}")
            else:
                # Retry without parse_mode in case of formatting issues
                payload.pop("parse_mode", None)
                resp2 = await client.post(url, json=payload, timeout=30)
                if resp2.status_code == 200:
                    print(f"✓ Notification sent (plain text) to {target_chat}")
                else:
                    print(f"✗ Failed: {resp2.status_code} {resp2.text}")
        except Exception as e:
            print(f"✗ Send failed: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Send Telegram notification")
    parser.add_argument("message", help="Message text to send")
    parser.add_argument("--chat_id", help="Target chat ID (default: admin)", default=None)
    args = parser.parse_args()

    asyncio.run(send_message(args.message, args.chat_id))


if __name__ == "__main__":
    main()
