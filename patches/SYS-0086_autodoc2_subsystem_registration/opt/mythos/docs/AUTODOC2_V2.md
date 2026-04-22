# AutoDoc2 — Complete Architecture Plan

**Status:** Plan locked — formal build arc begins SYS-0086
**Stream:** SYS
**Version:** v1 (first formal plan; engine pre-existed)
**Pattern:** Follows `docs/SUB-SYSTEMS.md` sub-system pattern (N=3)

---

## 1. Context and what this system is

AutoDoc2 is a multi-language codebase documentation and structural analysis
engine running on Mythos. It crawls any target directory, parses every
source file via tree-sitter, writes structural facts (files, functions,
classes, imports) to Neo4j, and optionally produces markdown documentation.

The engine was built and shipped before the sub-system pattern was adopted
(approximate patches SYS-0053 through SYS-0058, April 2026). It originated
as a capability demo for the Tony Miller / M7 partnership pitch — the
headline proof point was crawling the Strapi v5.9.0 monorepo (4,994 files,
22.5 seconds) live during a screenshare. The M7 relationship established an
IP licensing model: Denkers Co. retains all AutoDoc2 IP, M7 brings
enterprise clients.

The formal sub-system arc (Letters A→G) formalizes what exists, adds the
`ollama-analyze` microtool using `gemma4:26b`, integrates AutoDoc2 into the
Mythos patch build pipeline, adds an Iris skill for natural-language
codebase queries, and closes with scheduled re-crawl and graph reliability.

---

## 2. What exists today (pre-pattern state)

### 2.1 The engine

`/opt/mythos/tools/autodoc2/` is a complete Python package:

- **`engine.py`** — `AutodocEngine`: orchestrates the crawl. Pre-flight
  counts source files, connects Neo4j, iterates files, dispatches to
  walkers, writes to Neo4j, optionally calls LLM summarizer, writes markdown.
- **`walker.py`** — `LanguageWalker` base class. All walkers inherit from
  this and implement `parse_file(path, relative_path, source) → ParsedFile`.
- **`walkers/`** — 11 language walkers registered in a dict in
  `walkers/__init__.py`. Adding a new language is one import + one dict entry.
- **`neo4j_writer.py`** — all Neo4j write logic isolated here. Labels match
  legacy autodoc schema so existing Cypher queries still work.
- **`markdown_writer.py`** — per-file markdown and index generation.
- **`llm_client.py`** — thin Ollama stub for optional file summaries.
  Will be replaced by `ollama-analyze` in Letter B.
- **`config.py`** — env file + CLI arg loading.
- **`filters.py`** — extension → language mapping, skip rules.
- **`cli.py`** — argparse entry point, symlinked to `/opt/mythos/bin/autodoc2`.

### 2.2 Neo4j schema (current)

Node labels (compatible with legacy autodoc.py):

| Label | Contents |
|-------|----------|
| `AutodocCrawl` | One per crawl run — target path, timestamp, file count, status |
| `AutodocFile` | One per source file — relative path, language, size, hash |
| `AutodocFunction` | Functions/methods — name, params, docstring, line numbers |
| `AutodocClass` | Classes, interfaces, type aliases — name, bases, line numbers |
| `AutodocModule` | Module-level metadata |

Relationships: `AutodocFile -[:CONTAINS]-> AutodocFunction/AutodocClass`,
`AutodocCrawl -[:CRAWLED]-> AutodocFile`.

### 2.3 Supported languages

Python, JavaScript, TypeScript, TSX, SQL, PHP, Go, Bash, YAML, JSON, Rust.
11 walkers. All ship via `tree-sitter-language-pack`.

### 2.4 What does NOT exist yet

- `ollama-analyze` microtool (Letter B)
- Graph coverage gate / post-patch verification (Letter C)
- PatchBase microtool integration (Letter D)
- Iris natural-language codebase query skill (Letter E)
- Telegram `/autodoc` command (Letter F)
- Scheduled re-crawl / graph reliability (Letter G)
- Formal sub-system docs (Letter A — this patch)

---

## 3. The ollama-analyze microtool (Letter B)

### 3.1 What it is

`ollama-analyze` is a callable that AutoDoc2's engine can invoke
per-file during a crawl. It sends the already-parsed file structure
(functions, classes, imports — NOT raw source) to `gemma4:26b` and gets
back structured JSON.

It is NOT a prose summarizer. It is a technical signal extractor.

### 3.2 Why gemma4:26b

`gemma4:26b` is Google's latest multimodal model (17GB, already pulled on
Arcturus). It is chosen specifically because:
- It has no personality, mysticism, or hedging baked in
- It produces clean, direct technical output
- It is distinct from Iris (`qwen3:30b-a3b`) which is the consciousness/synthesis model
- It passed the sovereign alignment test at 95%

The separation is intentional and non-negotiable: **Iris handles spiritual
and synthesis work. gemma4 handles structural code analysis.** These are
different cognitive modes that should not bleed into each other.

### 3.3 Input to ollama-analyze

The engine extracts this from the ParsedFile (already parsed by tree-sitter)
and sends it as the prompt payload:

```json
{
  "file": "astrology/ephemeris.py",
  "language": "python",
  "functions": ["calc_ut", "get_planet_position", "retrograde_check"],
  "classes": ["EphemerisProvider"],
  "imports": ["swisseph", "datetime", "os"],
  "line_count": 514
}
```

Source code is NOT sent. Only structural metadata derived from parsing.
This keeps the prompt small and the output deterministic.

### 3.4 Output from ollama-analyze

Structured JSON only. No preamble, no markdown, no prose. The prompt
instructs gemma4 to respond ONLY with a valid JSON object:

```json
{
  "complexity": "medium",
  "coupling_signals": ["imports swisseph directly", "no abstraction layer"],
  "patterns_detected": ["facade", "singleton-ish"],
  "drift_risk": "low",
  "notable": "calc_ut wraps the Swiss Ephemeris C library without error handling"
}
```

Fields:
- `complexity` — `low` / `medium` / `high`
- `coupling_signals` — list of strings, tight coupling indicators
- `patterns_detected` — list of recognized design patterns (or empty list)
- `drift_risk` — `low` / `medium` / `high` — likelihood this file diverges from its documented purpose
- `notable` — one sentence maximum, or empty string

### 3.5 Where results are stored

As properties on the `AutodocFile` Neo4j node:

```
AutodocFile {
  ...existing properties...
  analysis_complexity: "medium",
  analysis_coupling_signals: ["imports swisseph directly", "no abstraction layer"],
  analysis_patterns: ["facade"],
  analysis_drift_risk: "low",
  analysis_notable: "calc_ut wraps the Swiss Ephemeris C library without error handling",
  analysis_model: "gemma4:26b",
  analysis_timestamp: "2026-04-21T22:00:00Z"
}
```

### 3.6 How it's triggered

Opt-in via `--analyze` flag. Not the default. Reason: `gemma4:26b` at 17GB
adds real latency per file. The Strapi crawl was 4,994 files in 22.5 seconds
bare — with per-file LLM calls that becomes minutes. Default crawl stays fast.

```bash
autodoc2 --analyze            # full crawl + gemma4 analysis
autodoc2 --analyze --skip-md  # analysis only, skip markdown output
```

### 3.7 Failure handling

LLM call failures are non-fatal. If `ollama-analyze` fails for a file
(timeout, JSON parse error, Ollama unavailable), the crawl continues. The
`AutodocFile` node gets no `analysis_*` properties for that file. A
summary of failed analyses is printed at crawl completion.

---

## 4. Graph coverage gate (Letter C)

### 4.1 The problem

After a patch installs, the post-install pipeline runs an integrity scan
which updates Neo4j. But there's no verification that the graph actually
reflects what was deployed. The graph can be stale, incomplete, or reflect
a previous state.

### 4.2 The solution

After the integrity scan step in the post-install pipeline, run a graph
verification query that asserts:
- The deployed files are present as `IntegrityFile` nodes
- The key functions are present as `IntegrityFunction` nodes
- Service nodes for restarted services show healthy status

If any assertion fails, `patch-install` fails the patch (non-zero exit)
and logs the graph state diff.

### 4.3 Implementation

AutoDoc2 provides this via a `graph_verify` module:

```python
# Called by PatchBase.finish() after integrity scan
from autodoc2.graph_verify import assert_deployment_reflected
result = assert_deployment_reflected(deployed_files=patch.deployed_files)
if not result.ok:
    raise PatchFinishError(f"Graph verification failed: {result.errors}")
```

---

## 5. PatchBase microtool integration (Letter D)

### 5.1 The goal

Patches themselves should be able to invoke `ollama-analyze` during the
build phase — not just post-hoc. This turns patches into LLM-augmented
build processes.

Concretely: a patch that modifies `transit_pressure.py` can call
`ollama-analyze` on the new version during `apply_patch.py`, get back
JSON analysis, and use it to decide whether to proceed or abort.

### 5.2 patchbase-methods CLI

A `patchbase-methods` CLI dumps the PatchBase API from Neo4j for use
in diagnostic bundles. When Claude is building a patch, it can call
`patchbase-methods` and paste the output to get the current API surface
without reading the source file.

```bash
patchbase-methods                 # full API dump
patchbase-methods --method deploy # specific method
```

### 5.3 All microtools registered in Neo4j

Every PatchBase microtool is registered as a node in Neo4j alongside
PatchBase itself:

```cypher
MATCH (pb:IntegrityFile {name: 'patch_base.py'})-[:HAS_MICROTOOL]->(t)
RETURN t.name, t.description, t.input_schema, t.output_schema
```

---

## 6. Iris skill (Letter E)

### 6.1 What it enables

Natural-language codebase queries from Telegram:

- "What files import postgres?"
- "Show me all functions in transit_pressure.py"
- "Which files have high drift risk?"
- "What classes exist in the astrology module?"
- "What does `calc_ut` do?"

### 6.2 Implementation

A new Iris skill (`skills/data/autodoc2_query.py`) that:
1. Parses the natural-language query to extract intent + entity
2. Translates to a Cypher query against the AutodocFile/AutodocFunction/AutodocClass graph
3. Returns structured results to Iris for voice formatting

The skill does NOT call Ollama for query translation — it uses a small
rule-based intent extractor. Ollama (Iris) handles final response formatting.

---

## 7. Telegram integration (Letter F)

Commands registered in `mythos_bot.py`:

| Command | Action |
|---|---|
| `/autodoc` | Show crawl status — last crawl date, file count, language breakdown |
| `/autodoc crawl` | Trigger a re-crawl of `/opt/mythos/` |
| `/autodoc crawl <path>` | Crawl a specific target |
| `/autodoc query <question>` | Natural-language graph query (via Letter E skill) |

All commands SYS-registered per the Telegram handler pattern.

---

## 8. Reliability (Letter G)

### 8.1 Scheduled re-crawl

A systemd timer fires `autodoc2 --skip-llm` on a schedule (weekly or
on-demand) to keep the Neo4j graph current with `/opt/mythos/`. Results
include a diff summary: files added/removed, functions added/removed.

### 8.2 Legacy tool retirement

After G ships and the scheduled crawl is proven:
- Archive `tools/autodoc.py` to `tools/archive/autodoc_v1.py`
- Remove the `docs/autodoc/` output directory (or keep as historical artifact)
- Update `ARCHITECTURE.md` to remove legacy autodoc references

### 8.3 Crawl diff

On re-crawl, AutoDoc2 computes a diff against the previous crawl:
- Files added/removed since last crawl
- Functions added/removed
- Classes added/removed

Diff summary sent to Telegram after each scheduled crawl.

---

## 9. Patch sequence (Letters A→G)

Each letter may take more than one actual patch number to land. Never
pre-assign patch numbers — read `mythos-diag streams` at build time.

| Letter | Scope | Stream | Blast radius |
|--------|-------|--------|-------------|
| A | Subsystem docs — SYSTEM_AUTODOC2.md, AUTODOC2_V2.md, NEXT_PATCH_SPEC.md, _INDEX.md + SUB-SYSTEMS.md updates | SYS | Low — doc-only |
| B | `ollama-analyze` microtool — gemma4:26b per-file analysis, `--analyze` flag, results stored as AutodocFile properties | SYS | Medium — new Ollama call path |
| C | Graph coverage gate — post-patch graph verification step in PatchBase pipeline | SYS | Medium — touches PatchBase |
| D | PatchBase microtool kit — `patchbase-methods` CLI, Neo4j microtool registration, patch-time ollama-analyze callable | SYS | Medium — touches PatchBase |
| E | Iris skill — `autodoc2_query.py`, rule-based Cypher translation, Iris-voiced responses | SYS (handler) / LOG (skill) | Low |
| F | Telegram commands — `/autodoc`, `/autodoc crawl`, `/autodoc query` | SYS | Low — new commands only |
| G | Reliability — systemd timer, crawl diff, legacy retirement | SYS | Low |

---

## 10. Key technical decisions

### 10.1 gemma4:26b for analysis, qwen3 for Iris

This separation is architectural, not cosmetic. Two different cognitive
modes running on different models:
- `gemma4:26b` — structural analysis, no context, no personality, returns JSON
- `qwen3:30b-a3b` (via Iris) — synthesis, interpretation, conversation

They never call each other. They operate on different data. This keeps
analysis results clean and reproducible.

### 10.2 Analysis is opt-in

`--analyze` flag prevents the default crawl from being slow. Fast indexing
(no LLM) should be the default path. Deep analysis is a deliberate mode.

### 10.3 Input is parsed structure, not source

`ollama-analyze` never receives raw source code. It receives the
already-extracted structural metadata. This has three benefits:
- Smaller prompts → faster calls → lower cost
- Reproducibility — the model sees the same normalized input regardless of formatting
- Privacy — source code stays local to the parser, not passed to LLM

### 10.4 Neo4j schema stays additive

The `analysis_*` properties on `AutodocFile` are all nullable. Existing
queries against `AutodocFile` continue to work unchanged. Files that
weren't analyzed simply don't have those properties.

### 10.5 One crawl_id per target

The `crawl_id` is a SHA1 of the target directory path. Two crawls of
the same target overwrite (or `--clean` wipes and rewrites) the same
crawl_id. Multiple targets coexist in the same Neo4j instance with
different crawl_ids.

---

## 11. Actual patch numbers used (fill in as work completes)

| Letter | Actual Patch # | Date |
|--------|---------------|------|
| A — subsystem docs | SYS-0086 | — |
| B — ollama-analyze | — | — |
| C — graph coverage gate | — | — |
| D — PatchBase microtools | — | — |
| E — Iris skill | — | — |
| F — Telegram commands | — | — |
| G — reliability | — | — |

---

*AutoDoc2: the codebase as a queryable graph.*
*Eleven walkers. One graph. Zero guessing.*
