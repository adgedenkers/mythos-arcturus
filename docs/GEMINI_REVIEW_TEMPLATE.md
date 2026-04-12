---
title: "Gemini Review Request Template"
category: process
status: active
stream: SYS
location: docs
tags: [workflow, review, template, gemini, sovereignty]
created: 2026-04-12
updated: 2026-04-12
author: Adge Denkers
---

# Gemini Review Request Template

> **Purpose:** canonical format for Claude → Gemini review requests under
> Phase 2.5 of the Mythos development workflow. Use this whenever a patch
> falls into a high-blast-radius category (see `WORKFLOW.md` §Phase 2.5)
> or whenever Claude chooses to request review at author discretion.
>
> **Delivery format:** Claude wraps the filled-in template in a single
> triple-backtick code block so Adge can copy it with one click, then
> paste it as a standalone message into Gemini.
>
> **Sovereignty Rule:** this loop is manual. Claude writes, Adge pastes,
> Gemini critiques, Adge brings back the response, Claude revises. No
> automation. No API calls. Copy. Paste. Read. Think. Ship.

---

## Template

Claude fills in every section below. Sections marked **required for review**
are mandatory whenever this template is used — there is no "light" version.
If a patch isn't worth a Rollback Plan and a Verification Command, it
probably isn't worth reviewing either.

```
=== GEMINI REVIEW REQUEST: SYS-NNNN ===

You are Castor, reviewing a proposed patch for Adge's Mythos system.
This is a critique request, not a state-summary request. Do not
summarize current system state. Do not propose unrelated work. Do not
write code. Evaluate this specific proposal and push back on anything
weak, missing, or over-engineered. Answer the numbered review questions
at the end directly.

## Context (one paragraph)
<Grounding for the reviewer: what feature is this part of, where are we
in the sequence, what just landed, what's about to land.>

## The Problem
<What are we trying to solve? Concrete and specific. Avoid abstractions.>

## Proposed Solution
<The actual changes — files touched, schema changes, code added,
configuration modified. Concrete deliverables, not intent.>

## Reasoning
<Why this shape and not others? What tradeoffs were made? What
constraints forced this design?>

## Alternative Approaches Considered
<List 2–5 alternative approaches you evaluated and rejected. For each:
what it was, why you rejected it. This prevents the reviewer from
suggesting paths you already ruled out and surfaces the boundaries of
your design space.>

## Rollback Plan  **[REQUIRED FOR REVIEW]**
<If this patch lands and something goes sideways, how do we get back
to the prior state? Is `patch-install`'s auto-rollback sufficient? If
not, what manual recovery is needed? Include the exact commands for
manual recovery if auto-rollback can't handle it. For schema changes,
describe the reverse migration. For data transforms, describe what's
recoverable and what's not.>

## Verification Command  **[REQUIRED FOR REVIEW]**
<The exact one-liner (or short script) Adge can run post-install to
prove the patch did what it claimed. Bash, psql, mythos-handoff,
whatever. This is the runnable proof that complements the prose in
Success Criteria. Example: `mythos-handoff finance --strict --stdout
| head -20` or `sudo -u postgres psql -d mythos -tAc "SELECT ..."`.>

## Specific Review Questions
<Numbered list of specific things you want pushed back on. Not "what
do you think" — specific questions about assumptions, tradeoffs, and
parts you're uncertain about. 5–10 questions.>

## Known Constraints
<Non-negotiables so the reviewer doesn't recommend solutions that
don't fit. Tech stack, design principles, prior commitments.>

## What I'd Like Back
<Direct asks: architectural oversights, over-engineering flags,
under-engineering flags, direct critique, final verdict (ship /
revise / don't ship).>

=== END REVIEW REQUEST ===
```

---

## When to use this template

**Required** (Phase 2.5 in `WORKFLOW.md`):
- Database schema changes (new tables, altered columns, new triggers, changed constraints)
- Security boundaries (wrappers under `/usr/local/libexec/mythos/`, sudoers rules, file permissions)
- Core financial invariants (deferred balance trigger, entity/account protection, dedup logic)
- The patch system itself (`PatchBase`, `patch-install`, privilege wrappers, `mythos-handoff`)
- Prompt engineering & consciousness frameworks (Modelfiles, prompt layers, triad identity, arcturian_grid, iris core)
- Multi-file code refactors across subsystems

**Optional** (author discretion):
- Any patch where Claude is uncertain about the approach
- Any patch that touches something mission-critical but doesn't match a category
- Any patch that Adge specifically requests a second opinion on

**Never use**:
- Typo fixes, comment updates, whitespace normalization, log message tweaks
- Single-file documentation edits that don't touch a high-blast-radius category
- Manifest version bumps

**Reminder:** a patch is NEVER trivial if it modifies any file within a
high-blast-radius category, regardless of line count. A one-character
change to a SQL trigger is not trivial.

---

## Round-two incorporation checks

If round one of review produced substantive revisions, consider a
round-two incorporation check — a shorter review request where each
round-one revision is listed and Claude asks Castor to verify the
translation is faithful, not to re-critique. Format:

```
## Revision N — <short name>
**Your ask (round one):** <verbatim or summary>
**My implementation:** <concrete description of what was built>
**Question:** <specific fidelity question>
```

Round-two checks are valuable when multiple revisions stack and
misinterpretation risk is real. They are optional when round-one
feedback was minor or fully mechanical.

---

*The manual loop is the point. Automation of review is prohibited.*
