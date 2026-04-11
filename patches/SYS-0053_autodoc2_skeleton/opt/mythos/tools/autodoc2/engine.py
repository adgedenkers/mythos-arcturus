"""
AutodocEngine — orchestrates the whole crawl.

Flow:
  1. Set up Neo4j constraints, begin crawl record
  2. Iterate source files via filters.iter_source_files()
  3. For each file: dispatch to the right walker, get a ParsedFile
  4. Write ParsedFile to Neo4j
  5. Optionally call LLM for markdown summary
  6. Write per-file markdown
  7. Write index.md
  8. Mark crawl finished

Failure handling: any single file's parse/write failure is logged and the
crawl continues. Crawl-level errors mark the crawl 'failed'.
"""

import hashlib
import time
from collections import Counter
from pathlib import Path

from .config import Config
from .filters import iter_source_files
from .walkers import get_walker, supported_languages
from .neo4j_writer import Neo4jWriter
from .markdown_writer import MarkdownWriter
from .llm_client import LLMClient


class AutodocEngine:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.crawl_id = self._make_crawl_id(cfg.target)
        self.neo4j: Neo4jWriter | None = None
        self.markdown = MarkdownWriter(cfg.output_dir)
        self.llm = LLMClient(cfg.ollama_url, cfg.ollama_model) if not cfg.skip_llm else None
        self.stats = {
            'files_total': 0,
            'files_parsed': 0,
            'files_failed': 0,
            'files_skipped_no_walker': 0,
            'language_counts': Counter(),
        }

    @staticmethod
    def _make_crawl_id(target: Path) -> str:
        h = hashlib.sha1(str(target.resolve()).encode()).hexdigest()[:12]
        return f"autodoc2_{target.name}_{h}"

    def run(self) -> int:
        cfg = self.cfg
        print(f"[autodoc2] target:      {cfg.target}")
        print(f"[autodoc2] output:      {cfg.output_dir}")
        print(f"[autodoc2] neo4j:       {cfg.neo4j_uri}")
        print(f"[autodoc2] crawl_id:    {self.crawl_id}")
        print(f"[autodoc2] languages:   {', '.join(supported_languages())}")
        print(f"[autodoc2] llm:         {'disabled' if cfg.skip_llm else cfg.ollama_model}")

        if not cfg.target.exists():
            print(f"[autodoc2] ERROR: target does not exist: {cfg.target}")
            return 2

        # Connect Neo4j
        try:
            self.neo4j = Neo4jWriter(
                uri=cfg.neo4j_uri,
                user=cfg.neo4j_user,
                password=cfg.neo4j_password,
                crawl_id=self.crawl_id,
                target=str(cfg.target),
            )
            self.neo4j.setup_constraints()
        except Exception as e:
            print(f"[autodoc2] ERROR: Neo4j connection failed: {e}")
            return 3

        if cfg.clean:
            print("[autodoc2] --clean: deleting existing crawl data...")
            self.neo4j.clean_crawl()

        self.neo4j.begin_crawl()

        t0 = time.time()
        try:
            for path, language in iter_source_files(
                cfg.target, include=cfg.include, exclude=cfg.exclude
            ):
                self.stats['files_total'] += 1
                self.stats['language_counts'][language] += 1
                self._process_file(path, language)

                if self.stats['files_total'] % 50 == 0:
                    elapsed = time.time() - t0
                    print(
                        f"[autodoc2] progress: {self.stats['files_total']} files, "
                        f"{self.stats['files_parsed']} parsed, "
                        f"{self.stats['files_failed']} failed, "
                        f"{elapsed:.1f}s"
                    )
        except KeyboardInterrupt:
            print("[autodoc2] interrupted by user")
            self.neo4j.finish_crawl(self.stats['files_parsed'], status='interrupted')
            self.neo4j.close()
            return 130

        # Write index
        self.markdown.write_index(
            cfg.target, self.stats['files_parsed'], dict(self.stats['language_counts'])
        )

        self.neo4j.finish_crawl(self.stats['files_parsed'], status='completed')
        self.neo4j.close()

        elapsed = time.time() - t0
        print()
        print(f"[autodoc2] done in {elapsed:.1f}s")
        print(f"[autodoc2] files total:    {self.stats['files_total']}")
        print(f"[autodoc2] files parsed:   {self.stats['files_parsed']}")
        print(f"[autodoc2] files failed:   {self.stats['files_failed']}")
        print(f"[autodoc2] no walker:      {self.stats['files_skipped_no_walker']}")
        print(f"[autodoc2] languages:")
        for lang, n in self.stats['language_counts'].most_common():
            print(f"             {lang}: {n}")
        print(f"[autodoc2] crawl_id:       {self.crawl_id}")
        print(f"[autodoc2] markdown:       {cfg.output_dir}")
        return 0

    def _process_file(self, path: Path, language: str):
        cfg = self.cfg
        walker = get_walker(language)
        if walker is None:
            self.stats['files_skipped_no_walker'] += 1
            return

        try:
            source = path.read_bytes()
        except Exception as e:
            print(f"[autodoc2] read failed: {path}: {e}")
            self.stats['files_failed'] += 1
            return

        try:
            relative_path = str(path.relative_to(cfg.target))
        except ValueError:
            relative_path = str(path)

        try:
            pf = walker.parse_file(path, relative_path, source)
        except Exception as e:
            print(f"[autodoc2] parse failed: {relative_path}: {e}")
            self.stats['files_failed'] += 1
            return

        # Neo4j write
        try:
            self.neo4j.write_file(pf)
        except Exception as e:
            print(f"[autodoc2] neo4j write failed: {relative_path}: {e}")
            # don't increment files_failed — we still got the parse, mark partial
            # but the crawl continues

        # LLM summary (optional)
        summary = None
        if self.llm is not None:
            try:
                excerpt = source.decode('utf-8', errors='replace')[:6000]
                summary = self.llm.summarize_file(relative_path, language, excerpt)
            except Exception as e:
                print(f"[autodoc2] llm summary failed: {relative_path}: {e}")

        # Markdown write
        try:
            self.markdown.write_file(pf, llm_summary=summary)
        except Exception as e:
            print(f"[autodoc2] markdown write failed: {relative_path}: {e}")

        self.stats['files_parsed'] += 1

        if cfg.verbose:
            print(
                f"[autodoc2] {relative_path}: "
                f"{len(pf.classes)}c {len(pf.functions)}fn {len(pf.imports)}imp"
            )
