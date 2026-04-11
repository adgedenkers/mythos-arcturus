#!/usr/bin/env python3
"""
Vault Sorter TUI
================
Interactive terminal interface for reviewing and routing unsorted vault files.
Reads files from UNSORTED/, classifies them, lets you review/override, and moves them.

Usage:
    vault-sorter                          # launch TUI
    vault-sorter --classify-only          # classify all and show report, don't move
    vault-sorter --index                  # rebuild the vault index
"""

import argparse
import curses
import hashlib
import json
import os
import re
import shutil
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path

import requests

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────

VAULT_ROOT = Path.home() / "curated-vault"
UNSORTED_DIR = VAULT_ROOT / "UNSORTED"
INDEX_PATH = VAULT_ROOT / "_vault_index.json"
MOVE_LOG_PATH = VAULT_ROOT / "_move_log.json"
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:7b"
MAX_CONTENT_CHARS = 6000

VAULT_FOLDERS = [
    "scrolls/codex",
    "scrolls/flame_orders",
    "scrolls/flame_archives",
    "scrolls/lineage",
    "scrolls/identity",
    "scrolls/sealed_orders",
    "scrolls/orders",
    "scrolls/grail",
    "scrolls/rose_lattice",
    "scrolls/rituals",
    "scrolls/rituals/breathcraft",
    "scrolls/rituals/flame_healing",
    "scrolls/relics",
    "scrolls/embodiment",
    "scrolls/thrones",
    "scrolls/vaults",
    "scrolls/forge",
    "scrolls/voice",
    "scrolls/tones",
    "scrolls/protocols",
    "scrolls/field-records",
    "scrolls/field-naming",
    "scrolls/foundations",
    "scrolls/construction",
    "scrolls/solar-returns",
    "scrolls/testimony",
    "scrolls/temporal-loops",
    "scrolls/exodus",
    "scrolls/collapse",
    "scrolls/sites",
    "scrolls/fragments",
    "scrolls/logs",
    "scrolls/spiral",
    "scrolls/weapons",
    "sigils",
    "glyphs",
    "spiritual/channeling",
    "spiritual/seraphe",
    "spiritual/seraphe/tarot-sessions",
    "spiritual/thresholds",
    "spiritual/lineage",
    "spiritual/numerology",
    "spiritual/sovereignty",
    "astrology/natal-charts/ka",
    "astrology/natal-charts/seraphe",
    "astrology/natal-charts/fitz",
    "astrology/natal-charts/brandi",
    "astrology/natal-charts/riley-green",
    "astrology/natal-charts/harry-styles",
    "astrology/natal-charts/ryan-reynolds",
    "astrology/natal-charts/jj",
    "astrology/natal-charts/dave-matthews",
    "astrology/synastry",
    "astrology/transits",
    "astrology/sacred-geometry",
    "astrology/methodology",
    "astrology/reference",
    "astrology/interp-data",
    "research/genealogy",
    "research/psychology",
    "technical/mythos/architecture",
    "technical/mythos/iris",
    "technical/mythos/arcturian-grid",
    "technical/mythos/graph",
    "technical/mythos/witness-system",
    "technical/mythos/finance",
    "technical/mythos/sales-intake",
    "technical/mythos/sentinel",
    "technical/mythos/spiral-time",
    "technical/mythos/streams",
    "technical/mythos/reports",
    "technical/mythos/guides",
    "technical/mythos/business",
    "technical/mythos/scroll-system",
    "technical/reference",
    "personal/journal",
    "personal/dates",
    "personal/finance",
    "personal/travel",
    "personal/misc",
    "published",
    "system/instructions",
    "system/protocols",
    "_archive",
    "_inbox",
]

# ──────────────────────────────────────────────
# HELP TEXT
# ──────────────────────────────────────────────

HELP_TEXT = [
    "╔══════════════════════════════════════════════════════════════╗",
    "║                    VAULT SORTER — HELP                      ║",
    "╠══════════════════════════════════════════════════════════════╣",
    "║                                                              ║",
    "║  WORKFLOW — Follow these steps in order:                     ║",
    "║                                                              ║",
    "║  1. REVIEW    Scroll through your unsorted files.            ║",
    "║               Press ENTER on any file to preview its         ║",
    "║               content and understand what it is.             ║",
    "║                                                              ║",
    "║  2. SELECT    Press SPACE to select files you want to        ║",
    "║               sort. Press 'a' to select/deselect all.        ║",
    "║               Only selected files will be classified         ║",
    "║               or processed.                                  ║",
    "║                                                              ║",
    "║  3. CLASSIFY  Press 'c' to run selected files through        ║",
    "║               the LLM classifier. Each file gets a           ║",
    "║               suggested destination folder, a summary,       ║",
    "║               and a confidence score.                        ║",
    "║                 ✓ 80%+  = high confidence, probably right    ║",
    "║                 ~ 50-79% = medium, worth checking            ║",
    "║                 ? <50%  = low, review or set manually        ║",
    "║                                                              ║",
    "║  4. REVIEW    Check the suggested destinations.              ║",
    "║               Press ENTER to preview any file.               ║",
    "║               The destination and summary appear at top.     ║",
    "║                                                              ║",
    "║  5. OVERRIDE  Press 'e' on any file to manually pick         ║",
    "║               its destination. Type to filter the folder     ║",
    "║               list (e.g. 'iris' or 'synastry'), arrow        ║",
    "║               to the right one, ENTER to set it.             ║",
    "║               Manual picks always override the LLM.          ║",
    "║                                                              ║",
    "║  6. PROCESS   Press 'p' to move all selected+classified      ║",
    "║               files to their destinations. Every move is     ║",
    "║               logged in _move_log.json for undo.             ║",
    "║               Files that aren't classified yet are skipped.  ║",
    "║                                                              ║",
    "╠══════════════════════════════════════════════════════════════╣",
    "║                                                              ║",
    "║  KEYBOARD REFERENCE                                          ║",
    "║                                                              ║",
    "║  NAVIGATION                                                  ║",
    "║    Up/Down or j/k   Move cursor up/down                     ║",
    "║    ENTER             Preview highlighted file                ║",
    "║                                                              ║",
    "║  SELECTION                                                   ║",
    "║    SPACE             Toggle select on highlighted file       ║",
    "║    a                 Select all / Deselect all               ║",
    "║                                                              ║",
    "║  ACTIONS                                                     ║",
    "║    c      Classify selected (or cursor if none selected)    ║",
    "║    e      Edit destination for highlighted file              ║",
    "║    p      Process — move selected+classified files           ║",
    "║    r      Refresh file list from disk                       ║",
    "║    i      Show vault index (file counts by folder)          ║",
    "║    h/?    Show this help screen                              ║",
    "║    q      Quit                                               ║",
    "║                                                              ║",
    "║  IN PREVIEW MODE                                             ║",
    "║    Up/Down   Scroll content                                  ║",
    "║    SPACE     Toggle select                                   ║",
    "║    c         Classify this file                              ║",
    "║    e         Edit destination                                ║",
    "║    ESC/q     Back to list                                    ║",
    "║                                                              ║",
    "║  IN DESTINATION PICKER                                       ║",
    "║    type       Filter folder list                             ║",
    "║    Up/Down    Navigate filtered folders                      ║",
    "║    ENTER      Confirm selection                              ║",
    "║    Backspace  Delete filter character                        ║",
    "║    ESC        Cancel                                         ║",
    "║                                                              ║",
    "╠══════════════════════════════════════════════════════════════╣",
    "║                                                              ║",
    "║  TIPS                                                        ║",
    "║                                                              ║",
    "║  * Classify one file at a time from preview mode with 'c'   ║",
    "║    — useful for spot-checking before batch.                  ║",
    "║                                                              ║",
    "║  * Files the LLM can't confidently classify go to _inbox.   ║",
    "║    Use 'e' to manually route these.                          ║",
    "║                                                              ║",
    "║  * Press 'i' anytime to see your full vault inventory.      ║",
    "║                                                              ║",
    "║  * All moves are logged in _move_log.json.                  ║",
    "║                                                              ║",
    "╚══════════════════════════════════════════════════════════════╝",
    "",
    "              Press any key to return...",
]

# ──────────────────────────────────────────────
# LLM CLASSIFICATION
# ──────────────────────────────────────────────

CLASSIFY_PROMPT = """You are a vault organizer. Classify this note into the correct folder.

Available folders:
{folders}

File: {filename}
Content (first {max_chars} chars):
---
{content}
---

Respond with ONLY a JSON object, no markdown, no backticks:
{{
    "folder": "<exact folder path from the list above>",
    "summary": "<1 sentence summary of the file>",
    "confidence": <0.0 to 1.0>,
    "reasoning": "<brief explanation>"
}}

For spiritual/channeling content, ALWAYS classify confidently.
For technical Mythos content, route to the most specific subfolder.
If genuinely unsure, use "_inbox".
"""


def call_ollama(prompt, model=DEFAULT_MODEL):
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": model, "prompt": prompt, "stream": False,
            "options": {"temperature": 0.1, "num_predict": 300},
        }, timeout=120)
        resp.raise_for_status()
        raw = resp.json().get("response", "").strip()
        match = re.search(r'\{[\s\S]*\}', raw)
        if match:
            return json.loads(match.group())
        return {"error": "No JSON", "raw": raw[:300]}
    except Exception as e:
        return {"error": str(e)}


def classify_file(filepath):
    try:
        content = filepath.read_text(encoding='utf-8', errors='replace')[:MAX_CONTENT_CHARS]
    except:
        return {"folder": "_inbox", "summary": "Error reading file", "confidence": 0.0}
    if len(content.strip()) < 10:
        return {"folder": "_inbox", "summary": "Empty or near-empty", "confidence": 1.0}
    folders_list = "\n".join(f"  - {f}" for f in VAULT_FOLDERS)
    prompt = CLASSIFY_PROMPT.format(
        folders=folders_list, filename=filepath.name,
        max_chars=MAX_CONTENT_CHARS, content=content,
    )
    result = call_ollama(prompt)
    if "error" in result:
        return {"folder": "_inbox", "summary": f"LLM error: {result['error']}", "confidence": 0.0}
    if result.get("folder") not in VAULT_FOLDERS and result.get("folder") != "_inbox":
        result["folder"] = "_inbox"
    return result


# ──────────────────────────────────────────────
# VAULT INDEX
# ──────────────────────────────────────────────

def build_index():
    index = {"built": datetime.now().isoformat(), "files": [], "stats": {}}
    folder_counts = {}
    for root, dirs, files in os.walk(VAULT_ROOT):
        dirs[:] = [d for d in dirs if d not in {'.obsidian', '.git', 'UNSORTED', '_templates'}]
        for f in files:
            fpath = Path(root) / f
            rel = str(fpath.relative_to(VAULT_ROOT))
            folder = str(fpath.parent.relative_to(VAULT_ROOT))
            title = f
            if fpath.suffix == '.md':
                try:
                    first_lines = fpath.read_text(encoding='utf-8', errors='replace')[:500]
                    for line in first_lines.split('\n'):
                        line = line.strip()
                        if line.startswith('# '):
                            title = line[2:].strip()
                            break
                        elif line and not line.startswith('---'):
                            title = line[:80]
                            break
                except:
                    pass
            entry = {
                "path": rel, "folder": folder, "filename": f, "title": title,
                "size": fpath.stat().st_size,
                "modified": datetime.fromtimestamp(fpath.stat().st_mtime).isoformat(),
            }
            index["files"].append(entry)
            folder_counts[folder] = folder_counts.get(folder, 0) + 1
    index["stats"] = {
        "total_files": len(index["files"]),
        "total_folders": len(folder_counts),
        "by_folder": dict(sorted(folder_counts.items(), key=lambda x: -x[1])),
    }
    return index


def save_index(index):
    INDEX_PATH.write_text(json.dumps(index, indent=2))


# ──────────────────────────────────────────────
# MOVE LOG
# ──────────────────────────────────────────────

def log_move(source, dest, classification):
    log = []
    if MOVE_LOG_PATH.exists():
        try:
            log = json.loads(MOVE_LOG_PATH.read_text())
        except:
            pass
    log.append({
        "id": len(log) + 1,
        "timestamp": datetime.now().isoformat(),
        "source": source, "destination": dest,
        "classification": classification,
    })
    MOVE_LOG_PATH.write_text(json.dumps(log, indent=2))


# ──────────────────────────────────────────────
# FILE ENTRY
# ──────────────────────────────────────────────

class FileEntry:
    def __init__(self, path):
        self.path = path
        self.name = path.name
        self.size = path.stat().st_size
        self.modified = datetime.fromtimestamp(path.stat().st_mtime)
        self.selected = False
        self.classified = False
        self.classification = {}
        self.destination = ""
        self.summary = ""
        self.confidence = 0.0
        self.preview_lines = []
        try:
            text = path.read_text(encoding='utf-8', errors='replace')[:2000]
            self.preview_lines = text.split('\n')[:40]
        except:
            self.preview_lines = ["[Could not read file]"]

    def classify(self):
        result = classify_file(self.path)
        self.classification = result
        self.destination = result.get("folder", "_inbox")
        self.summary = result.get("summary", "")
        self.confidence = result.get("confidence", 0.0)
        self.classified = True

    @property
    def size_str(self):
        if self.size < 1024: return f"{self.size}B"
        elif self.size < 1024*1024: return f"{self.size//1024}K"
        else: return f"{self.size//(1024*1024)}M"

    @property
    def status_str(self):
        if not self.classified: return "  ???  "
        if self.confidence >= 0.8: return f" ✓ {self.confidence:.0%} "
        elif self.confidence >= 0.5: return f" ~ {self.confidence:.0%} "
        else: return f" ? {self.confidence:.0%} "


# ──────────────────────────────────────────────
# TUI
# ──────────────────────────────────────────────

class VaultSorterTUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.files = []
        self.cursor = 0
        self.scroll_offset = 0
        self.mode = "list"
        self.status_msg = "Press 'h' or '?' for help"
        self.status_time = time.time()
        self.preview_scroll = 0
        self.dest_filter = ""
        self.dest_cursor = 0
        self.index_data = None
        self.index_scroll = 0
        self.help_scroll = 0

        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        curses.init_pair(3, curses.COLOR_CYAN, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)

        self.load_files()

    def safe_print(self, y, x, text, attr=0):
        try:
            h, w = self.stdscr.getmaxyx()
            if y >= h or x >= w:
                return
            text = str(text)[:w - x - 1]
            self.stdscr.addnstr(y, x, text, w - x - 1, attr)
        except curses.error:
            pass

    def load_files(self):
        self.files = []
        if not UNSORTED_DIR.exists():
            UNSORTED_DIR.mkdir(parents=True)
            return
        for f in sorted(UNSORTED_DIR.iterdir()):
            if f.is_file() and not f.name.startswith('.'):
                self.files.append(FileEntry(f))
        if self.cursor >= len(self.files):
            self.cursor = max(0, len(self.files) - 1)

    def set_status(self, msg):
        self.status_msg = msg
        self.status_time = time.time()

    def run(self):
        curses.curs_set(0)
        self.stdscr.timeout(100)
        while True:
            self.draw()
            key = self.stdscr.getch()
            if key == -1:
                continue
            if self.mode == "list":
                if not self.handle_list_key(key):
                    break
            elif self.mode == "preview":
                self.handle_preview_key(key)
            elif self.mode == "dest_picker":
                self.handle_dest_picker_key(key)
            elif self.mode == "index_view":
                self.handle_index_key(key)
            elif self.mode == "help":
                self.handle_help_key(key)

    def draw(self):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()
        if self.mode == "list": self.draw_list(h, w)
        elif self.mode == "preview": self.draw_preview(h, w)
        elif self.mode == "dest_picker": self.draw_dest_picker(h, w)
        elif self.mode == "index_view": self.draw_index(h, w)
        elif self.mode == "help": self.draw_help(h, w)
        self.stdscr.refresh()

    def draw_list(self, h, w):
        title = f" VAULT SORTER — {len(self.files)} files in UNSORTED "
        selected = sum(1 for f in self.files if f.selected)
        classified = sum(1 for f in self.files if f.classified)
        header_right = f" sel:{selected} cls:{classified} "
        header = title + " " * max(0, w - len(title) - len(header_right) - 1) + header_right
        self.safe_print(0, 0, header, curses.color_pair(6))

        cols = f"  {'SEL':>3}  {'STATUS':^7}  {'SIZE':>5}  {'FILE':<30}  {'DESTINATION':<30}  SUMMARY"
        self.safe_print(1, 0, cols, curses.color_pair(3))

        list_h = h - 5
        visible = self.files[self.scroll_offset:self.scroll_offset + list_h]
        for i, f in enumerate(visible):
            y = i + 2
            if y >= h - 2: break
            idx = i + self.scroll_offset
            is_cursor = idx == self.cursor
            sel_mark = " [✓]" if f.selected else " [ ]"
            dest = f.destination[:28] if f.destination else ""
            summary = f.summary[:max(0, w - 80)] if f.summary else ""
            line = f"  {sel_mark}  {f.status_str}  {f.size_str:>5}  {f.name:<30.30}  {dest:<30.28}  {summary}"
            attr = 0
            if is_cursor: attr = curses.color_pair(2) | curses.A_BOLD
            elif f.selected: attr = curses.color_pair(1)
            self.safe_print(y, 0, line, attr)

        self.safe_print(h - 2, 0, " ↑↓:nav  SPC:select  a:all  RET:preview  c:classify  e:edit dest  p:process  i:index  h:help  q:quit", curses.color_pair(3))
        msg = self.status_msg if time.time() - self.status_time < 8 else ""
        self.safe_print(h - 1, 0, f" {msg}", curses.color_pair(6))

    def draw_preview(self, h, w):
        if not self.files: return
        f = self.files[self.cursor]
        self.safe_print(0, 0, f" PREVIEW: {f.name} ({f.size_str}) ", curses.color_pair(6))
        if f.classified:
            self.safe_print(1, 0, f" → {f.destination}  ({f.confidence:.0%})  {f.summary}", curses.color_pair(5))
        start = self.preview_scroll
        for i, line in enumerate(f.preview_lines[start:start + h - 4]):
            y = i + 3
            if y >= h - 1: break
            self.safe_print(y, 0, line)
        self.safe_print(h - 1, 0, " ↑↓:scroll  ESC/q:back  c:classify  e:edit dest  SPC:toggle select", curses.color_pair(3))

    def draw_dest_picker(self, h, w):
        f = self.files[self.cursor]
        self.safe_print(0, 0, f" CHOOSE DESTINATION for: {f.name} ", curses.color_pair(6))
        self.safe_print(1, 0, f" Filter: {self.dest_filter}█")
        filtered = [fl for fl in VAULT_FOLDERS if self.dest_filter.lower() in fl.lower()]
        if self.dest_cursor >= len(filtered):
            self.dest_cursor = max(0, len(filtered) - 1)
        for i, folder in enumerate(filtered[:h - 4]):
            y = i + 3
            if y >= h - 1: break
            attr = curses.color_pair(2) | curses.A_BOLD if i == self.dest_cursor else 0
            self.safe_print(y, 2, folder, attr)
        self.safe_print(h - 1, 0, " ↑↓:nav  ENTER:select  type:filter  ESC:cancel", curses.color_pair(3))

    def draw_index(self, h, w):
        total = self.index_data["stats"]["total_files"] if self.index_data else 0
        self.safe_print(0, 0, f" VAULT INDEX — {total} files ", curses.color_pair(6))
        if not self.index_data:
            self.safe_print(2, 2, "Building index...")
            return
        lines = [f"  {count:>4}  {folder}" for folder, count in self.index_data["stats"]["by_folder"].items()]
        for i, line in enumerate(lines[self.index_scroll:self.index_scroll + h - 3]):
            y = i + 2
            if y >= h - 1: break
            self.safe_print(y, 0, line)
        self.safe_print(h - 1, 0, " ↑↓:scroll  ESC/q:back  r:rebuild index", curses.color_pair(3))

    def draw_help(self, h, w):
        pad = max(0, (w - 64) // 2)
        for i, line in enumerate(HELP_TEXT[self.help_scroll:self.help_scroll + h]):
            if i >= h: break
            self.safe_print(i, pad, line, curses.color_pair(3))

    # ── Key Handlers ──

    def handle_list_key(self, key):
        if key == ord('q'): return False
        elif key in (curses.KEY_UP, ord('k')):
            if self.cursor > 0:
                self.cursor -= 1
                if self.cursor < self.scroll_offset:
                    self.scroll_offset = self.cursor
        elif key in (curses.KEY_DOWN, ord('j')):
            if self.cursor < len(self.files) - 1:
                self.cursor += 1
                h = self.stdscr.getmaxyx()[0]
                if self.cursor >= self.scroll_offset + h - 5:
                    self.scroll_offset += 1
        elif key == ord(' '):
            if self.files:
                self.files[self.cursor].selected = not self.files[self.cursor].selected
        elif key == ord('a'):
            all_sel = all(f.selected for f in self.files)
            for f in self.files: f.selected = not all_sel
        elif key in (curses.KEY_ENTER, ord('\n'), 10, 13):
            if self.files:
                self.mode = "preview"
                self.preview_scroll = 0
        elif key == ord('c'): self.classify_selected()
        elif key == ord('e'):
            if self.files:
                self.mode = "dest_picker"
                self.dest_filter = ""
                self.dest_cursor = 0
        elif key == ord('p'): self.process_selected()
        elif key == ord('r'):
            self.load_files()
            self.set_status("File list refreshed")
        elif key == ord('i'):
            self.mode = "index_view"
            self.index_scroll = 0
            self.set_status("Building index...")
            self.draw()
            self.index_data = build_index()
            save_index(self.index_data)
            self.set_status(f"Index built: {self.index_data['stats']['total_files']} files")
        elif key in (ord('h'), ord('?')):
            self.mode = "help"
            self.help_scroll = 0
        return True

    def handle_preview_key(self, key):
        if key in (27, ord('q')): self.mode = "list"
        elif key in (curses.KEY_UP, ord('k')):
            if self.preview_scroll > 0: self.preview_scroll -= 1
        elif key in (curses.KEY_DOWN, ord('j')): self.preview_scroll += 1
        elif key == ord(' '):
            self.files[self.cursor].selected = not self.files[self.cursor].selected
        elif key == ord('c'):
            f = self.files[self.cursor]
            self.set_status(f"Classifying {f.name}...")
            self.draw()
            f.classify()
            self.set_status(f"Classified → {f.destination} ({f.confidence:.0%})")
        elif key == ord('e'):
            self.mode = "dest_picker"
            self.dest_filter = ""
            self.dest_cursor = 0

    def handle_dest_picker_key(self, key):
        filtered = [f for f in VAULT_FOLDERS if self.dest_filter.lower() in f.lower()]
        if key == 27: self.mode = "list"
        elif key == curses.KEY_UP:
            if self.dest_cursor > 0: self.dest_cursor -= 1
        elif key == curses.KEY_DOWN:
            if self.dest_cursor < len(filtered) - 1: self.dest_cursor += 1
        elif key in (curses.KEY_ENTER, ord('\n'), 10, 13):
            if filtered and self.dest_cursor < len(filtered):
                f = self.files[self.cursor]
                f.destination = filtered[self.dest_cursor]
                f.classified = True
                f.confidence = 1.0
                f.summary = f"Manually set to {f.destination}"
                self.set_status(f"Destination set: {f.destination}")
                self.mode = "list"
        elif key == curses.KEY_BACKSPACE or key == 127:
            self.dest_filter = self.dest_filter[:-1]
            self.dest_cursor = 0
        elif 32 <= key <= 126:
            self.dest_filter += chr(key)
            self.dest_cursor = 0

    def handle_index_key(self, key):
        if key in (27, ord('q')): self.mode = "list"
        elif key in (curses.KEY_UP, ord('k')):
            if self.index_scroll > 0: self.index_scroll -= 1
        elif key in (curses.KEY_DOWN, ord('j')): self.index_scroll += 1
        elif key == ord('r'):
            self.set_status("Rebuilding index...")
            self.draw()
            self.index_data = build_index()
            save_index(self.index_data)
            self.set_status(f"Index rebuilt: {self.index_data['stats']['total_files']} files")

    def handle_help_key(self, key):
        if key in (27, ord('q'), ord('h'), ord('?'), ord('\n'), ord(' ')):
            self.mode = "list"
        elif key in (curses.KEY_UP, ord('k')):
            if self.help_scroll > 0: self.help_scroll -= 1
        elif key in (curses.KEY_DOWN, ord('j')): self.help_scroll += 1

    # ── Actions ──

    def classify_selected(self):
        targets = [f for f in self.files if f.selected and not f.classified]
        if not targets:
            targets = [f for f in self.files if f.selected]
        if not targets and self.files:
            targets = [self.files[self.cursor]]
        total = len(targets)
        for i, f in enumerate(targets, 1):
            self.set_status(f"Classifying {i}/{total}: {f.name}...")
            self.draw()
            f.classify()
        self.set_status(f"Classified {total} files")

    def process_selected(self):
        targets = [f for f in self.files if f.selected and f.classified and f.destination]
        if not targets:
            self.set_status("Select files, classify them, then process. (h for help)")
            return
        moved = 0
        errors = 0
        for f in targets:
            dest_dir = VAULT_ROOT / f.destination
            dest_file = dest_dir / f.name
            counter = 1
            while dest_file.exists():
                stem = f.path.stem
                suffix = f.path.suffix
                dest_file = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            try:
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(f.path), str(dest_file))
                log_move(f"UNSORTED/{f.name}", str(dest_file.relative_to(VAULT_ROOT)), f.classification)
                moved += 1
            except Exception as e:
                self.set_status(f"Error: {f.name}: {e}")
                errors += 1
        self.load_files()
        self.set_status(f"Processed {moved} files, {errors} errors")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Vault Sorter TUI")
    parser.add_argument("--classify-only", action="store_true")
    parser.add_argument("--index", action="store_true")
    args = parser.parse_args()

    if args.index:
        print("Building vault index...")
        index = build_index()
        save_index(index)
        print(f"\nVault Index — {index['stats']['total_files']} files in {index['stats']['total_folders']} folders\n")
        for folder, count in index["stats"]["by_folder"].items():
            print(f"  {count:>4}  {folder}")
        print(f"\nSaved to {INDEX_PATH}")
        return

    if args.classify_only:
        print("Classifying UNSORTED files...\n")
        if not UNSORTED_DIR.exists():
            print("No UNSORTED directory found")
            return
        for f in sorted(UNSORTED_DIR.iterdir()):
            if f.is_file() and not f.name.startswith('.'):
                print(f"  {f.name}...", end="", flush=True)
                result = classify_file(f)
                print(f" → {result.get('folder', '?')} ({result.get('confidence', 0):.0%})")
                print(f"    {result.get('summary', '')}")
        return

    UNSORTED_DIR.mkdir(parents=True, exist_ok=True)
    curses.wrapper(lambda stdscr: VaultSorterTUI(stdscr).run())


if __name__ == "__main__":
    main()
