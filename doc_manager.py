#!/usr/bin/env python3
"""
doc_manager.py — Download Version Manager & LLM Renamer
========================================================
TUI tool for managing Chrome's auto-versioned downloads.

Two modes:
  1. VERSION EXPORT — Pick files with multiple versions, grab the latest, zip with manifest
  2. LLM RENAME   — Pick files, have Ollama read each and suggest a meaningful name

Usage:
  python3 doc_manager.py [--dir ~/Downloads] [--model llama3.2]

Requires: textual, rich, requests (for Ollama API)
"""

import argparse
import json
import os
import re
import shutil
import sys
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from textual.app import App
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    OptionList,
    RadioButton,
    RadioSet,
    RichLog,
    Rule,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

# ─── File Version Detection ──────────────────────────────────────────────────

# Chrome pattern: name(N).ext  or  name (N).ext
CHROME_VERSION_RE = re.compile(r'^(.+?)\s*\((\d+)\)(\.[^.]+)$')


def parse_versioned_name(filename: str) -> tuple[str, int, str]:
    """
    Parse a filename into (base_name, version, extension).
    'report.md'      → ('report', 0, '.md')
    'report(1).md'   → ('report', 1, '.md')
    'report (3).md'  → ('report', 3, '.md')
    """
    m = CHROME_VERSION_RE.match(filename)
    if m:
        base, ver, ext = m.group(1).strip(), int(m.group(2)), m.group(3)
        return base, ver, ext
    # No version suffix → version 0 (original)
    stem = Path(filename).stem
    ext = Path(filename).suffix
    return stem, 0, ext


def scan_directory(directory: Path) -> dict[str, list[dict]]:
    """
    Scan directory and group files by their base name.
    Returns: { "base_name.ext": [ {path, version, mtime, size}, ... ] }
    Only includes groups with 2+ versions.
    """
    groups = defaultdict(list)

    for f in directory.iterdir():
        if f.is_file() and not f.name.startswith('.'):
            base, ver, ext = parse_versioned_name(f.name)
            key = f"{base}{ext}"
            groups[key].append({
                'path': f,
                'version': ver,
                'mtime': f.stat().st_mtime,
                'size': f.stat().st_size,
                'filename': f.name,
            })

    # Sort each group by version, filter to multi-version only
    multi = {}
    for key, files in sorted(groups.items()):
        files.sort(key=lambda x: x['version'])
        if len(files) >= 2:
            multi[key] = files

    return multi


def scan_all_files(directory: Path) -> dict[str, list[dict]]:
    """
    Scan directory and group ALL files by base name (including singles).
    Used for LLM rename mode where even single files might need renaming.
    """
    groups = defaultdict(list)

    for f in directory.iterdir():
        if f.is_file() and not f.name.startswith('.'):
            base, ver, ext = parse_versioned_name(f.name)
            key = f"{base}{ext}"
            groups[key].append({
                'path': f,
                'version': ver,
                'mtime': f.stat().st_mtime,
                'size': f.stat().st_size,
                'filename': f.name,
            })

    for key, files in groups.items():
        files.sort(key=lambda x: x['version'])

    return dict(sorted(groups.items()))


def get_latest(files: list[dict]) -> dict:
    """Get the highest-versioned file from a group."""
    return max(files, key=lambda x: x['version'])


def sanitize_id(name: str) -> str:
    """Make a string safe for Textual widget IDs (letters, numbers, underscores, hyphens only)."""
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)


def human_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


# ─── Ollama Integration ──────────────────────────────────────────────────────

def ollama_suggest_name(filepath: Path, model: str = "llama3.2",
                        base_url: str = "http://localhost:11434") -> Optional[str]:
    """
    Send file content to Ollama and get a suggested filename.
    Returns suggested name (without extension) or None on failure.
    """
    import requests

    try:
        content = filepath.read_text(errors='replace')[:4000]  # Cap at 4k chars
    except Exception:
        return None

    prompt = f"""You are a file naming assistant. Read the following file content and suggest a single, 
descriptive filename (WITHOUT extension). Use lowercase_snake_case. Be specific and descriptive 
about what this file actually contains or does. Keep it under 60 characters.

Reply with ONLY the filename, nothing else. No explanation, no extension, no path.

File content:
---
{content}
---

Suggested filename:"""

    try:
        resp = requests.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        name = resp.json().get("response", "").strip()
        # Clean up the response
        name = name.strip('`"\'').strip()
        name = re.sub(r'[^\w\-.]', '_', name)
        name = re.sub(r'_+', '_', name).strip('_')
        if name and len(name) > 2:
            return name[:60]
    except Exception as e:
        return None

    return None


# ─── Export Functions ─────────────────────────────────────────────────────────

def export_latest_versions(selected_groups: dict[str, list[dict]],
                           output_dir: Path,
                           label: str = "export") -> Path:
    """
    Export latest version of each selected group into a zip with manifest.
    Returns path to created zip.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d")
    safe_label = re.sub(r'[^\w\-]', '_', label)[:40]
    zip_name = f"doc_export_{timestamp}__{safe_label}.zip"
    zip_path = output_dir / zip_name

    manifest = {
        "created": datetime.now().isoformat(),
        "label": label,
        "tool": "doc_manager",
        "files": [],
    }

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for base_name, files in sorted(selected_groups.items()):
            latest = get_latest(files)
            # Store as the clean base name (no version suffix)
            arc_name = base_name
            zf.write(latest['path'], arc_name)

            manifest["files"].append({
                "exported_as": arc_name,
                "original_file": latest['filename'],
                "version": latest['version'],
                "total_versions": len(files),
                "size": latest['size'],
                "modified": datetime.fromtimestamp(latest['mtime']).isoformat(),
                "all_versions": [f['filename'] for f in files],
            })

        # Add manifest
        manifest_json = json.dumps(manifest, indent=2)
        zf.writestr("MANIFEST.json", manifest_json)

    return zip_path


def export_llm_renamed(renamed_files: list[dict], output_dir: Path,
                       label: str = "renamed") -> Path:
    """
    Export LLM-renamed files into a zip with manifest.
    renamed_files: [ {original_path, new_name, ext}, ... ]
    """
    timestamp = datetime.now().strftime("%Y-%m-%d")
    safe_label = re.sub(r'[^\w\-]', '_', label)[:40]
    zip_name = f"doc_export_{timestamp}__{safe_label}.zip"
    zip_path = output_dir / zip_name

    manifest = {
        "created": datetime.now().isoformat(),
        "label": label,
        "tool": "doc_manager/llm_rename",
        "files": [],
    }

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for item in renamed_files:
            arc_name = f"{item['new_name']}{item['ext']}"
            zf.write(item['original_path'], arc_name)
            manifest["files"].append({
                "exported_as": arc_name,
                "original_file": item['original_path'].name,
                "llm_suggested_name": item['new_name'],
            })

        manifest_json = json.dumps(manifest, indent=2)
        zf.writestr("MANIFEST.json", manifest_json)

    return zip_path


# ─── TUI Application ─────────────────────────────────────────────────────────

class LabelInputScreen(ModalScreen[str]):
    """Modal to get export label from user."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, default: str = "export"):
        super().__init__()
        self.default = default

    def compose(self):
        with Container(id="label-dialog"):
            yield Label("Export Label", id="label-title")
            yield Label("Used in zip filename: doc_export_DATE__LABEL.zip")
            yield Input(value=self.default, id="label-input", placeholder="e.g. consciousness, skills, research")
            with Horizontal(id="label-buttons"):
                yield Button("Export", variant="success", id="btn-export")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-export":
            val = self.query_one("#label-input", Input).value.strip() or self.default
            self.dismiss(val)
        else:
            self.dismiss(None)

    def action_cancel(self):
        self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted):
        val = event.value.strip() or self.default
        self.dismiss(val)


class DocManagerApp(App):
    """TUI for managing versioned downloads."""

    CSS = """
    Screen {
        background: $surface;
    }

    #label-dialog {
        width: 60;
        height: 12;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
        align: center middle;
    }

    #label-dialog #label-title {
        text-style: bold;
        width: 100%;
        content-align: center middle;
        margin-bottom: 1;
    }

    #label-buttons {
        margin-top: 1;
        align: center middle;
        height: 3;
    }

    #label-buttons Button {
        margin: 0 1;
    }

    .tab-content {
        height: 1fr;
        padding: 1;
    }

    .file-list {
        height: 1fr;
        border: solid $accent;
        padding: 0 1;
        overflow-y: auto;
    }

    .action-bar {
        height: 3;
        align: center middle;
        margin-top: 1;
    }

    .action-bar Button {
        margin: 0 1;
    }

    .status-bar {
        height: 1;
        background: $accent;
        color: $text;
        padding: 0 1;
    }

    .file-entry {
        height: auto;
        padding: 0;
        margin: 0;
    }

    .file-entry Checkbox {
        height: auto;
        padding: 0;
        margin: 0;
    }

    .section-label {
        text-style: bold;
        margin: 1 0 0 0;
        color: $accent;
    }

    .info-text {
        color: $text-muted;
        margin: 0 0 1 0;
    }

    RichLog {
        height: 1fr;
        border: solid $accent;
        padding: 0 1;
    }

    #model-input {
        width: 30;
        margin: 0 1;
    }

    .config-row {
        height: 3;
        align: left middle;
        margin-bottom: 1;
    }

    .config-row Label {
        margin: 0 1 0 0;
        width: auto;
    }
    """

    TITLE = "Doc Manager — Version Export & LLM Rename"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("a", "select_all", "Select All"),
        Binding("n", "select_none", "Select None"),
    ]

    def __init__(self, scan_dir: Path, output_dir: Path, model: str = "llama3.2",
                 ollama_url: str = "http://localhost:11434"):
        super().__init__()
        self.scan_dir = scan_dir
        self.output_dir = output_dir
        self.model = model
        self.ollama_url = ollama_url
        self.multi_groups = scan_directory(scan_dir)
        self.all_groups = scan_all_files(scan_dir)
        self.version_checkboxes: dict[str, Checkbox] = {}
        self.rename_checkboxes: dict[str, Checkbox] = {}

    def compose(self):
        yield Header()
        with TabbedContent("Version Export", "LLM Rename"):
            # ── Tab 1: Version Export ──
            with TabPane("Version Export", id="tab-version"):
                with Vertical(classes="tab-content"):
                    yield Static(
                        f"📂 Scanning: {self.scan_dir}",
                        classes="section-label",
                    )
                    yield Static(
                        f"Found {len(self.multi_groups)} file(s) with multiple versions. "
                        "Select which to export (latest version only).",
                        classes="info-text",
                    )
                    with VerticalScroll(classes="file-list", id="version-list"):
                        if not self.multi_groups:
                            yield Static("No files with multiple versions found.")
                        for base_name, files in self.multi_groups.items():
                            latest = get_latest(files)
                            vers_count = len(files)
                            size = human_size(latest['size'])
                            label = (
                                f"{base_name}  "
                                f"[dim]({vers_count} versions → v{latest['version']}, {size})[/dim]"
                            )
                            cb = Checkbox(label, id=f"vcb_{sanitize_id(base_name)}")
                            self.version_checkboxes[base_name] = cb
                            yield cb
                    with Horizontal(classes="action-bar"):
                        yield Button("Export Selected", variant="success", id="btn-version-export")
                        yield Button("Select All", variant="default", id="btn-version-all")
                        yield Button("Select None", variant="default", id="btn-version-none")

            # ── Tab 2: LLM Rename ──
            with TabPane("LLM Rename", id="tab-rename"):
                with Vertical(classes="tab-content"):
                    yield Static(
                        f"📂 Scanning: {self.scan_dir}",
                        classes="section-label",
                    )
                    yield Static(
                        "Select file groups for Ollama to review and rename. "
                        "Each file gets a descriptive name based on its content.",
                        classes="info-text",
                    )
                    with Horizontal(classes="config-row"):
                        yield Label("Ollama Model:")
                        yield Input(value=self.model, id="model-input", placeholder="e.g. llama3.2")
                    with VerticalScroll(classes="file-list", id="rename-list"):
                        for base_name, files in self.all_groups.items():
                            count = len(files)
                            total_size = sum(f['size'] for f in files)
                            label = (
                                f"{base_name}  "
                                f"[dim]({count} file{'s' if count > 1 else ''}, "
                                f"{human_size(total_size)})[/dim]"
                            )
                            cb = Checkbox(label, id=f"rcb_{sanitize_id(base_name)}")
                            self.rename_checkboxes[base_name] = cb
                            yield cb
                    with Horizontal(classes="action-bar"):
                        yield Button("Rename & Export", variant="success", id="btn-rename-export")
                        yield Button("Select All", variant="default", id="btn-rename-all")
                        yield Button("Select None", variant="default", id="btn-rename-none")
                    yield RichLog(id="rename-log", highlight=True, markup=True)

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id

        # Version Export actions
        if bid == "btn-version-export":
            self._do_version_export()
        elif bid == "btn-version-all":
            for cb in self.version_checkboxes.values():
                cb.value = True
        elif bid == "btn-version-none":
            for cb in self.version_checkboxes.values():
                cb.value = False

        # LLM Rename actions
        elif bid == "btn-rename-export":
            self._do_rename_export()
        elif bid == "btn-rename-all":
            for cb in self.rename_checkboxes.values():
                cb.value = True
        elif bid == "btn-rename-none":
            for cb in self.rename_checkboxes.values():
                cb.value = False

    def _get_selected_version_groups(self) -> dict[str, list[dict]]:
        selected = {}
        for base_name, cb in self.version_checkboxes.items():
            if cb.value:
                selected[base_name] = self.multi_groups[base_name]
        return selected

    def _get_selected_rename_groups(self) -> dict[str, list[dict]]:
        selected = {}
        for base_name, cb in self.rename_checkboxes.items():
            if cb.value:
                selected[base_name] = self.all_groups[base_name]
        return selected

    def _do_version_export(self):
        selected = self._get_selected_version_groups()
        if not selected:
            self.notify("No files selected!", severity="warning")
            return

        def on_label(label: Optional[str]):
            if label is None:
                return
            try:
                zip_path = export_latest_versions(selected, self.output_dir, label)
                self.notify(
                    f"✅ Exported {len(selected)} files → {zip_path.name}",
                    severity="information",
                    timeout=10,
                )
            except Exception as e:
                self.notify(f"❌ Export failed: {e}", severity="error")

        self.push_screen(LabelInputScreen("export"), on_label)

    def _do_rename_export(self):
        selected = self._get_selected_rename_groups()
        if not selected:
            self.notify("No files selected!", severity="warning")
            return

        # Update model from input
        model_input = self.query_one("#model-input", Input)
        self.model = model_input.value.strip() or "llama3.2"

        log = self.query_one("#rename-log", RichLog)
        log.clear()
        log.write(f"[bold]Starting LLM rename with model: {self.model}[/bold]")
        log.write(f"Ollama URL: {self.ollama_url}")
        log.write("")

        renamed_files = []
        errors = []

        for base_name, files in selected.items():
            log.write(f"[cyan]── {base_name} ({len(files)} files) ──[/cyan]")

            for finfo in files:
                fpath = finfo['path']
                ext = fpath.suffix
                log.write(f"  📄 {finfo['filename']}...")

                suggested = ollama_suggest_name(fpath, self.model, self.ollama_url)

                if suggested:
                    # Check for collisions
                    final_name = suggested
                    counter = 1
                    existing_names = {r['new_name'] for r in renamed_files}
                    while final_name in existing_names:
                        final_name = f"{suggested}_{counter}"
                        counter += 1

                    renamed_files.append({
                        'original_path': fpath,
                        'new_name': final_name,
                        'ext': ext,
                    })
                    log.write(f"    → [green]{final_name}{ext}[/green]")
                else:
                    errors.append(finfo['filename'])
                    log.write(f"    → [red]FAILED (keeping original)[/red]")
                    # Fall back to original name
                    renamed_files.append({
                        'original_path': fpath,
                        'new_name': fpath.stem,
                        'ext': ext,
                    })

        if not renamed_files:
            log.write("[red]No files to export.[/red]")
            return

        log.write("")
        log.write(f"[bold]Renaming complete. {len(renamed_files)} files ready.[/bold]")

        def on_label(label: Optional[str]):
            if label is None:
                return
            try:
                zip_path = export_llm_renamed(renamed_files, self.output_dir, label)
                log.write(f"[bold green]✅ Exported → {zip_path.name}[/bold green]")
                self.notify(
                    f"✅ Exported {len(renamed_files)} files → {zip_path.name}",
                    severity="information",
                    timeout=10,
                )
            except Exception as e:
                log.write(f"[bold red]❌ Export failed: {e}[/bold red]")
                self.notify(f"❌ Export failed: {e}", severity="error")

        self.push_screen(LabelInputScreen("renamed"), on_label)

    def action_select_all(self):
        """Select all in current tab."""
        # Try version tab first
        for cb in self.version_checkboxes.values():
            cb.value = True

    def action_select_none(self):
        """Deselect all in current tab."""
        for cb in self.version_checkboxes.values():
            cb.value = False


# ─── CLI Entry Point ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Doc Manager — Version Export & LLM Rename TUI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Scan ~/Downloads, output to ~/Downloads
  %(prog)s --dir ~/Downloads         # Explicit directory
  %(prog)s --output ~/exports        # Custom output directory
  %(prog)s --model mistral           # Use different Ollama model
  %(prog)s --ollama http://server:11434  # Remote Ollama instance
        """,
    )
    parser.add_argument(
        '--dir', '-d',
        type=Path,
        default=Path.home() / 'Downloads',
        help='Directory to scan for versioned files (default: ~/Downloads)',
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=None,
        help='Output directory for zip exports (default: same as scan dir)',
    )
    parser.add_argument(
        '--model', '-m',
        type=str,
        default='llama3.2',
        help='Ollama model for LLM rename (default: llama3.2)',
    )
    parser.add_argument(
        '--ollama',
        type=str,
        default='http://localhost:11434',
        help='Ollama API base URL (default: http://localhost:11434)',
    )

    args = parser.parse_args()

    scan_dir = args.dir.expanduser().resolve()
    output_dir = (args.output or scan_dir).expanduser().resolve()

    if not scan_dir.is_dir():
        print(f"Error: Directory not found: {scan_dir}", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    app = DocManagerApp(
        scan_dir=scan_dir,
        output_dir=output_dir,
        model=args.model,
        ollama_url=args.ollama,
    )
    app.run()


if __name__ == "__main__":
    main()
