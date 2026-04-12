#!/usr/bin/env python3
"""
SYS-0082: Finance v2 doc reconciliation.

Trivial doc-only patch. Uses pathlib + str.replace directly rather than
PatchBase.edit_file (which does not exist — the round-1 build assumed
it did and failed loudly at install). set -e + patch-install rollback
caught the bad assumption cleanly.

This rebuild:
  - Reads /opt/mythos/docs/SYSTEM_FINANCE.md
  - Backs it up to /opt/mythos/docs/SYSTEM_FINANCE.md.SYS-0082.bak
  - Asserts each old_str block appears EXACTLY ONCE before replacing
  - Writes the new content atomically via a temp file + rename
  - Calls PatchBase.finish() to bump STREAMS.json and write PATCH_HISTORY
"""
import sys
import shutil
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

SYSDOC = Path('/opt/mythos/docs/SYSTEM_FINANCE.md')
BACKUP = Path('/opt/mythos/docs/SYSTEM_FINANCE.md.SYS-0082.bak')

EDITS = [
    # Edit 1: Status block
    {
        "name": "Status block (last shipped B -> C.1 hardening SYS-0081)",
        "old": """## Status

- **Last shipped patch:** B (SYS-0076) — 2026-04-12
- **Next patch:** D — Merchants + merchant_patterns + FK on `transactions.merchant_id`
- **Build phase:** active (A→L sequence, currently at B→C→D)
- **Design plan:** `docs/FINANCE_V2.md`

> Note: Patch C (this one, SYS-0077) is the workflow/documentation
> bootstrap. It ships no schema or code — only `WORKFLOW.md`,
> `SYSTEM_FINANCE.md`, and an `ARCHITECTURE.md` edit. The
> handoff-diag script itself is deferred pending external review
> and will land in a follow-up doc patch.""",
        "new": """## Status

- **Last shipped patch:** C.1 hardening (SYS-0081) — 2026-04-12
- **Next patch:** D — Merchants + merchant_patterns + FK on `transactions.merchant_id` (will be SYS-0083)
- **Build phase:** active (A→L sequence, C.1 infrastructure complete, D next)
- **Design plan:** `docs/FINANCE_V2.md`

> Note: Patch C (SYS-0077) shipped the workflow/documentation bootstrap.
> Patch C.1 (SYS-0078) shipped the `mythos-handoff` tool, manifest schema,
> and `NEXT_PATCH_SPEC.md` pattern. Three follow-up hardening patches
> (SYS-0079 tgdeferrable cast + guards, SYS-0080 `--strict` +
> `verify_handoff()`, SYS-0081 Gemini review workflow + Phase 2.5) shipped
> infrastructure under the C.1 umbrella — none of them map to a locked
> feature letter, and the letter sequence is unchanged.""",
    },
    # Edit 2: Patch Ledger rows C and D
    {
        "name": "Patch Ledger (add C.1/C.1a/C.1b/C.1c/C.2 rows between C and D)",
        "old": "| C | Workflow bootstrap — WORKFLOW.md, SYSTEM_FINANCE.md, ARCHITECTURE.md edit | SYS-0077 | 2026-04-12 | This patch. No schema or code changes. |\n| D | Merchants + merchant_patterns + FK on `transactions.merchant_id` | — | — | **Next up** |",
        "new": """| C | Workflow bootstrap — WORKFLOW.md, SYSTEM_FINANCE.md, ARCHITECTURE.md edit | SYS-0077 | 2026-04-12 | Shipped. Doc-only. |
| C.1 | Handoff system — `mythos-handoff` tool, `MANIFEST.yaml` schema, `NEXT_PATCH_SPEC.md` pattern | SYS-0078 | 2026-04-12 | Shipped. Replaces per-subsystem handoff scripts. |
| C.1a | Handoff hardening — tgdeferrable cast fix + empty-ledger guards | SYS-0079 | 2026-04-12 | Manifest validation fixes. |
| C.1b | Handoff hardening — `mythos-handoff --strict` flag + `PatchBase.verify_handoff()` helper | SYS-0080 | 2026-04-12 | Enforcement option for CI-style use. |
| C.1c | Gemini review workflow — template, Phase 2.5 blast-radius rules, `review_link` field | SYS-0081 | 2026-04-12 | Castor-reviewed 2 rounds. |
| C.2 | SYSTEM_FINANCE doc reconciliation (this patch) | SYS-0082 | 2026-04-12 | Trivial doc-only patch. No schema, no code. |
| D | Merchants + merchant_patterns + FK on `transactions.merchant_id` | — | — | **Next up — will be SYS-0083, Phase 2.5 required** |""",
    },
]


def main():
    patch = PatchBase(
        stream='SYS',
        number=82,
        description='finance v2 doc reconciliation (SYSTEM_FINANCE status + ledger)',
        patch_type='PATCH',
    )
    patch.begin()

    if not SYSDOC.exists():
        raise SystemExit(f"FATAL: {SYSDOC} does not exist")

    content = SYSDOC.read_text(encoding='utf-8')
    original = content

    # Pre-flight: every old_str must appear EXACTLY ONCE.
    for edit in EDITS:
        n = content.count(edit["old"])
        if n != 1:
            raise SystemExit(
                f"FATAL: edit '{edit['name']}' expected exactly 1 match in "
                f"{SYSDOC}, found {n}. File has drifted from handoff payload. "
                f"Aborting — no writes performed."
            )

    # Apply edits in order.
    for edit in EDITS:
        content = content.replace(edit["old"], edit["new"], 1)
        print(f"  ✓ {edit['name']}")

    if content == original:
        raise SystemExit("FATAL: content unchanged after edits — something is wrong")

    # Backup, then atomic write via temp + rename.
    shutil.copy2(SYSDOC, BACKUP)
    print(f"  ✓ backup written to {BACKUP}")

    tmp = SYSDOC.with_suffix(SYSDOC.suffix + '.tmp')
    tmp.write_text(content, encoding='utf-8')
    tmp.replace(SYSDOC)
    print(f"  ✓ {SYSDOC} updated ({len(content) - len(original):+d} bytes)")

    patch.finish()


if __name__ == '__main__':
    main()
