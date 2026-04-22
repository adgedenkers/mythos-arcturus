# AutoDoc2 — Next Patch Spec

> This file is rewritten wholesale after every feature patch lands.
> It always describes exactly one patch ahead.
> Run `mythos-handoff autodoc2` to get the full context payload.

---

## Patch: SYS-0086 — AutoDoc2 subsystem registration (doc-only)

**Letter:** A
**Stream:** SYS
**Patch type:** PATCH (doc-only, no code, no schema, no service changes)
**Blast radius:** Low

---

## Scope

This is a documentation-only patch. No code changes, no SQL, no service
restarts.

**Files deployed:**

| File | Action |
|------|--------|
| `/opt/mythos/docs/SYSTEM_AUTODOC2.md` | New — canonical current state doc |
| `/opt/mythos/docs/AUTODOC2_V2.md` | New — locked design plan |
| `/opt/mythos/docs/autodoc2/NEXT_PATCH_SPEC.md` | New — this file |
| `/opt/mythos/docs/_INDEX.md` | Edit — add AutoDoc2 entries |
| `/opt/mythos/docs/SUB-SYSTEMS.md` | Edit — increment N=2 to N=3, add AutoDoc2 to examples |
| `/opt/mythos/docs/ARCHITECTURE.md` | Edit — add SYSTEM_AUTODOC2.md pointer in subsystem docs list |

---

## Verification

After `patch-install SYS-0086`:

```bash
# All three docs exist
ls -la /opt/mythos/docs/SYSTEM_AUTODOC2.md
ls -la /opt/mythos/docs/AUTODOC2_V2.md
ls -la /opt/mythos/docs/autodoc2/NEXT_PATCH_SPEC.md

# SUB-SYSTEMS.md reflects N=3
grep "N=3" /opt/mythos/docs/SUB-SYSTEMS.md

# ARCHITECTURE.md lists SYSTEM_AUTODOC2.md
grep "SYSTEM_AUTODOC2" /opt/mythos/docs/ARCHITECTURE.md

# _INDEX.md has AutoDoc2 entries
grep -i "autodoc2" /opt/mythos/docs/_INDEX.md
```

All five checks should return output. No output = something didn't deploy.

---

## Rollback

Doc-only patch. To rollback: delete the three new files and restore
the previous versions of `_INDEX.md`, `SUB-SYSTEMS.md`, and
`ARCHITECTURE.md` from their `.bak` files created by PatchBase.

---

## What comes next (Letter B)

After SYS-0086 lands, the next patch is **SYS-0087 — `ollama-analyze`
microtool**.

Scope of SYS-0087:
- New file: `/opt/mythos/tools/autodoc2/analyzer.py` — the gemma4:26b
  analysis callable
- Modified: `engine.py` — add `--analyze` flag handling, call
  `analyzer.run(parsed_file)` after walker, store results as AutodocFile
  properties
- Modified: `cli.py` — add `--analyze` / `-a` flag
- Modified: `neo4j_writer.py` — add `analysis_*` property writes to
  `write_file()`
- No new services, no SQL, no bot changes

Run a live diagnostic before building SYS-0087:

```bash
D=~/diag.txt; > "$D"
echo "=== ENGINE ===" >> "$D"
cat /opt/mythos/tools/autodoc2/engine.py >> "$D" 2>&1
echo -e "\n\n=== CLI ===" >> "$D"
cat /opt/mythos/tools/autodoc2/cli.py >> "$D" 2>&1
echo -e "\n\n=== NEO4J WRITER ===" >> "$D"
cat /opt/mythos/tools/autodoc2/neo4j_writer.py >> "$D" 2>&1
echo -e "\n\n=== LLM CLIENT ===" >> "$D"
cat /opt/mythos/tools/autodoc2/llm_client.py >> "$D" 2>&1
echo -e "\n\n=== STREAMS ===" >> "$D"
mythos-diag streams >> "$D" 2>&1
cat "$D" | xclip -selection clipboard && echo "✓ Copied"
```
