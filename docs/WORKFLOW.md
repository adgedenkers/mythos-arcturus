---
title: "Mythos Development Workflow"
category: process
status: active
stream: SYS
location: docs
tags: [workflow, patches, documentation, handoff]
created: 2026-04-12
updated: 2026-04-12
author: Adge Denkers
---

# Mythos Development Workflow

> **Purpose:** Describe the loop Claude and Adge use to build multi-patch
> features without losing state between conversations. If you're starting
> a new conversation about a feature in progress, read this first, then
> read the relevant `SYSTEM_<name>.md`.

---

## Core idea

Long features (like Finance v2) take many patches to land. A single
Claude conversation cannot hold all the context those patches need —
context rot, token pressure, and plain human fatigue make it worse as
it grows. So we break the work into **letters**, track progress in a
per-subsystem **SYSTEM doc**, and start each new conversation with a
**handoff payload** that snapshots current reality.

Three rules drive the loop:

1. **Plan by letter, number at build time.**
   Features are broken into Patch A, B, C, … during design. Patch
   numbers are only assigned when the patch is actually built, from
   `mythos-diag streams` (the live counter). A single logical letter
   can map to multiple patch numbers if the work takes retries.

2. **Feature patches and documentation patches are separate.**
   When a feature patch lands, it is followed by a documentation patch
   that updates `ARCHITECTURE.md` and the relevant `SYSTEM_<name>.md`.
   The schema/code change and the doc change are never bundled — if
   the schema install fails, the docs shouldn't have moved.

3. **Every new conversation starts from a handoff payload.**
   Before opening a new conversation, run the handoff diagnostic for
   the system you're working on. It assembles a single pastable block
   containing: current `ARCHITECTURE.md`, current `SYSTEM_<name>.md`,
   live DB state, live stream counters, and the next patch's spec.
   Paste that as the first message of the new conversation.

---

## The loop, step by step

### Phase 1 — Planning (once per feature)

1. Write the design document (`FINANCE_V2.md`, etc.)
2. Break the work into letters: Patch A, B, C, …
3. Each letter is a self-contained, independently verifiable chunk
4. Record the letter sequence in the design doc
5. Create the `SYSTEM_<name>.md` doc with the letter table

### Phase 2 — Per-patch cycle

For each letter:

1. **Start conversation from a handoff payload** (or from the design
   doc, for the very first patch of the feature)
2. **Claude builds the feature patch** using the letter's spec
3. **Claude delivers** zip + install command
3.5. **[HIGH-BLAST-RADIUS ONLY] Claude writes a Gemini review
   request** using `docs/GEMINI_REVIEW_TEMPLATE.md`, delivers it
   in a single triple-backtick code block. Adge pastes into
   Gemini, brings back the response, Claude revises if needed,
   may require another review round. Only then is the zip
   finalized. See Phase 2.5 below for full rules.
4. **Adge installs on Arcturus** via `patch-install SYS-NNNN`
5. **Adge confirms** the install worked and the verification passed
6. **Claude builds a doc patch** that updates:
   - `ARCHITECTURE.md` — durable "what exists" reference
   - `SYSTEM_<name>.md` — letter ledger, architecture summary, next-up
   - The design doc's §15-equivalent patch table (if any)
7. **Adge installs the doc patch**
8. **Claude generates the handoff payload for the next letter**
9. **Adge copies the payload, starts a new conversation, pastes it**
10. Repeat from step 2 with the next letter

### Phase 3 — Feature complete

When the last letter lands:
- Final doc patch marks the feature as deployed in `ARCHITECTURE.md`
- `SYSTEM_<name>.md` moves from "active build" to "maintenance mode"
- Design doc is frozen (historical reference only)

---

## Incoming notes

Every `SYSTEM_<name>.md` ends with an **Incoming notes** section.
This is a free-form append area for anything that comes up mid-build
that shouldn't be forgotten but also shouldn't derail the current
patch. Examples:

- "Noticed foo table has no index on bar — address in Patch F"
- "This trigger fires on every insert, may need EXCLUSIVE MODE later"
- "Adge mentioned LLC activation date might slip, revisit entity dim"

Rules for incoming notes:

- **Append, never edit.** Stamp each note with a date.
- **Review when the next patch starts.** Either triage into the
  "Next Up" spec, defer to a later letter, or file into open questions.
- **Never lose one.** The handoff payload always includes this section,
  so notes travel with the work.

---

## SYSTEM doc structure

Every `SYSTEM_<name>.md` follows the same template:

```
# SYSTEM: <name>

## Status
- Last shipped patch: <letter> (<SYS-number>) — <date>
- Next patch: <letter> — <one-line scope>
- Design plan: docs/<DESIGN>.md

## Architecture Summary
<2-3 paragraphs of what this subsystem actually is and how it works.
 Updated every time a patch changes reality.>

## Patch Ledger
| Letter | Scope | Patch # | Shipped | Notes |
|--------|-------|---------|---------|-------|

## Next Up: Patch <letter>
### Why
### What
### How
### Success criteria
### Depends on

## Open questions
<carried forward from design doc until resolved>

## Incoming notes
<date-stamped append-only section>
```

---

## Why this works

- **Context rot stops mattering.** Every conversation starts fresh with
  an authoritative snapshot. Claude's memory of "what we did last time"
  is irrelevant — the docs are the source of truth.
- **Letters survive retries.** If Patch B takes three tries to land,
  it's still Patch B in the design doc. Only the number changes.
- **Doc/code split prevents drift.** Docs only update after the code
  lands and verifies. If a feature patch fails, the docs still reflect
  pre-patch reality.
- **Incoming notes prevent loss.** Mid-build realizations don't
  evaporate into chat history.
- **The handoff diag is a forcing function.** If Claude can't write a
  handoff that fully describes the next patch, Claude doesn't
  understand the next patch well enough to build it.

---

## Handoff System (three-artifact pattern)

<!-- SYS-0078: handoff system documented -->

After Gemini review, the handoff is implemented as **three artifacts**
with different lifecycles, not a single monolithic script:

| Artifact | Path | Lifecycle |
|---|---|---|
| **Generic tool** | `/opt/mythos/bin/mythos-handoff` | Permanent, subsystem-agnostic. Updated rarely, when new capabilities are needed (e.g., "also pull Neo4j integrity state"). |
| **Feature manifest** | `docs/<n>/MANIFEST.yaml` | Versioned per feature. Updated when dependencies change (new tables, new validations). |
| **Next patch spec** | `docs/<n>/NEXT_PATCH_SPEC.md` | Rewritten wholesale each turn. Ephemeral content; history lives in `SYSTEM_<n>.md`. |

### Usage

```bash
mythos-handoff finance           # assemble payload, copy to clipboard
mythos-handoff finance --stdout  # write to stdout
mythos-handoff finance --file F  # write to file
mythos-handoff --list            # list available subsystems
```

The tool reads `docs/<subsystem>/MANIFEST.yaml`, then walks its
sections: docs to include, SQL queries to run, validations to assert,
integrity state to pull, and stream counters to report. The
assembled payload goes to the clipboard via `xclip`.

### Validation policy (soft warning)

If any manifest validation fails, the payload still gets assembled
and copied — but a bright `⚠⚠⚠ VALIDATION FAILURES ⚠⚠⚠` banner
appears at the top. Rationale: failures are information, and
sometimes you hand off *precisely because* something is broken and
you need Claude to fix it. Hard-blocking would prevent that.

### Adding a new subsystem

1. Create `docs/<n>/MANIFEST.yaml` (schema: see `docs/finance/MANIFEST.yaml` as reference)
2. Create `docs/<n>/NEXT_PATCH_SPEC.md`
3. `mythos-handoff <n>` auto-discovers it

The tool does not hardcode any subsystem names. `docs/<n>/` is the convention.

---



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

---

*The vessel is filling. The workflow is the scaffolding.*
