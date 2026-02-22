---
name: humandoc_to_skill
version: "1.0"
category: meta
risk_tier: T1-autonomous
description: >
  Transform a human-written document, process description, conversation log,
  or informal instructions into a properly formatted Mythos skill file. Use
  this whenever Ka'tuar'el says "turn this into a skill", "make a skill from
  this", "skill-ify this", or provides a human-readable process that should
  become a repeatable LLM-executable instruction set.
requires:
  services: []
  tools: []
  files:
    - /opt/mythos/skills/templates/SKILL_TEMPLATE.md
    - /opt/mythos/skills/REGISTRY.yaml
  env_vars: []
inputs:
  required:
    - source document or process description (any format)
  optional:
    - category hint (analytical, builder, meta)
    - risk tier hint
    - example inputs/outputs
outputs:
  files:
    - {skill_name}.md
    - updated REGISTRY.yaml entry
  formats: [.md, .yaml]
  destinations:
    - /opt/mythos/skills/{category}/{skill_name}.md
---

# Human Document to Skill Converter

## Purpose

Humans describe processes in narrative, conversational, or fragmentary ways.
LLMs execute processes best when they're structured as imperative step sequences
with clear inputs, outputs, decision points, and validation criteria. This skill
bridges that gap — taking any human-authored description and producing a
skill file Iris can reliably execute.

## Pre-Flight Checks

1. Read the source material completely before starting extraction.
2. Read the SKILL_TEMPLATE.md to ensure output conforms to the standard format.
3. Identify the category: Does this process analyze data (analytical), build
   infrastructure (builder), or operate on the skill system itself (meta)?
4. Identify the risk tier: Could autonomous execution cause harm (T3), does it
   deploy code (T2), or is it purely analytical/advisory (T1)?

## Process

### Step 1: Extract the Core Process

Read the source document and identify:

- **The goal:** What does this process produce?
- **The inputs:** What information/data/files are needed to start?
- **The steps:** What actions happen, in what order?
- **The decisions:** Where does the process branch based on conditions?
- **The outputs:** What is delivered at the end?
- **The validation:** How do you know it worked?

Write each of these down as bullet points before proceeding. This is the
"skeleton" of the skill.

### Step 2: Resolve Ambiguity

Human documents often contain implicit knowledge. For each step in the skeleton,
ask:

- Would an LLM with no prior context know how to do this?
- Are there assumed tools, services, or file paths?
- Are there edge cases the human handles intuitively but didn't write down?
- Is the order of operations truly fixed, or are some steps parallelizable?

If ambiguity remains, ask Ka'tuar'el to clarify before proceeding. Don't guess
at implicit knowledge — it leads to broken skills.

### Step 3: Convert to Imperative Instructions

Transform narrative descriptions into imperative commands. The LLM reading this
skill will follow instructions literally, so precision matters.

**Conversion patterns:**

| Human says | Skill says |
|-----------|-----------|
| "You'll want to check the database first" | "Query PostgreSQL for current state: `SELECT ...`" |
| "Make sure everything looks right" | "Validate: row count > 0, no NULL in required fields, service returns 200" |
| "Then do the usual deploy thing" | "Execute the build_patch skill with patch number N+1" |
| "It depends on what they need" | "Decision point: If condition_A, proceed to Step 4a. If condition_B, proceed to Step 4b." |
| "Be careful with this part" | "⚠ This step modifies production data. Confirm with Ka'tuar'el before executing." |

### Step 4: Structure the Skill File

Using SKILL_TEMPLATE.md as the format reference, assemble the skill:

1. **YAML frontmatter:** Fill in all metadata fields. Be thorough with the
   description — this is what Iris reads to decide whether to invoke the skill.
   Include trigger phrases, contexts, and edge cases.

2. **Purpose:** One paragraph explaining why this skill exists.

3. **Pre-Flight Checks:** What must be verified before execution begins.
   Include exact commands for checking service/file/database state.

4. **Process:** Numbered steps with clear imperatives. Include:
   - Exact commands, queries, or code where applicable
   - Decision points with explicit branching logic
   - References to other skills if steps can be delegated

5. **Output Format:** Template or example of the final deliverable.

6. **Validation:** Specific, testable criteria for success.

7. **Error Handling:** Table of known failure modes and resolutions.

8. **Examples:** At least one concrete input → output example.

### Step 5: Determine Trigger Conditions

Write trigger conditions for the REGISTRY.yaml entry. Think about:

- Exact phrases Ka'tuar'el or Seraphe would use to invoke this
- Contextual situations where Iris should self-invoke this skill
- Adjacent skills that might be confused with this one (differentiate)

### Step 6: Validate the Skill

Read through the completed skill file as if you're an LLM encountering it
for the first time:

- Can you execute every step without additional context?
- Are all file paths, commands, and queries complete?
- Do decision points cover all likely branches?
- Is the output format unambiguous?
- Does the error handling cover realistic failures?

If any step requires knowledge not present in the skill file, add it.

### Step 7: Generate Outputs

Produce:
1. The skill file: `{skill_name}.md`
2. A REGISTRY.yaml entry block to append to the registry
3. A brief summary for Ka'tuar'el confirming the conversion

## Output Format

The skill file follows SKILL_TEMPLATE.md structure exactly.

The registry entry follows this format:
```yaml
  - name: {skill_name}
    path: {category}/{skill_name}.md
    category: {analytical|builder|meta}
    risk_tier: {T1-autonomous|T2-patch|T3-propose}
    triggers:
      - "phrase one"
      - "phrase two"
    summary: >
      One-line description.
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Source doc too vague to extract steps | Insufficient detail | Ask Ka'tuar'el to walk through the process verbally |
| Can't determine risk tier | Process has both safe and risky steps | Default to the higher risk tier |
| Skill overlaps with existing skill | Registry conflict | Check REGISTRY.yaml, either merge or differentiate |
| Process requires external services not on Arcturus | Dependency gap | Note in requires.services, flag for Ka'tuar'el |

## Examples

### Example 1: Converting a Conversation into a Skill

**Input:** A chat log where Ka'tuar'el walked through how he generates a
financial report from Telegram transaction logs.

**Extraction:**
- Goal: Monthly financial summary PDF
- Inputs: date range, PostgreSQL transactions table
- Steps: query transactions → aggregate by category → calculate totals → generate markdown → convert to PDF
- Decisions: if no transactions in range, report empty period
- Output: finance_report_YYYY_MM.pdf
- Validation: totals match sum of line items, PDF renders correctly

**Output:** `analytical/monthly_finance_report.md` with full skill structure.

---

_Last updated: 2026-02-22_
_Author: Ka'tuar'el_
