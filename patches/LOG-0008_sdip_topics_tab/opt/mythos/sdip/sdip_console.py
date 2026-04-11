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

from dotenv import load_dotenv
load_dotenv('/opt/mythos/.env')

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


# ── Neo4j Connection ───────────────────────────────────────────

def get_neo4j_driver():
    from neo4j import GraphDatabase
    uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
    user = os.environ.get('NEO4J_USER', 'neo4j')
    password = os.environ.get('NEO4J_PASSWORD', 'neo4j')
    return GraphDatabase.driver(uri, auth=(user, password))


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


def fetch_topics():
    """Fetch topics from Neo4j with document counts and connected systems."""
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (t:SDIPTopic)
                OPTIONAL MATCH (d:SDIPDocument)-[:COVERS_TOPIC]->(t)
                WITH t, count(d) as doc_count, collect(d.path)[..5] as samples
                OPTIONAL MATCH (t)<-[:COVERS_TOPIC]-(d2:SDIPDocument)-[:DESCRIBES_SYSTEM]->(s:SDIPSystem)
                WITH t, doc_count, samples, collect(DISTINCT s.name) as systems
                RETURN t.name as name, doc_count, samples, systems
                ORDER BY doc_count DESC
            """)
            topics = [{
                'name': r['name'],
                'doc_count': r['doc_count'],
                'samples': r['samples'],
                'systems': r['systems'],
            } for r in result]
        driver.close()
        return topics
    except Exception as e:
        return [{'name': f'Error: {e}', 'doc_count': 0, 'samples': [], 'systems': []}]


def fetch_topic_documents(topic_name: str):
    """Fetch all documents covering a specific topic from Neo4j."""
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (d:SDIPDocument)-[r:COVERS_TOPIC]->(t:SDIPTopic {name: $name})
                RETURN d.doc_id as doc_id, d.path as path, d.format as format,
                       d.chunk_count as chunks, d.word_count as words,
                       d.max_sensitivity as sensitivity, r.weight as weight
                ORDER BY r.weight DESC, d.path
            """, name=topic_name)
            docs = [{
                'doc_id': r['doc_id'],
                'path': r['path'],
                'format': r['format'],
                'chunks': r['chunks'] or 0,
                'words': r['words'] or 0,
                'sensitivity': r['sensitivity'] or 'PUBLIC',
                'weight': r['weight'] or 0,
            } for r in result]
        driver.close()
        return docs
    except Exception as e:
        return []


def fetch_topic_connections(topic_name: str):
    """Fetch related topics (topics that share documents with this one)."""
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (t1:SDIPTopic {name: $name})<-[:COVERS_TOPIC]-(d:SDIPDocument)-[:COVERS_TOPIC]->(t2:SDIPTopic)
                WHERE t2.name <> $name
                WITH t2.name as related, count(d) as shared
                RETURN related, shared
                ORDER BY shared DESC
                LIMIT 15
            """, name=topic_name)
            return [{'name': r['related'], 'shared': r['shared']} for r in result]
        driver.close()
    except Exception:
        return []


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

            display_text = text[:2000]
            if len(text) > 2000:
                display_text += f"\n[dim]... ({len(text) - 2000} more characters)[/dim]"
            log.write(display_text)

        log.write(f"\n{'━' * 70}")
        log.write(f"[bold]{len(chunks)} chunks[/bold]  │  {sum(c[4] for c in chunks):,} words")


# ── Topic Drilldown Screen ────────────────────────────────────

class TopicDrilldownScreen(ModalScreen):
    """Modal showing documents and connections for a topic."""

    BINDINGS = [
        Binding("escape", "dismiss", "Back"),
        Binding("q", "dismiss", "Back"),
    ]

    CSS = """
    TopicDrilldownScreen {
        align: center middle;
    }
    #topic-viewer {
        width: 90%;
        height: 85%;
        border: thick $accent;
        background: $surface;
    }
    #topic-title {
        dock: top;
        height: 3;
        padding: 1;
        background: $boost;
        text-style: bold;
    }
    #topic-log {
        height: 1fr;
        padding: 1;
    }
    """

    def __init__(self, topic_name: str):
        super().__init__()
        self.topic_name = topic_name

    def compose(self) -> ComposeResult:
        with Container(id="topic-viewer"):
            yield Label(f"  Topic: {self.topic_name}", id="topic-title")
            yield RichLog(id="topic-log", wrap=True, highlight=True)

    def on_mount(self) -> None:
        log = self.query_one("#topic-log", RichLog)

        # Connected topics
        connections = fetch_topic_connections(self.topic_name)
        if connections:
            log.write("[bold]Related Topics[/bold]")
            log.write(f"{'─' * 70}")
            for c in connections:
                bar = '█' * min(c['shared'], 40)
                log.write(f"  {c['name']:25s}  {c['shared']:3d} shared docs  [dim]{bar}[/dim]")
            log.write("")

        # Documents
        docs = fetch_topic_documents(self.topic_name)
        log.write(f"[bold]Documents ({len(docs)})[/bold]")
        log.write(f"{'─' * 70}")

        if not docs:
            log.write("[dim]No documents found.[/dim]")
            return

        for d in docs:
            color = LEVEL_COLORS.get(d['sensitivity'], 'white')
            weight_bar = '●' * max(1, int(d['weight'] * 5))
            log.write(
                f"  [{color}]{d['sensitivity']:10s}[/{color}]  "
                f"{d['chunks']:3d} chunks  "
                f"{d['words']:6,} words  "
                f"[dim]{weight_bar}[/dim]  "
                f"{d['path']}"
            )

        log.write(f"\n{'━' * 70}")
        total_words = sum(d['words'] for d in docs)
        total_chunks = sum(d['chunks'] for d in docs)
        log.write(
            f"[bold]{len(docs)} documents[/bold]  │  "
            f"{total_chunks:,} chunks  │  "
            f"{total_words:,} words"
        )


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
        Binding("t", "focus_tab('topics')", "Topics", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("", id="stats-text")

        with TabbedContent():
            with TabPane("Documents", id="documents"):
                yield Input(placeholder="Search documents...", id="doc-search")
                yield DataTable(id="doc-table")

            with TabPane("Topics", id="topics"):
                yield DataTable(id="topic-table")

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
        self._load_topics()
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

    def _load_topics(self) -> None:
        table = self.query_one("#topic-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Topic", "Docs", "Systems", "Sample Documents")
        table.cursor_type = "row"

        topics = fetch_topics()
        for t in topics:
            systems_str = ', '.join(t['systems'][:4]) if t['systems'] else ''
            samples_str = ', '.join(
                (p if len(p) <= 30 else '...' + p[-27:])
                for p in (t['samples'] or [])[:3]
            )
            table.add_row(
                t['name'],
                str(t['doc_count']),
                systems_str,
                samples_str,
                key=t['name'],
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
            table = self.query_one("#doc-table", DataTable)
            row_idx = event.cursor_row
            path = str(table.get_cell_at((row_idx, 1)))
            self.push_screen(ChunkViewerScreen(doc_id, path))

    @on(DataTable.RowSelected, "#topic-table")
    def on_topic_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key:
            topic_name = str(event.row_key.value)
            self.push_screen(TopicDrilldownScreen(topic_name))

    def action_refresh(self) -> None:
        self._load_stats()
        self._load_documents()
        self._load_topics()
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
