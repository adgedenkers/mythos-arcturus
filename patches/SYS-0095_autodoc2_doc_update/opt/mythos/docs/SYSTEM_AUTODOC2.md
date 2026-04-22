---
title: "SYSTEM: AutoDoc2"
category: system
status: active
stream: SYS
location: docs
tags: [autodoc, codebase, documentation, neo4j, tree-sitter, system-doc]
created: 2026-04-21
updated: 2026-04-21
author: Adge Denkers
---

# SYSTEM: AutoDoc2

> **Design plan:** see `docs/AUTODOC2_V2.md`
> **Pattern:** see `docs/SUB-SYSTEMS.md`
> **This doc:** canonical current state of AutoDoc2. Updated after
> every patch lands. Read this before starting any AutoDoc2 conversation.

---

## Status

- **Build phase:** COMPLETE — all letters A→G shipped (F deferred, not blocked)
- **Last shipped patch:** SYS-0094 (Letter G — reliability, legacy retirement)
- **Next patch:** F — Telegram `/autodoc` commands (deferred, not blocking anything)
- **Arc:** A→G complete. AutoDoc2 is a fully operational, scheduled, queryable system.

---

## Architecture Summary

AutoDoc2 is a **multi-language codebase documentation and structural analysis engine**
at `/opt/mythos/tools/autodoc2/`. It crawls any target directory, parses every source
file via tree-sitter, writes structural facts (files, functions, classes, imports) to
Neo4j, and optionally runs per-file LLM structural analysis via `analyzer.py`.

The engine is a Python package with a CLI at `/opt/mythos/bin/autodoc2`. It supports
11 languages via `tree-sitter-language-pack`. Neo4j labels are compatible with the
legacy autodoc1 crawl schema. Crawls target any directory; multiple targets are
isolated by `crawl_id` in Neo4j.

Analysis (opt-in via `--analyze`) calls `qwen3-coder:30b` per file and stores
`analysis_*` properties on `AutodocFile` nodes. Analysis is non-fatal and separated
from Iris (`qwen3:30b-a3b`) by design — two different cognitive modes, two models,
zero bleed.

A weekly systemd timer (`mythos-autodoc2-crawl.timer`) fires the worker every Sunday
at 3am, diffs against the previous crawl, and sends a Telegram summary. The legacy
`autodoc.py` monolith has been retired and archived.

---

## Patch Ledger

### Pre-pattern patches (retroactive record)

| Scope | Approx Patch # | Notes |
|-------|----------------|-------|
| AutoDoc2 skeleton — package, CLI, Python walker, Neo4j writer, markdown writer, LLM stub | SYS-0053 | Phase 1. tree-sitter-languages → tree-sitter-language-pack in SYS-0054 |
| JS + TS + TSX walkers | SYS-0055 | Phase 2. TSX subclass of TypeScriptWalker. .d.ts excluded |
| SQL, PHP, Go, Bash, YAML, JSON, Rust walkers | SYS-0056–0057 approx | Phase 3 |
| Demo infrastructure — demo-live/demo-complete Neo4j containers, Jupyter, autodoc2-demo CLI | SYS-0058–0060 approx | M7 demo. Strapi v5.9.0 crawl: 4,994 files in 22.5s |

### Formal letter sequence

| Letter | Scope | Patch(es) | Status |
|--------|-------|-----------|--------|
| A | Subsystem registration — SYSTEM_AUTODOC2.md, AUTODOC2_V2.md, NEXT_PATCH_SPEC.md, _INDEX.md + SUB-SYSTEMS.md updates | SYS-0086 | ✅ 2026-04-21 |
| B | `ollama-analyze` microtool — qwen3-coder:30b per-file structural analysis, `--analyze` flag, results as AutodocFile properties | SYS-0088, SYS-0090 | ✅ 2026-04-21 |
| C | Graph coverage gate — post-patch Neo4j verification in post_install.py, non-fatal, direct neo4j driver | SYS-0091 | ✅ 2026-04-21 |
| D | PatchBase microtool registration — `patchbase_register.py`, `patchbase-methods` CLI, 23 MythosTool nodes in Neo4j | SYS-0092 | ✅ 2026-04-21 |
| E | Iris skill — `autodoc2_query.py`, 8 intent handlers, rule-based regex routing | SYS-0093 | ✅ 2026-04-21 |
| F | Telegram commands — `/autodoc`, `/autodoc crawl`, `/autodoc query` | — | ⏳ deferred |
| G | Reliability — `autodoc2_worker.py`, systemd timer (weekly Sun 3am), crawl diff, legacy retirement | SYS-0094 | ✅ 2026-04-21 |

---

## Current Disk State

### Package

```
/opt/mythos/tools/autodoc2/
├── __init__.py              # version: "2.0.0-phase1" (needs bump)
├── analyzer.py              # SYS-0088: qwen3-coder:30b analysis microtool
├── cli.py                   # argparse entry point (executable, chmod 755)
├── config.py                # env file + CLI arg loading (analyze: bool field)
├── engine.py                # AutodocEngine: orchestrates crawl + analysis
├── filters.py               # skip rules, extension → language mapping
├── walker.py                # LanguageWalker base class + ParsedFile dataclass
├── llm_client.py            # Ollama summarizer stub (--skip-llm path)
├── markdown_writer.py       # per-file + index markdown output
├── neo4j_writer.py          # all Neo4j write logic + write_analysis() method
└── walkers/
    ├── __init__.py          # walker registry dict
    ├── python_walker.py
    ├── javascript_walker.py
    ├── typescript_walker.py # TsxWalker subclasses this
    ├── sql_walker.py
    ├── php_walker.py
    ├── go_walker.py
    ├── bash_walker.py
    ├── yaml_walker.py
    ├── json_walker.py
    └── rust_walker.py
```

### CLI and tools

```
/opt/mythos/bin/autodoc2          → /opt/mythos/tools/autodoc2/cli.py
/opt/mythos/bin/patchbase-methods → /opt/mythos/tools/patchbase_register.py
/opt/mythos/tools/patchbase_register.py  # SYS-0092: AST extracts PatchBase API
/opt/mythos/workers/autodoc2_worker.py   # SYS-0094: scheduled re-crawl worker
/opt/mythos/systemd/mythos-autodoc2-crawl.service
/opt/mythos/systemd/mythos-autodoc2-crawl.timer
/opt/mythos/skills/data/autodoc2_query.py  # SYS-0093: Iris skill
```

### Legacy (retired SYS-0094)

```
/opt/mythos/tools/archive/autodoc_v1.py   # archived 2026-04-21 — do not use
```

The legacy `autodoc.py` monolith (1,612 lines, Python-only) was archived in
SYS-0094. The `/opt/mythos/bin/autodoc` symlink has been removed. Use `autodoc2`.

---

## Neo4j State

### AutoDoc2 crawl nodes (as of 2026-04-21)

| Label | Count | Notes |
|-------|-------|-------|
| AutodocCrawl | 1 | autodoc2 package crawl only — full Mythos crawl not yet run |
| AutodocFile | 21 | autodoc2 package itself (the test crawl) |
| AutodocFunction | ~140 | from 21-file test crawl |
| AutodocClass | ~20 | from 21-file test crawl |
| AutodocModule | ~80 | from 21-file test crawl |

The only completed crawl is the autodoc2 package itself (21 files, verified with
`--analyze`, all 21/21 analyzed, 0 failures, ~307s). A full `/opt/mythos/` crawl
has not been run yet — the weekly timer will do this on the next Sunday 3am.

### AutoDoc2 analysis results (from test crawl)

All 21 files: `analysis_complexity = medium`, `analysis_drift_risk = medium`.
Highest coupling: `cli.py` (7 imports), `rust_walker.py`, `javascript_walker.py`.
Patterns: facade (engine.py, analyzer.py), visitor+composite (walkers), data class (walker.py).

### PatchBase registration nodes (SYS-0092)

| Label | Count |
|-------|-------|
| MythosToolClass | 1 (`PatchBase`) |
| MythosTool | 23 (all public PatchBase methods) |

Query:
```cypher
MATCH (pb:MythosToolClass {name:'PatchBase'})-[:HAS_METHOD]->(t:MythosTool)
RETURN t.name, t.signature, t.doc_first ORDER BY t.lineno
```

---

## Supported Languages

| Language | Walker | Notes |
|---|---|---|
| Python | python_walker.py | Functions, classes, imports, decorators |
| JavaScript | javascript_walker.py | Functions, classes, imports, exports |
| TypeScript | typescript_walker.py | Interfaces stored as AutodocClass |
| TSX | typescript_walker.py (TsxWalker) | Subclass, tsx grammar key |
| SQL | sql_walker.py | Tables, views, functions |
| PHP | php_walker.py | Functions, classes |
| Go | go_walker.py | Functions, structs, interfaces |
| Bash | bash_walker.py | Functions |
| YAML | yaml_walker.py | Top-level keys |
| JSON | json_walker.py | Schema structure |
| Rust | rust_walker.py | Functions, structs, enums, traits |

`.d.ts` TypeScript declaration files are excluded.

---

## How to use

### Standard crawl (fast, no LLM)

```bash
autodoc2                         # target=/opt/mythos, output=docs/autodoc2/
autodoc2 --verbose               # per-file parse stats
autodoc2 --skip-llm              # skip markdown LLM summaries
autodoc2 --clean                 # wipe existing crawl data first
```

### Crawl with structural analysis (opt-in, ~15s/file)

```bash
autodoc2 --analyze               # qwen3-coder:30b analysis per file
autodoc2 --analyze --skip-llm    # analysis only, no markdown summaries
```

### Crawl an external repo

```bash
autodoc2 /path/to/repo --output-dir /tmp/repo-docs --skip-llm
```

### Trigger on-demand crawl via worker

```bash
sudo systemctl start mythos-autodoc2-crawl.service
journalctl -u mythos-autodoc2-crawl.service -f
```

### Query the graph

```cypher
-- Files by language
MATCH (f:AutodocFile) RETURN f.language, count(*) ORDER BY count(*) DESC

-- Functions in a file
MATCH (f:AutodocFile {relative_path: 'engine.py'})-[:CONTAINS]->(fn:AutodocFunction)
RETURN fn.name, fn.line_start ORDER BY fn.line_start

-- High drift risk files (requires --analyze crawl)
MATCH (f:AutodocFile) WHERE f.analysis_drift_risk = 'high'
RETURN f.relative_path, f.analysis_notable

-- Files importing a module
MATCH (f:AutodocFile)-[:IMPORTS]->(m:AutodocModule)
WHERE toLower(m.name) CONTAINS 'neo4j'
RETURN DISTINCT f.relative_path
```

### Iris skill queries (via Telegram or Iris chat)

```
what files import neo4j
show me functions in engine.py
high drift risk files
how many files in the codebase
what languages does mythos use
what does function run_crawl do
```

---

## Known Issues / Debt

1. **`__init__.py` version string** — still says `2.0.0-phase1`. Needs bump to `2.1.0`.
2. **Full Mythos crawl not yet run** — only the autodoc2 package (21 files) has been crawled. The weekly timer will run the first full crawl Sunday 3am. Run manually: `autodoc2 --skip-llm --clean`.
3. **Demo infrastructure state unknown** — demo-live/demo-complete Docker containers from the M7 pitch may be stale. Check `docker ps | grep demo` before any demo work.
4. **Letter F deferred** — Telegram `/autodoc` commands not yet wired. The Iris skill (Letter E) handles natural-language queries; the bot commands are convenience wrappers.
5. **`integrity.graph` crash loop** — `mythos-obs-graph.service` fails every time, making step 3 of the post-install pipeline always show `⊘`. Tracked in REQUESTS.md. Graph coverage gate (step 1.5) works fine via direct neo4j driver.
6. **`patchbase-methods` Neo4j registration** — reflects 23 methods from SYS-0092. Adge added more PatchBase methods after that patch; re-run `patchbase-methods --register` to sync.

---

## Incoming Notes

> Append-only, date-stamped, never edit.

**2026-04-21** (SYS-0086): AutoDoc2 registered as Mythos sub-system #3. Engine + all 11 walkers were pre-pattern. Formal letter sequence A→G established.

**2026-04-21** (SYS-0088): `ollama-analyze` microtool shipped. `gemma4:26b` rejected — safety filtering returns empty on code analysis prompts. `qwen3-coder:30b` chosen as final model: 21/21 files analyzed, 0 failures, ~15s/file. Model locked via `ANALYSIS_MODEL` constant in `analyzer.py`.

**2026-04-21** (SYS-0090): Model constant locked in git. `cli.py` chmod 755 fixed. Engine display string updated to read model from `analyzer.py` instead of hardcoded `gemma4:26b`.

**2026-04-21** (SYS-0091): Graph coverage gate added to post_install.py as step 1.5. Non-fatal, direct neo4j driver (bypasses broken `integrity.graph`). First patch to show `✓ Graph coverage: N/N verified`.

**2026-04-21** (SYS-0092): PatchBase registered in Neo4j. 23 `MythosTool` nodes + 1 `MythosToolClass` node. `patchbase-methods` CLI live at `/opt/mythos/bin/`.

**2026-04-21** (SYS-0093): Iris skill deployed. 8 intent handlers, rule-based regex routing. Import path: `from data.autodoc2_query import Autodoc2QuerySkill` with `/opt/mythos/skills` on sys.path.

**2026-04-21** (SYS-0094): Letter G complete. `autodoc2_worker.py` deployed. Weekly timer active. `tools/autodoc.py` archived to `tools/archive/autodoc_v1.py`. `bin/autodoc` symlink removed.

---

*AutoDoc2: the system that knows what the system is.*
*Eleven walkers. One graph. Weekly crawl. Zero guessing.*
