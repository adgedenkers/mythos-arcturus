---
title: "Docs Librarian Specification"
category: reference
status: active
stream: null
location: docs
tags: [docs, spec, system]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Mythos Docs Librarian — Autonomous Documentation Management

## Summary

A reusable, autonomous system that keeps the Mythos documentation library
organized. Markdown files self-describe via YAML frontmatter. A scanner
reads that metadata to file, move, and index documents automatically.
An Ollama classifier handles unknown files that lack frontmatter.

---

## 1. Frontmatter Schema

Every markdown document in the Mythos ecosystem should carry this
YAML frontmatter block at the top of the file:

```yaml
---
title: "Human-readable title"
category: consciousness | methods | finance | tools | streams | grid | orchestrator | design-patterns | reference | planning
status: active | draft | stale | superseded | archive
stream: NEU | LOG | MNE | SEN | SYS | null
location: docs | downloads | external
tags: [iris, autonomic, transit, genealogy, tarot, astrology]
created: 2026-03-12
updated: 2026-03-12
author: katuar | seraphe | iris | claude
---
```

### Field Definitions

| Field | Required | Values | Purpose |
|-------|----------|--------|---------|
| `title` | yes | free text | Display name for indexes |
| `category` | yes | enum (see above) | Maps to docs subdirectory |
| `status` | yes | active/draft/stale/superseded/archive | Lifecycle state |
| `stream` | no | NEU/LOG/MNE/SEN/SYS/null | Owning dev stream, null if cross-cutting |
| `location` | yes | docs/downloads/external | Where the file *should* live |
| `tags` | no | list of strings | Searchable tags for Iris and Neo4j |
| `created` | yes | ISO date | Creation date |
| `updated` | yes | ISO date | Last meaningful update |
| `author` | no | katuar/seraphe/iris/claude | Who wrote/generated it |

### Category → Directory Mapping

| Category | Target Directory |
|----------|-----------------|
| consciousness | /opt/mythos/docs/consciousness/ |
| methods | /opt/mythos/docs/methods/ |
| finance | /opt/mythos/docs/finance/ |
| tools | /opt/mythos/docs/tools/ |
| streams | /opt/mythos/docs/streams/ |
| grid | /opt/mythos/docs/grid/ |
| orchestrator | /opt/mythos/docs/orchestrator/ |
| design-patterns | /opt/mythos/docs/design-patterns/ |
| reference | /opt/mythos/docs/ (root) |
| planning | /opt/mythos/docs/ (root) |

### Status Routing

| Status | Action |
|--------|--------|
| active | Move to target directory |
| draft | Move to target directory (drafts live alongside active docs) |
| stale | Move to archive/stale/ |
| superseded | Move to archive/superseded/ |
| archive | Move to archive/ |

---

## 2. Scanner Script — `docs-librarian`

The scanner is a Python CLI tool that:
1. Scans one or more directories for `.md` files
2. Reads YAML frontmatter from each
3. Applies routing rules (category → directory, status → archive)
4. Moves files to their correct location
5. Flags files without frontmatter for classification
6. Regenerates `_INDEX.md` after changes
7. Logs all actions

### CLI Interface

```bash
# Scan Downloads, move docs-bound files, report unknowns
docs-librarian scan ~/Downloads

# Scan Downloads and auto-classify unknowns via Ollama
docs-librarian scan ~/Downloads --classify

# Scan the docs directory itself for misplaced or stale files
docs-librarian audit

# Regenerate _INDEX.md from current docs state
docs-librarian reindex

# Show what would happen without moving anything
docs-librarian scan ~/Downloads --dry-run

# Backfill frontmatter into existing docs that lack it
docs-librarian backfill /opt/mythos/docs
```

### Core Logic (pseudocode)

```
for each .md file in scan_path:
    frontmatter = parse_yaml_header(file)

    if frontmatter is None:
        if --classify flag:
            frontmatter = ollama_classify(file)
            inject_frontmatter(file, frontmatter)
        else:
            add_to_unknown_report(file)
            continue

    if frontmatter.location == "docs":
        target_dir = category_to_dir(frontmatter.category)
        target_name = to_screaming_snake(frontmatter.title) + ".md"

        if frontmatter.status in ("stale", "superseded", "archive"):
            target_dir = archive_subdir(frontmatter.status)

        move(file, target_dir / target_name)
        log_action("moved", file, target_dir / target_name)

    # Files with location=downloads or location=external stay put
```

### Non-Markdown File Tracking

Files that aren't markdown (`.json`, `.py`, `.xlsx`, `.jsx`, `.sql`, etc.)
are NOT auto-moved but ARE tracked in a manifest:

```
/opt/mythos/docs/live/downloads_manifest.json
```

This manifest records what's in Downloads, when it was last seen, and
a best-guess category (from filename patterns or Ollama classification).
Iris can use this to suggest cleanup actions or flag stale artifacts.

---

## 3. Ollama Classifier

For files without frontmatter, the librarian can call the local Ollama
instance to read the file and generate frontmatter.

### Classification Prompt

```
You are the Mythos documentation librarian. Read the following markdown
document and generate YAML frontmatter for it.

Rules:
- category must be one of: consciousness, methods, finance, tools,
  streams, grid, orchestrator, design-patterns, reference, planning
- status must be one of: active, draft, stale, superseded, archive
- stream must be one of: NEU, LOG, MNE, SEN, SYS, or null
- location should be "docs" if this is documentation/reference material,
  "downloads" if it's a one-time deliverable or session artifact
- tags should be 1-5 relevant keywords
- author should be katuar, seraphe, iris, or claude based on content

Respond with ONLY the YAML frontmatter block, no explanation.

Document content:
{file_content_first_2000_chars}
```

### Confidence Gating

The classifier returns frontmatter, but the decision gate applies:
- If the file clearly matches a known category → auto-move
- If ambiguous → add to review queue (Telegram notification to Adge)
- Never auto-move files > 30 days old without confirmation

---

## 4. Idle Task Definition

This runs as an Iris autonomic idle task.

### Task Registration

```json
{
    "task_id": "docs_librarian_scan",
    "name": "Documentation Library Scan",
    "description": "Scan Downloads and docs for filing, cleanup, and index updates",
    "trigger": "idle",
    "priority": 3,
    "cooldown_minutes": 360,
    "steps": [
        {
            "action": "scan_downloads",
            "path": "~/Downloads",
            "classify": true,
            "dry_run": false
        },
        {
            "action": "audit_docs",
            "path": "/opt/mythos/docs"
        },
        {
            "action": "reindex",
            "path": "/opt/mythos/docs"
        },
        {
            "action": "report",
            "notify": "telegram",
            "summary": true
        }
    ]
}
```

### What the Idle Task Does

1. **Scan ~/Downloads** for new `.md` files with frontmatter → auto-file
2. **Classify unknowns** via Ollama → auto-file high-confidence, queue low-confidence
3. **Audit /opt/mythos/docs** → flag files without frontmatter, detect naming violations
4. **Regenerate _INDEX.md** from actual directory state
5. **Update downloads_manifest.json** for non-markdown tracking
6. **Send Telegram summary** — what was moved, what needs review, any anomalies

### Telegram Report Format

```
📚 Docs Librarian Report

Filed: 3 documents
  → SERAPHE_NATAL_LUNAR_POINTS.md → methods/
  → CC3_ARCHITECTURE.md → root (reference)
  → VAULT_OPERATIONS_GUIDE.md → root (reference)

Needs Review: 1 document
  → cognitive_ai_architecture_supplement.md (ambiguous category)

Index: Regenerated ✓
Downloads: 47 non-doc files tracked
```

---

## 5. _INDEX.md Auto-Generation

The `reindex` command rebuilds `_INDEX.md` by:

1. Walking the docs directory tree
2. Reading frontmatter from every `.md` file found
3. Grouping by category/directory
4. Generating the markdown table for each section
5. Including the "For Iris" section at the bottom
6. Writing to `/opt/mythos/docs/_INDEX.md`

Files without frontmatter get listed in a "⚠ Unindexed" section at the
bottom so they're visible but clearly flagged.

---

## 6. Backfill Strategy

Existing docs in `/opt/mythos/docs/` don't have frontmatter yet. The
`backfill` command handles this:

1. Scan all `.md` files in docs
2. For each file without frontmatter:
   - Infer category from directory location
   - Infer status as "active" (it's in the live docs)
   - Use Ollama to generate tags and confirm category
   - Inject frontmatter at top of file
3. Commit changes via git

This is a one-time operation to bootstrap the system. After that, all
new docs are expected to carry frontmatter from creation.

---

## 7. Implementation Plan

### Phase 1: Schema + Scanner (no Ollama)
- Define frontmatter schema (this doc)
- Build `docs-librarian` CLI (Python, symlink to /opt/mythos/bin/)
- Implement `scan`, `audit`, `reindex` commands
- Implement `--dry-run` for safe testing
- Backfill existing docs with frontmatter

### Phase 2: Ollama Classification
- Build classifier prompt
- Integrate with local Ollama endpoint
- Add confidence gating
- Add `--classify` flag to scan command

### Phase 3: Idle Task Integration
- Register as autonomic idle task
- Wire up Telegram reporting
- Add downloads manifest tracking
- Set cooldown and priority

### Phase 4: Neo4j Integration
- Push document metadata to Neo4j as `:Document` nodes
- Link to `:Stream`, `:Category`, `:Tag` nodes
- Enable graph queries: "show me all active NEU docs about consciousness"

---

## Stream Ownership

This system spans LOG (skill/tool infrastructure) and SYS (system utilities).
Primary ownership: **SYS** (it's system maintenance tooling).
The Ollama classification piece touches LOG (orchestrator routing).

Patch sequence: SYS for the CLI + idle task, LOG if orchestrator changes needed.
