#!/usr/bin/env python3
"""
File Analyzer - LLM-powered file cataloging and analysis.

Every file that lands in ~/Downloads gets:
1. Metadata captured (name, size, hash, MIME type)
2. Cataloged to file_catalog table in Postgres
3. If readable + under size threshold: sent to Ollama for summary/keywords/tags
4. Routed to appropriate handler (patch, CSV import, etc.)

Uses qwen2.5:7b for fast classification (~2s per file).
"""

import hashlib
import json
import logging
import mimetypes
import os
import time
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
import requests

logger = logging.getLogger("FileAnalyzer")

MAX_ANALYZE_SIZE = 512 * 1024  # 512 KB
MAX_CONTENT_CHARS = 8000
ANALYZE_MODEL = "qwen2.5:7b"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

READABLE_EXTENSIONS = {
    ".txt", ".md", ".rst", ".org",
    ".py", ".sh", ".bash", ".js", ".ts", ".jsx", ".tsx",
    ".html", ".htm", ".css", ".sql", ".r", ".rb", ".go",
    ".java", ".c", ".cpp", ".h", ".hpp", ".rs", ".lua",
    ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".conf",
    ".env", ".properties",
    ".csv", ".tsv", ".xml",
    ".log",
}

BINARY_EXTENSIONS = {
    ".zip", ".gz", ".tar", ".bz2", ".7z", ".rar",
    ".exe", ".dll", ".so", ".dylib",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg",
    ".mp3", ".mp4", ".wav", ".flac", ".ogg", ".m4a",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".iso", ".dmg", ".img",
}

SKIP_ANALYSIS_ARTIFACTS = {"bank_csv"}


class FileAnalyzer:
    """Analyzes files via LLM and catalogs them to Postgres."""

    def __init__(self):
        self.conn = None
        self._connect_db()

    def _connect_db(self):
        try:
            self.conn = psycopg2.connect(
                host=os.environ.get("POSTGRES_HOST", "localhost"),
                database=os.environ.get("POSTGRES_DB", "mythos"),
                user=os.environ.get("POSTGRES_USER", "postgres"),
                password=os.environ.get("POSTGRES_PASSWORD", ""),
                port=os.environ.get("POSTGRES_PORT", "5432"),
            )
            self.conn.autocommit = True
        except Exception as e:
            logger.error(f"DB connection failed: {e}")
            self.conn = None

    def _ensure_db(self):
        if self.conn is None or self.conn.closed:
            self._connect_db()

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()

    @staticmethod
    def compute_hash(filepath):
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def detect_mime(filepath):
        mime, _ = mimetypes.guess_type(str(filepath))
        return mime or "application/octet-stream"

    @staticmethod
    def is_readable(filepath):
        ext = filepath.suffix.lower()
        if ext in BINARY_EXTENSIONS:
            return False
        if ext in READABLE_EXTENSIONS:
            return filepath.stat().st_size <= MAX_ANALYZE_SIZE
        if filepath.stat().st_size > MAX_ANALYZE_SIZE:
            return False
        try:
            with open(filepath, "r", encoding="utf-8", errors="strict") as f:
                f.read(1024)
            return True
        except (UnicodeDecodeError, PermissionError):
            return False

    @staticmethod
    def read_content(filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(MAX_CONTENT_CHARS)
            if filepath.stat().st_size > MAX_CONTENT_CHARS:
                content += "\n\n[... truncated ...]"
            return content
        except Exception as e:
            logger.warning(f"Could not read {filepath}: {e}")
            return ""

    def analyze_with_llm(self, filepath, content):
        filename = filepath.name
        ext = filepath.suffix.lower()
        size_kb = filepath.stat().st_size / 1024

        prompt = (
            "Analyze this file and respond ONLY with a JSON object. No other text.\n\n"
            f"File: {filename}\nExtension: {ext}\nSize: {size_kb:.1f} KB\n\n"
            f"Content:\n---\n{content}\n---\n\n"
            "Respond with this exact JSON structure:\n"
            "{\n"
            '  "summary": "2-3 sentence summary of what this file contains and its purpose",\n'
            '  "keywords": ["keyword1", "keyword2", "keyword3"],\n'
            '  "tags": ["tag1", "tag2", "tag3"],\n'
            '  "content_type": "one of: code, configuration, documentation, financial_data, '
            'correspondence, notes, data_export, log, script, template, manifest, unknown"\n'
            "}\n\n"
            "Rules:\n"
            "- summary: Be specific about what the file does or contains.\n"
            "- keywords: 3-8 specific searchable terms from the content.\n"
            "- tags: 3-6 category tags useful for organizing.\n"
            "- content_type: Pick the single best match.\n"
            "- JSON only. No markdown fences. No explanation."
        )

        start_ms = time.monotonic()
        raw_response = ""
        try:
            resp = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": ANALYZE_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 512},
                },
                timeout=60,
            )
            duration_ms = int((time.monotonic() - start_ms) * 1000)

            if resp.status_code != 200:
                return {"error": f"Ollama HTTP {resp.status_code}", "duration_ms": duration_ms}

            data = resp.json()
            raw_response = data.get("response", "").strip()

            cleaned = raw_response
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

            result = json.loads(cleaned)
            result["duration_ms"] = duration_ms
            return result

        except json.JSONDecodeError:
            duration_ms = int((time.monotonic() - start_ms) * 1000)
            return {
                "summary": raw_response[:500] if raw_response else "Analysis failed",
                "keywords": [], "tags": [], "content_type": "unknown",
                "duration_ms": duration_ms,
            }
        except Exception as e:
            duration_ms = int((time.monotonic() - start_ms) * 1000)
            return {"error": str(e), "duration_ms": duration_ms}

    def catalog_file(self, filepath, artifact_type=None, skip_analysis=False):
        """Full pipeline: metadata -> catalog -> analyze (if eligible) -> store."""
        self._ensure_db()
        if not self.conn:
            logger.error("No DB connection, cannot catalog")
            return {}

        filepath = Path(filepath)
        filename = filepath.name
        file_size = filepath.stat().st_size
        file_hash = self.compute_hash(filepath)
        mime_type = self.detect_mime(filepath)
        extension = filepath.suffix.lower()
        readable = self.is_readable(filepath)

        should_analyze = (
            readable
            and not skip_analysis
            and artifact_type not in SKIP_ANALYSIS_ARTIFACTS
        )

        existing = self._find_by_hash(file_hash)
        if existing:
            logger.info(f"Already cataloged (hash match): {filename} -> id={existing['id']}")
            return existing

        record = {
            "filename": filename, "filepath": str(filepath),
            "file_size": file_size, "file_hash": file_hash,
            "mime_type": mime_type, "file_extension": extension,
            "artifact_type": artifact_type or "unknown",
            "is_readable": readable, "was_analyzed": False,
        }

        catalog_id = self._insert_catalog(record)
        if not catalog_id:
            return record
        record["id"] = catalog_id

        if should_analyze:
            content = self.read_content(filepath)
            if content:
                logger.info(f"Analyzing {filename} with {ANALYZE_MODEL}...")
                analysis = self.analyze_with_llm(filepath, content)

                if "error" not in analysis:
                    self._update_analysis(catalog_id, analysis)
                    record.update({
                        "was_analyzed": True,
                        "summary": analysis.get("summary"),
                        "keywords": analysis.get("keywords", []),
                        "tags": analysis.get("tags", []),
                        "content_type": analysis.get("content_type"),
                        "llm_model": ANALYZE_MODEL,
                        "llm_duration_ms": analysis.get("duration_ms"),
                    })
                    logger.info(
                        f"Analyzed {filename}: {analysis.get('content_type', '?')} "
                        f"({analysis.get('duration_ms', 0)}ms)"
                    )
                else:
                    self._update_error(catalog_id, analysis.get("error", "unknown"))

        return record

    def update_handler_result(self, catalog_id, action, result=None, archived_path=None):
        """Update catalog record after handler processes the file."""
        self._ensure_db()
        if not self.conn:
            return
        try:
            cur = self.conn.cursor()
            cur.execute(
                """UPDATE file_catalog
                   SET handler_action = %s, handler_result = %s,
                       archived_path = %s, processed_at = NOW()
                   WHERE id = %s""",
                (action, json.dumps(result or {}), archived_path, catalog_id),
            )
        except Exception as e:
            logger.error(f"Handler result update failed: {e}")

    def _find_by_hash(self, file_hash):
        try:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                "SELECT * FROM file_catalog WHERE file_hash = %s ORDER BY id DESC LIMIT 1",
                (file_hash,),
            )
            row = cur.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Hash lookup failed: {e}")
            return None

    def _insert_catalog(self, record):
        try:
            cur = self.conn.cursor()
            cur.execute(
                """INSERT INTO file_catalog
                   (filename, filepath, file_size, file_hash, mime_type,
                    file_extension, artifact_type, is_readable, was_analyzed)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                (
                    record["filename"], record["filepath"], record["file_size"],
                    record["file_hash"], record["mime_type"], record["file_extension"],
                    record["artifact_type"], record["is_readable"], record["was_analyzed"],
                ),
            )
            row = cur.fetchone()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Catalog insert failed: {e}")
            return None

    def _update_analysis(self, catalog_id, analysis):
        try:
            cur = self.conn.cursor()
            cur.execute(
                """UPDATE file_catalog
                   SET was_analyzed = TRUE, summary = %s, keywords = %s, tags = %s,
                       content_type = %s, llm_model = %s, llm_duration_ms = %s,
                       analyzed_at = NOW()
                   WHERE id = %s""",
                (
                    analysis.get("summary"), analysis.get("keywords", []),
                    analysis.get("tags", []), analysis.get("content_type"),
                    ANALYZE_MODEL, analysis.get("duration_ms"), catalog_id,
                ),
            )
        except Exception as e:
            logger.error(f"Analysis update failed: {e}")

    def _update_error(self, catalog_id, error_msg):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "UPDATE file_catalog SET error_message = %s, analyzed_at = NOW() WHERE id = %s",
                (error_msg, catalog_id),
            )
        except Exception as e:
            logger.error(f"Error update failed: {e}")

    def search_files(self, query, limit=10):
        """Full-text search across summaries and keywords."""
        self._ensure_db()
        if not self.conn:
            return []
        try:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """SELECT id, filename, artifact_type, content_type, summary,
                          keywords, tags, file_size, detected_at
                   FROM file_catalog
                   WHERE to_tsvector('english',
                         COALESCE(summary, '') || ' ' ||
                         COALESCE(array_to_string(keywords, ' '), '') || ' ' ||
                         COALESCE(array_to_string(tags, ' '), ''))
                         @@ plainto_tsquery('english', %s)
                   ORDER BY detected_at DESC LIMIT %s""",
                (query, limit),
            )
            return [dict(r) for r in cur.fetchall()]
        except Exception as e:
            logger.error(f"File search failed: {e}")
            return []

    def recent_files(self, limit=10):
        """Get most recently cataloged files."""
        self._ensure_db()
        if not self.conn:
            return []
        try:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """SELECT id, filename, artifact_type, content_type, summary,
                          keywords, tags, file_size, handler_action, detected_at
                   FROM file_catalog
                   ORDER BY detected_at DESC LIMIT %s""",
                (limit,),
            )
            return [dict(r) for r in cur.fetchall()]
        except Exception as e:
            logger.error(f"Recent files query failed: {e}")
            return []

    def files_by_tag(self, tag, limit=20):
        """Find files by tag."""
        self._ensure_db()
        if not self.conn:
            return []
        try:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """SELECT id, filename, artifact_type, content_type, summary,
                          tags, detected_at
                   FROM file_catalog
                   WHERE %s = ANY(tags)
                   ORDER BY detected_at DESC LIMIT %s""",
                (tag, limit),
            )
            return [dict(r) for r in cur.fetchall()]
        except Exception as e:
            logger.error(f"Tag search failed: {e}")
            return []
