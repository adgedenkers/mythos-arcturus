# AutoDoc2 — Complete Architecture Plan

**Status:** ARC COMPLETE — all letters A→G shipped (F deferred)
**Stream:** SYS
**Version:** v1
**Pattern:** Follows `docs/SUB-SYSTEMS.md` sub-system pattern (N=3)
**Last updated:** 2026-04-21 (SYS-0094)

---

## 1. Context and what this system is

AutoDoc2 is a multi-language codebase documentation and structural analysis
engine running on Mythos. It crawls any target directory, parses every
source file via tree-sitter, writes structural facts (files, functions,
classes, imports) to Neo4j, and optionally runs per-file LLM structural
analysis returning structured JSON.

The engine was built and shipped before the sub-system pattern was adopted
(approximate patches SYS-0053 through SYS-0058, April 2026). It originated
as a capability demo for the Tony Miller / M7 partnership pitch — the
headline proof point was crawling the Strapi v5.9.0 monorepo (4,994 files,
22.5 seconds) live during a screenshare. The M7 relationship established an
IP licensing model: Denkers Co. retains all AutoDoc2 IP, M7 brings
enterprise clients.

The formal sub-system arc (Letters A→G) formalized what existed, added the
`ollama-analyze` microtool, registered PatchBase in Neo4j, added an Iris
skill for natural-language codebase queries, and closed with scheduled
re-crawl and legacy retirement. All letters complete as of 2026-04-21.

---

## 2. Deployed system (current state)

### 2.1 The engine

`/opt/mythos/tools/autodoc2/` is a complete Python package:

- **`engine.py`** — `AutodocEngine`: orchestrates the crawl. Pre-flight
  counts source files, connects Neo4j, iterates files, dispatches to
  walkers, writes to Neo4j, optionally runs analyzer, writes markdown.
- **`analyzer.py`** — SYS-0088: `Analyzer` class calling `qwen3-coder:30b`
  per file. Returns `AnalysisResult` dataclass. Non-fatal. Opt-in via
  `--analyze` flag. `ANALYSIS_MODEL = "qwen3-coder:30b"` (locked).
- **`walker.py`** — `LanguageWalker` base class. All walkers inherit and
  implement `parse_file(path, relative_path, source) → ParsedFile`.
- **`walkers/`** — 11 language walkers registered in a dict.
- **`neo4j_writer.py`** — all Neo4j write logic. Includes `write_analysis()`
  method (SYS-0088) that sets `analysis_*` properties on `AutodocFile` nodes.
- **`markdown_writer.py`** — per-file markdown and index generation.
- **`llm_client.py`** — thin Ollama stub for optional markdown summaries
  (separate from `analyzer.py` — different purpose, different model).
- **`config.py`** — env file + CLI arg loading. Includes `analyze: bool`.
- **`filters.py`** — extension → language mapping, skip rules.
- **`cli.py`** — argparse entry point, symlinked to `/opt/mythos/bin/autodoc2`.
  Includes `--analyze` / `-a` flag (SYS-0088).

### 2.2 Supporting tools

- **`patchbase_register.py`** — SYS-0092. AST-extracts PatchBase public
  methods, writes `MythosTool` nodes to Neo4j, `patchbase-methods` CLI.
- **`autodoc2_worker.py`** — SYS-0094. Scheduled re-crawl worker. Snapshots
  pre-crawl state, runs `autodoc2 --skip-llm`, computes diff, sends Telegram.
- **`autodoc2_query.py`** (in `skills/data/`) — SYS-0093. Iris skill with 8
  intent handlers. Rule-based regex routing, direct Neo4j queries.

### 2.3 Systemd units

- `mythos-autodoc2-crawl.service` — one-shot service, runs the worker
- `mythos-autodoc2-crawl.timer` — weekly, Sunday 3am, 30min random delay

### 2.4 Neo4j schema

**AutoDoc2 crawl nodes:**

| Label | Contents |
|-------|----------|
| `AutodocCrawl` | One per crawl run — target, timestamp, file count, status |
| `AutodocFile` | One per source file — path, language, line count, + `analysis_*` props |
| `AutodocFunction` | Functions/methods — name, qualified name, line numbers, docstring |
| `AutodocClass` | Classes, interfaces — name, bases, line numbers |
| `AutodocModule` | One per imported module name |

**Analysis properties on AutodocFile (opt-in):**

```
analysis_complexity:       "low" | "medium" | "high"
analysis_coupling_signals: ["signal1", ...]
analysis_patterns:         ["pattern1", ...]
analysis_drift_risk:       "low" | "medium" | "high"
analysis_notable:          "one sentence or empty"
analysis_model:            "qwen3-coder:30b"
analysis_timestamp:        ISO datetime
```

**PatchBase registration nodes:**

| Label | Contents |
|-------|----------|
| `MythosToolClass` | One node: `{name: 'PatchBase', source_path: '...'}` |
| `MythosTool` | One per public PatchBase method — signature, docstring, lineno |

Relationships: `MythosToolClass -[:HAS_METHOD]-> MythosTool`

### 2.5 Supported languages

Python, JavaScript, TypeScript, TSX, SQL, PHP, Go, Bash, YAML, JSON, Rust.
11 walkers. All via `tree-sitter-language-pack`.

---

## 3. The ollama-analyze microtool (Letter B — shipped SYS-0088/0090)

### 3.1 Model decision

`qwen3-coder:30b` — code-specialized, no safety filtering, structured JSON
output. `gemma4:26b` was the original plan but was rejected: returns empty
responses on code analysis prompts (safety filtering). Model is locked via
`ANALYSIS_MODEL` constant in `analyzer.py`.

The separation is architectural: **Iris (`qwen3:30b-a3b`) handles spiritual
and synthesis work. `qwen3-coder:30b` handles structural code analysis.**
They never call each other. Different data, different modes.

### 3.2 Input / output

Input: structured metadata from tree-sitter (no source code). Functions,
classes, imports, line count. Capped at 40 functions, 20 classes, 30 imports.

Output: `AnalysisResult` dataclass → `to_neo4j_props()` → stored as
`analysis_*` properties on `AutodocFile`. All nullable.

### 3.3 Performance

~15s per file on Arcturus (RTX 5090, qwen3-coder:30b). For 21 files (test
crawl): 307s total, 21/21 success, 0 failures. For full Mythos crawl
(~1,725 files): ~7 hours — which is why `--analyze` stays opt-in.

### 3.4 Triggering

```bash
autodoc2 --analyze              # full crawl + per-file analysis
autodoc2 --analyze --skip-llm   # analysis only, no markdown summaries
```

---

## 4. Graph coverage gate (Letter C — shipped SYS-0091)

After every patch install, `post_install.py` step 1.5 queries Neo4j directly
(bypassing the broken `integrity.graph` import) to verify each deployed file
exists as an `IntegrityFile` node with `status: 'active'`. Non-fatal — warns
but doesn't block. Will be made fatal once the `integrity.graph` crash loop
is resolved.

---

## 5. PatchBase microtool registration (Letter D — shipped SYS-0092)

`patchbase_register.py` uses Python AST to extract all public PatchBase
method signatures and docstrings, then writes `MythosTool` nodes to Neo4j.
`patchbase-methods` CLI dumps the live API to stdout for diagnostic bundles.

23 methods registered as of SYS-0092. Adge added more methods after that
patch — re-run `patchbase-methods --register` to sync Neo4j.

---

## 6. Iris skill (Letter E — shipped SYS-0093)

`skills/data/autodoc2_query.py` — `Autodoc2QuerySkill`. 8 intent handlers:

| Intent | Example query |
|--------|---------------|
| `files_importing` | "what files import neo4j" |
| `functions_in_file` | "show me functions in engine.py" |
| `function_detail` | "what does function run_crawl do" |
| `classes_in_file` | "classes in walker.py" |
| `high_drift_risk` | "high drift risk files" |
| `high_complexity` | "high complexity files" |
| `file_count` | "how many files in the codebase" |
| `languages` | "what languages does mythos use" |
| `search_generic` | "find files matching ephemeris" |

Rule-based regex routing — no LLM for query translation. Iris handles
response formatting. Import path: `from data.autodoc2_query import Autodoc2QuerySkill`
with `/opt/mythos/skills` on sys.path.

---

## 7. Telegram integration (Letter F — deferred)

Not blocking anything. The Iris skill handles natural-language queries.
When Letter F ships, it registers these commands in `mythos_bot.py`:

| Command | Action |
|---|---|
| `/autodoc` | Show crawl status — last crawl date, file count, language breakdown |
| `/autodoc crawl` | Trigger a re-crawl of `/opt/mythos/` |
| `/autodoc crawl <path>` | Crawl a specific target |
| `/autodoc query <question>` | Natural-language graph query via Iris skill |

---

## 8. Reliability (Letter G — shipped SYS-0094)

### 8.1 Scheduled re-crawl

`workers/autodoc2_worker.py` runs weekly (Sunday 3am via systemd timer).
Snapshots pre-crawl Neo4j state, runs `autodoc2 --skip-llm`, computes diff
(files added/removed, function delta), sends Telegram summary.

On-demand:
```bash
sudo systemctl start mythos-autodoc2-crawl.service
journalctl -u mythos-autodoc2-crawl.service -f
```

### 8.2 Legacy tool retirement

`tools/autodoc.py` (1,612 lines, Python-only, hardcoded target) archived to
`tools/archive/autodoc_v1.py` in SYS-0094. The `bin/autodoc` symlink removed.
Use `autodoc2` for all crawl operations.

---

## 9. Actual patch numbers used

| Letter | Scope | Actual Patch(es) | Date |
|--------|-------|-----------------|------|
| A | Subsystem docs | SYS-0086 | 2026-04-21 |
| B | `ollama-analyze` microtool | SYS-0088 (ship) + SYS-0090 (lock model) | 2026-04-21 |
| C | Graph coverage gate | SYS-0091 | 2026-04-21 |
| D | PatchBase microtool registration | SYS-0092 | 2026-04-21 |
| E | Iris skill | SYS-0093 | 2026-04-21 |
| F | Telegram commands | — | deferred |
| G | Reliability + legacy retirement | SYS-0094 | 2026-04-21 |

Intermediate patches: SYS-0087 (PatchBase microtool kit — landed before
our arc, adds `str_replace` + 7 helpers), SYS-0089 (skipped/renumbered).

---

## 10. Key technical decisions

**qwen3-coder:30b for analysis, qwen3:30b-a3b for Iris.** Architectural
separation — different cognitive modes. Never call each other.

**Analysis is opt-in.** Default crawl stays fast (22.5s for 4,994 files).
`--analyze` adds ~15s/file. Use it on targeted modules, not full crawls.

**Input is parsed structure, not source.** Smaller prompts, reproducible
results, source stays local.

**Neo4j schema is additive.** `analysis_*` properties are all nullable.
Existing queries continue to work unchanged.

**One crawl_id per target.** SHA1 of resolved target path. Re-crawl same
target → overwrites same nodes (or `--clean` wipes first).

**post_install.py uses direct neo4j driver for coverage gate.** Bypasses
the broken `integrity.graph` module. Non-fatal. See REQUESTS.md.

---

*AutoDoc2: the codebase as a queryable graph.*
*Eleven walkers. One graph. Weekly crawl. Zero guessing.*
