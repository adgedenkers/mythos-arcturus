#!/usr/bin/env python3
"""
Conversation Engine — Telegram Formatter
==========================================
Renders Response objects as Telegram HTML messages.

LOG-0018: Foundation deploy.
"""
import json
from typing import Any

from ..response.response import Response


class TelegramFormatter:
    """Format Response objects for Telegram (HTML parse mode)."""

    def format(self, response: Response) -> str:
        match response.type:
            case "text":
                return response.content or ""

            case "card":
                lines = [f"<b>{response.title}</b>"]
                for k, v in (response.fields or {}).items():
                    lines.append(f"  {k}: {v}")
                if response.footer:
                    lines.append(f"\n<i>{response.footer}</i>")
                return "\n".join(lines)

            case "table":
                if not response.headers or not response.rows:
                    return "(empty table)"
                header = " | ".join(response.headers)
                sep = "─" * len(header)
                rows = "\n".join(" | ".join(row) for row in response.rows)
                return f"<pre>{header}\n{sep}\n{rows}</pre>"

            case "error":
                msg = f"⚠️ {response.content}"
                if response.footer:
                    msg += f"\n<i>{response.footer}</i>"
                return msg

            case "chain_result":
                if response.content:
                    return response.content
                if response.data:
                    return f"<pre>{json.dumps(response.data, indent=2)[:3000]}</pre>"
                return "(no result)"

            case _:
                return str(response.content or "")
