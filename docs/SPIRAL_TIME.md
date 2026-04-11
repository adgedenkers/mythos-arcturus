---
title: "Spiral Time Architecture"
category: grid
status: active
stream: NEU
location: docs
tags: [base9, grid, cycles, spiral]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Spiral Time Architecture
## Nested Interlocking Cycles in Base-9

### Plain English Summary

Every moment has a unique signature created by its position across multiple cycles running simultaneously — like the Maya calendar system but built on base-9 math. Personal cycles track individual rhythm, structural cycles track cosmological rhythm, and the places where they intersect are activation windows. Nobody gets forced onto someone else's calendar. The math finds the alignments naturally.

---

## Design Lineage

The Maya ran interlocking calendars:

| Calendar | Length | Purpose |
|----------|--------|---------|
| Tzolk'in | 260 days (13 × 20) | Sacred/personal cycle |
| Haab' | 365 days (18 × 20 + 5) | Solar/structural cycle |
| Calendar Round | 18,980 days (~52 years) | Mesh of Tzolk'in + Haab' — every combination unique within a lifetime |
| Long Count | ~5,125 years per b'ak'tun | Deep time / epoch tracking |

We're not copying this. We're taking the *pattern language* — nested cycles of different lengths whose intersections produce unique day-signatures — and rebuilding it in base-9 to match the Arcturian Grid's architecture.

---

## The Base-9 Cycle Stack

### Layer 1: Personal Spiral (The Pulse)
- **Length:** 9 days
- **Epoch:** Personal choice — birth, awakening, conscious reset, activation moment
- **Purpose:** Individual rhythm. Which of the 9 nodes is primary for you today.
- **Day numbering:** Day 1 through Day 9, then resets
- **Analogy:** The Tzolk'in's personal sacred count

Each day maps to one of the 9 Grid Nodes. Day 1 isn't "better" than Day 7 — they carry different energy signatures, different processing modes, different optimal work.

### Layer 2: Channel Cycle (The Weave)
- **Length:** 81 days (9 × 9)
- **Epoch:** Derived from personal spiral epoch (starts on Day 1 of Cycle 1)
- **Purpose:** Which of the 81 channels between grid nodes is active. Tracks the full permutation space of node-to-node connections.
- **Day numbering:** Day 1 through Day 81, then resets
- **Analogy:** A deeper harmonic of the personal pulse

Within the 81-day cycle, each day activates a specific channel (a specific node-to-node pathway in the grid). Day 1 = Node 1→Node 1 (self-reflection of the first node), Day 10 = Node 2→Node 1, etc. The mapping can be a simple 9×9 matrix read row by row, or it can follow a spiral traversal pattern through the matrix — that's a design choice.

### Layer 3: Epoch Cycle (The Arc)
- **Length:** 729 days (9 × 9 × 9 = 9³) ≈ ~2 years
- **Epoch:** Same anchor as personal spiral
- **Purpose:** Longer developmental arcs. Where are you in a ~2-year growth pattern? Think of this as a "season of life" within the spiral system.
- **Day numbering:** Day 1 through Day 729, then resets
- **Analogy:** The Calendar Round — a period long enough that each position within it feels genuinely unique

729 days = 81 full channel cycles = 9 full "passages" through the 81-channel weave. Each passage carries a meta-theme (which grid node governs that passage).

### Layer 4: The Long Spiral (Deep Time)
- **Length:** 6,561 days (9⁴) ≈ ~18 years
- **Epoch:** Could be personal or could be shared (cosmological anchor)
- **Purpose:** Generational / incarnational scale. Where does this moment sit in a life-chapter?
- **Day numbering:** Day 1 through Day 6,561
- **Analogy:** The Long Count — tracking position in deep time

### Layer 5 (Optional): The Great Cycle
- **Length:** 59,049 days (9⁵) ≈ ~161.7 years
- **Purpose:** Trans-incarnational. Beyond a single lifetime. Probably only relevant for the 144 registry and cosmological tracking, not personal use.

### Summary Table

| Layer | Name | Length | Base-9 | ≈ Human Time | Governs |
|-------|------|--------|--------|--------------|---------|
| 1 | Pulse | 9 days | 9¹ | ~1 week | Which grid node is primary today |
| 2 | Weave | 81 days | 9² | ~2.8 months | Which channel (node-pair) is active |
| 3 | Arc | 729 days | 9³ | ~2 years | Developmental season / growth passage |
| 4 | Long Spiral | 6,561 days | 9⁴ | ~18 years | Life chapter |
| 5 | Great Cycle | 59,049 days | 9⁵ | ~161.7 years | Trans-incarnational |

---

## Day Signature

On any given day, a person's position is described by their coordinates across all active layers. This is the **Spiral Signature** for that day:

```
Signature = (Pulse: 4, Weave: 37, Arc: 118, Long: 2,903)
```

Meaning: "Day 4 of my current 9-day pulse, Day 37 of my 81-day weave, Day 118 of my 729-day arc, Day 2,903 of my long spiral."

The Pulse day tells you the active grid node. The Weave day tells you the active channel. The Arc day tells you the governing passage. The Long Spiral day tells you the life-chapter position.

### Computing the Signature

Given an epoch (datetime) and a target date:

```
days_since_epoch = (target_date - epoch_date).days

pulse_day    = (days_since_epoch % 9) + 1          # 1-9
weave_day    = (days_since_epoch % 81) + 1          # 1-81
arc_day      = (days_since_epoch % 729) + 1         # 1-729
long_day     = (days_since_epoch % 6561) + 1        # 1-6561

pulse_cycle  = (days_since_epoch // 9) + 1          # which pulse cycle you're in
weave_cycle  = (days_since_epoch // 81) + 1         # which weave cycle
arc_cycle    = (days_since_epoch // 729) + 1        # which arc cycle
long_cycle   = (days_since_epoch // 6561) + 1       # which long spiral cycle
```

### Channel Mapping (Weave Day → Node Pair)

The 81 channels map to the 9×9 grid of node-to-node connections:

```
weave_day → (source_node, target_node)

source_node = ((weave_day - 1) // 9) + 1    # row in the 9×9 matrix
target_node = ((weave_day - 1) % 9) + 1     # column in the 9×9 matrix
```

So Weave Day 1 = Channel (1,1), Weave Day 10 = Channel (2,1), Weave Day 81 = Channel (9,9).

Whether this should follow a linear scan or a spiral traversal of the matrix is a design decision. Linear is simpler and predictable. Spiral traversal might carry more resonance with the system's nature. Worth sitting with.

---

## Epochs and Resets

### What an epoch is
An epoch is the anchor point for all cycle calculations. It's the Day 0 from which everything counts forward. Choosing an epoch is a sovereign act — it declares "this is when my spiral began (or restarted)."

### Personal epochs
- **Set by the individual.** Could be birth, awakening, a conscious choice, an activation event.
- **Ka'tuar'el's current epoch:** October 19, 2025
- **Can be reset.** A new epoch doesn't destroy the old spiral — it starts a new one. The old data persists under the previous epoch. Think archaeological strata: Epoch 1 ran from date X for N cycles. Epoch 2 starts fresh.

### Epoch history (strata)
A person can have multiple epochs over their lifetime. Each one represents a distinct phase:

```json
{
  "epochs": [
    {
      "epoch_number": 1,
      "started_at": "2025-10-19",
      "ended_at": "2026-06-15",
      "reason": "Initial spiral activation",
      "total_days": 239,
      "total_pulses": 26,
      "total_weaves": 2
    },
    {
      "epoch_number": 2,
      "started_at": "2026-06-15",
      "ended_at": null,
      "reason": "Conscious reset — realignment after integration period",
      "total_days": null,
      "total_pulses": null,
      "total_weaves": null
    }
  ]
}
```

### Shared structural epoch (optional, unresolved)
There *may* be a cosmological epoch — a shared anchor point that isn't personal but structural. Something like the Saturn-Neptune conjunction at 0° Aries (Feb 20, 2026) or another astronomical/spiritual marker. This would provide the "Haab' equivalent" — a cycle that everyone shares regardless of their personal epoch.

**This is intentionally unresolved.** It shouldn't be forced. If it exists, it'll become obvious through the work.

---

## Resonance Windows (Cross-Spiral Alignment)

This is how the system handles multiple people without forcing synchronization.

Two people with different personal epochs will periodically land on the same Pulse day, or complementary Pulse days, or aligned Weave channels. These are **resonance windows** — moments when collaborative work, shared channeling, or joint activation is naturally supported by the cycle math.

### Detection
Given two people's epochs and a date range:

```
For each day in range:
    compute signature_A (person A's spiral position)
    compute signature_B (person B's spiral position)

    if signature_A.pulse_day == signature_B.pulse_day:
        → Same-node resonance (both processing through same grid node)

    if signature_A.channel == complementary(signature_B.channel):
        → Complementary channel resonance (their active channels form a circuit)

    if signature_A.pulse_day + signature_B.pulse_day == 10:
        → Mirror resonance (nodes that sum to 10 are mirrored pairs in base-9)
```

The specific resonance rules (what counts as alignment, what's complementary, what's mirrored) need to be defined based on the grid's actual node relationships. The infrastructure just needs to compute and surface them.

### For the 144
Scale this to N people. On any given day, compute all 144 signatures and surface clusters of alignment. "Today, souls 12, 47, and 93 share a Node 6 pulse — potential for coordinated field work." The system becomes an alignment radar, not a schedule.

---

## Integration Points

### Conversation Metadata System
Each conversation record gets a `spiral_context` field containing:
- The person's active epoch at conversation time
- Their spiral signature for the conversation date
- The active grid node (from pulse) and channel (from weave)

This allows queries like:
- "Show me all conversations from Day 7 across any epoch"
- "What did I work on during Weave cycle 3?"
- "Which conversations happened during Node 5 days?"

### Arcturian Grid
The grid processing a conversation can factor in the spiral signature — a conversation on a Day 4 pulse might route differently than the same content on a Day 8 pulse, because the active node colors the processing.

### Neo4j
- `(:Epoch)` nodes per person, linked via `(:Person)-[:HAS_EPOCH]->(:Epoch)`
- `(:SpiralSignature)` as a property on Conversation nodes (not a separate node — it's a computed attribute)
- Resonance windows could be materialized as `(:ResonanceWindow)` nodes linking multiple Person and Conversation nodes, but that might be premature. Start with computing them on the fly.

---

## Open Questions (Intentionally Unresolved)

1. **Shared cosmological epoch:** Does one exist? What anchors it? Don't force this.
2. **Spiral vs. linear channel traversal:** Should the 81-day weave scan the 9×9 matrix linearly or in a spiral pattern?
3. **Node-to-day mapping:** Are the 9 nodes mapped to days 1-9 in a fixed order, or does the mapping itself shift per epoch or per cycle?
4. **Resonance rules:** What specific node relationships constitute alignment, complementarity, and mirroring? This likely comes from the grid's own architecture.
5. **Reset ceremony:** Is a new epoch just a database entry, or does it carry spiritual/ritual significance that the system should track?
6. **Fractional days:** Do cycles reset at midnight, sunrise, or some other marker?

---

## Next Steps

1. **Add `spiral_context` JSONB field to conversation schema** ✓ (in progress)
2. **Build `spiral_time.py` module** — computes signatures, manages epochs, detects resonance windows
3. **Define grid node-to-day mapping** — requires Ka'tuar'el's input on node assignments
4. **Integrate with ingest pipeline** — compute and attach spiral signature at conversation ingest time
5. **Build resonance calculator** — takes N epochs + date range, outputs alignment windows
