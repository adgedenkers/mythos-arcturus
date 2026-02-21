"""
Mythos Context Handler — Telegram /context command
====================================================
Dumps TODO.md + ARCHITECTURE.md + BUILD_PROTOCOL.md
formatted for pasting into a new Claude conversation.

Usage:
  /context        — All three docs
  /context todo   — Just TODO.md
  /context arch   — Just ARCHITECTURE.md
  /context build  — Just BUILD_PROTOCOL.md
"""

import os
import tempfile
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes


DOCS_DIR = "/opt/mythos/docs"

DOC_FILES = {
    "todo":  ("TODO.md", "TODO.md"),
    "arch":  ("ARCHITECTURE.md", "ARCHITECTURE.md"),
    "build": ("BUILD_PROTOCOL.md", "BUILD_PROTOCOL.md"),
}


def _read_doc(filename: str) -> str:
    path = os.path.join(DOCS_DIR, filename)
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return f"({filename} not found)"


async def handle_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /context command."""
    args = context.args or []

    if args:
        # Specific doc(s) requested
        docs_to_include = []
        for arg in args:
            arg_lower = arg.lower()
            if arg_lower in DOC_FILES:
                label, filename = DOC_FILES[arg_lower]
                docs_to_include.append((label, _read_doc(filename)))
            else:
                available = ", ".join(DOC_FILES.keys())
                await update.message.reply_text(
                    f"Unknown doc: {arg}\nAvailable: {available}\n\n"
                    f"Usage:\n  /context — all docs\n  /context todo — just TODO"
                )
                return
    else:
        # All docs
        docs_to_include = [
            (label, _read_doc(filename))
            for label, filename in DOC_FILES.values()
        ]

    # Build output
    parts = []
    for label, content in docs_to_include:
        parts.append(f"=== {label} ===")
        parts.append(content)
        parts.append("")

    full_output = "\n".join(parts)

    # Always send as file — these docs are too long for messages
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, prefix="context_"
    ) as f:
        f.write(full_output)
        temp_path = f.name

    try:
        doc_names = [a for a in args] if args else ["all"]
        with open(temp_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=f"mythos_context_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                caption=f"📋 Context dump: {', '.join(doc_names)}\nPaste this into a new Claude session."
            )
    finally:
        os.unlink(temp_path)
