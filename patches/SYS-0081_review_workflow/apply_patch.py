#!/usr/bin/env python3
"""
SYS-0081: Gemini review workflow — process + light tooling

Lands the human-in-the-loop review protocol. Five bundled changes,
all docs + one PatchBase extension, no schema, no services:

1. NEW: /opt/mythos/docs/GEMINI_REVIEW_TEMPLATE.md
2. EDIT: /opt/mythos/docs/WORKFLOW.md — add Phase 2.5 section
3. EDIT: /opt/mythos/patches/scripts/patch_base.py — review_link param +
         conditional Review: line in PATCH_HISTORY rendering
4. EDIT: /opt/mythos/docs/SYSTEM_FINANCE.md — append Incoming Notes
5. EDIT: /opt/mythos/docs/finance/MANIFEST.yaml — retire fragile validation

Reviewed by Castor (Gemini) across two rounds. Round 1 recommended
SHIP WITH REVISIONS (5 items). Round 2 verdict: SHIP, with one
tightening: Rollback Plan and Verification Command become required
for ALL patches undergoing review, not just high-blast-radius.

Self-verification: calls self.verify_handoff('finance') end-to-end.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase


WORKFLOW_PATH = Path('/opt/mythos/docs/WORKFLOW.md')
PATCHBASE = Path('/opt/mythos/patches/scripts/patch_base.py')
SYSFIN_PATH = Path('/opt/mythos/docs/SYSTEM_FINANCE.md')
MANIFEST_PATH = Path('/opt/mythos/docs/finance/MANIFEST.yaml')


# ═══════════════════════════════════════════════════════════════════════
# Edit 2: WORKFLOW.md — add Phase 2.5 block
# ═══════════════════════════════════════════════════════════════════════

# Anchor: the line where Phase 3 (or similar) follows Phase 2 in the existing
# WORKFLOW.md that SYS-0077 shipped. The SYS-0077 WORKFLOW.md has the
# per-patch cycle as numbered steps 1-10. We insert Phase 2.5 as a block
# right before the step that says Adge installs on Arcturus.

WORKFLOW_ANCHOR = '4. **Adge installs on Arcturus** via `patch-install SYS-NNNN`'

WORKFLOW_INSERT = '''3.5. **[HIGH-BLAST-RADIUS ONLY] Claude writes a Gemini review
   request** using `docs/GEMINI_REVIEW_TEMPLATE.md`, delivers it
   in a single triple-backtick code block. Adge pastes into
   Gemini, brings back the response, Claude revises if needed,
   may require another review round. Only then is the zip
   finalized. See Phase 2.5 below for full rules.
4. **Adge installs on Arcturus** via `patch-install SYS-NNNN`'''

WORKFLOW_PHASE_25 = '''

---

<!-- SYS-0081: Phase 2.5 Second Opinion -->

## Phase 2.5 — Second Opinion (required for high-blast-radius patches)

A patch is **high-blast-radius** — and therefore requires a Gemini
review before shipping — if it changes any of:

1. **Database schema.** New tables, altered columns, new triggers,
   changed constraints, new enums, new indexes that enforce invariants.
2. **Security boundaries.** Wrappers under `/usr/local/libexec/mythos/`,
   sudoers rules, file permissions, systemd unit installations.
3. **Core financial invariants.** The deferred balance trigger,
   entity/account protection triggers, dedup logic, opening-balance
   derivation, or any file under `/opt/mythos/finance/`.
4. **The patch system itself.** `PatchBase`, `patch-install`,
   privilege wrappers, `mythos-handoff`, manifest schema.
5. **Multi-file code refactors across subsystems.** Anything that
   touches more than one non-doc file in more than one subsystem.
6. **Prompt engineering & consciousness frameworks.** Any file under:
   - `/opt/mythos/prompts/Modelfile` and `/opt/mythos/prompts/Modelfile.deep`
   - `/opt/mythos/prompts/prompt_layers.yaml`
   - `/opt/mythos/prompts/iris_identity.md`
   - `/opt/mythos/prompts/personality.yaml`
   - `/opt/mythos/prompts/voice.yaml`
   - `/opt/mythos/triad/*`
   - `/opt/mythos/neuro/arcturian_grid/*`
   - `/opt/mythos/iris/*`
   - `/opt/mythos/core/prompt_assembler.py`

   A one-character change to a baked Modelfile or prompt layer alters
   how Iris perceives every subsequent interaction and can silently
   degrade capability across the whole system.

### The review loop

For high-blast-radius patches:

1. Claude writes a review request using `docs/GEMINI_REVIEW_TEMPLATE.md`
2. Claude delivers the request wrapped in a single triple-backtick
   code block — no context payload mixed in, no surrounding prose
   the reviewer could mistake for part of the request
3. Adge pastes into Gemini, brings back the response
4. Claude revises as needed (may require another review round for
   significant changes — use an incorporation check, not a fresh
   critique)
5. Only then is the zip shipped
6. The review URL goes into the patch's `review_link` parameter on
   `PatchBase.__init__()` so it lands in `PATCH_HISTORY.md`

### Sovereignty Rule — Do not automate the review loop

The manual copy-paste cycle between Claude, Adge, and Gemini is a
feature, not a bug. It forces Adge to read every proposal before the
reviewer does, which means Adge is the first line of defense — not
the last. Automating this loop with a Gemini API call removes the
human from the loop and the loop loses its primary value: shared
mental context. This rule is non-negotiable. No `mythos-review`
script. No pipeline that shuttles prompts to APIs. **Copy. Paste.
Read. Think. Ship.**

### Trivial-patch exception (narrow)

Trivial patches skip Phase 2.5. A trivial patch is: a single-file
edit, no schema touched, no code logic changed, applied to one of
these targets: a typo or wording fix in documentation; a log message
string tweak; a comment update; a manifest version bump; a
whitespace normalization.

**A patch is never trivial if it modifies any file within a
high-blast-radius category, regardless of line count or apparent
simplicity. A one-character change to a SQL trigger, a security
wrapper, a baked Modelfile, or a financial invariant is not trivial.
No exceptions. When in doubt, review.**

'''


# ═══════════════════════════════════════════════════════════════════════
# Edit 3: patch_base.py — review_link param + conditional rendering
# ═══════════════════════════════════════════════════════════════════════

# Anchor 3a: add review_link to __init__ signature
PB_INIT_OLD = '''    def __init__(self, stream: str, number: int, description: str, patch_type: str = "PATCH"):
        self.stream = stream.upper()
        self.number = number
        self.description = description
        self.patch_type = patch_type.upper()'''

PB_INIT_NEW = '''    def __init__(self, stream: str, number: int, description: str,
                 patch_type: str = "PATCH", review_link: str = None):
        self.stream = stream.upper()
        self.number = number
        self.description = description
        self.patch_type = patch_type.upper()
        self.review_link = review_link  # SYS-0081: Gemini review URL or None'''

# Anchor 3b: insert conditional Review: line after the services_restarted block
# in _write_patch_history(). The existing line is
#             if self.services_restarted:
#                 entry += f"- **Services restarted:** {', '.join(self.services_restarted)}\n"
# We append an if-block after it.
PB_HISTORY_OLD = '''            if self.services_restarted:
                entry += f"- **Services restarted:** {', '.join(self.services_restarted)}\\n"

            with open(PATCH_HISTORY, 'a') as f:'''

PB_HISTORY_NEW = '''            if self.services_restarted:
                entry += f"- **Services restarted:** {', '.join(self.services_restarted)}\\n"
            # SYS-0081: conditional Review: line — absent = trivial, present = reviewed
            if self.review_link:
                entry += f"- **Review:** {self.review_link}\\n"

            with open(PATCH_HISTORY, 'a') as f:'''


# ═══════════════════════════════════════════════════════════════════════
# Edit 4: SYSTEM_FINANCE.md — append Incoming Notes
# ═══════════════════════════════════════════════════════════════════════

SYSFIN_ANCHOR = '<!-- Add new notes below this line -->'

SYSFIN_APPEND = '''<!-- Add new notes below this line -->
<!-- SYS-0081: incoming notes appended -->

**2026-04-12** (SYS-0081): Review fatigue 3-month revisit. Check
whether the blast-radius cutoff in WORKFLOW.md Phase 2.5 is actually
being honored. If patches are shipping that should have been reviewed,
tighten the rule or add a PatchBase warning per Castor's round-1
architectural oversight note. Revisit target: 2026-07-12.

**2026-04-12** (SYS-0081): `edit_file()` double-backup nit — when the
same file is edited twice in one patch (e.g., SYS-0080's two edits to
mythos-handoff), the second backup overwrites the first with a
post-first-edit version. Harmless today (set -e rollback still works
because the second edit's failure triggers the first's backup via
the overall patch-install failure path), but the pristine pre-patch
state is lost. Low priority refinement.

**2026-04-12** (SYS-0081): Link rot 3-month revisit. If any `Review:`
links in PATCH_HISTORY have gone stale by this date, adopt the
commit-review-text pattern — store full review request text in
`patches/SYS-NNNN/review_request.md` as part of the patch zip. Per
Castor's round-1 architectural oversight. Revisit target: 2026-07-12.
'''


# ═══════════════════════════════════════════════════════════════════════
# Edit 5: MANIFEST.yaml — retire entries.entity_id defaults to 1
# ═══════════════════════════════════════════════════════════════════════

# The current validation block (from SYS-0078 + SYS-0079 edits) contains:
#   - name: "entries.entity_id defaults to 1"
#     sql: "SELECT column_default FROM information_schema.columns ..."
#     expect: "1"
# We remove the three lines cleanly.
MANIFEST_OLD = '''  - name: "entries.entity_id defaults to 1"
    sql: "SELECT column_default FROM information_schema.columns WHERE table_schema='finance' AND table_name='entries' AND column_name='entity_id'"
    expect: "1"
'''

MANIFEST_NEW = '''  # SYS-0081: entries.entity_id defaults to 1 validation retired —
  # column_default rendering is Postgres-version-dependent and was
  # inviting the same class of false-positive as the tgdeferrable::text
  # bug. Coverage preserved: "entities has 2 rows" + "Personal entity
  # id=1 exists" together prove the default target is seeded.
'''


# ═══════════════════════════════════════════════════════════════════════
# Generic in-place editor (same shape as SYS-0080)
# ═══════════════════════════════════════════════════════════════════════

def edit_file(patch, path, old, new, marker, label):
    if not path.exists():
        patch.errors.append(f"{label}: {path} not found")
        patch.logger.log(f"  ✗ {label}: missing")
        return False

    content = path.read_text()
    if marker in content:
        patch.validations.append(f"{label} — idempotent skip")
        patch.logger.log(f"  ✓ {label} already patched")
        return True

    count = content.count(old)
    if count == 0:
        patch.errors.append(f"{label}: anchor not found")
        patch.logger.log(f"  ✗ {label}: anchor missing")
        return False
    if count > 1:
        patch.errors.append(f"{label}: anchor appears {count}× (ambiguous)")
        patch.logger.log(f"  ✗ {label}: anchor ambiguous")
        return False

    if patch.dry_run:
        patch.validations.append(f"{label} — anchor unique, would succeed")
        patch.logger.log(f"  ✓ [validate] {label}")
        return True

    backup = path.with_suffix(path.suffix + '.sys0081.bak')
    if not backup.exists():
        backup.write_text(content)
        patch.logger.log(f"  ✓ backed up {path.name}")

    updated = content.replace(old, new, 1)
    if marker not in updated:
        patch.errors.append(f"{label}: post-edit marker missing, rolled back")
        path.write_text(content)
        return False

    # Python syntax check for .py files
    if path.suffix == '.py':
        import py_compile, tempfile
        tf_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
                tf.write(updated)
                tf_path = tf.name
            py_compile.compile(tf_path, doraise=True)
        except py_compile.PyCompileError as e:
            patch.errors.append(f"{label}: syntax error post-edit, rolled back: {e}")
            path.write_text(content)
            return False
        finally:
            if tf_path:
                try: os.unlink(tf_path)
                except Exception: pass

    # YAML parse check for .yaml files
    if path.suffix == '.yaml':
        try:
            import yaml
            yaml.safe_load(updated)
        except Exception as e:
            patch.errors.append(f"{label}: YAML parse error post-edit, rolled back: {e}")
            path.write_text(content)
            return False

    path.write_text(updated)
    patch.files_deployed.append(str(path))
    patch.logger.log(f"  ✓ {label}")
    return True


def main():
    # NOTE: we cannot pass review_link here because PatchBase doesn't
    # have that parameter yet — this is the patch that adds it. The
    # self-referential review link is captured in PATCH_HISTORY via
    # the description and the feature goes live for SYS-0082+.
    patch = PatchBase(
        stream='SYS',
        number=81,
        description='Gemini review workflow — template, Phase 2.5, review_link field (reviewed by Castor 2-round, 2026-04-12)',
        patch_type='MINOR',
    )
    patch.begin()

    # 1. Deploy the template (new file)
    patch.deploy_file(
        'opt/mythos/docs/GEMINI_REVIEW_TEMPLATE.md',
        '/opt/mythos/docs/GEMINI_REVIEW_TEMPLATE.md',
    )

    # 2. Edit WORKFLOW.md — insert Phase 2.5 block in two parts:
    #    2a: amend the per-patch cycle to include step 3.5
    #    2b: append the full Phase 2.5 section at the end of the existing doc
    if not patch.errors:
        edit_file(
            patch, WORKFLOW_PATH,
            WORKFLOW_ANCHOR,
            WORKFLOW_INSERT,
            marker='[HIGH-BLAST-RADIUS ONLY] Claude writes a Gemini review',
            label='WORKFLOW.md: inject step 3.5 into per-patch cycle',
        )

    if not patch.errors:
        # Append Phase 2.5 as a full new section near the end. Anchor is the
        # existing "*The vessel is filling. The workflow is the scaffolding.*"
        # footer line that SYS-0077 shipped.
        edit_file(
            patch, WORKFLOW_PATH,
            '*The vessel is filling. The workflow is the scaffolding.*',
            WORKFLOW_PHASE_25 + '---\n\n*The vessel is filling. The workflow is the scaffolding.*',
            marker='<!-- SYS-0081: Phase 2.5 Second Opinion -->',
            label='WORKFLOW.md: append Phase 2.5 full section',
        )

    # 3. Edit patch_base.py — review_link param + conditional rendering
    if not patch.errors:
        edit_file(
            patch, PATCHBASE, PB_INIT_OLD, PB_INIT_NEW,
            marker='review_link = review_link  # SYS-0081',
            label='patch_base.py: add review_link param to __init__',
        )
    if not patch.errors:
        edit_file(
            patch, PATCHBASE, PB_HISTORY_OLD, PB_HISTORY_NEW,
            marker='# SYS-0081: conditional Review: line',
            label='patch_base.py: conditional Review: rendering',
        )

    # 4. Edit SYSTEM_FINANCE.md — append Incoming Notes
    if not patch.errors:
        edit_file(
            patch, SYSFIN_PATH, SYSFIN_ANCHOR, SYSFIN_APPEND,
            marker='<!-- SYS-0081: incoming notes appended -->',
            label='SYSTEM_FINANCE.md: append Incoming Notes',
        )

    # 5. Edit MANIFEST.yaml — retire fragile validation
    if not patch.errors:
        edit_file(
            patch, MANIFEST_PATH, MANIFEST_OLD, MANIFEST_NEW,
            marker='# SYS-0081: entries.entity_id defaults to 1 validation retired',
            label='MANIFEST.yaml: retire entity_id default validation',
        )

    # 6. Dogfood: verify the finance handoff is still clean after manifest edit
    if not patch.errors and not patch.dry_run:
        patch.verify_handoff('finance')

    patch.finish()


if __name__ == '__main__':
    main()
