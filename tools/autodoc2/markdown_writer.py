"""
Markdown writer for AutoDoc2.

Writes one markdown file per source file, plus an index.md at the root of
the output directory. Markdown format mirrors legacy autodoc1 closely so
existing tooling that consumes it keeps working.
"""

from pathlib import Path
from typing import Optional
from .walker import ParsedFile


class MarkdownWriter:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._files_written = []

    def write_file(self, pf: ParsedFile, llm_summary: Optional[str] = None):
        # Mirror the source path structure under output_dir
        rel = Path(pf.relative_path)
        out_path = self.output_dir / rel.with_suffix(rel.suffix + '.md')
        out_path.parent.mkdir(parents=True, exist_ok=True)

        lines = []
        lines.append(f"# {pf.relative_path}")
        lines.append("")
        lines.append(f"- **Language:** {pf.language}")
        lines.append(f"- **Lines:** {pf.line_count}")
        lines.append(f"- **Path:** `{pf.path}`")
        lines.append("")

        if llm_summary:
            lines.append("## Summary")
            lines.append("")
            lines.append(llm_summary.strip())
            lines.append("")

        if pf.classes:
            lines.append("## Classes")
            lines.append("")
            for cls in pf.classes:
                bases = f"({', '.join(cls.bases)})" if cls.bases else ""
                lines.append(f"### `{cls.name}{bases}`")
                lines.append("")
                lines.append(f"Lines {cls.line_start}–{cls.line_end}")
                lines.append("")
                if cls.docstring:
                    lines.append(f"> {cls.docstring}")
                    lines.append("")
                if cls.methods:
                    lines.append("**Methods:** " + ", ".join(f"`{m}`" for m in cls.methods))
                    lines.append("")

        if pf.functions:
            module_funcs = [f for f in pf.functions if not f.is_method]
            if module_funcs:
                lines.append("## Functions")
                lines.append("")
                for fn in module_funcs:
                    async_marker = "async " if fn.is_async else ""
                    lines.append(f"### `{async_marker}{fn.name}()`")
                    lines.append("")
                    lines.append(f"Lines {fn.line_start}–{fn.line_end}")
                    lines.append("")
                    if fn.docstring:
                        lines.append(f"> {fn.docstring}")
                        lines.append("")
                    if fn.calls:
                        unique_calls = sorted(set(fn.calls))[:20]
                        lines.append("**Calls:** " + ", ".join(f"`{c}`" for c in unique_calls))
                        lines.append("")

        if pf.imports:
            lines.append("## Imports")
            lines.append("")
            for imp in pf.imports:
                if imp.names:
                    lines.append(f"- `from {imp.module} import {', '.join(imp.names)}`")
                else:
                    lines.append(f"- `import {imp.module}`")
            lines.append("")

        if pf.parse_errors:
            lines.append("## Parse Errors")
            lines.append("")
            for err in pf.parse_errors:
                lines.append(f"- {err}")
            lines.append("")

        out_path.write_text("\n".join(lines), encoding='utf-8')
        self._files_written.append(pf.relative_path)

    def write_index(self, target: Path, file_count: int, language_counts: dict):
        index_path = self.output_dir / 'index.md'
        lines = []
        lines.append("# AutoDoc2 Index")
        lines.append("")
        lines.append(f"- **Target:** `{target}`")
        lines.append(f"- **Files:** {file_count}")
        lines.append("")
        lines.append("## Languages")
        lines.append("")
        for lang, count in sorted(language_counts.items(), key=lambda x: -x[1]):
            lines.append(f"- **{lang}:** {count}")
        lines.append("")
        lines.append("## Files")
        lines.append("")
        for rel in sorted(self._files_written):
            md_path = Path(rel).with_suffix(Path(rel).suffix + '.md').as_posix()
            lines.append(f"- [{rel}]({md_path})")
        index_path.write_text("\n".join(lines), encoding='utf-8')
