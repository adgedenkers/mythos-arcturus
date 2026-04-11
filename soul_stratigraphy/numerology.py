"""
Soul Stratigraphy - Enhanced Numerology Engine
Ka'tuar'el Extension: Stratified Reduction with Tarot Mapping

Every number reduced through ALL intermediate stages.
Each intermediate ≤ 21 maps to a Major Arcana card.
This creates a reduction stack — the full path from raw number to root digit.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import date, datetime
import json


# =============================================================================
# TAROT MAPPING
# =============================================================================

MAJOR_ARCANA = {
    0: "The Fool",
    1: "The Magician",
    2: "The High Priestess",
    3: "The Empress",
    4: "The Emperor",
    5: "The Hierophant",
    6: "The Lovers",
    7: "The Chariot",
    8: "Strength",
    9: "The Hermit",
    10: "Wheel of Fortune",
    11: "Justice",
    12: "The Hanged Man",
    13: "Death",
    14: "Temperance",
    15: "The Devil",
    16: "The Tower",
    17: "The Star",
    18: "The Moon",
    19: "The Sun",
    20: "Judgement",
    21: "The World",
}

# Alternate tradition (Thoth / Marseilles swap 8 and 11)
MAJOR_ARCANA_ALT = {
    **MAJOR_ARCANA,
    8: "Justice",
    11: "Strength (Lust)",
}

MASTER_NUMBERS = {11, 22, 33}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ReductionStep:
    """A single step in the reduction stack."""
    value: int
    tarot_card: Optional[str] = None
    tarot_card_alt: Optional[str] = None  # Thoth/Marseilles mapping
    is_master: bool = False
    is_root: bool = False

    def to_dict(self):
        d = {"value": self.value}
        if self.tarot_card:
            d["tarot_card"] = self.tarot_card
        if self.tarot_card_alt and self.tarot_card_alt != self.tarot_card:
            d["tarot_card_alt"] = self.tarot_card_alt
        if self.is_master:
            d["is_master"] = True
        if self.is_root:
            d["is_root"] = True
        return d


@dataclass
class ReductionStack:
    """Full reduction path from raw number to root digit."""
    label: str
    raw_value: int
    steps: list = field(default_factory=list)
    root: int = 0

    def to_dict(self):
        return {
            "label": self.label,
            "raw_value": self.raw_value,
            "steps": [s.to_dict() for s in self.steps],
            "root": self.root,
            "tarot_signature": self.tarot_signature(),
        }

    def tarot_signature(self) -> list:
        """All tarot cards that appear in this reduction stack."""
        return [s.tarot_card for s in self.steps if s.tarot_card]


@dataclass
class DateProfile:
    """Full numerology profile for a date."""
    raw_date: str
    month_stack: ReductionStack = None
    day_stack: ReductionStack = None
    year_full_stack: ReductionStack = None
    year_high_stack: ReductionStack = None
    year_low_stack: ReductionStack = None
    life_path_stack: ReductionStack = None

    def to_dict(self):
        d = {"raw_date": self.raw_date}
        for key in ["month_stack", "day_stack", "year_full_stack",
                     "year_high_stack", "year_low_stack", "life_path_stack"]:
            val = getattr(self, key)
            if val:
                d[key] = val.to_dict()
        d["all_tarot_cards"] = self.all_tarot_cards()
        d["all_root_numbers"] = self.all_root_numbers()
        return d

    def all_tarot_cards(self) -> list:
        """Every unique tarot card across all stacks."""
        cards = []
        for key in ["month_stack", "day_stack", "year_full_stack",
                     "year_high_stack", "year_low_stack", "life_path_stack"]:
            val = getattr(self, key)
            if val:
                cards.extend(val.tarot_signature())
        return list(dict.fromkeys(cards))  # unique, preserving order

    def all_root_numbers(self) -> list:
        """All root numbers from all stacks."""
        roots = []
        for key in ["month_stack", "day_stack", "year_full_stack",
                     "year_high_stack", "year_low_stack", "life_path_stack"]:
            val = getattr(self, key)
            if val:
                roots.append(val.root)
        return roots


@dataclass
class NameProfile:
    """Numerology profile derived from a name."""
    full_name: str
    expression_stack: ReductionStack = None   # all letters
    soul_urge_stack: ReductionStack = None    # vowels
    personality_stack: ReductionStack = None   # consonants

    def to_dict(self):
        d = {"full_name": self.full_name}
        for key in ["expression_stack", "soul_urge_stack", "personality_stack"]:
            val = getattr(self, key)
            if val:
                d[key] = val.to_dict()
        return d


@dataclass
class NumerologyProfile:
    """Complete numerology profile for a subject."""
    name: str
    birth_date_profile: DateProfile = None
    name_profile: NameProfile = None
    additional_numbers: list = field(default_factory=list)  # list of ReductionStack

    def to_dict(self):
        d = {"name": self.name}
        if self.birth_date_profile:
            d["birth_date"] = self.birth_date_profile.to_dict()
        if self.name_profile:
            d["name_numerology"] = self.name_profile.to_dict()
        if self.additional_numbers:
            d["additional_numbers"] = [s.to_dict() for s in self.additional_numbers]
        d["full_tarot_signature"] = self.full_tarot_signature()
        return d

    def full_tarot_signature(self) -> list:
        """Every unique tarot card across the entire profile."""
        cards = []
        if self.birth_date_profile:
            cards.extend(self.birth_date_profile.all_tarot_cards())
        if self.name_profile:
            for key in ["expression_stack", "soul_urge_stack", "personality_stack"]:
                val = getattr(self.name_profile, key)
                if val:
                    cards.extend(val.tarot_signature())
        for stack in self.additional_numbers:
            cards.extend(stack.tarot_signature())
        return list(dict.fromkeys(cards))


# =============================================================================
# CORE REDUCTION ENGINE
# =============================================================================

def digit_sum(n: int) -> int:
    """Sum the digits of a non-negative integer."""
    return sum(int(d) for d in str(abs(n)))


def stratified_reduce(value: int, label: str = "", preserve_master: bool = True) -> ReductionStack:
    """
    Reduce a number through all intermediate stages.
    Record tarot mapping for each intermediate ≤ 21.
    Preserve master numbers (11, 22, 33) if preserve_master=True.
    """
    stack = ReductionStack(label=label, raw_value=value)
    current = value

    seen = set()  # safety against infinite loops

    while True:
        if current in seen and current >= 10:
            break
        seen.add(current)

        step = ReductionStep(value=current)

        # Tarot mapping
        if 0 <= current <= 21:
            step.tarot_card = MAJOR_ARCANA.get(current)
            step.tarot_card_alt = MAJOR_ARCANA_ALT.get(current)

        # Master number check
        if current in MASTER_NUMBERS:
            step.is_master = True

        # Check if we've reached a root
        if 1 <= current <= 9:
            step.is_root = True
            stack.steps.append(step)
            stack.root = current
            break

        # Master number: record it but also continue to show the reduced form
        if preserve_master and current in MASTER_NUMBERS:
            stack.steps.append(step)
            stack.root = current  # master IS a valid root
            # Also add the reduced form as a secondary
            reduced = digit_sum(current)
            reduced_step = ReductionStep(
                value=reduced,
                tarot_card=MAJOR_ARCANA.get(reduced),
                tarot_card_alt=MAJOR_ARCANA_ALT.get(reduced),
                is_root=True,
            )
            stack.steps.append(reduced_step)
            break

        stack.steps.append(step)
        current = digit_sum(current)

    return stack


def analyze_number(value: int, label: str = "") -> ReductionStack:
    """Analyze any arbitrary number."""
    return stratified_reduce(value, label=label)


# =============================================================================
# DATE ANALYSIS
# =============================================================================

def analyze_date(d: date, label_prefix: str = "Birth") -> DateProfile:
    """
    Full stratified analysis of a date.
    Analyzes: month, day, year (full), year (split high/low), life path.
    """
    profile = DateProfile(raw_date=d.isoformat())

    month = d.month
    day = d.day
    year = d.year

    # Month
    profile.month_stack = stratified_reduce(month, label=f"{label_prefix} Month")

    # Day
    profile.day_stack = stratified_reduce(day, label=f"{label_prefix} Day")

    # Year - full
    profile.year_full_stack = stratified_reduce(year, label=f"{label_prefix} Year (full)")

    # Year - split into two halves
    year_str = str(year)
    if len(year_str) == 4:
        high = int(year_str[:2])
        low = int(year_str[2:])
        profile.year_high_stack = stratified_reduce(high, label=f"{label_prefix} Year (high: {high})")
        profile.year_low_stack = stratified_reduce(low, label=f"{label_prefix} Year (low: {low})")

    # Life Path - sum of all components then reduce
    life_path_raw = digit_sum(month) + digit_sum(day) + digit_sum(year)
    # Wait - traditional life path reduces each component first, then sums
    # Let's do it the traditional way: reduce month, day, year separately, then sum and reduce
    m_root = _reduce_to_root(month)
    d_root = _reduce_to_root(day)
    y_root = _reduce_to_root(year)
    lp_sum = m_root + d_root + y_root
    profile.life_path_stack = stratified_reduce(lp_sum, label=f"{label_prefix} Life Path")

    return profile


def _reduce_to_root(n: int) -> int:
    """Reduce to single digit or master number."""
    while n > 9 and n not in MASTER_NUMBERS:
        n = digit_sum(n)
    return n


# =============================================================================
# NAME ANALYSIS (Pythagorean System)
# =============================================================================

PYTHAGOREAN_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}

VOWELS = set('AEIOU')
# Y is treated as a vowel when it's the only vowel sound in a syllable
# For simplicity, we treat Y as a consonant by default (can be overridden)


def _name_to_values(name: str, filter_fn=None) -> list:
    """Convert name characters to Pythagorean values, optionally filtering."""
    values = []
    for char in name.upper():
        if char.isalpha():
            if filter_fn is None or filter_fn(char):
                values.append(PYTHAGOREAN_MAP.get(char, 0))
    return values


def analyze_name(full_name: str) -> NameProfile:
    """Full numerology analysis of a name."""
    profile = NameProfile(full_name=full_name)

    # Expression number (all letters)
    all_values = _name_to_values(full_name)
    if all_values:
        profile.expression_stack = stratified_reduce(
            sum(all_values), label="Expression/Destiny Number"
        )

    # Soul Urge (vowels only)
    vowel_values = _name_to_values(full_name, filter_fn=lambda c: c in VOWELS)
    if vowel_values:
        profile.soul_urge_stack = stratified_reduce(
            sum(vowel_values), label="Soul Urge/Heart's Desire Number"
        )

    # Personality (consonants only)
    consonant_values = _name_to_values(full_name, filter_fn=lambda c: c not in VOWELS)
    if consonant_values:
        profile.personality_stack = stratified_reduce(
            sum(consonant_values), label="Personality Number"
        )

    return profile


# =============================================================================
# FULL PROFILE BUILDER
# =============================================================================

def build_profile(
    name: str,
    birth_date: date,
    additional_numbers: Optional[dict] = None,
) -> NumerologyProfile:
    """
    Build a complete numerology profile for a subject.

    Args:
        name: Full name
        birth_date: Date of birth
        additional_numbers: Dict of {label: number} for any extra numbers to analyze
    """
    profile = NumerologyProfile(name=name)
    profile.birth_date_profile = analyze_date(birth_date)
    profile.name_profile = analyze_name(name)

    if additional_numbers:
        for label, value in additional_numbers.items():
            profile.additional_numbers.append(
                analyze_number(value, label=label)
            )

    return profile


# =============================================================================
# COMPARISON ENGINE
# =============================================================================

@dataclass
class ResonanceResult:
    """Result of comparing two numerology profiles."""
    subject_a: str
    subject_b: str
    shared_root_numbers: list = field(default_factory=list)
    shared_tarot_cards: list = field(default_factory=list)
    complementary_numbers: list = field(default_factory=list)
    mirror_pairs: list = field(default_factory=list)
    shared_master_numbers: list = field(default_factory=list)
    detail_notes: list = field(default_factory=list)

    def to_dict(self):
        return {
            "subject_a": self.subject_a,
            "subject_b": self.subject_b,
            "shared_root_numbers": self.shared_root_numbers,
            "shared_tarot_cards": self.shared_tarot_cards,
            "complementary_numbers": self.complementary_numbers,
            "mirror_pairs": self.mirror_pairs,
            "shared_master_numbers": self.shared_master_numbers,
            "detail_notes": self.detail_notes,
        }


# Mirror pairs: numbers that sum to 10 (completion)
MIRROR_MAP = {1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 3, 8: 2, 9: 1}


def _collect_all_roots(profile: NumerologyProfile) -> set:
    """Collect all root numbers from a profile."""
    roots = set()
    if profile.birth_date_profile:
        roots.update(profile.birth_date_profile.all_root_numbers())
    if profile.name_profile:
        for key in ["expression_stack", "soul_urge_stack", "personality_stack"]:
            val = getattr(profile.name_profile, key)
            if val:
                roots.add(val.root)
    for stack in profile.additional_numbers:
        roots.add(stack.root)
    return roots


def _collect_all_intermediates(profile: NumerologyProfile) -> set:
    """Collect all intermediate values from all stacks."""
    values = set()
    stacks = []
    if profile.birth_date_profile:
        for key in ["month_stack", "day_stack", "year_full_stack",
                     "year_high_stack", "year_low_stack", "life_path_stack"]:
            val = getattr(profile.birth_date_profile, key)
            if val:
                stacks.append(val)
    if profile.name_profile:
        for key in ["expression_stack", "soul_urge_stack", "personality_stack"]:
            val = getattr(profile.name_profile, key)
            if val:
                stacks.append(val)
    stacks.extend(profile.additional_numbers)

    for stack in stacks:
        for step in stack.steps:
            values.add(step.value)
    return values


def _collect_master_numbers(profile: NumerologyProfile) -> set:
    """Collect any master numbers that appear in any stack."""
    masters = set()
    stacks = []
    if profile.birth_date_profile:
        for key in ["month_stack", "day_stack", "year_full_stack",
                     "year_high_stack", "year_low_stack", "life_path_stack"]:
            val = getattr(profile.birth_date_profile, key)
            if val:
                stacks.append(val)
    if profile.name_profile:
        for key in ["expression_stack", "soul_urge_stack", "personality_stack"]:
            val = getattr(profile.name_profile, key)
            if val:
                stacks.append(val)
    stacks.extend(profile.additional_numbers)

    for stack in stacks:
        for step in stack.steps:
            if step.is_master:
                masters.add(step.value)
    return masters


def compare_profiles(profile_a: NumerologyProfile, profile_b: NumerologyProfile) -> ResonanceResult:
    """Compare two numerology profiles for resonance patterns."""
    result = ResonanceResult(
        subject_a=profile_a.name,
        subject_b=profile_b.name,
    )

    # Shared root numbers
    roots_a = _collect_all_roots(profile_a)
    roots_b = _collect_all_roots(profile_b)
    shared_roots = roots_a & roots_b
    result.shared_root_numbers = sorted(shared_roots)

    if shared_roots:
        result.detail_notes.append(
            f"Shared root numbers: {sorted(shared_roots)} — these represent core vibrational alignment"
        )

    # Shared tarot cards
    tarot_a = set(profile_a.full_tarot_signature())
    tarot_b = set(profile_b.full_tarot_signature())
    shared_tarot = tarot_a & tarot_b
    result.shared_tarot_cards = sorted(shared_tarot)

    if shared_tarot:
        result.detail_notes.append(
            f"Shared tarot signatures: {sorted(shared_tarot)} — archetypal resonance across reduction stacks"
        )

    # Mirror pairs
    for root_a in roots_a:
        mirror = MIRROR_MAP.get(root_a)
        if mirror and mirror in roots_b:
            pair = tuple(sorted([root_a, mirror]))
            if pair not in result.mirror_pairs:
                result.mirror_pairs.append(pair)

    if result.mirror_pairs:
        result.detail_notes.append(
            f"Mirror pairs (sum to 10 = completion): {result.mirror_pairs}"
        )

    # Complementary numbers (numbers that together form a master number)
    all_a = _collect_all_intermediates(profile_a)
    all_b = _collect_all_intermediates(profile_b)
    for master in [11, 22, 33]:
        for val_a in all_a:
            complement = master - val_a
            if complement > 0 and complement in all_b:
                result.complementary_numbers.append({
                    "master": master,
                    "from_a": val_a,
                    "from_b": complement,
                })

    # Shared master numbers
    masters_a = _collect_master_numbers(profile_a)
    masters_b = _collect_master_numbers(profile_b)
    shared_masters = masters_a & masters_b
    result.shared_master_numbers = sorted(shared_masters)

    if shared_masters:
        result.detail_notes.append(
            f"Shared master numbers: {sorted(shared_masters)} — high-frequency alignment"
        )

    return result


# =============================================================================
# REPORT GENERATION
# =============================================================================

def _stack_to_markdown(stack: ReductionStack, indent: str = "") -> str:
    """Render a reduction stack as markdown."""
    lines = []
    lines.append(f"{indent}**{stack.label}** (raw: {stack.raw_value})")

    path_parts = []
    for step in stack.steps:
        part = str(step.value)
        if step.tarot_card:
            part += f" [{step.tarot_card}]"
        if step.is_master:
            part += " ★master"
        if step.is_root:
            part += " ◆root"
        path_parts.append(part)

    lines.append(f"{indent}Reduction: {' → '.join(path_parts)}")
    return "\n".join(lines)


def profile_to_markdown(profile: NumerologyProfile) -> str:
    """Generate a markdown report for a single profile."""
    lines = []
    lines.append(f"# Numerology Profile: {profile.name}")
    lines.append("")

    if profile.birth_date_profile:
        bp = profile.birth_date_profile
        lines.append(f"## Birth Date Analysis: {bp.raw_date}")
        lines.append("")
        for key in ["month_stack", "day_stack", "year_full_stack",
                     "year_high_stack", "year_low_stack", "life_path_stack"]:
            val = getattr(bp, key)
            if val:
                lines.append(_stack_to_markdown(val))
                lines.append("")

        lines.append(f"### Complete Birth Tarot Signature")
        lines.append(f"{', '.join(bp.all_tarot_cards())}")
        lines.append("")
        lines.append(f"### Root Number Set")
        lines.append(f"{bp.all_root_numbers()}")
        lines.append("")

    if profile.name_profile:
        np = profile.name_profile
        lines.append(f"## Name Analysis: {np.full_name}")
        lines.append("")
        for key in ["expression_stack", "soul_urge_stack", "personality_stack"]:
            val = getattr(np, key)
            if val:
                lines.append(_stack_to_markdown(val))
                lines.append("")

    if profile.additional_numbers:
        lines.append("## Additional Numbers")
        lines.append("")
        for stack in profile.additional_numbers:
            lines.append(_stack_to_markdown(stack))
            lines.append("")

    lines.append("## Full Tarot Signature (All Sources)")
    lines.append(f"{', '.join(profile.full_tarot_signature())}")
    lines.append("")

    return "\n".join(lines)


def comparison_to_markdown(
    profile_a: NumerologyProfile,
    profile_b: NumerologyProfile,
    result: ResonanceResult,
) -> str:
    """Generate a comparison report."""
    lines = []
    lines.append(f"# Soul Stratigraphy: Numerological Resonance Report")
    lines.append(f"## {result.subject_a} ↔ {result.subject_b}")
    lines.append(f"*Generated: {datetime.now().isoformat()}*")
    lines.append("")

    # Side by side roots
    lines.append("## Root Number Comparison")
    lines.append("")
    lines.append(f"| Component | {result.subject_a} | {result.subject_b} | Match |")
    lines.append(f"|-----------|{'-' * (len(result.subject_a) + 2)}|{'-' * (len(result.subject_b) + 2)}|-------|")

    def _get_root(profile, stack_path):
        parts = stack_path.split(".")
        obj = profile
        for part in parts:
            obj = getattr(obj, part, None)
            if obj is None:
                return "—"
        return str(obj.root) if hasattr(obj, 'root') else "—"

    comparisons = [
        ("Life Path", "birth_date_profile.life_path_stack"),
        ("Month", "birth_date_profile.month_stack"),
        ("Day", "birth_date_profile.day_stack"),
        ("Year (full)", "birth_date_profile.year_full_stack"),
        ("Expression", "name_profile.expression_stack"),
        ("Soul Urge", "name_profile.soul_urge_stack"),
        ("Personality", "name_profile.personality_stack"),
    ]

    for label, path in comparisons:
        val_a = _get_root(profile_a, path)
        val_b = _get_root(profile_b, path)
        match = "✦" if val_a == val_b and val_a != "—" else ""
        lines.append(f"| {label} | {val_a} | {val_b} | {match} |")

    lines.append("")

    # Shared tarot
    lines.append("## Shared Tarot Signatures")
    if result.shared_tarot_cards:
        for card in result.shared_tarot_cards:
            lines.append(f"- **{card}** — appears in both reduction stacks")
    else:
        lines.append("No shared tarot cards in reduction stacks.")
    lines.append("")

    # Mirror pairs
    lines.append("## Mirror Pairs (Sum to 10)")
    if result.mirror_pairs:
        for pair in result.mirror_pairs:
            lines.append(f"- {pair[0]} ↔ {pair[1]} — completion polarity")
    else:
        lines.append("No mirror pairs detected.")
    lines.append("")

    # Master numbers
    lines.append("## Shared Master Numbers")
    if result.shared_master_numbers:
        for m in result.shared_master_numbers:
            lines.append(f"- **{m}** — high-frequency shared vibration")
    else:
        lines.append("No shared master numbers.")
    lines.append("")

    # Notes
    lines.append("## Analysis Notes")
    for note in result.detail_notes:
        lines.append(f"- {note}")
    lines.append("")

    return "\n".join(lines)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def quick_date_analysis(month: int, day: int, year: int) -> dict:
    """Quick analysis of a date, returns dict."""
    d = date(year, month, day)
    profile = analyze_date(d)
    return profile.to_dict()


def quick_compare(
    name_a: str, birth_a: tuple,
    name_b: str, birth_b: tuple,
) -> dict:
    """
    Quick comparison of two people.
    birth_a/birth_b are (month, day, year) tuples.
    """
    profile_a = build_profile(name_a, date(*reversed(birth_a)))  # expects (year, month, day)
    profile_b = build_profile(name_b, date(*reversed(birth_b)))
    result = compare_profiles(profile_a, profile_b)
    return {
        "profile_a": profile_a.to_dict(),
        "profile_b": profile_b.to_dict(),
        "resonance": result.to_dict(),
    }


# =============================================================================
# CLI / DEMO
# =============================================================================

if __name__ == "__main__":
    # Demo: Seraphe (placeholder DOB) vs Harry Styles
    print("=" * 70)
    print("SOUL STRATIGRAPHY - NUMEROLOGY ENGINE DEMO")
    print("=" * 70)

    # Build profiles
    seraphe = build_profile(
        name="Rebecca Lydia Denkers",
        birth_date=date(1988, 10, 18),
    )

    harry = build_profile(
        name="Harry Edward Styles",
        birth_date=date(1994, 2, 1),
        additional_numbers={
            "One Direction formed (age)": 16,
            "Fine Line track count": 12,
            "Harry's House track count": 13,
        },
    )

    # Print individual profiles
    print(profile_to_markdown(seraphe))
    print("\n" + "=" * 70 + "\n")
    print(profile_to_markdown(harry))

    # Compare
    result = compare_profiles(seraphe, harry)
    print("\n" + "=" * 70 + "\n")
    print(comparison_to_markdown(seraphe, harry, result))

    # Also output JSON
    output = {
        "seraphe": seraphe.to_dict(),
        "harry": harry.to_dict(),
        "resonance": result.to_dict(),
    }
    with open("/home/claude/soul-stratigraphy-feature/demo_output.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    print("\nJSON output written to demo_output.json")
