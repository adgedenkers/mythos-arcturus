# Document Registry
> **Location:** `/opt/mythos/docs/DOCUMENT_REGISTRY.md`
> **Established:** Patch 0144
> **Status:** Authoritative reference for Iris's document repository system

---

## What This Is

The Document Registry is Iris's authoritative reference library. It's a Postgres-backed catalog of every standard, pattern, specification, guide, and reference document that Iris (or any AI session) might need to consult when performing work.

The key insight: **the model doesn't need to know React, Svelte, NIST standards, or genealogical methods at prompt time. It reads the appropriate reference document from the registry at task time.** The registry IS the tool.

---

## Core Concepts

### Documents Are Not Just Files

A registry entry is not just a pointer to a file. It's a metadata-rich object:

| Field | Purpose |
|-------|---------|
| `slug` | Machine-readable ID (`cmd-center-dev-guide`) |
| `title` | Human-readable name |
| `doc_type` | What kind of document (see types below) |
| `domain` | Knowledge domain (see domains below) |
| `version` | Semantic version — changes when content changes |
| `status` | `active`, `deprecated`, `draft`, `archived` |
| `summary` | 1-3 sentence description |
| `file_path` | Where the actual file lives on Arcturus |
| `file_hash` | SHA-256 for change detection |
| `supersedes` | Slug of the document this replaced |
| `superseded_by` | Slug of the document that replaced this |
| `tags` | Searchable keyword array |
| `metadata` | Flexible JSONB for anything else |

### Document Types

| Type | Use |
|------|-----|
| `build_pattern` | How to build something (Command Center dev guide, patch conventions) |
| `reference` | Living reference material (ARCHITECTURE.md, TODO.md) |
| `specification` | Formal specification (consciousness layers, grid, 81 functions) |
| `standard` | External standards (NIST, ISO, etc.) |
| `guide` | How-to guides and tutorials |
| `schema` | Database schemas, API specs |
| `policy` | Rules and policies |

### Domains

| Domain | Covers |
|--------|--------|
| `frontend` | Command Center, React, UI patterns |
| `backend` | FastAPI, Python, API conventions |
| `infrastructure` | Servers, services, deployment, patches |
| `finance` | Financial system, imports, forecasting |
| `consciousness` | Iris, grid, layers, perception |
| `astrology` | Soul Stratigraphy, calculations, charts |
| `genealogy` | Bloodline research, Merovingian connections |
| `security` | NIST, federal compliance, VA standards |
| `general` | Cross-cutting or uncategorized |

---

## How Iris Uses the Registry

### Discovery: "What do I need to know?"

When Iris (or a Claude session) needs to perform a task, the first step is querying the registry:

```
GET /api/docs/search?q=frontend
GET /api/docs/search?domain=consciousness
GET /api/docs/search?tag=react
GET /api/docs/search?doc_type=build_pattern
```

### Reading: "Let me learn this pattern"

Once Iris finds the right document, she reads its contents:

```
GET /api/docs/cmd-center-dev-guide/content
```

This returns the raw file contents — the full dev guide, specification, or standard. Iris ingests this into her context and follows it.

### Registration: "I made something that should be reusable"

After building something significant, Iris (or a patch) registers it:

```
POST /api/docs/register
{
  "slug": "svelte-dashboard-pattern",
  "title": "Svelte Dashboard Build Pattern",
  "doc_type": "build_pattern",
  "domain": "frontend",
  "version": "1.0.0",
  "summary": "How to build dashboard pages using SvelteKit + D3",
  "file_path": "/opt/mythos/docs/patterns/svelte_dashboard.md",
  "tags": ["svelte", "frontend", "dashboard", "d3"]
}
```

### Versioning: "The pattern changed"

When a document is updated, the old version is archived automatically:

```
PUT /api/docs/cmd-center-dev-guide
{
  "version": "1.1.0",
  "change_summary": "Added Svelte component pattern alongside React"
}
```

### Deprecation: "This was replaced by something better"

When a standard or pattern becomes obsolete:

```
POST /api/docs/nist-800-53-r4/deprecate
{
  "superseded_by": "nist-800-53-r5",
  "reason": "Rev 5 published, Rev 4 withdrawn by NIST"
}
```

The old document stays in the registry (for history) but is marked `deprecated` with a pointer to the replacement. Searches default to `status=active` so deprecated docs don't surface unless explicitly requested.

---

## Workflow for Adding External Standards

When a new external standard needs to be tracked (e.g., NIST SP 800-53 Rev 5):

1. **Obtain the document** — download PDF or extract relevant sections
2. **Store it** — save to `/opt/mythos/documents/standards/nist_800_53_r5.md` (or .pdf)
3. **Register it** — POST to `/api/docs/register` with full metadata
4. **If replacing an older version** — POST to `/api/docs/{old-slug}/deprecate`

The file itself lives on disk. The registry tracks where it is, what it contains, and whether it's current.

---

## Telegram Integration (Future)

Planned commands:
- `/docs search <query>` — Search the registry
- `/docs list [domain]` — List documents by domain
- `/docs read <slug>` — Iris reads and summarizes a document
- `/docs register <path>` — Register a file Iris just created

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/docs/search` | Search by query, domain, type, tag, status |
| GET | `/api/docs/registry` | List all active documents grouped by domain |
| GET | `/api/docs/{slug}` | Get full entry + version history |
| GET | `/api/docs/{slug}/content` | Get raw file contents |
| POST | `/api/docs/register` | Register new document |
| PUT | `/api/docs/{slug}` | Update document (auto-versions old) |
| POST | `/api/docs/{slug}/deprecate` | Deprecate with pointer to replacement |

---

*The registry is not a filing cabinet. It's Iris's library card catalog.*
*When she needs to know how to build something, she looks it up here first.*
