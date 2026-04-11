#!/usr/bin/env python3
"""
SDIP Console — Interactive TUI
Browse documents, chunks, sensitivity findings, and topics.

Usage:
    sdip-console
"""

import sys
import os

sys.path.insert(0, '/opt/mythos/sdip')

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header, Footer, Static, DataTable, Input, Label,
    TabbedContent, TabPane, RichLog,
)
from textual.binding import Binding
from textual.screen import ModalScreen
from textual import on
from rich.text import Text
from rich.panel import Panel

from config import get_db_connection


# ── Data Access ────────────────────────────────────────────────

def fetch_stats():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM sdip_documents")
            docs = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM sdip_chunks")
            chunks = cur.fetchone()[0]
            cur.execute("SELECT COALESCE(SUM(word_count), 0) FROM sdip_chunks")
            words = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM sdip_sensitivity")
            findings = cur.fetchone()[0]
            cur.execute("""
                SELECT sensitivity_level, COUNT(*)
                FROM sdip_chunks GROUP BY sensitivity_level
                ORDER BY CASE sensitivity_level
                    WHEN 'PUBLIC' THEN 0 WHEN 'INTERNAL' THEN 1
                    WHEN 'SENSITIVE' THEN 2 WHEN 'RESTRICTED' THEN 3
                END
            """)
            levels = cur.fetchall()
        return {
            "documents": docs, "chunks": chunks, "words": words,
            "findings": findings, "levels": levels,
        }
    finally:
        conn.close()


def fetch_documents(search: str = '', limit: int = 200):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if search:
                cur.execute("""
                    SELECT d.id, d.relative_path, d.file_format,
                           COALESCE(cs.chunk_count, 0),
                           COALESCE(cs.total_words, 0),
                           COALESCE(cs.max_sens, 'PUBLIC')
                    FROM sdip_documents d
                    LEFT JOIN (
                        SELECT document_id, COUNT(*) as chunk_count,
                               SUM(word_count) as total_words,
                               MAX(sensitivity_level) as max_sens
                        FROM sdip_chunks GROUP BY document_id
                    ) cs ON cs.document_id = d.id
                    WHERE d.status = 'active'
                    AND (d.relative_path ILIKE %s OR d.filename ILIKE %s)
                    ORDER BY d.relative_path
                    LIMIT %s
                """, (f'%{search}%', f'%{search}%', limit))
            else:
                cur.execute("""
                    SELECT d.id, d.relative_path, d.file_format,
                           COALESCE(cs.chunk_count, 0),
                           COALESCE(cs.total_words, 0),
                           COALESCE(cs.max_sens, 'PUBLIC')
                    FROM sdip_documents d
                    LEFT JOIN (
                        SELECT document_id, COUNT(*) as chunk_count,
                               SUM(word_count) as total_words,
                               MAX(sensitivity_level) as max_sens
                        FROM sdip_chunks GROUP BY document_id
                    ) cs ON cs.document_id = d.id
                    WHERE d.status = 'active'
                    ORDER BY d.relative_path
                    LIMIT %s
                """, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


def fetch_chunks_for_doc(doc_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.chunk_index, c.parent_heading,
                       c.content_text, c.word_count,
                       c.sensitivity_level, c.sensitivity_tags
                FROM sdip_chunks c
                WHERE c.document_id = %s
                ORDER BY c.chunk_index
            """, (doc_id,))
            return cur.fetchall()
    finally:
        conn.close()


def search_chunks(query: str, limit: int = 100):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.chunk_index, c.parent_heading,
                       c.content_text, c.word_count,
                       c.sensitivity_level, d.relative_path
                FROM sdip_chunks c
                JOIN sdip_documents d ON d.id = c.document_id
                WHERE c.content_text ILIKE %s
                ORDER BY d.relative_path, c.chunk_index
                LIMIT %s
            """, (f'%{query}%', limit))
            return cur.fetchall()
    finally:
        conn.close()


def fetch_findings(limit: int = 200):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT s.id, s.sensitivity_type, s.detection_method,
                       s.detected_pattern, s.confidence,
                       c.sensitivity_level, d.relative_path, c.chunk_index
                FROM sdip_sensitivity s
                JOIN sdip_chunks c ON c.id = s.chunk_id
                JOIN sdip_documents d ON d.id = c.document_id
                ORDER BY
                    CASE c.sensitivity_level
                        WHEN 'RESTRICTED' THEN 0 WHEN 'SENSITIVE' THEN 1
                        WHEN 'INTERNAL' THEN 2 ELSE 3
                    END,
                    s.confidence DESC
                LIMIT %s
            """, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


def fetch_hot_documents(limit: int = 30):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.relative_path,
                       MAX(c.sensitivity_level) as max_level,
                       COUNT(s.id) as finding_count,
                       array_agg(DISTINCT s.sensitivity_type) as types
                FROM sdip_documents d
                JOIN sdip_chunks c ON c.document_id = d.id
                JOIN sdip_sensitivity s ON s.chunk_id = c.id
                WHERE c.sensitivity_level != 'PUBLIC'
                GROUP BY d.relative_path
                ORDER BY
                    CASE MAX(c.sensitivity_level)
                        WHEN 'RESTRICTED' THEN 0 WHEN 'SENSITIVE' THEN 1
                        WHEN 'INTERNAL' THEN 2 ELSE 3
                    END,
                    COUNT(s.id) DESC
                LIMIT %s
            """, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


# ── Sensitivity Colors ─────────────────────────────────────────

LEVEL_COLORS = {
    'PUBLIC': 'green',
    'INTERNAL': 'cyan',
    'SENSITIVE': 'yellow',
    'RESTRICTED': 'red',
}

def styled_level(level: str) -> Text:
    color = LEVEL_COLORS.get(level, 'white')
    return Text(level, style=f"bold {color}")


# ── Chunk Viewer Screen ───────────────────────────────────────

class ChunkViewerScreen(ModalScreen):
    """Modal screen showing chunks for a document."""

    BINDINGS = [
        Binding("escape", "dismiss", "Back"),
        Binding("q", "dismiss", "Back"),
    ]

    CSS = """
    ChunkViewerScreen {
        align: center middle;
    }
    #chunk-viewer {
        width: 90%;
        height: 85%;
        border: thick $accent;
        background: $surface;
    }
    #chunk-title {
        dock: top;
        height: 3;
        padding: 1;
        background: $boost;
        text-style: bold;
    }
    #chunk-log {
        height: 1fr;
        padding: 1;
    }
    """

    def __init__(self, doc_id: int, doc_path: str):
        super().__init__()
        self.doc_id = doc_id
        self.doc_path = doc_path

    def compose(self) -> ComposeResult:
        with Container(id="chunk-viewer"):
            yield Label(f"  {self.doc_path}", id="chunk-title")
            yield RichLog(id="chunk-log", wrap=True, highlight=True)

    def on_mount(self) -> None:
        log = self.query_one("#chunk-log", RichLog)
        chunks = fetch_chunks_for_doc(self.doc_id)

        if not chunks:
            log.write("[dim]No chunks found for this document.[/dim]")
            return

        for chunk_id, idx, heading, text, words, level, tags in chunks:
            color = LEVEL_COLORS.get(level, 'white')
            tag_str = ', '.join(tags) if tags else ''

            header = f"[bold]Chunk {idx}[/bold]"
            if heading:
                header += f"  [dim]│[/dim]  [italic]{heading}[/italic]"
            header += f"  [dim]│[/dim]  [{color}]{level}[/{color}]"
            header += f"  [dim]│[/dim]  {words}w"
            if tag_str:
                header += f"  [dim]│[/dim]  [yellow]{tag_str}[/yellow]"

            log.write(f"\n{'─' * 70}")
            log.write(header)
            log.write(f"{'─' * 70}")

            # Trim very long chunks for display
            display_text = text[:2000]
            if len(text) > 2000:
                display_text += f"\n[dim]... ({len(text) - 2000} more characters)[/dim]"
            log.write(display_text)

        log.write(f"\n{'━' * 70}")
        log.write(f"[bold]{len(chunks)} chunks[/bold]  │  {sum(c[4] for c in chunks):,} words")


# ── Main App ───────────────────────────────────────────────────

class SDIPConsole(App):
    """SDIP Console — Sovereign Document Intelligence Platform"""

    TITLE = "SDIP Console"
    SUB_TITLE = "Sovereign Document Intelligence Platform"

    CSS = """
    #stats-bar {
        dock: top;
        height: 3;
        padding: 0 1;
        background: $boost;
    }
    #stats-text {
        height: 3;
        padding: 1;
    }
    .search-bar {
        dock: top;
        height: 3;
        padding: 0 1;
    }
    DataTable {
        height: 1fr;
    }
    #chunk-results-log {
        height: 1fr;
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("d", "focus_tab('documents')", "Documents", show=False),
        Binding("s", "focus_tab('sensitivity')", "Sensitivity", show=False),
        Binding("c", "focus_tab('chunks')", "Chunks", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("", id="stats-text")

        with TabbedContent():
            with TabPane("Documents", id="documents"):
                yield Input(placeholder="Search documents...", id="doc-search")
                yield DataTable(id="doc-table")

            with TabPane("Sensitivity", id="sensitivity"):
                yield DataTable(id="hot-table")

            with TabPane("Findings", id="findings"):
                yield DataTable(id="findings-table")

            with TabPane("Chunk Search", id="chunks"):
                yield Input(placeholder="Search chunk content...", id="chunk-search")
                yield RichLog(id="chunk-results-log", wrap=True, highlight=True)

        yield Footer()

    def on_mount(self) -> None:
        self._load_stats()
        self._load_documents()
        self._load_hot_documents()
        self._load_findings()

    def _load_stats(self) -> None:
        stats = fetch_stats()
        levels_str = "  ".join(
            f"[{LEVEL_COLORS.get(l, 'white')}]{l}: {c}[/{LEVEL_COLORS.get(l, 'white')}]"
            for l, c in stats['levels']
        )
        self.query_one("#stats-text", Static).update(
            f"  [bold]{stats['documents']}[/bold] docs  │  "
            f"[bold]{stats['chunks']}[/bold] chunks  │  "
            f"[bold]{stats['words']:,}[/bold] words  │  "
            f"[bold]{stats['findings']}[/bold] findings  │  "
            f"{levels_str}"
        )

    def _load_documents(self, search: str = '') -> None:
        table = self.query_one("#doc-table", DataTable)
        table.clear(columns=True)
        table.add_columns("ID", "Path", "Fmt", "Chunks", "Words", "Sensitivity")
        table.cursor_type = "row"

        docs = fetch_documents(search)
        for doc_id, path, fmt, chunks, words, sens in docs:
            table.add_row(
                str(doc_id),
                path if len(path) <= 70 else '...' + path[-67:],
                fmt or '?',
                str(chunks),
                f"{words:,}" if words else "0",
                sens,
                key=str(doc_id),
            )

    def _load_hot_documents(self) -> None:
        table = self.query_one("#hot-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Path", "Level", "Findings", "Types")
        table.cursor_type = "row"

        hot = fetch_hot_documents()
        for path, level, count, types in hot:
            type_str = ', '.join(t for t in types if t) if types else ''
            table.add_row(
                path if len(path) <= 60 else '...' + path[-57:],
                level,
                str(count),
                type_str,
            )

    def _load_findings(self) -> None:
        table = self.query_one("#findings-table", DataTable)
        table.clear(columns=True)
        table.add_columns("ID", "Type", "Method", "Pattern", "Conf", "Level", "Document", "Chunk#")
        table.cursor_type = "row"

        findings = fetch_findings()
        for fid, stype, method, pattern, conf, level, doc_path, cidx in findings:
            table.add_row(
                str(fid),
                stype,
                method,
                (pattern or '')[:30],
                f"{conf:.1f}",
                level,
                doc_path if len(doc_path) <= 45 else '...' + doc_path[-42:],
                str(cidx),
            )

    @on(Input.Submitted, "#doc-search")
    def on_doc_search(self, event: Input.Submitted) -> None:
        self._load_documents(event.value)

    @on(Input.Submitted, "#chunk-search")
    def on_chunk_search(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            return

        log = self.query_one("#chunk-results-log", RichLog)
        log.clear()

        results = search_chunks(query)
        if not results:
            log.write(f"[dim]No chunks matching '{query}'[/dim]")
            return

        log.write(f"[bold]{len(results)} chunks matching '{query}'[/bold]\n")

        for chunk_id, idx, heading, text, words, level, doc_path in results:
            color = LEVEL_COLORS.get(level, 'white')
            header = f"[dim]{doc_path}[/dim]  chunk {idx}"
            if heading:
                header += f"  [italic]{heading}[/italic]"
            header += f"  [{color}]{level}[/{color}]  {words}w"

            log.write(f"{'─' * 70}")
            log.write(header)

            # Show snippet around the match
            text_lower = text.lower()
            query_lower = query.lower()
            pos = text_lower.find(query_lower)
            if pos >= 0:
                start = max(0, pos - 100)
                end = min(len(text), pos + len(query) + 100)
                snippet = text[start:end]
                if start > 0:
                    snippet = '...' + snippet
                if end < len(text):
                    snippet = snippet + '...'
                log.write(snippet)
            else:
                log.write(text[:200] + ('...' if len(text) > 200 else ''))

            log.write("")

    @on(DataTable.RowSelected, "#doc-table")
    def on_doc_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key:
            doc_id = int(str(event.row_key.value))
            # Get path from the table
            table = self.query_one("#doc-table", DataTable)
            row_idx = event.cursor_row
            path = str(table.get_cell_at((row_idx, 1)))
            self.push_screen(ChunkViewerScreen(doc_id, path))

    def action_refresh(self) -> None:
        self._load_stats()
        self._load_documents()
        self._load_hot_documents()
        self._load_findings()
        self.notify("Refreshed")

    def action_focus_tab(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id


def main():
    app = SDIPConsole()
    app.run()


if __name__ == '__main__':
    main()
