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

## Handoff diag script

*(Location and structure of the handoff diagnostic script is pending
external review. Will be specified in a follow-up doc patch once
settled.)*

---

*The vessel is filling. The workflow is the scaffolding.*
