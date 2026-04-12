# SYSTEM_Astrology.md

**Stream:** SEN (SENSUS)
**Location:** `/opt/mythos/astrology/`
**Status:** Production-ready as of April 2026
**Purpose:** Deterministic astrological calculation layer + LLM interpretation layer, strictly separated.

---

## Core Principle — NON-NEGOTIABLE

**LLMs do not do astrological math. Ever.**

Every planetary position, aspect orb, house cusp, and date calculation is produced by the calculator layer using Swiss Ephemeris via Kerykeion. The LLM (Claude, Iris, or any model) only *interprets* the output of the calculator. Never the reverse.

**Why this rule exists:** Early attempts at free-hand position calculation from LLM memory produced catastrophic errors — including inventing birth years, mis-placing Sedna by an entire sign, and fabricating orbs that didn't exist. The calculator layer is the ground truth. The LLM is the meaning layer. Do not cross the streams.

**Operational consequence:** If someone asks for astrological information and the calculator output is not in context, the correct response is to either (a) run the script, or (b) stop and ask for the data. Never free-hand. Never "estimate." Never "roughly speaking."

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 INTERPRETATION LAYER                     │
│        (Claude / Iris / human astrologer)               │
│                                                          │
│   Reads: calculator output (text)                       │
│   Writes: interpretation, narrative, synthesis          │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ text output (positions, aspects)
                          │
┌─────────────────────────────────────────────────────────┐
│                  CALCULATOR LAYER                        │
│          /opt/mythos/astrology/weekly_report.py         │
│                                                          │
│   Reads: people.json + Swiss Ephemeris files            │
│   Uses:  kerykeion 5.10.1 (wraps pyswisseph)            │
│   Output: deterministic text report                     │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │
┌──────────────────────┐  │  ┌───────────────────────────┐
│   people.json        │  │  │   /opt/mythos/ephemeris/  │
│   (chmod 600)        │──┴──│   Swiss Ephemeris files   │
│   Natal birth data   │     │   ast90, ast136, etc.     │
└──────────────────────┘     └───────────────────────────┘
```

---

## File Locations

| Path | Purpose |
|------|---------|
| `/opt/mythos/astrology/weekly_report.py` | Main calculator script. Takes date range + people, outputs positions and transit aspects. |
| `/opt/mythos/astrology/people.json` | Natal birth data for Adge, Seraphe, Fitz. `chmod 600`. Never world-readable. |
| `/opt/mythos/astrology/daily_transits.py` | Daily transit script with pre-configured natal data (earlier skill, still operational). |
| `/opt/mythos/ephemeris/` | Swiss Ephemeris data files. Required for asteroid calculations beyond the default set. |
| `/opt/mythos/.venv/bin/python3` | The venv Python. **Always use this.** System Python will fail. |

### Ephemeris Files Present

Complete set covering all 41 points the calculator supports:

- `ast90` — Sedna
- `ast136` — Eris, Haumea, Makemake
- `ast50` — Quaoar
- `ast10` — Chariklo
- `ast5` — Pholus
- `ast7` — Nessus
- Plus default ephemeris for inner planets, outer planets, Chiron, lunar nodes, Lilith

### Natal Data Sources

Canonical JSON gists (read-only, fetched on demand):

- **Adge:** https://gist.githubusercontent.com/adgedenkers/eb272c7b13449796eb008252f830870b/raw
- **Seraphe:** https://gist.githubusercontent.com/adgedenkers/ca159fc7118da2f0411efec7772ed9f1/raw

These gists contain the full natal chart export: `chart_objects`, `house_cusps`, `chart_points`, `chart_aspects`, `dignities`, `dispositors`, `fixed_star_conjunctions`, `geometric_patterns`, `arabic_parts`, `balance`. They are the authoritative natal reference for LLM interpretation work. **LLMs must fetch these when deep interpretation is requested — do not free-hand houses, angles, or dispositors from memory.**

---

## Calculator: `weekly_report.py`

### Invocation

```bash
/opt/mythos/.venv/bin/python3 /opt/mythos/astrology/weekly_report.py \
    <start-date> <end-date> [--core|--full] --people <person1>,<person2>,...
```

### Arguments

| Argument | Values | Purpose |
|----------|--------|---------|
| `<start-date>` | `YYYY-MM-DD` | First day of range (inclusive) |
| `<end-date>` | `YYYY-MM-DD` | Last day of range (inclusive) |
| `--core` | flag | 18 points: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Chiron, Mean_Lilith, True N/S Nodes, ASC, MC, DSC, IC |
| `--full` | flag | 41 points: core set + Ceres, Pallas, Juno, Vesta, Pholus, Eris, Sedna, Haumea, Makemake, Ixion, Orcus, Quaoar, four Arabic Parts, Vertex, Anti-Vertex, Regulus, Spica, Mean nodes, True Lilith |
| `--people` | comma-separated | `adge`, `seraphe`, `fitz` (any subset) |

### Example

```bash
# Full week report for Adge and Seraphe, all 41 points
/opt/mythos/.venv/bin/python3 /opt/mythos/astrology/weekly_report.py \
    2026-04-12 2026-04-18 --full --people adge,seraphe

# Single day quick read for Fitz, core points only
/opt/mythos/.venv/bin/python3 /opt/mythos/astrology/weekly_report.py \
    2026-04-12 2026-04-12 --core --people fitz
```

### Pipe to clipboard for paste-back into LLM context

```bash
/opt/mythos/.venv/bin/python3 /opt/mythos/astrology/weekly_report.py \
    2026-04-12 2026-04-18 --full --people adge,seraphe \
    | tee ~/week_$(date +%Y%m%d).txt \
    | xclip -selection clipboard && echo "✓ Copied to clipboard"
```

### Output Format

The report has four sections:

1. **Header** — roster, date range, generation timestamp
2. **Natal chart summary** — Sun/Moon/Rising for each person (sanity check)
3. **Daily transit positions** — for each day in range, all N points with sign, degree, minute, retrograde flag, and Aries stellium composition when applicable. Calculated at noon ET, Oxford NY.
4. **Transit aspects** — for each person, each day, every transit-to-natal aspect within 6° orb, sorted by tightest orb first. Includes major and minor/harmonic aspects (conjunction, opposition, square, trine, sextile, quincunx, semi-sextile, semi-square, sesquiquadrate, quintile, biquintile, tridecile, quindecile, septile, biseptile, triseptile).
5. **Natal chart reminders** — tight natal aspects (<2°) per person at the bottom for interpretive anchoring.

### Time Reference

All positions calculated at **noon ET (America/New_York), Oxford NY coordinates**. This is the standard daily snapshot — not birth time, not current time. For transit-to-event timing, interpret accordingly (a partile aspect at noon ET means the aspect is tightest around that moment but is functionally active for the whole day).

---

## Data File: `people.json`

### Schema

```json
{
  "people": {
    "<name>": {
      "name": "Display Name",
      "birth_date": "YYYY-MM-DD",
      "birth_time": "HH:MM",
      "birth_location": "City, State, Country",
      "latitude": 00.000000,
      "longitude": 00.000000,
      "timezone": "America/New_York"
    }
  }
}
```

### Currently Seeded

- **adge** — Adriaan Harold Denkers (Adge / Ka'tuar'el), Sag Sun / Aries Moon / Sag Rising
- **seraphe** — Rebecca Lydia Denkers (Seraphe), Leo Sun / Pisces Moon / Scorpio Rising
- **fitz** — Adriaan Fitzgerald Denkers (Fitz), b. September 8, 2010

### Security

`people.json` is `chmod 600`. It contains birth data that should not be world-readable. Never check this file into a public repo. If you add a new person, set permissions explicitly:

```bash
chmod 600 /opt/mythos/astrology/people.json
```

---

## Interpretation Workflow (LLM-facing)

### When a weekly read is requested

1. **Run the calculator.** Do not interpret from memory.
2. **Read every line of the output before writing anything.** Do not skim.
3. **If house-level precision is needed, fetch the natal gist(s).** The `weekly_report.py` output gives transit-to-natal aspects by orb but does not resolve *which house* the transiting planet is walking through on the native's chart. For that you need `house_cusps` from the natal JSON.
4. **Cite real numbers only.** Every orb, every degree, every aspect must appear in the pasted data. No free-handing.
5. **Respect the separation.** If a number isn't there, say "I don't have that in the output — re-run the script with X" or "let me fetch the natal gist." Do not confabulate.

### Depth vs. length

For deep reads (like a week-long activation interpretation), expect 3,000–5,000 words when full depth is requested. For daily quick-reads, 200–500 words is appropriate. For "just tell me the positions," zero words of interpretation — just confirm the numbers are loaded.

### Plain-English mode

Adge sometimes requests "translate this for someone who doesn't know astrology" or "plain English version." In that mode: no jargon, no sign names unless necessary, no house numbers, no aspect names. Translate into felt experience. The numbers stay deterministic underneath; only the vocabulary changes.

---

## Known Pitfalls (learned the hard way)

1. **LLM position hallucination.** Fixed by script-only calculation. Do not undo this.
2. **Sedna is in Gemini, not Aries.** It was mis-placed in early sessions. Do not repeat.
3. **Birth year invention.** A fallback branch in an early script invented Adge's birth year "in case the gist fetch failed." This was removed and must never return. If a data source is unreachable, stop and ask — never synthesize.
4. **Kerykeion was already installed.** Early work rolled custom aspect math before checking. Always check what libraries exist before writing math.
5. **Ollama chat API vs baked models.** Not directly astrology-related, but relevant if Iris is the interpreter: when using baked Modelfiles (iris:latest), system messages override the baked SYSTEM block — inject dynamic context as `[Context]...[/Context]` preamble in the user message.
6. **Free-hand house placement.** The weekly report gives aspect orbs but not transit-house placements. If house matters, fetch the natal gist for cusps. Don't guess from rising sign.

---

## Planned Integration (Not Yet Built)

### Telegram Command Surface

Target: wire `weekly_report.py` into `mythos-bot` so reports can be triggered from Telegram.

```
/astro <person> <range> <mode>

person: adge | seraphe | fitz
range:  today | tomorrow | week | YYYY-MM-DD | YYYY-MM-DD..YYYY-MM-DD
mode:   positions | full

Examples:
  /astro seraphe today positions        → numbers only
  /astro seraphe today full             → numbers + Iris interpretation
  /astro adge week full                 → full week + interpretation
  /astro fitz tomorrow positions        → positions only
```

**This is a SYS patch (bot handler) + SEN patch (command wiring).** Do not build mid-conversation. Start a fresh session with the full diagnostic dump (TODO.md, ARCHITECTURE.md, STREAMS.md, `mythos-diag streams` for live counters) and build it under the normal Mythos patch protocol. The handler shells out to `weekly_report.py` and either returns raw output (`positions` mode) or pipes through Iris for interpretation (`full` mode).

### Automatic Daily Transit Push

Target: cron-triggered daily transit summary pushed to Telegram each morning, separate messages for Adge and Seraphe, using the `daily_transits.py` skill.

### Conversation Bridge Integration

Target: store significant transit activations as Exchange nodes in Neo4j so Iris can recall "what was happening in the sky when X happened" during later conversations.

---

## Quick Reference Card

**Run a weekly report:**
```bash
/opt/mythos/.venv/bin/python3 /opt/mythos/astrology/weekly_report.py \
    2026-04-12 2026-04-18 --full --people adge,seraphe
```

**Fetch natal gists for house-level work:**
```bash
curl -s https://gist.githubusercontent.com/adgedenkers/eb272c7b13449796eb008252f830870b/raw \
    | python3 -m json.tool | head -500   # Adge

curl -s https://gist.githubusercontent.com/adgedenkers/ca159fc7118da2f0411efec7772ed9f1/raw \
    | python3 -m json.tool | head -500   # Seraphe
```

**Check people.json permissions:**
```bash
ls -l /opt/mythos/astrology/people.json   # should show -rw-------
```

**Confirm ephemeris path is set:**
```bash
ls /opt/mythos/ephemeris/ast*.se1
```

**Venv sanity check:**
```bash
/opt/mythos/.venv/bin/python3 -c "import kerykeion; print(kerykeion.__version__)"
# Expected: 5.10.1 or later
```

---

## The Discipline

The whole system rests on one rule: **numbers come from the calculator, meaning comes from the interpreter, and the two never swap jobs.**

When that rule holds, the output is trustworthy and the interpretation has ground to stand on. When the rule breaks — when an LLM "just estimates" a position or an orb — everything downstream is contaminated and cannot be trusted. There is no middle ground. The script is the source of truth. The interpreter's job is to make meaning from what the script produces, not to produce the numbers themselves.

This rule is not bureaucratic overhead. It is what makes the difference between real astrological work and confident hallucination dressed in astrological vocabulary. Hold the line.

---

**Stream owner:** SEN
**Last updated:** 2026-04-12
**Tested against:** kerykeion 5.10.1, pyswisseph 2.10.03, Python 3.12, Ubuntu 24.04
