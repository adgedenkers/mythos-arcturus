#!/usr/bin/env python3
"""
Conversation Engine — Response System
=======================================
One Response class for all output. Channel formatters render it
appropriately for Telegram, REST API, voice, etc.

LOG-0018: Foundation deploy.
"""
import json
from typing import Any, Optional

from pydantic import BaseModel, Field


class Response(BaseModel):
    """Unified response object. One class for every output path."""

    type: str = Field(description="text, card, table, error, chain_result")
    content: Optional[str] = None
    title: Optional[str] = None
    fields: Optional[dict[str, str]] = None
    headers: Optional[list[str]] = None
    rows: Optional[list[list[str]]] = None
    data: Optional[dict[str, Any]] = None
    footer: Optional[str] = None

    # ── Factory methods ──────────────────────────────────────────────────

    @classmethod
    def text(cls, content: str) -> "Response":
        return cls(type="text", content=content)

    @classmethod
    def card(cls, title: str, fields: dict[str, str], footer: str | None = None) -> "Response":
        return cls(type="card", title=title, fields=fields, footer=footer)

    @classmethod
    def table(cls, headers: list[str], rows: list[list[str]]) -> "Response":
        return cls(type="table", headers=headers, rows=rows)

    @classmethod
    def error(cls, message: str, details: str | None = None) -> "Response":
        return cls(type="error", content=message, footer=details)

    @classmethod
    def chain_result(cls, data: dict, summary: str | None = None) -> "Response":
        return cls(type="chain_result", data=data, content=summary)
