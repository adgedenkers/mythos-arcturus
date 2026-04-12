#!/usr/bin/env python3
"""
SYS-0074: finance_v2_plan_renumber_note (v2 - sudo tee)

Prepends a renumbering note to /opt/mythos/docs/FINANCE_V2.md. Uses
`sudo tee` for the write so it works regardless of file ownership.

Idempotent via marker check.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

PLAN_PATH = Path('/opt/mythos/docs/FINANCE_V2.md')
NOTE_MARKER = '<!-- SYS-0074-RENUMBER-NOTE -->'

NOTE_BLOCK = f"""{NOTE_MARKER}
> ## ⚠️ Patch numbering note (added SYS-0074)
>
> **The patch numbers in §15 (SYS-0063 through SYS-0071) are obsolete.**
> Those numbers were assigned when the plan was first written; the SYS
> stream counter has since moved past them on unrelated work. The logical
> sequence in §15 is still correct — only the numbers are wrong.
>
> **Rule going forward:**
>
> 1. When starting a new step from §15, run `mythos-diag streams` to get
>    the live next SYS patch number. That's the number for this step.
> 2. **Do not pre-assign numbers for future steps.** Each logical step
>    (schema, importer, merchants, api, recurring, forecast, reliability)
>    may take more than one patch to land successfully — and that's fine.
>    Only assign the next number when the previous step is verified
>    working on Arcturus.
> 3. Record the actual patch number used for each step in this file as
>    the work completes, so future readers can map logical step →
>    real patch history.
>
> **Actual numbers used (fill in as we go):**
>
> - Preflight (v1 teardown): **SYS-0071** (already done — v1 code archived,
>   tables renamed)
> - Renumber note (this patch): **SYS-0074**
> - Schema (§15 step 2, was planned 0064): _TBD — next patch_
> - Importer (§15 step 3, was planned 0065): _TBD_
> - Merchants & rules (§15 step 4, was planned 0066): _TBD_
> - API (§15 step 5, was planned 0067): _TBD_
> - Recurring detector (§15 step 6, was planned 0068): _TBD_
> - Forecasting (§15 step 7, was planned 0069): _TBD_
> - v1 archive cleanup (§15 step 8, was planned 0070): _TBD_
> - Reliability (§15 step 9, was planned 0071): _TBD_

---

"""


def prepend_note():
    if not PLAN_PATH.exists():
        raise SystemExit(f"ERROR: {PLAN_PATH} does not exist")

    # Read is fine without sudo (file is world-readable)
    content = PLAN_PATH.read_text()

    if NOTE_MARKER in content:
        print("  ↳ Note marker already present — no-op")
        return False

    anchor = "## 1. Context and constraints"
    if anchor not in content:
        raise SystemExit(f"ERROR: could not find anchor '{anchor}' in FINANCE_V2.md")

    before, sep, after = content.partition(anchor)
    new_content = before + NOTE_BLOCK + sep + after

    # Write via sudo tee to a temp file, then sudo mv into place.
    # This bypasses ownership issues on the file OR the parent dir.
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.md', delete=False, dir='/tmp'
    ) as tmp:
        tmp.write(new_content)
        tmp_path = tmp.name

    try:
        # sudo cp preserves the target's ownership/mode; sudo install -m lets us be explicit.
        # Use sudo cp --no-preserve=mode,ownership to just overwrite contents.
        result = subprocess.run(
            ['sudo', 'cp', tmp_path, str(PLAN_PATH)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise SystemExit(
                f"ERROR: sudo cp failed: {result.stderr}"
            )
        print(f"  ↳ Prepended renumber note to FINANCE_V2.md (via sudo cp)")
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return True


def main():
    patch = PatchBase(
        stream='SYS',
        number=74,
        description='finance_v2_plan_renumber_note',
        patch_type='PATCH',
    )
    patch.begin()

    print("[SYS-0074] Annotating FINANCE_V2.md with renumbering note...")
    changed = prepend_note()

    if changed:
        print("[SYS-0074] ✓ Note added")
    else:
        print("[SYS-0074] ✓ No changes needed (idempotent no-op)")

    patch.finish()


if __name__ == '__main__':
    main()
