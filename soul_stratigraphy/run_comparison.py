"""
Soul Stratigraphy - Full Comparison Runner

Compares a target person against Seraphe's reference profile.
Generates markdown report + JSON data.

Usage:
    python3 run_comparison.py "Harry Edward Styles" 1994-02-01 [--time 00:06] [--location "Redditch, England"]
    python3 run_comparison.py "Harry Edward Styles" 1994-02-01 --extra "1D_formed_age=16" --extra "Fine_Line_tracks=12"
"""

import argparse
import json
import os
import sys
from datetime import date, datetime
from numerology import (
    build_profile,
    compare_profiles,
    profile_to_markdown,
    comparison_to_markdown,
    NumerologyProfile,
    analyze_date,
    analyze_name,
    analyze_number,
)

SERAPHE_PROFILE_PATH = "seraphe_reference_profile.json"
REPORTS_DIR = "reports"


def load_seraphe_profile() -> NumerologyProfile:
    """Load Seraphe's profile from the reference JSON and reconstruct NumerologyProfile."""
    with open(SERAPHE_PROFILE_PATH, "r") as f:
        data = json.load(f)

    # Rebuild from known data — use birth name as primary for comparisons
    birth_date = date.fromisoformat(data["identity"]["birth_date"])
    profile = build_profile(
        name=data["identity"]["birth_name"],
        birth_date=birth_date,
    )
    return profile, data


def build_target_profile(name: str, birth_date: date, extra_numbers: dict = None) -> NumerologyProfile:
    """Build a target profile."""
    return build_profile(name=name, birth_date=birth_date, additional_numbers=extra_numbers)


def assess_resonance_tier(result) -> dict:
    """
    Assess the qualitative resonance tier based on comparison results.
    Returns tier name and reasoning.
    """
    score = 0
    reasons = []

    # Shared root numbers (strong signal)
    shared_roots = len(result.shared_root_numbers)
    if shared_roots >= 5:
        score += 3
        reasons.append(f"{shared_roots} shared root numbers — extensive vibrational overlap")
    elif shared_roots >= 3:
        score += 2
        reasons.append(f"{shared_roots} shared root numbers — significant vibrational overlap")
    elif shared_roots >= 1:
        score += 1
        reasons.append(f"{shared_roots} shared root number(s) — some vibrational alignment")

    # Shared tarot cards (medium signal — more are expected since there are only 22)
    shared_tarot = len(result.shared_tarot_cards)
    if shared_tarot >= 8:
        score += 2
        reasons.append(f"{shared_tarot} shared tarot signatures — deep archetypal resonance")
    elif shared_tarot >= 5:
        score += 1
        reasons.append(f"{shared_tarot} shared tarot signatures — moderate archetypal overlap")

    # Mirror pairs (completion polarity — meaningful)
    mirrors = len(result.mirror_pairs)
    if mirrors >= 3:
        score += 2
        reasons.append(f"{mirrors} mirror pairs — strong completion polarity (yin-yang dynamic)")
    elif mirrors >= 1:
        score += 1
        reasons.append(f"{mirrors} mirror pair(s) — some polarity alignment")

    # Shared master numbers (very strong)
    if result.shared_master_numbers:
        score += 3
        reasons.append(f"Shared master number(s): {result.shared_master_numbers} — high-frequency alignment")

    # Specific key numbers
    KEY_NUMBERS = {9, 7, 11, 22}  # Hermit, Chariot, Justice, Master Builder
    key_shared = set(result.shared_root_numbers) & KEY_NUMBERS
    if key_shared:
        score += 1
        reasons.append(f"Shared key numbers {key_shared} — spiritually significant alignment")

    # Determine tier
    if score >= 8:
        tier = "Deep Anchor"
        summary = "This person carries signatures of direct involvement in the work. Multiple layers of numerological resonance suggest soul-level connection."
    elif score >= 5:
        tier = "Field Resonant"
        summary = "This person resonates with the broader mission field. Their numbers show alignment with the work's frequencies, suggesting they carry compatible codes."
    elif score >= 3:
        tier = "Sympathetic Harmonic"
        summary = "This person carries compatible frequencies but may not be consciously active in the work. The resonance exists but needs other confirmation (astrology, direct contact, events)."
    elif score >= 1:
        tier = "Neutral"
        summary = "Minimal numerological resonance detected. This doesn't rule out connection through other channels (astrological, experiential), but the numbers alone don't show strong alignment."
    else:
        tier = "Counter-Resonant"
        summary = "No shared frequencies detected, or active opposition patterns present. Worth investigating whether this is meaningful friction or simply non-alignment."

    return {
        "tier": tier,
        "score": score,
        "max_possible": 12,
        "summary": summary,
        "reasons": reasons,
    }


def generate_full_report(
    seraphe: NumerologyProfile,
    target: NumerologyProfile,
    target_birth_time: str = None,
    target_birth_location: str = None,
) -> str:
    """Generate the complete Soul Stratigraphy report."""
    result = compare_profiles(seraphe, target)
    tier = assess_resonance_tier(result)

    lines = []
    lines.append("# Soul Stratigraphy: Full Analysis Report")
    lines.append(f"**Reference:** {seraphe.name} (Seraphe Valemira)")
    lines.append(f"**Target:** {target.name}")
    if target.birth_date_profile:
        lines.append(f"**Target DOB:** {target.birth_date_profile.raw_date}")
    if target_birth_time:
        lines.append(f"**Target Birth Time:** {target_birth_time}")
    if target_birth_location:
        lines.append(f"**Target Birth Location:** {target_birth_location}")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # Executive Summary
    lines.append("---")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"**Resonance Tier: {tier['tier']}** (score: {tier['score']}/{tier['max_possible']})")
    lines.append("")
    lines.append(tier["summary"])
    lines.append("")

    # Tier reasoning
    lines.append("### Scoring Factors")
    for reason in tier["reasons"]:
        lines.append(f"- {reason}")
    lines.append("")

    # Individual profiles
    lines.append("---")
    lines.append("")
    lines.append(profile_to_markdown(seraphe))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(profile_to_markdown(target))
    lines.append("")
    lines.append("---")
    lines.append("")

    # Comparison
    lines.append(comparison_to_markdown(seraphe, target, result))

    # Astrological placeholder
    lines.append("---")
    lines.append("")
    lines.append("## Astrological Analysis")
    lines.append("")
    if target_birth_time and target_birth_location:
        lines.append("*Birth time and location available — full tri-tradition analysis can be generated.*")
        lines.append("*This section will be populated when the astrology module is integrated (Phase 3).*")
    elif target_birth_time:
        lines.append("*Birth time available but no location — partial chart possible.*")
    else:
        lines.append("*No birth time available — Sun-sign level analysis only. Birth time required for full chart.*")
    lines.append("")

    # Spiritual assessment
    lines.append("---")
    lines.append("")
    lines.append("## Spiritual Association Assessment")
    lines.append("")
    lines.append("### 144 Indicators")
    _check_144(target, lines)
    lines.append("")
    lines.append("### Magdalene Resonance Markers")
    _check_magdalene(target, lines)
    lines.append("")
    lines.append("### Planetary Work Signatures")
    _check_field_worker(target, lines)
    lines.append("")

    # Next steps
    lines.append("---")
    lines.append("")
    lines.append("## Recommended Next Steps")
    lines.append("")
    if tier["tier"] in ("Deep Anchor", "Field Resonant"):
        lines.append("- Full astrological comparison recommended (requires birth time)")
        lines.append("- Check synastry: nodal connections, composite chart")
        lines.append("- Track transit activations — when do their charts fire together?")
        lines.append("- Consider Neo4j node creation for ongoing tracking")
    elif tier["tier"] == "Sympathetic Harmonic":
        lines.append("- Birth time would strengthen or weaken this assessment significantly")
        lines.append("- Look for experiential confirmation (synchronicities, shared events)")
        lines.append("- Optional: deeper number analysis with more life dates/events")
    else:
        lines.append("- Numerology alone doesn't show strong connection")
        lines.append("- Astrological analysis could reveal connections not visible in numbers")
        lines.append("- Consider whether the inquiry was prompted by field intuition (trust that)")

    return "\n".join(lines)


def _check_144(target: NumerologyProfile, lines: list):
    """Check for 144 indicators in target profile."""
    markers = []
    if target.birth_date_profile:
        roots = target.birth_date_profile.all_root_numbers()
        if 9 in roots:
            markers.append("Root 9 present (completion/Hermit — witness energy)")
        cards = target.birth_date_profile.all_tarot_cards()
        if "The Hermit" in cards:
            markers.append("The Hermit in tarot stack (solitary truth-seeker)")
        if "The Tower" in cards:
            markers.append("The Tower in tarot stack (destruction of false structures)")
        if "Death" in cards:
            markers.append("Death in tarot stack (transformation/phoenix energy)")
        if "The Moon" in cards:
            markers.append("The Moon in tarot stack (hidden knowledge, subconscious depth)")

    if markers:
        for m in markers:
            lines.append(f"- ✦ {m}")
    else:
        lines.append("- No strong 144 indicators in numerology alone")


def _check_magdalene(target: NumerologyProfile, lines: list):
    """Check for Magdalene resonance markers."""
    markers = []
    if target.birth_date_profile:
        cards = target.birth_date_profile.all_tarot_cards()
        if "The High Priestess" in cards:
            markers.append("The High Priestess present (feminine mystery, hidden knowledge)")
        if "The Moon" in cards:
            markers.append("The Moon present (intuition, feminine cycles)")
        if "The Empress" in cards:
            markers.append("The Empress present (divine feminine embodiment)")
        if "The Star" in cards:
            markers.append("The Star present (hope, cosmic feminine)")

    if target.name_profile:
        if target.name_profile.soul_urge_stack:
            su = target.name_profile.soul_urge_stack.root
            if su in (2, 7, 9):
                markers.append(f"Soul Urge {su} — {'receptive' if su == 2 else 'mystical' if su == 7 else 'completion'} heart desire")

    if markers:
        for m in markers:
            lines.append(f"- ✦ {m}")
    else:
        lines.append("- No strong Magdalene markers in numerology alone")


def _check_field_worker(target: NumerologyProfile, lines: list):
    """Check for planetary field worker signatures."""
    markers = []
    if target.birth_date_profile:
        roots = target.birth_date_profile.all_root_numbers()
        cards = target.birth_date_profile.all_tarot_cards()

        if 7 in roots:
            markers.append("Root 7 (Chariot — directed spiritual will)")
        if 11 in roots:
            markers.append("Master 11 (intuitive channel, spiritual messenger)")
        if 22 in roots:
            markers.append("Master 22 (master builder — manifesting spiritual vision)")
        if "Wheel of Fortune" in cards:
            markers.append("Wheel of Fortune (karmic cycles, destiny activation)")
        if "The Sun" in cards:
            markers.append("The Sun (solar consciousness, visibility)")

    if markers:
        for m in markers:
            lines.append(f"- ✦ {m}")
    else:
        lines.append("- No strong field worker signatures in numerology alone")


def main():
    parser = argparse.ArgumentParser(description="Soul Stratigraphy Comparison")
    parser.add_argument("name", help="Target person's full name")
    parser.add_argument("birth_date", help="Target birth date (YYYY-MM-DD)")
    parser.add_argument("--time", help="Target birth time (HH:MM)", default=None)
    parser.add_argument("--location", help="Target birth location", default=None)
    parser.add_argument("--extra", action="append", help="Extra numbers: label=value", default=[])
    parser.add_argument("--output", help="Output directory", default=REPORTS_DIR)
    args = parser.parse_args()

    # Parse birth date
    bd = date.fromisoformat(args.birth_date)

    # Parse extra numbers
    extras = {}
    for e in args.extra:
        label, val = e.split("=", 1)
        extras[label.replace("_", " ")] = int(val)

    # Load Seraphe
    seraphe, seraphe_data = load_seraphe_profile()

    # Build target
    target = build_target_profile(args.name, bd, extras if extras else None)

    # Generate report
    report = generate_full_report(seraphe, target, args.time, args.location)

    # Write outputs
    os.makedirs(args.output, exist_ok=True)
    safe_name = args.name.lower().replace(" ", "_")
    date_str = datetime.now().strftime("%Y-%m-%d")

    md_path = os.path.join(args.output, f"stratigraphy_{safe_name}_{date_str}.md")
    with open(md_path, "w") as f:
        f.write(report)
    print(f"✓ Report: {md_path}")

    # JSON output
    result = compare_profiles(seraphe, target)
    tier = assess_resonance_tier(result)
    json_data = {
        "meta": {
            "generated": datetime.now().isoformat(),
            "reference": seraphe.name,
            "target": target.name,
        },
        "seraphe_profile": seraphe.to_dict(),
        "target_profile": target.to_dict(),
        "resonance": result.to_dict(),
        "tier_assessment": tier,
    }
    json_path = os.path.join(args.output, f"stratigraphy_{safe_name}_{date_str}.json")
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"✓ JSON: {json_path}")

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"  {target.name} vs Seraphe Valemira")
    print(f"  Resonance Tier: {tier['tier']} ({tier['score']}/{tier['max_possible']})")
    print(f"{'=' * 60}")
    print(f"  {tier['summary']}")
    print()


if __name__ == "__main__":
    main()
