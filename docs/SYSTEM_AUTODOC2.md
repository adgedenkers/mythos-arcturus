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

> **Workflow:** see `docs/WORKFLOW.md`
> **Design plan:** see `docs/AUTODOC2_V2.md`
> **Pattern:** see `docs/SUB-SYSTEMS.md`
> **This doc:** canonical current state of AutoDoc2. Updated after
> every patch lands. Read this before starting any AutoDoc2 conversation.

---

## Status

- **Build phase:** BOOTSTRAPPED — engine and all walkers shipped pre-subsystem-pattern; formal A→G arc begins now
- **Last shipped patch:** Pre-pattern (SYS-0053 through SYS-0058 approximate range — AutoDoc2 deployed without subsystem docs)
- **Next patch:** SYS-0086 — subsystem registration + `SYSTEM_AUTODOC2.md` + `AUTODOC2_V2.md` + `docs/autodoc2/NEXT_PATCH_SPEC.md` (doc-only, no code)
- **Next code patch:** SYS-0087 — `ollama-analyze` microtool using `gemma4:26b`
- **Design plan:** `docs/AUTODOC2_V2.md`

---

## Architecture Summary

AutoDoc2 is a **multi-language codebase documentation engine** living at
`/opt/mythos/tools/autodoc2/`. It crawls a target directory, parses every
source file via tree-sitter, and writes structural facts to Neo4j plus
optional markdown summaries to disk. It replaces the legacy single-file
`tools/autodoc.py` (1,612 lines, Python-only, hardcoded target).

The engine is a Python package (`import autodoc2`) with a CLI entry point
symlinked to `/opt/mythos/bin/autodoc2`. It supports 11 languages via
`tree-sitter-language-pack` and writes to Neo4j using labels that are
compatible with the legacy autodoc crawl schema (`AutodocFile`,
`AutodocFunction`, `AutodocClass`, `AutodocModule`, `AutodocCrawl`).

Crawls target any directory (not just `/opt/mythos/`). Multiple crawl
targets are isolated by `crawl_id` in Neo4j. The demo-era infrastructure
(Strapi crawl, demo-live/demo-complete Neo4j containers, Jupyter notebook)
was built for the M7 Tony Miller partnership pitch in April 2026.

The `llm_client.py` module currently calls whatever model is configured
via `config.py`. The planned `ollama-analyze` microtool (SYS-0087) will
replace this with a dedicated `gemma4:26b` call returning structured JSON
analysis — no prose, no personality, pure technical signal.

---

## Patch Ledger

### Pre-pattern patches (retroactive record)

These patches shipped AutoDoc2 before the subsystem pattern was adopted.
Exact patch numbers are approximate — check PATCH_HISTORY.md for confirmed
numbers.

| Scope | Approx Patch # | Notes |
|-------|----------------|-------|
| AutoDoc2 skeleton — package structure, CLI, Python walker, Neo4j writer, markdown writer, LLM client stub | SYS-0053 | Phase 1. tree-sitter-languages replaced with tree-sitter-language-pack in SYS-0054 due to incompatibility |
| JS + TS + TSX walkers | SYS-0055 | Phase 2. TSX subclass of TypeScriptWalker. .d.ts files excluded |
| SQL, PHP, Go, Bash, YAML walkers | SYS-0056–0057 approx | Phase 3. JSON and Rust also added |
| Demo infrastructure — demo-live/demo-complete Neo4j containers, Jupyter notebook, prep_demo_graphs.sh, autodoc2-demo CLI | SYS-0058–0060 approx | M7 demo. Strapi v5.9.0 crawl: 4,994 files, 22.5 seconds |

### Formal letter sequence (begins now)

| Letter | Scope | Patch # | Shipped |
|--------|-------|---------|---------|
| A | Subsystem registration — this doc, AUTODOC2_V2.md, NEXT_PATCH_SPEC.md, _INDEX.md + SUB-SYSTEMS.md updates | SYS-0086 | — |
| B | `ollama-analyze` microtool — gemma4:26b per-file structural analysis, JSON output, stored as AutodocFile properties in Neo4j | SYS-0087 | — |
| C | Neo4j graph coverage gate — every deployed AutoDoc2 tool/script registered as queryable node; post-patch verification asserts graph reflects deployed state | — | — |
| D | PatchBase microtool registration — `patchbase-methods` CLI dumps API from Neo4j; `ollama-analyze` callable during patch build, not just post-hoc | — | — |
| E | Iris skill — `autodoc2_query` Iris skill enabling natural-language queries against the graph ("what files import postgres?", "show me the functions in transit_pressure.py") | — | — |
| F | Telegram integration — `/autodoc` command, `/autodoc crawl <target>`, `/autodoc query <question>` via Iris skill | — | — |
| G | Reliability — crawl diffing (detect deleted files, new files, changed signatures), scheduled re-crawl of /opt/mythos, result summary to Telegram | — | — |

---

## Current Disk State

### Package

```
/opt/mythos/tools/autodoc2/
├── __init__.py          # version: "2.0.0-phase1"
├── cli.py               # argparse entry point (executable)
├── config.py            # env file + CLI arg loading
├── engine.py            # AutodocEngine: orchestrates crawl, dispatch, writes
├── filters.py           # skip rules, extension → language mapping
├── walker.py            # LanguageWalker base class
├── llm_client.py        # Ollama summarizer (thin stub — to be replaced by ollama-analyze)
├── markdown_writer.py   # per-file + index markdown output
├── neo4j_writer.py      # all Neo4j write logic
└── walkers/
    ├── __init__.py          # walker registry
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

### CLI

```
/opt/mythos/bin/autodoc2  →  /opt/mythos/tools/autodoc2/cli.py
```

### Legacy

```
/opt/mythos/tools/autodoc.py   # 1,612-line monolith, Python-only. Not removed yet.
```

Legacy autodoc.py should be archived or deleted in Letter G after AutoDoc2
has proven stable with scheduled crawls.

### Output from last crawl (April 4, 2026)

```
/opt/mythos/docs/autodoc/
├── index.json          # 1,725 files indexed across 5 streams
├── INDEX.md            # human-readable index
├── system_overview.md  # LLM-generated architecture summary
├── files/              # per-file markdown (1,725 files)
├── modules/            # per-module markdown (19 modules)
└── streams/            # per-stream overview markdown
```

This output is from the **legacy autodoc.py**, not from AutoDoc2 (which
writes to Neo4j and `docs/autodoc2/` when targeting `/opt/mythos/`).

---

## Neo4j State (as of last crawl)

The current Neo4j graph reflects a crawl of `/opt/mythos/` itself:

| Label | Count |
|-------|-------|
| AutodocCrawl | 1 |
| AutodocFile | 1,725 |
| AutodocFunction | 5,085 |
| AutodocClass | 721 |
| AutodocModule | 19 |

crawl_id: `autodoc2_mythos_<hash>` (single crawl node)

The demo-era Strapi crawl (4,994 files) ran against isolated
`demo-live`/`demo-complete` Neo4j containers on ports 7688/7689.
Those containers may or may not still be running — check
`docker ps | grep demo` before any demo-related work.

---

## Supported Languages

| Language | Walker | Notes |
|---|---|---|
| Python | python_walker.py | Functions, classes, imports, decorators |
| JavaScript | javascript_walker.py | Functions, classes, imports, exports |
| TypeScript | typescript_walker.py | Interfaces stored as AutodocClass with `bases=['__interface__']` |
| TSX | typescript_walker.py (TsxWalker) | Subclass, tsx grammar key |
| SQL | sql_walker.py | Tables, views, functions |
| PHP | php_walker.py | Functions, classes |
| Go | go_walker.py | Functions, structs, interfaces |
| Bash | bash_walker.py | Functions |
| YAML | yaml_walker.py | Top-level keys |
| JSON | json_walker.py | Schema structure |
| Rust | rust_walker.py | Functions, structs, enums, traits |

`.d.ts` TypeScript declaration files are excluded via glob pattern and
compound-extension check in `filters.language_for_path()`.

---

## How to use

### Crawl Mythos itself

```bash
autodoc2                     # target=/opt/mythos, output=docs/autodoc2/
autodoc2 --verbose           # show per-file parse stats
autodoc2 --skip-llm          # skip LLM summaries (much faster)
autodoc2 --clean             # wipe existing crawl data first
```

### Crawl an external repo

```bash
autodoc2 /path/to/repo --output-dir /tmp/repo-docs --skip-llm
```

### Query the graph after crawl

```cypher
-- All functions in a file
MATCH (f:AutodocFile {relative_path: 'astrology/ephemeris.py'})
      -[:CONTAINS]->(fn:AutodocFunction)
RETURN fn.name, fn.lineno

-- All classes across the crawl
MATCH (n:AutodocClass) RETURN n.name, n.file_path LIMIT 50

-- Files by language
MATCH (f:AutodocFile) RETURN f.language, count(*) ORDER BY count(*) DESC
```

---

## Known Issues / Debt

1. **`llm_client.py` is a thin stub** — calls Ollama but is not wired to `gemma4:26b` or any specific technical model. LLM summaries are generic prose. Letter B replaces this with `ollama-analyze`.
2. **Legacy autodoc.py not retired** — both tools coexist. The legacy tool's output (`docs/autodoc/`) predates AutoDoc2's output (`docs/autodoc2/`). Letter G retires the legacy tool.
3. **No graph coverage gate** — after a crawl, there's no assertion that Neo4j reflects the actual deployed state. Letter C adds this.
4. **Demo infrastructure state unknown** — demo-live/demo-complete Docker containers were created for the M7 pitch and may be stale. Check before any demo-related work.
5. **`__init__.py` still says `2.0.0-phase1`** — version string was never updated after Phase 3 walkers shipped.
6. **No Iris skill** — AutoDoc2 graph is not queryable via natural language from Telegram. Letter E adds this.
7. **No scheduled re-crawl** — the graph goes stale unless manually re-run. Letter G adds a scheduled worker.

---

## Post-pattern Work (from REQUESTS.md)

Two requests filed during Astrology v2 arc:

1. **SYS: Full graph coverage + post-patch verification gate** — after integrity scan, assert graph state is valid and queryable. Fails patch-install if graph doesn't reflect deployed state. This is AutoDoc2 Letter C.
2. **SYS: PatchBase microtool kit with Ollama integration** — patches invoke local LLM to analyze files/changes, return structured JSON. `ollama-analyze` is the first microtool. This is AutoDoc2 Letter B (the microtool) + Letter D (PatchBase integration).

---

## Incoming Notes

> Append-only, date-stamped, never edit.

**2026-04-21** (SYS-0086): AutoDoc2 registered as Mythos sub-system #3. Engine + all 11 walkers were pre-pattern. Formal letter sequence A→G established. gemma4:26b confirmed pulled and available for ollama-analyze.

**2026-04-21**: Adge confirmed AutoDoc2 belongs to SYS stream. `gemma4:26b` chosen for ollama-analyze specifically because it is technically precise and grounded — no mysticism, no personality drift. Iris (`qwen3:30b-a3b`) handles spiritual/synthesis; gemma4 handles structural code analysis.

---

*AutoDoc2: the system that knows what the system is.*
*Eleven walkers. One graph. The codebase as a queryable fact.*
