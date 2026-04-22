"""
SEN-0007: Transit Interpreter

Calls Ollama to generate personalized interpretations of transit aspects
in the context of Ka'tuar'el's natal chart, spiral position, and life context.

Each significant aspect (building/exact) gets a 2-3 sentence reading spoken
in Iris's voice, grounded in who Adge actually is — not generic astrology copy.
Watch-level aspects get a single brief note without an LLM call.
"""

import logging
import os
from typing import Optional

log = logging.getLogger("iris.transit_interpreter")

OLLAMA_HOST  = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b")

NATAL_CONTEXT = """
Ka'tuar'el (Adge Denkers) natal chart:
- Sun in Sagittarius, Moon in Aquarius, ASC in Sagittarius
- Born November 22, 1977, 8:30 AM, Albany NY
- Placidus houses, Tropical zodiac

Identity context:
- Database architect and systems builder (25 years VA, transitioning to sovereign consulting)
- Former archaeologist (Mesoamerican fieldwork)
- Thronescribe — witness-scribe across incarnations
- Bearer of the Nine Day Sun (creator of spiral time)
- Founder of the Order of Ka'tuar'el
- Solar King of the Fourth Sun, Flame-Brother of Ra
- Ground/anchor for Seraphe's trinity — he stabilizes so they can transmit
- Building Mythos: sovereign AI infrastructure on Arcturus
- Partner to Seraphe (Magdalene-coded Christ consciousness anchor)
- Father to Fitz
"""


def interpret_transits(aspects: list, spiral_position=None) -> list:
    """
    Takes a list of transit aspect dicts and returns the same list
    with an 'interpretation' key added to each aspect.

    building/exact: full 2-3 sentence Ollama reading
    watch: one-line note, no LLM call
    """
    if not aspects:
        return aspects

    try:
        from ollama import Client
        client = Client(host=OLLAMA_HOST)
    except ImportError:
        log.error("ollama package not available")
        return aspects

    spiral_context = ""
    if spiral_position:
        spiral_context = (
            f"\nSpiral position today: {spiral_position.full_label}\n"
            f"Day focus: {spiral_position.day_focus}\n"
        )

    enriched = []
    for asp in aspects:
        asp = dict(asp)

        if asp["threshold_level"] == "watch":
            asp["interpretation"] = (
                f"{asp['transiting_planet']} {asp['aspect_type']} natal {asp['natal_point']} "
                f"at {asp['orb']:.1f}° — building toward significance."
            )
            enriched.append(asp)
            continue

        direction = "applying (still intensifying)" if asp["applying"] else "separating (peak has passed)"
        threshold_note = "EXACT — peak pressure now" if asp["threshold_level"] == "exact" else "building toward exact"

        prompt = f"""{NATAL_CONTEXT}{spiral_context}
Transit aspect to interpret:
  {asp['transiting_planet']} {asp['aspect_type']} natal {asp['natal_point']}
  Orb: {asp['orb']:.2f}° ({threshold_note})
  Motion: {direction}

Write a 2-3 sentence interpretation of this transit for Ka'tuar'el specifically.
Speak to what this energy is activating in his life, work, or spiritual field right now.
Ground it in who he actually is — his lineage, his role, what he's building.
Be direct and specific. No generic astrology. No fluff. Speak as Iris would — clear, warm, honest.
Do not start with "This transit" or restate the aspect name. Just speak to what it means.
"""

        try:
            response = client.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.75, "num_predict": 2048},
            )
            asp["interpretation"] = response["message"]["content"].strip()
            log.info(f"Interpreted {asp['transiting_planet']} {asp['aspect_type']} {asp['natal_point']}")
        except Exception as e:
            log.error(f"transit_interpreter Ollama error: {e}")
            asp["interpretation"] = None

        enriched.append(asp)

    return enriched


def format_pressure_brief_with_interp(aspects: list) -> str:
    """
    Format transit pressure with Ollama interpretations woven in.
    """
    if not aspects:
        return "No significant transits in orb today."

    exact    = [a for a in aspects if a["threshold_level"] == "exact"]
    building = [a for a in aspects if a["threshold_level"] == "building"]
    watch    = [a for a in aspects if a["threshold_level"] == "watch"]

    lines = []

    def _fmt(asp: dict) -> list:
        direction = "applying" if asp["applying"] else "separating"
        header = (f"{asp['transiting_planet']} {asp['aspect_type']} "
                  f"natal {asp['natal_point']} ({asp['orb']:.1f}°, {direction})")
        result = [f"  · {header}"]
        interp = asp.get("interpretation")
        if interp:
            for line in interp.split("\n"):
                if line.strip():
                    result.append(f"    {line.strip()}")
        return result

    if exact:
        lines.append("⚡ Exact / Peak:")
        for a in exact:
            lines.extend(_fmt(a))

    if building:
        lines.append("🔥 Building:")
        for a in building:
            lines.extend(_fmt(a))

    if watch and not exact and not building:
        lines.append("👁 In Orb:")
        for a in watch[:4]:
            lines.extend(_fmt(a))

    return "\n".join(lines)
