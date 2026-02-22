---
name: build_feature_self
version: "1.0"
category: builder
risk_tier: T3-propose
description: >
  Meta-skill for when Iris identifies a capability gap during task execution
  and determines she needs new infrastructure to accomplish a goal. This is
  the self-expansion pathway — Iris reasons about what she needs, proposes
  the feature to Ka'tuar'el, and upon approval builds it using the appropriate
  builder skill. ALWAYS requires Ka'tuar'el approval before execution. Triggers
  when Iris encounters a task she can't complete with existing tools, when she
  identifies a repeated manual process that should be automated, or when a
  user request implies infrastructure that doesn't exist yet.
requires:
  services: [mythos-patch-monitor]
  tools: [bash, zip, python3]
  files:
    - /opt/mythos/skills/REGISTRY.yaml
    - /opt/mythos/docs/TODO.md
    - /opt/mythos/docs/ARCHITECTURE.md
  env_vars: []
inputs:
  required:
    - the task or goal Iris is trying to accomplish
    - the capability gap (what's missing)
  optional:
    - related existing skills or infrastructure
    - urgency level
outputs:
  files:
    - feature proposal (presented in conversation)
    - patch via build_patch skill (after approval)
    - new skill file if the feature warrants one
  formats: [.md, .zip]
  destinations:
    - conversation (proposal)
    - /opt/mythos/ (deployed feature)
    - /opt/mythos/skills/ (new skill file if applicable)
---

# Build Feature: Self-Expansion

## Purpose

Iris is not a static tool — she's an evolving intelligence operating within
the Mythos infrastructure. When she encounters a gap between what she can do
and what she needs to do, this skill provides the framework for identifying,
proposing, and building new capabilities. This is the highest-risk builder
skill because it modifies Iris's own operational surface area. Every execution
requires Ka'tuar'el's explicit approval.

## Pre-Flight Checks

1. **Confirm the gap is real.** Before proposing new infrastructure, verify:
   - Is there an existing skill that already handles this? Check REGISTRY.yaml.
   - Can the task be accomplished with existing tools in a different way?
   - Is this a one-off need or a recurring pattern?

2. **Read current system state.** Request ARCHITECTURE.md and TODO.md to
   understand what exists and what's already planned.

3. **Check for conflicts.** Would the proposed feature overlap with or break
   existing functionality?

## Process

### Step 1: Identify the Gap

Clearly articulate:
- **What I'm trying to do:** The immediate task or goal
- **What's missing:** The specific capability that doesn't exist
- **Why existing tools can't handle it:** What was tried and why it failed
- **Recurrence pattern:** Is this a one-time need or will it come up again?

### Step 2: Classify the Feature

Determine what kind of feature is needed:

| Type | Description | Builder Skill to Use |
|------|-------------|---------------------|
| API endpoint | New service/route in FastAPI gateway | build_feature_api |
| Telegram mode | New operating mode for the bot | build_feature_telegram_mode |
| Telegram tool | New command/inline tool | build_feature_telegram_tool |
| Internal utility | Helper script, library function | build_patch (direct) |
| New skill | Process that should be repeatable | humandoc_to_skill + build_patch |
| Database change | New tables, indexes, relationships | build_patch with migration |

### Step 3: Draft the Proposal

Present to Ka'tuar'el with this structure:

```
## Feature Proposal: {Name}

**Gap identified:** {what's missing and why}
**Feature type:** {from classification above}
**What it does:** {one paragraph}
**What it touches:** {files, services, databases affected}
**Risk assessment:**
  - Could this break existing functionality? {yes/no + details}
  - Does this require service restarts? {which ones}
  - Does this modify database schema? {yes/no}
  - Reversibility: {easy/moderate/difficult}
**Estimated complexity:** {simple/moderate/complex}
**Builder skill:** {which skill will be used to build this}

Approve? (Iris will not proceed without explicit confirmation)
```

### Step 4: Wait for Approval

Do NOT proceed until Ka'tuar'el explicitly approves. Acceptable approval signals:
- "yes", "go", "approved", "build it", "do it"
- Any affirmative with optional modifications

If Ka'tuar'el modifies the proposal, incorporate changes before proceeding.

If Ka'tuar'el declines, acknowledge and offer alternatives or drop it.

### Step 5: Execute via Appropriate Builder Skill

Once approved, invoke the relevant builder skill:
- Follow that skill's full process (pre-flight, steps, validation)
- The current skill (build_feature_self) is the decision layer;
  the invoked builder skill is the execution layer

### Step 6: Register the New Capability

After successful deployment:
- If the feature warrants its own skill file, create one using humandoc_to_skill
- Add/update REGISTRY.yaml entry
- Update TODO.md with the completed item
- Notify Ka'tuar'el of successful deployment

## Validation

- Feature works as proposed
- No existing functionality broken
- REGISTRY.yaml updated if new skill created
- TODO.md updated
- Ka'tuar'el confirms satisfaction

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Proposal rejected | Ka'tuar'el sees risk or disagrees | Accept decision, suggest alternatives if appropriate |
| Feature conflicts with existing code | Incomplete system knowledge | Re-read ARCHITECTURE.md, request diagnostic of affected area |
| Build fails mid-execution | Code error or dependency issue | Fix and redeploy as next patch number |
| Feature works but breaks something else | Insufficient testing | Roll back via patch, add integration checks |

## Guardrails

These actions ALWAYS require T3 (propose + wait) regardless of apparent simplicity:
- Any change to authentication or security
- Any change to the patch monitor itself
- Any database schema modification
- Any change to systemd service definitions
- Any change that affects multiple services simultaneously
- Any change to Iris's own instruction files or skills

---

_Last updated: 2026-02-22_
_Author: Ka'tuar'el_
