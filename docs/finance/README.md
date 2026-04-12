# docs/finance/

Per-feature artifacts for the Finance v2 build.

| File | Purpose | Lifecycle |
|---|---|---|
| `MANIFEST.yaml` | Drives `mythos-handoff finance` — lists docs, SQL queries, validations, and integrity scope for the handoff payload | Versioned. Updated when the feature's dependencies change (new tables, new validations to assert). |
| `NEXT_PATCH_SPEC.md` | Full spec for the next patch letter in the Finance v2 sequence | Rewritten wholesale every turn. History lives in `docs/SYSTEM_FINANCE.md` → Patch Ledger. |

**Usage:**

```bash
mythos-handoff finance          # assemble payload, copy to clipboard
mythos-handoff finance --stdout # write to stdout
mythos-handoff --list           # list available subsystems
```

**Adding a new subsystem:** create `docs/<name>/MANIFEST.yaml` and
`docs/<name>/NEXT_PATCH_SPEC.md` following this layout. The
`mythos-handoff` tool is generic — it auto-discovers any subsystem
that has a `MANIFEST.yaml`.

See `docs/WORKFLOW.md` for the full build loop.
